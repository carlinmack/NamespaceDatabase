import re
import subprocess
import os

import mysql.connector as sql
from mysql.connector import errorcode


def countLines(f):
    wc = subprocess.check_output(["wc", "-l", f]).decode("utf-8")
    lines = int(wc.split(" ")[0])

    return lines


def findFastestMirror():
    mirror = subprocess.check_output(["python3", "mirrors.py"]).decode("utf-8").strip()

    return mirror


wiki = "enwiki/"
dump = "20200101/"

if os.path.isfile("dumps.txt"):
    with open("dumps.txt") as f:
        firstLine = f.readline().strip()
else:
    firstLine = ""

if not re.match("\/.*7z$", firstLine):
    fastestMirror = findFastestMirror()

    download = subprocess.run(["./download.sh", fastestMirror, wiki, dump])

# while (files to go)
while countLines("dumps.txt") > 0:
    print("start")

    # if theres space etc
    if not os.path.exists("dumps") or len(os.listdir("dumps")) == 0:
        ## Download one file
        with open("dumps.txt") as f:
            firstLine = f.readline().strip()
            fileName = re.findall("\/([^\/]*)$", firstLine)[0]
            print(fileName)

        try:
            fastestMirror
        except:
            fastestMirror = findFastestMirror()

        subprocess.run(["wget", "-P", "archives/", fastestMirror + firstLine])

        # delete first line

        ## Unzip and delete if successful
        extract = subprocess.run(["7z", "e", "archives/" + fileName, "-odumps"])

        # delete archive

        ## Split into 40 partitions
        split = subprocess.run(
            ["python3", "splitwiki.py", "-n", "40", "-o", "partitions"]
        )

        # delete dump

    ## write jobs to DB ids
    try:
        database = sql.connect(
            host="wikiactors.cs.virginia.edu",
            database="wikiactors",
            username="wikiactors",
            option_files="private.cnf",
            option_groups="wikiactors",
        )

        cursor = database.cursor()
    except sql.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        with open("partitions.txt") as f:
            for line in f:
                query = "INSERT INTO partition (file_name) VALUES (%s)"
                cursor.execute(query, (line.strip(),))

        database.commit()

        cursor.close()
        database.close()

        # clear partitions.txt
        open("partitions.txt", "w").close()

    ## fire off 40 concurrenmt jobs - sbatch? hadoop?
    ##   - read job data from database
    ##   - read XML
    ##   - write data to database
    ##   - write status to database - job done (0) or error
    ## while (jobs are running)
    ##   - query jobs
    ##       - restart dumps with errors, mark as restarted
    ##       - remove completed dumps with no error, mark as cleaned
    ##   - if (jobs < max and more-files-to-read and more-space)
    ##       -break loop
