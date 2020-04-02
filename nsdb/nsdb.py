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
from sys import argv
import time
from datetime import datetime
from glob import glob
from typing import List

import Database
from mirrors import fastest
import parse
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


def downloadFirstDump(listOfDumps, archivesDir) -> str:
    """Downloads the first dump in dumps.txt"""

    with open(listOfDumps) as file:
        firstLine = file.readline().strip()
        fileName = re.findall(r"\/([^\/]*)$", firstLine)[0]
        print(fileName)

        data = file.read().splitlines(True)

    # delete first line
    with open(listOfDumps, "w") as file:
        file.writelines(data)

    fastestMirror = fastest()

    subprocess.run(["wget", "-nc", "-P", archivesDir, fastestMirror + firstLine])

    return fileName


def extractFile(fileName: str, archivesDir, dumpsDir):
    """Unzip and delete if successful
    
    Excecution takes 5-15 minutes as a guideline"""
    try:
        extract = subprocess.run(["7z", "e", archivesDir + fileName, "-o" + dumpsDir, '-aos'])
    except:
        raise
    else:
        # delete archive
        os.remove(archivesDir + fileName)
        return fileName[:-3]


def splitFile(fileName, queue, cursor, dumps, partitionsDir, numOfPartitions):
    """Split first dump into 40 partitions"""
    try:
        split(fileName=fileName, queue=queue, cursor=cursor, inputFolder=dumps, outputFolder=partitionsDir,number=numOfPartitions,)
    except:
        raise
    else:
        pass


def writeJobIds(fileName, numberOfPartitions: str, cursor):
    """Write list of partitions to database"""
    for index in range(numberOfPartitions):
        partitionName = fileName + "." + str(index)
        query = "INSERT INTO partition (file_name) VALUES (%s)"
        cursor.execute(query, (partitionName,))


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


def noDiskSpace(dataDir):
    """Returns True if the folder is more than 100GB in size"""    
    try:
        space = int(
            subprocess.check_output(["du", "-s", dataDir], stderr=subprocess.STDOUT).split()[0].decode("utf-8")
        )
    except:
        space = 999999999
        
    return space > 150000000


def outstandingJobs(cursor) -> int:
    """Returns number of jobs with status 'todo' or 'failed'"""
    query = "SELECT count(*) FROM partition WHERE status = 'todo' OR status = 'failed'"
    cursor.execute(query)
    numJobs = cursor.fetchone()[0]

    numJobs = max(numJobs - 25, 0)

    return numJobs


def jobsDone(cursor) -> bool:
    """Returns number of jobs with status 'todo' or 'failed'"""
    query = "SELECT count(*) FROM partition WHERE status = 'running' OR status = 'todo'"
    cursor.execute(query)
    numJobs = cursor.fetchone()[0]

    return numJobs == 0


def markLongRunningJobsAsError(cursor):
    """Marks jobs that take over 20 minutes as error.

    This doesn't halt execution but does allow the job to be requeued."""
    query = "UPDATE partition SET status = 'failed' WHERE TIMESTAMPDIFF(MINUTE,start_time_1,end_time_1) > 15;"
    cursor.execute(query)


def removeDoneJobs(cursor, partitionsDir):
    """Remove partitions that are completed"""
    query = "SELECT file_name FROM partition WHERE status = 'done'"
    cursor.execute(query)
    output = cursor.fetchall()

    for file in output:
        fileName = partitionsDir + file[0]
        if os.path.exists(fileName):
            try:
                os.remove(fileName)
            except FileNotFoundError:
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
        # cursor.execute(query, (currenttime, file))


def main(parallel=0, dataDir="/bigtemp/ckm8gz/"):
    """Download a list of dumps if it doesn't exist. If there are no dumps,
    download one and split it, then process the dump on multiple threads

    Parameters
    ----------
    dataDir: str - directory where the dumps, partitions etc will be stored. If you 
        are using this on a personal computer, I recommend using '../'. The current 
        default is the large storage area at the University of Virginia."""
    wiki = "enwiki/"
    dump = "20200101/"
    
    listOfDumps = "../dumps.txt" # not stored in data dir as it stores state

    dumpsDir = os.path.join(dataDir, "dumps/")
    archivesDir = os.path.join(dataDir, "archives/")
    partitionsDir = os.path.join(dataDir, "partitions/")
    
    namespaces = [1]

    print("main")
    cores = multiprocessing.cpu_count()

    queue = multiprocessing.Queue()

    # cores - 2 as 1 thread to run nsdb.py and 1 to run splitwiki
    # min, max ensures that it is within 1 and 10
    numOfCores = min(max(cores-2, 1), 10)
    numOfPartitions = 3 * numOfCores

    pool = multiprocessing.Pool(numOfCores, parse.multiprocess, (partitionsDir,namespaces, queue, parallel))
    
    createDumpsFile(listOfDumps, wiki, dump)
    
    database, cursor = Database.connect()

    # while (things-to-do or jobs still running)
    while countLines(listOfDumps) > 0:
        # if countLines(listOfDumps) > 0:
        print("before")
        if not os.path.exists(dumpsDir) or len(os.listdir(dumpsDir)) < 8:
            print("download")
            tick = time.time()
            fileName = downloadFirstDump(listOfDumps, archivesDir)
            print("--- Downloading %s took %s seconds ---" % (fileName, time.time() - tick))

            tick = time.time()
            fileName = extractFile(fileName, archivesDir, dumpsDir)
            print("--- Extracting %s took %s seconds ---" % (fileName, time.time() - tick))

            tick = time.time()
            splitter = multiprocessing.Pool(1, splitFile, (fileName, queue, cursor, dumpsDir, partitionsDir, numOfPartitions))
            print("--- Partitioning %s took %s seconds ---" % (fileName, time.time() - tick))

        jobsTodo = outstandingJobs(cursor)

        if jobsDone(cursor):
            print("sleeping")
        #     break

        print(queue)

        # While (jobs labelled todo|error > threads or no-more-files or no-more-space)
        while jobsTodo or noDiskSpace(dataDir):

            # Mark jobs as error if taken too long
            markLongRunningJobsAsError(cursor)

            removeDoneJobs(cursor, partitionsDir)

            restartJobs(namespaces, cursor)

            # sleep
            time.sleep(30)
            jobsTodo = outstandingJobs(cursor)
            
        time.sleep(5)

    # clean up Pool

    cursor.close()
    database.close()


if __name__ == "__main__":
    if len(argv) > 1:
        id = argv[1]
        main(id)
    else:
        main()
