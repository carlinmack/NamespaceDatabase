"""
This script looks in the dumps/ directory and splits the first file into 40
partitions by default. This can be changed by adjusting the parameters to split()
"""
import glob
import os
import subprocess
import time

from tqdm import tqdm


def countLines(file: str) -> int:
    """Returns the estimated number of lines in a dump using wcle.sh"""
    print("counting lines: ", file)
    lines = int(subprocess.check_output(["./wcle.sh", file]))

    return lines


def addJobToDatabase(cursor, partitionName: str):
    """Inserts partition into the database"""
    query = "INSERT INTO partition (file_name) VALUES (%s)"
    cursor.execute(query, (partitionName,))


def addJobToQueue(queue, jobId: str):
    """Adds partition to the multiprocessing queue"""
    queue.put(jobId)


def split(
    number: int = 10,
    inputFolder: str = "/bigtemp/ckm8gz/dumps/",
    outputFolder: str = "/bigtemp/ckm8gz/partitions/",
    deleteDump: bool = True,
    fileName: str = "",
    queue=0,
    cursor=0,
    dryRun=False,
):
    """Splits Wikipedia dumps into smaller partitions. Creates a file
    partitions.txt with the created partitions.

    The lower the number of partitions, the lower the total size of the partitions
    and the lower the running time to generate them. For this reason, it is recommended
    to set the number to a multiple of the number of processes running splitwiki.

    For example, splitting one dump:
    100 partitions - 5046 seconds - 39.2 GB
     50 partitions - 5002 seconds - 39.2 GB
     10 partitions - 4826 seconds - 37.2 GB
      5 partitions - 3820 seconds - 36   GB
    """
    if not fileName:
        files = glob.glob(inputFolder + "/*.xml*")
        file = files[0]
        fileName = file[len(inputFolder) :]
    else:
        file = inputFolder + fileName

    lines = countLines(file)

    chunkSize = lines / number * 0.4

    header = """<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" 
    version="0.10" xml:lang="en">
    <siteinfo>
    <sitename>Wikipedia</sitename>
    <dbname>enwiki</dbname>
    <base>https://en.wikipedia.org/wiki/Main_Page</base>
    <generator>MediaWiki 1.35.0-wmf.11</generator>
    <case>first-letter</case>
    <namespaces>
        <namespace key="-2" case="first-letter">Media</namespace>
        <namespace key="-1" case="first-letter">Special</namespace>
        <namespace key="0" case="first-letter" />
        <namespace key="1" case="first-letter">Talk</namespace>
        <namespace key="2" case="first-letter">User</namespace>
        <namespace key="3" case="first-letter">User talk</namespace>
        <namespace key="4" case="first-letter">Wikipedia</namespace>
        <namespace key="5" case="first-letter">Wikipedia talk</namespace>
        <namespace key="6" case="first-letter">File</namespace>
        <namespace key="7" case="first-letter">File talk</namespace>
        <namespace key="8" case="first-letter">MediaWiki</namespace>
        <namespace key="9" case="first-letter">MediaWiki talk</namespace>
        <namespace key="10" case="first-letter">Template</namespace>
        <namespace key="11" case="first-letter">Template talk</namespace>
        <namespace key="12" case="first-letter">Help</namespace>
        <namespace key="13" case="first-letter">Help talk</namespace>
        <namespace key="14" case="first-letter">Category</namespace>
        <namespace key="15" case="first-letter">Category talk</namespace>
        <namespace key="100" case="first-letter">Portal</namespace>
        <namespace key="101" case="first-letter">Portal talk</namespace>
        <namespace key="108" case="first-letter">Book</namespace>
        <namespace key="109" case="first-letter">Book talk</namespace>
        <namespace key="118" case="first-letter">Draft</namespace>
        <namespace key="119" case="first-letter">Draft talk</namespace>
        <namespace key="446" case="first-letter">Education Program</namespace>
        <namespace key="447" case="first-letter">Education Program talk</namespace>
        <namespace key="710" case="first-letter">TimedText</namespace>
        <namespace key="711" case="first-letter">TimedText talk</namespace>
        <namespace key="828" case="first-letter">Module</namespace>
        <namespace key="829" case="first-letter">Module talk</namespace>
        <namespace key="2300" case="first-letter">Gadget</namespace>
        <namespace key="2301" case="first-letter">Gadget talk</namespace>
        <namespace key="2302" case="case-sensitive">Gadget definition</namespace>
        <namespace key="2303" case="case-sensitive">Gadget definition talk</namespace>
    </namespaces>
    </siteinfo>\n"""

    footer = "\n</mediawiki>\n"

    i = 0
    inPage = False
    moreFile = True

    t = tqdm(total=number, desc=fileName, unit=" partition")  # Initialise
    index = 0

    with open(file) as inFile:
        while True:
            if not moreFile:
                t.close()
                break

            partitionName = fileName + "." + str(index)
            outputFileName = os.path.join(outputFolder, partitionName)

            if index > 0 and queue:
                prevPartitionName = fileName + "." + str(index - 1)
                if not dryRun and cursor:
                    addJobToDatabase(cursor, prevPartitionName)
                    time.sleep(1)
                addJobToQueue(queue, prevPartitionName)
            elif not os.path.exists(outputFolder):
                os.mkdir(outputFolder)

            with open(outputFileName, "w+") as outFile:
                outFile.write(header)

                for line in inFile:
                    moreFile = False

                    if inPage:
                        i = i + 1
                        outFile.write(line)
                        if i > chunkSize and line == "  </page>\n":
                            i = 0
                            moreFile = True

                            index = index + 1
                            t.update()
                            break
                    elif line == "  <page>\n":
                        inPage = True
                        i = i + 1
                        outFile.write(line)

                if moreFile:
                    outFile.write(footer)

    if queue:
        partitionName = fileName + "." + str(index)
        if not dryRun and cursor:
            addJobToDatabase(cursor, partitionName)
            time.sleep(1)
        addJobToQueue(queue, partitionName)

    if deleteDump:
        os.remove(file)


if __name__ == "__main__":
    split()
