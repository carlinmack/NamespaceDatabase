"""
This script finds the fastest mirror, downloads and splits one Wikipedia
dump.

This script relies on running in a bash environment. Windows users are
encouraged to install Windows Subsystem for Linux.

This tool uses a MySQL database.

Please run pip install -r requirements.txt before running this script.
"""

import argparse
import http.client
import json
import multiprocessing
import os
import re
import subprocess
import time
import traceback
import urllib
import urllib.request
from datetime import datetime
from typing import List

from tqdm import tqdm

import Database
import parse
from splitwiki import split


def parseError(error):
    """Logs errors from parse processes to a file"""
    currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("error/parseError.txt", "a+") as outFile:
        outFile.write(currenttime + "\n\n")
        outFile.write(str(error) + "\n\n")
        outFile.write(traceback.format_exc() + "\n\n")


def splitError(error):
    """Logs errors from split processes to a file"""
    currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("error/splitError.txt", "a+") as outFile:
        outFile.write(currenttime + "\n\n")
        outFile.write(str(error) + "\n\n")
        outFile.write(traceback.format_exc() + "\n\n")


def createDumpsFile(
    listOfDumps: str = "../dumps.txt",
    wiki: str = "enwiki",
    dump: str = "",
    test: bool = False,
) -> str:
    """Creates dumps.txt if it doesn't exist"""

    if test or not os.path.isfile(listOfDumps):
        mirror = "https://dumps.wikimedia.org/"

        if dump == "":
            # find latest
            url = mirror + wiki
            content = urllib.request.urlopen(url).read().decode("utf-8")
            dumps = re.findall(r"(?<=href=\")\d+(?=/\">)", content)

            for i in reversed(dumps):
                url = mirror + wiki + "/" + i + "/dumpstatus.json"
                content = urllib.request.urlopen(url).read().decode("utf-8")
                metaHistory7z = json.loads(content)["jobs"]["metahistory7zdump"]

                if metaHistory7z["status"] == "done":
                    dump = i
                    break
            else:
                raise RuntimeError("7zip dumps not found at %s." % (mirror,))

        if test:
            url = mirror + wiki + "/" + dump + "/dumpstatus.json"
            content = urllib.request.urlopen(url).read().decode("utf-8")
            metaHistory7z = json.loads(content)["jobs"]["metahistory7zdump"]

            for i in metaHistory7z["files"]:
                size = metaHistory7z["files"][i]["size"] / 1024 / 1024
                if 4 < size < 50:
                    with open(listOfDumps, "w") as file:
                        file.write(metaHistory7z["files"][i]["url"] + "\n")
            return dump

        url = mirror + wiki + "/" + dump

        content = urllib.request.urlopen(url).read().decode("utf-8")
        dumps = re.findall(r'(?<=href="/).*pages-meta-history.*7z(?=")', content)

        if len(dumps) > 0:
            with open(listOfDumps, "w") as file:
                for i in dumps:
                    file.write(i + "\n")
        elif dump == "":
            with open(listOfDumps, "w") as file:
                for i in metaHistory7z["files"]:
                    file.write(metaHistory7z["files"][i]["url"] + "\n")
    else:
        with open(listOfDumps) as file:
            firstLine = file.readline()
            dump = re.search(r"(?<=\/)\d+(?=\/)", firstLine).group()

    return dump


def countLines(file: str) -> int:
    """Returns the number of lines in a file using wc from bash"""
    wordCount = subprocess.check_output(["wc", "-l", file]).decode("utf-8")
    lines = int(wordCount.split(" ")[0])

    return lines


