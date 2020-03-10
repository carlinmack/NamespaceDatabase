import multiprocessing
import os
import re
import subprocess
import time
from glob import glob

import mysql.connector as sql
from mysql.connector import errorcode

from mirrors import fastest
from parse import parse
from splitwiki import split


def countLines(file):
    wordCount = subprocess.check_output(["wc", "-l", file]).decode("utf-8")
    lines = int(wordCount.split(" ")[0])

    return lines


wiki = "enwiki/"
dump = "20200101/"

if os.path.isfile("dumps.txt"):
    with open("dumps.txt") as f:
        firstLine = f.readline().strip()
else:
    firstLine = ""

if not re.match("\/.*7z$", firstLine):
    fastestMirror = fastest()

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

            data = f.read().splitlines(True)

        try:
            fastestMirror
        except NameError:
            fastestMirror = fastest()

        subprocess.run(["wget", "-P", "archives/", fastestMirror + firstLine])

        # delete first line
        with open("dumps.txt", "w") as fout:
            fout.writelines(data)

        ## Unzip and delete if successful
        try:
            extract = subprocess.run(["7z", "e", "archives/" + fileName, "-odumps"])
        except:
            raise
        else:
            # delete archive
            os.remove("archives/" + fileName)

        ## Split into 40 partitions
        try:
            split(40, "partitions", True)
        except:
            raise
        else:
            # delete dump
            files = glob("dumps/*.xml*")
            file = files[0]
            os.remove(file)

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
    starttime = time.time()
    processes = []
    print("begin")
    for i in range(0, 20):
        print(i)
        p = multiprocessing.Process(target=parse)
        processes.append(p)

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    print("That took {} seconds".format(time.time() - starttime))
    break
    ##   - write status to database - job done (0) or error
    ## while (jobs are running)
    ##   - query jobs
    ##       - restart dumps with errors, mark as restarted
    ##       - remove completed dumps with no error, mark as cleaned
    ##   - if (jobs < max and more-files-to-read and more-space)
    ##       -break loop
