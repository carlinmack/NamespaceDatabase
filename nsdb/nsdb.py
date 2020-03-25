"""
This script finds the fastest mirror, downloads and splits one Wikipedia
dump.

This script relies on running in a bash environment. Windows users are
encouraged to install Windows Subsystem for Linux.

This tool uses a MySQL database.

Please run pip install -r requirements.txt before running this script.
"""

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


def countLines(file) -> int:
    """Returns the number of lines in a file using wc from bash"""
    wordCount = subprocess.check_output(["wc", "-l", file]).decode("utf-8")
    lines = int(wordCount.split(" ")[0])

    return lines


def main():
    """Download a list of dumps if it doesn't exist. If there are no dumps,
    download one and split it, then process the dump on multiple threads"""
    wiki = "enwiki/"
    dump = "20200101/"
    listOfDumps = "../dumps.txt"
    listOfPartitions = "../partitions.txt"
    namespaces = [1]

    if os.path.isfile(listOfDumps):
        with open(listOfDumps) as file:
            firstLine = file.readline().strip()
    else:
        firstLine = ""

    if not re.match(r"\/.*7z$", firstLine):
        fastestMirror = fastest()

        download = subprocess.run(["./download.sh", fastestMirror, wiki, dump])

    # while (files to go)
    while countLines(listOfDumps) > 0:
        print("start")

        # if theres space etc
        if not os.path.exists("../dumps") or len(os.listdir("../partitions")) == 0:
            ## Download one file
            with open(listOfDumps) as file:
                firstLine = file.readline().strip()
                fileName = re.findall(r"\/([^\/]*)$", firstLine)[0]
                print(fileName)

                data = file.read().splitlines(True)

            try:
                fastestMirror
            except NameError:
                fastestMirror = fastest()

            subprocess.run(["wget", "-P", "../archives/", fastestMirror + firstLine])

            # delete first line
            with open(listOfDumps, "w") as file:
                file.writelines(data)

            ## Unzip and delete if successful
            try:
                extract = subprocess.run(
                    ["7z", "e", "../archives/" + fileName, "-o../dumps"]
                )
            except:
                raise
            else:
                # delete archive
                os.remove("../archives/" + fileName)

            ## Split into 40 partitions
            try:
                split()
            except:
                raise
            else:
                # delete dump
                files = glob("../dumps/*.xml*")
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
            with open(listOfPartitions) as file:
                for line in file:
                    query = "INSERT INTO partition (file_name) VALUES (%s)"
                    cursor.execute(query, (line.strip(),))

            database.commit()

            cursor.close()
            database.close()

            # clear partitions.txt
            open(listOfPartitions, "w").close()

        ## fire off 40 concurrenmt jobs - sbatch? hadoop?
        starttime = time.time()
        processes = []
        print("begin")
        for i in range(0, 90):
            print(i)
            process = multiprocessing.Process(target=parse, args=(namespaces, True))
            processes.append(process)

        for process in processes:
            process.start()

        # for i in range(10):
        print(processes)

        for process in processes:
            process.join()

        print("That took {} seconds".format(time.time() - starttime))
        break
        ##   - write status to database - job done (0) or error
        ## while (jobs are running)
        ##   - query jobs
        ##       - restart dumps with errors, mark as restarted
        ##       - remove completed dumps with no error, mark as cleaned
        ##   - if (jobs < max and more-files-to-read and more-space)
        ##       -break loop


if __name__ == "__main__":
    main()
