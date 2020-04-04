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
import traceback
from datetime import datetime
from sys import argv
from typing import List

import Database
import parse
from mirrors import fastest
from splitwiki import split


def parseReturn(value):
    with open('error/parseReturn.txt', 'a+') as outFile:
        outFile.writelines(str(value))


def parseError(error):
    currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open('error/parseError.txt', 'a+') as outFile:
        outFile.write(currenttime + "\n\n")
        outFile.write(str(error) + "\n\n")
        outFile.write(traceback.format_exc() + "\n\n")


def splitReturn(value):
    with open('error/splitReturn.txt', 'a+') as outFile:
        outFile.writelines(str(value))


def splitError(error):
    currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open('error/splitError.txt', 'a+') as outFile:
        outFile.write(currenttime + "\n\n")
        outFile.write(str(error) + "\n\n")
        outFile.write(traceback.format_exc() + "\n\n")


def createDumpsFile(listOfDumps: str, wiki: str, dump: str):
    """Creates dumps.txt if it doesn't exist"""

    if not os.path.isfile(listOfDumps):
        subprocess.run(["./download.sh", "https://dumps.wikimedia.org/", wiki, dump])


def countLines(file) -> int:
    """Returns the number of lines in a file using wc from bash"""
    wordCount = subprocess.check_output(["wc", "-l", file]).decode("utf-8")
    lines = int(wordCount.split(" ")[0])

    return lines


def downloadFirstDump(listOfDumps, archivesDir, dumpsDir) -> str:
    """Downloads the first dump in dumps.txt"""

    with open(listOfDumps) as file:
        firstLine = file.readline().strip()
        fileName = re.findall(r"\/([^\/]*)$", firstLine)[0]
        print(fileName)

        data = file.read().splitlines(True)

    # delete first line
    with open(listOfDumps, "w") as file:
        file.writelines(data)
    
    print('=== === ===')
    print(dumpsDir + firstLine, flush=True)
    if not os.path.exists(dumpsDir + firstLine):
        fastestMirror = fastest()

        subprocess.run(["wget", "-nc", "-nv", "-P", archivesDir, fastestMirror + firstLine])

    return fileName


def extractFile(fileName: str, archivesDir, dumpsDir):
    """Unzip and delete if successful

    Excecution takes 5-15 minutes as a guideline"""
    if not os.path.exists(dumpsDir + firstLine):
        try:
            subprocess.run(["7z", "e", archivesDir + fileName, "-o" + dumpsDir, "-aos"])
        except:
            raise
        else:
            # delete archive
            os.remove(archivesDir + fileName)
    return fileName[:-3]


def splitFile(fileName, queue, cursor, dumpsDir, partitionsDir, numOfPartitions):
    """Split first dump into 40 partitions"""
    try:
        split(
            fileName=fileName,
            queue=queue,
            cursor=cursor,
            inputFolder=dumpsDir,
            outputFolder=partitionsDir,
            number=numOfPartitions,
        )
    except:
        raise
    else:
        pass


def checkDiskSpace(dataDir):
    """Returns True if the folder is more than 100GB in size"""
    try:
        space = int(
            subprocess.check_output(["du", "-s", dataDir], stderr=subprocess.STDOUT)
            .split()[0]
            .decode("utf-8")
        )
    except:
        space = 999999999

    return space


def outstandingJobs() -> int:
    """Returns number of jobs with status 'todo' or 'failed'"""
    query = "SELECT count(*) FROM partition WHERE status = 'todo' OR status = 'failed';"
    database, cursor = Database.connect()
    try:
        cursor.execute(query)
    except BrokenPipeError:
        numJobs = 0
    except Exception as e: 
        print('fuck', flush=True)
        print(str(e), flush=True)
    else:
        numJobs = cursor.fetchone()[0]

        cursor.close()
        database.close()
    return numJobs


def jobsDone() -> bool:
    """Returns number of jobs with status 'todo' or 'failed'"""
    query = "SELECT count(*) FROM partition WHERE status = 'running' OR status = 'todo'"
    database, cursor = Database.connect()
    try:
        cursor.execute(query)
    except BrokenPipeError:
        numJobs = 1
    else:
        numJobs = cursor.fetchone()[0]

        cursor.close()
        database.close()

    return numJobs == 0