def findFastestMirror(dump: str = "20200401", wiki: str = "enwiki/") -> str:
    """Gets a list of the fastest mirrors, downloads a single file from each
    and returns the fastest one.

    Execution takes 5-10 seconds as a guideline

    Returns
    -------
    fastestMirror: str - the url of the fastest mirror
    """

    # find a list of mirrors
    url = "https://dumps.wikimedia.org/mirrors.html"

    html = urllib.request.urlopen(url).read().decode("utf-8")

    # https is always going to be slower than http for download but check in case mirror
    # is only available over https
    mirrors = re.findall(r'href="(https?:.*)"', html)
    mirrorDownloadTime = []
    dumps = []
    sizes = []

    # Add main site
    mirrors.append("https://dumps.wikimedia.org/")

    # find test file
    url = "https://dumps.wikimedia.org/" + wiki + "/" + dump + "/dumpstatus.json"
    content = urllib.request.urlopen(url).read().decode("utf-8")
    metaHistory7z = json.loads(content)["jobs"]["metahistory7zdump"]

    for i in metaHistory7z["files"]:
        size = metaHistory7z["files"][i]["size"] / 1024 / 1024
        if size > 4:
            if size < 10:
                testFile = i
                break
            dumps.append(i)
            sizes.append(size)
    else:
        _, index = min((val, index) for (index, val) in enumerate(sizes))
        testFile = dumps[index]

    print("Finding fastest mirror")
    for index, mirror in enumerate(tqdm(mirrors, unit=" mirror")):
        url = mirror + wiki + "/" + dump + "/" + testFile

        tick = time.time()
        try:
            urllib.request.urlopen(url)

            # add the time to download
            mirrorDownloadTime.append(time.time() - tick)
        except urllib.error.HTTPError as err:
            if str(err.code)[0] in ["4", "5"]:
                # try other url scheme
                url = mirror + "dumps/" + wiki + dump + testFile

                tick = time.time()
                try:
                    urllib.request.urlopen(url)

                    mirrorDownloadTime.append(time.time() - tick)
                except urllib.error.HTTPError as err:
                    if str(err.code)[0] in ["4", "5"]:
                        mirrorDownloadTime.append(1000)
                    else:
                        raise
            else:
                raise

    # for i in range(len(mirrors)):
    #     print(mirrors[i], mirrorDownloadTime[i])
    # print("Fastest mirror is " + mirrors[index])

    if all(time == 1000 for time in mirrorDownloadTime):
        raise RuntimeError("Dump " + dump + " is no longer hosted on any mirror")

    # return fastest mirror
    _, index = min((val, index) for (index, val) in enumerate(mirrorDownloadTime))

    return mirrors[index]


def downloadDump(dump: str, listOfDumps: str, archivesDir: str, dumpsDir: str) -> str:
    """Downloads the first dump in dumps.txt if it is not already present
    in the dumps directory"""
    # check internet connectivity
    # source https://stackoverflow.com/a/29854274
    conn = http.client.HTTPConnection("www.fast.com", timeout=5)
    for _ in range(5):
        try:
            conn.request("HEAD", "/")
        except:
            conn.close()
        else:
            conn.close()
            break
    else:
        print("Internet connection lost")
        return ""

    with open(listOfDumps) as file:
        firstLine = file.readline().strip()
        fileName = re.findall(r"\/([^\/]*)$", firstLine)[0]
        print("Downloading", fileName)

        data = file.read().splitlines(True)

    # delete first line
    with open(listOfDumps, "w") as file:
        file.writelines(data)

    if not os.path.exists(dumpsDir + fileName[:-3]):
        fastestMirror = findFastestMirror(dump)

        subprocess.run(
            [
                "wget",
                "-nc",
                "-nv",
                "--show-progress",
                "-P",
                archivesDir,
                fastestMirror + firstLine,
            ],
            check=True,
        )

    return fileName


def extractFile(fileName: str, archivesDir: str, dumpsDir: str):
    """Unzip if not already extracted, delete if extracted

    Execution takes 5-15 minutes as a guideline"""
    if not os.path.exists(dumpsDir + fileName[:-3]):
        subprocess.run(
            ["7z", "e", archivesDir + fileName, "-o" + dumpsDir, "-aos"], check=True
        )

    if os.path.exists(archivesDir + fileName):
        os.remove(archivesDir + fileName)

    return fileName[:-3]


def splitFile(
    fileName: str,
    queue,
    dumpsDir: str,
    partitionsDir: str,
    numPartitions: int,
    dryRun: bool,
):
    """Split a dump into a number of partitions"""
    if not dryRun:
        database, cursor = Database.connect()

        split(
            fileName=fileName,
            queue=queue,
            cursor=cursor,
            inputFolder=dumpsDir,
            outputFolder=partitionsDir,
            number=numPartitions,
        )

        cursor.close()
        database.close()
    else:
        split(
            fileName=fileName,
            queue=queue,
            inputFolder=dumpsDir,
            outputFolder=partitionsDir,
            number=numPartitions,
            dryRun=dryRun,
        )


def checkDiskSpace(dataDir: str) -> int:
    """Returns the size of the data directory"""
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
    query = "SELECT count(*) FROM partition WHERE status = 'todo';"
    database, cursor = Database.connect()
    try:
        cursor.execute(query)
    except BrokenPipeError:
        numJobs = 0
        database.close()
    except Exception as e:
        print(str(e), flush=True)
    else:
        numJobs = cursor.fetchone()[0]

        cursor.close()
        database.close()

    return numJobs


