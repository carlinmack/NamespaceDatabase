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
from datetime import datetime
from glob import glob
from typing import List

import Database
from mirrors import fastest
from parse import parse
from splitwiki import split


def createDumpsFile(listOfDumps: str, wiki: str, dump: str):
    """Creates dumps.txt if it doesn't exist"""

    if not os.path.isfile(listOfDumps):
        subprocess.run(["./download.sh", "https://dumps.wikimedia.org/", wiki, dump])


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


def writeJobIds(listOfPartitions: str, cursor):
    """Write list of partitions to database, clears partitions.txt"""
    with open(listOfPartitions) as file:
        for line in file:
            query = "INSERT INTO partition (file_name) VALUES (%s)"
            cursor.execute(query, (line.strip(),))

    # clear partitions.txt
    open(listOfPartitions, "w").close()


def startJobs(namespaces: List[int], cursor):
    """Start 40 concurrent jobs with python's multiprocessing"""
    starttime = time.time()
    processes = []
    
    for i in range(1, 99):
        process = multiprocessing.Process(target=parse, args=(namespaces, i))
        processes.append(process)

    for process in processes:
        time.sleep(1)
        process.start()

    # for i in range(10):
    print(processes)

    for process in processes:
        process.join()

    print("That took {} seconds".format(time.time() - starttime))


def outstandingJobs(cursor) -> int:
    """Returns number of jobs with status 'todo' or 'failed'"""
    query = "SELECT count(*) FROM partition WHERE status = 'todo' OR status = 'failed'"
    cursor.execute(query)
    numJobs = cursor.fetchone()[0]

    return numJobs


def markLongRunningJobsAsError(cursor):
    """Marks jobs that take over 20 minutes as error.

    This doesn't halt execution but does allow the job to be requeued."""
    query = "UPDATE partition SET status = 'failed' WHERE TIMESTAMPDIFF(MINUTE,start_time_1,end_time_1) > 15;"
    cursor.execute(query)


def removeDoneJobs(cursor):
    """Remove partitions that are completed"""
    query = "SELECT file_name FROM partition WHERE status = 'done'"
    cursor.execute(query)
    output = cursor.fetchall()

    for file in output:
        # os.remove("../partitions/" + file[0])
        pass


def restartJobs(namespaces: List[int], cursor):
    """Restart jobs labelled failed, mark them as restarted"""
    query = "SELECT file_name FROM partition WHERE status = 'failed'"
    cursor.execute(query)
    output = cursor.fetchall()

    for file in output:
        file = file[0]

        # start jobs

        currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = """UPDATE partition
            SET
                status = "restarted",
                start_time_1 = %s
            WHERE file_name = %s;"""
        cursor.execute(query, (currenttime, file))


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
        database, cursor = Database.connect()

        # if countLines(listOfDumps) > 0:
        if not os.path.exists("../dumps") or len(os.listdir("../partitions")) == 0:
            print('download')
            fileName = downloadFirstDump(listOfDumps)

            extractFile(fileName)

            splitFile()

            writeJobIds(listOfPartitions, cursor)

            # add jobs to queue ?
            # startJobs(namespaces)

        startJobs(namespaces, cursor)

        break

        jobsTodo = outstandingJobs(cursor)

        # While (jobs labelled todo|error > threads or no-more-files or no-more-space)
        while jobsTodo:

            # Mark jobs as error if taken too long
            markLongRunningJobsAsError(cursor)

            removeDoneJobs(cursor)

            restartJobs(namespaces, cursor)

            # sleep
            time.sleep(30)
            jobsTodo = outstandingJobs(cursor)

        cursor.close()
        database.close()


if __name__ == "__main__":
    main()
