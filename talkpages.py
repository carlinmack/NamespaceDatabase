import re
import subprocess

import mysql.connector as sql
from mysql.connector import errorcode

wiki = "enwiki/"
dump = "20200101/"

# fastestMirror=$(python3 mirrors.py)
fastestMirror = "http://dumps.wikimedia.org"
# echo $fastestMirror
# ./download.sh $fastestMirror $wiki $dump


def countLines(f):
    wc = subprocess.check_output(["wc", "-l", f]).decode("utf-8")
    lines = int(wc.split(" ")[0])

    return lines


# while (files to go)
while countLines("dumps.txt") > 0:
    print("start")
    ## Download one file
    # with open("dumps.txt") as f:
    #     firstLine = f.readline().strip()
    #     fileName = re.findall("\/([^\/]*)$", firstLine)[0]
    #     print(fileName)

    # subprocess.run(["wget", "-P", "archives/", fastestMirror + firstLine])

    ## Unzip and delete if successful
    # extract = subprocess.run(["7z", "e", "archives/" + fileName, "-odumps"])
    # extract.wait()

    ## Split into 40 partitions
    # split = subprocess.run(["python3", "splitwiki.py", "-n", "40", "-o", "partitions"])
    # split.wait()

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
                cursor.execute(query, (line,))

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