def jobsDone() -> bool:
    """Returns True if all jobs are done"""
    query = "SELECT count(*) FROM partition WHERE status = 'running' OR status = 'todo'"
    database, cursor = Database.connect()
    try:
        cursor.execute(query)
    except BrokenPipeError:
        database.close()
        numJobs = 1
    else:
        numJobs = cursor.fetchone()[0]

        cursor.close()
        database.close()

    return numJobs == 0


def markLongRunningJobsAsError():
    """Marks jobs that take over 15 minutes as error.

    This doesn't halt execution but does allow the job to be requeued."""
    query = """UPDATE partition
               SET status = 'failed', error = 'Timed out' 
               WHERE status = 'running'
               AND TIMESTAMPDIFF(MINUTE,start_time_1,CONVERT_TZ(NOW(),'+00:00','-4:00')) > 15;"""
    database, cursor = Database.connect()
    try:
        # unsure why multi has to be true here but it does ¯\_(ツ)_/¯
        cursor.execute(query, multi=True)
    except BrokenPipeError:
        database.close()
        return

    cursor.close()
    database.close()


def removeDoneJobs(partitionsDir: str):
    """Remove partitions that are completed"""
    query = "SELECT file_name FROM partition WHERE status = 'done'"
    database, cursor = Database.connect()
    try:
        cursor.execute(query)
    except BrokenPipeError:
        database.close()
        return

    output = cursor.fetchall()

    for file in output:
        fileName = partitionsDir + file[0]
        if os.path.exists(fileName):
            try:
                os.remove(fileName)
            except FileNotFoundError:
                pass

    cursor.close()
    database.close()


def restartJobs():
    """NOT IMPLEMENTED - Restart jobs labelled failed, mark them as restarted"""
    return
    query = "SELECT file_name FROM partition WHERE status = 'failed'"
    database, cursor = Database.connect()
    try:
        cursor.execute(query)
    except BrokenPipeError:
        database.close()
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
        cursor.execute(query, (currenttime, file))

    cursor.close()
    database.close()


def main(
    wiki: str = "enwiki/",
    dump: str = "",
    namespaces: List[int] = [1],
    parallelID: str = 0,
    numParallel: int = 1,
    dataDir: str = "/bigtemp/ckm8gz/",
    maxSpace: int = 600,
    freeCores: int = 0,
    dryRun: bool = False,
    test: bool = True,
):
    """Download a list of dumps if it doesn't exist. If there are no dumps,
    download one and split it, then process the dump on multiple threads

    Parameters
    ----------
    wiki: str - The name of the wiki you want to use
    dump: str - Which dump you want to use, a date string in the format YYYYMMDD. By
        default will use the dump before latest.
    namespaces: List[int] - Which namespace should be used.
    parallelID: str - set when called from the slurm script. Slurm is used for running
        this tool in a distributed fashion.
    numParallel: int - set when called from the slurm script.
    dataDir: str - directory where the dumps, partitions etc will be stored. If you
        are using this on a personal computer, I recommend using '../'. If external
        storage is available you should enter the path here.
    maxSpace: int - maximum number of gigabytes that you would like the program to use.
        At minimum this should be 50gB.
    freeCores: int - the number of cores you don't want to be used. For best results
        set this to zero."""

    if test:
        listOfDumps = "../test-dumps.txt"  # not stored in data dir as it stores state
    else:
        listOfDumps = "../dumps.txt"

    dumpsDir = os.path.join(dataDir, "dumps/")
    archivesDir = os.path.join(dataDir, "archives/")
    partitionsDir = os.path.join(dataDir, "partitions/")

    cores = max(multiprocessing.cpu_count() - freeCores, 1)
    queue = multiprocessing.Manager().Queue()

    if cores > 4:
        # cores - 3 as 1 thread to run nsdb.py and 2 to run splitwiki
        # min, max ensures that it is within 1 and 10
        numParseCores = min(max(cores - 3, 1), 10)
    else:
        numParseCores = max(cores - 2, 1)

    if numParallel > 1:
        numSplitCores = min(max(cores - 1 - numParseCores, 1), 3)
    else:
        numSplitCores = max(cores - 1 - numParseCores, 1)

    numPartitions = 8 * numParseCores

    parser = multiprocessing.Pool(numParseCores)
    splitter = multiprocessing.Pool(numSplitCores)

    for _ in range(numParseCores):
        parser.apply_async(
            parse.multiprocess,
            (partitionsDir, namespaces, queue, parallelID, dryRun),
            error_callback=parseError,
        )

    dump = createDumpsFile(listOfDumps, wiki, dump, test)

    print("Number of cores available:", cores, " Using dump:", dump)

    # while (things-to-do or jobs still running)
    while countLines(listOfDumps) > 0 or dryRun or jobsDone():
        if countLines(listOfDumps) > 0 and (
            not os.path.exists(dumpsDir)
            or len(os.listdir(dumpsDir)) < numParallel * 3
            or len(splitter._cache) < numSplitCores
        ):
            tick = time.time()
            fileName = downloadDump(dump, listOfDumps, archivesDir, dumpsDir)
            print(
                "--- Downloading %s took %s seconds ---"
                % (fileName, time.time() - tick)
            )

            if fileName != "":
                tick = time.time()
                fileName = extractFile(fileName, archivesDir, dumpsDir)
                print(
                    "--- Extracting %s took %s seconds ---"
                    % (fileName, time.time() - tick)
                )

                splitter.apply_async(
                    splitFile,
                    (fileName, queue, dumpsDir, partitionsDir, numPartitions, dryRun),
                    error_callback=splitError,
                )

        if not dryRun:
            numJobs = outstandingJobs()
            if jobsDone():
                print("sleeping", flush=True)
        else:
            numJobs = 0

        diskSpace = checkDiskSpace(dataDir)

        while numJobs > 30 * numParallel or diskSpace > (maxSpace * 1000000):
            print("in")
            markLongRunningJobsAsError()

            removeDoneJobs(partitionsDir)

            # restartJobs()

            time.sleep(30)
            numJobs = outstandingJobs()
            diskSpace = checkDiskSpace(dataDir)

        time.sleep(5)

    # clean up Pool
    print("=== EXIT ===")


