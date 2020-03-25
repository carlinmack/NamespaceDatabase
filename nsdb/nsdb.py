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
from typing import List

import mysql.connector as sql
from mysql.connector import errorcode

from mirrors import fastest
from parse import parse
from splitwiki import split


def createDumpsFile(listOfDumps: str, wiki: str, dump: str):
    """Creates dumps.txt if it doesn't exist"""

    if not os.path.isfile(listOfDumps):
        download = subprocess.run(
            ["./download.sh", "https://dumps.wikimedia.org/", wiki, dump]
        )


def countLines(file) -> int:
    """Returns the number of lines in a file using wc from bash"""
    wordCount = subprocess.check_output(["wc", "-l", file]).decode("utf-8")
    lines = int(wordCount.split(" ")[0])

    return lines


def downloadFirstDump(listOfDumps) -> str:
    """Downloads the first dump in dumps.txt"""

    with open(listOfDumps) as file:
        firstLine = file.readline().strip()
        fileName = re.findall(r"\/([^\/]*)$", firstLine)[0]
        print(fileName)

        data = file.read().splitlines(True)

    fastestMirror = fastest()

    subprocess.run(["wget", "-P", "../archives/", fastestMirror + firstLine])

    # delete first line
    with open(listOfDumps, "w") as file:
        file.writelines(data)

    return fileName


def extractFile(fileName: str):
    """Unzip and delete if successful"""
    try:
        extract = subprocess.run(["7z", "e", "../archives/" + fileName, "-o../dumps"])
    except:
        raise
    else:
        # delete archive
        os.remove("../archives/" + fileName)


def splitFile():
    """Split first dump into 40 partitions"""
    try:
        split()
    except:
        raise
    else:
        # delete dump
        files = glob("../dumps/*.xml*")
        file = files[0]
        os.remove(file)


def writeJobIds(listOfPartitions: str):
    """Write list of partitions to database, clears partitions.txt"""
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


def startJobs(namespaces: List[int]):
    """Start 40 concurrent jobs with python's multiprocessing"""
    starttime = time.time()
    processes = []
    print("begin")
    for i in range(0, 90):
        print(i)
        process = multiprocessing.Process(target=parse, args=(namespaces, i))
        processes.append(process)

    for process in processes:
        process.start()

    # for i in range(10):
    print(processes)

    for process in processes:
        process.join()

    print("That took {} seconds".format(time.time() - starttime))


def main():
    """Download a list of dumps if it doesn't exist. If there are no dumps,
    download one and split it, then process the dump on multiple threads"""
    wiki = "enwiki/"
    dump = "20200101/"
    listOfDumps = "../dumps.txt"
    listOfPartitions = "../partitions.txt"
    namespaces = [1]

    createDumpsFile(listOfDumps, wiki, dump)

    # while (things-to-do or jobs still running)
    while countLines(listOfDumps) > 0:
        print("start")

        # if countLines(listOfDumps) > 0:
        if not os.path.exists("../dumps") or len(os.listdir("../partitions")) == 0:
            fileName = downloadFirstDump(listOfDumps)

            extractFile(fileName)

            splitFile()

            # writeJobIds(listOfPartitions)

            # add jobs to queue ?
            # startJobs(namespaces)

        writeJobIds(listOfPartitions)

        # While (jobs labelled todo|error > threads or no-more-files or no-more-space)

            # Mark jobs as error if taken too long

            # Remove completed dumps with no error, mark as cleaned

            # add dumps labelled failed to sbatch queue, mark as restarted

            # sleep
        startJobs(namespaces)

        break


if __name__ == "__main__":
    main()
