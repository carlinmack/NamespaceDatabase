import re
import subprocess

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
    with open("dumps.txt") as f:
        firstLine = f.readline().strip()
        fileName = re.findall("\/([^\/]*)$", firstLine)[0]
        print(fileName)

    # subprocess.run(["wget", "-P", "archives/", fastestMirror + firstLine])

    ## Unzip and delete if successful
    # extract = subprocess.run(["7z", "e", "archives/" + fileName, "-odumps"])
    # extract.wait()

    ## Split into 40 partitions
    split = subprocess.run(["python3", "splitwiki.py", "-n", "40", "-o", "partitions"])
    split.wait()
    break

    ## write jobs to DB ids
    ##     id | file name | status | error | start time | end time

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