def markLongRunningJobsAsError():
    """Marks jobs that take over 20 minutes as error.

    This doesn't halt execution but does allow the job to be requeued."""
    query = """UPDATE partition
               SET status = 'failed' 
               WHERE TIMESTAMPDIFF(MINUTE,start_time_1,end_time_1) > 15;"""
    # unsure why multi has to be true here but it does ¯\_(ツ)_/¯
    database, cursor = Database.connect()
    try:
        cursor.execute(query, multi=True)
    except BrokenPipeError:
        return


def removeDoneJobs(partitionsDir):
    """Remove partitions that are completed"""
    query = "SELECT file_name FROM partition WHERE status = 'done'"
    database, cursor = Database.connect()
    try:
        cursor.execute(query)
    except BrokenPipeError:
        return

    output = cursor.fetchall()

    for file in output:
        fileName = partitionsDir + file[0]
        if os.path.exists(fileName):
            try:
                os.remove(fileName)
            except FileNotFoundError:
                pass


def restartJobs(namespaces: List[int]):
    """Restart jobs labelled failed, mark them as restarted"""
    return
    query = "SELECT file_name FROM partition WHERE status = 'failed'"
    database, cursor = Database.connect()
    try:
        cursor.execute(query)
    except BrokenPipeError:
        return
    
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


def main(parallel=0, numOfParallel=1, dataDir="/bigtemp/ckm8gz/"):
    """Download a list of dumps if it doesn't exist. If there are no dumps,
    download one and split it, then process the dump on multiple threads

    Parameters
    ----------
    dataDir: str - directory where the dumps, partitions etc will be stored. If you
        are using this on a personal computer, I recommend using '../'. The current
        default is the large storage area at the University of Virginia."""
    wiki = "enwiki/"
    dump = "20200101/"

    listOfDumps = "../dumps.txt"  # not stored in data dir as it stores state

    dumpsDir = os.path.join(dataDir, "dumps/")
    archivesDir = os.path.join(dataDir, "archives/")
    partitionsDir = os.path.join(dataDir, "partitions/")

    namespaces = [1]

    print("main")
    cores = multiprocessing.cpu_count()

    queue = multiprocessing.Manager().Queue()

    if cores > 4:
        # cores - 3 as 1 thread to run nsdb.py and 2 to run splitwiki
        # min, max ensures that it is within 1 and 10
        numOfCores = min(max(cores - 3, 1), 8)
    else:
        numOfCores = max(cores - 2, 1)
    numOfPartitions = 3 * numOfCores

    pool = multiprocessing.Pool(numOfCores)
   
    for _ in range(numOfCores):
        pool.apply_async(
            parse.multiprocess,
            (partitionsDir, namespaces, queue, parallel), 
            callback=parseReturn, 
            error_callback=parseError
        )

    createDumpsFile(listOfDumps, wiki, dump)

    database, cursor = Database.connect()

    # while (things-to-do or jobs still running)
    while countLines(listOfDumps) > 0:
        # if countLines(listOfDumps) > 0:
        print("before")
        if not os.path.exists(dumpsDir) or len(os.listdir(dumpsDir)) < numOfParallel*3:
            print("download")
            tick = time.time()
            fileName = downloadFirstDump(listOfDumps, archivesDir, dumpsDir)
            print(
                "--- Downloading %s took %s seconds ---"
                % (fileName, time.time() - tick)
            )

            tick = time.time()
            fileName = extractFile(fileName, archivesDir, dumpsDir)
            print(
                "--- Extracting %s took %s seconds ---" % (fileName, time.time() - tick)
            )

            tick = time.time()
            splitter = multiprocessing.Pool(1)
            splitter.apply_async(
                splitFile,
                (fileName, queue, cursor, dumpsDir, partitionsDir, numOfPartitions),
                callback=splitReturn, 
                error_callback=splitError
            )
            print(
                "--- Partitioning %s took %s seconds ---"
                % (fileName, time.time() - tick), flush=True
            )

        numJobs = outstandingJobs()
        diskSpace = checkDiskSpace(dataDir)

        if jobsDone():
            print("sleeping", flush=True)
        #     break

        # While (jobs labelled todo|error > threads or no-more-files or no-more-space)
        while numJobs > 10 or diskSpace > 600000000:

            markLongRunningJobsAsError()

            removeDoneJobs(partitionsDir)

            restartJobs(namespaces)

            time.sleep(30)
            numJobs = outstandingJobs()
            diskSpace = checkDiskSpace(dataDir)

        time.sleep(5)

    # clean up Pool
    print("=== EXIT ===")
    cursor.close()
    database.close()


if __name__ == "__main__":
    if len(argv) > 1:
        jobId = argv[1]
        numJobs = int(argv[2])
        main(jobId, numJobs)
    else:
        main()