def defineArgParser():
    """Creates parser for command line arguments"""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    def checkPositive(value):
        try:
            ivalue = int(value)
        except:
            raise argparse.ArgumentTypeError("invalid int value: '%s'" % value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError(
                "%s is an invalid positive int value" % value
            )
        return ivalue

    def checkStorageValue(value):
        try:
            ivalue = int(value)
        except:
            raise argparse.ArgumentTypeError("invalid int value: '%s'" % value)
        if ivalue < 50:
            raise argparse.ArgumentTypeError(
                "Available storage value needs to be at least 50"
            )
        return ivalue

    parser.add_argument(
        "--test",
        help="Only download one archive that is below 50MB in size",
        action="store_true",
    )

    parser.add_argument(
        "--dryrun",
        help="Don't use a database, no partitions will be deleted",
        action="store_true",
    )

    parser.add_argument(
        "-w",
        "--wiki",
        help="The name of the wiki you want to use [default: enwiki]",
        default="enwiki",
        type=str,
    )

    parser.add_argument(
        "-d",
        "--dump",
        help="""Which dump you want to use, a date string in the format YYYYMMDD. By
        default will use the dump before latest.""",
        default="",
        type=str,
    )

    parser.add_argument(
        "-n",
        "--namespaces",
        help="""Which namespaces you want to use, these are different for every wiki
                [default: 1]""",
        default=[1],
        type=int,
        nargs="+",
    )

    parser.add_argument(
        "-i",
        "--parallelID",
        help="Set when called from the slurm script [default: 0]",
        default=0,
        type=str,
    )

    parser.add_argument(
        "--numParallel",
        help="Set when called from the slurm script [default: 1]",
        default=1,
        type=checkPositive,
    )

    parser.add_argument(
        "-D",
        "--dataDir",
        help="Directory where the dumps, partitions etc will be stored [default: ../]",
        default="../",
        type=str,
    )

    parser.add_argument(
        "-s",
        "--maxSpace",
        help="Max gigabytes that you would like the program to use. Min 50gB [default: 150]",
        default=150,
        type=checkStorageValue,
    )

    parser.add_argument(
        "-c",
        "--freeCores",
        help="The number of cores you don't want to be used [default: 0]",
        default=0,
        type=checkPositive,
    )

    return parser


if __name__ == "__main__":

    argParser = defineArgParser()
    clArgs = argParser.parse_args()

    main(
        wiki=clArgs.wiki,
        dump=clArgs.dump,
        namespaces=clArgs.namespaces,
        parallelID=clArgs.parallelID,
        numParallel=clArgs.numParallel,
        dataDir=clArgs.dataDir,
        maxSpace=clArgs.maxSpace,
        freeCores=clArgs.freeCores,
        dryRun=clArgs.dryrun,
        test=clArgs.test,
    )
