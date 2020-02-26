import re
import subprocess
#from splitwiki import SplitWiki

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
    # split = SplitWiki()
    # split.split(40, "partitions")
    split = subprocess.run(["python3", "splitwiki.py", "-n", "40", "-o", "partitions"])
    split.wait()
    break

    ## write jobs to DB ids
    ##     id | file name | status | error | start time | end time -- status is in ("done", "error", "failed again", "restarted", "running", "todo", "cleaned")
    ## while (there are jobs in DB labeled (todo or error) and )
    ##    - query jobs
    ##       - remove completed dumps status done (no error), mark as cleaned
    ##    - fire off (40-currently running) concurrent jobs - sbatch? hadoop? (jobs that haven't been run or only restarted once)
    ##       but only fire off jobs labeled "todo" (mark as "running") or "error" (mark as "restarted")
    #       One python script that all "thread" would use
    ##      Individual Job Script
    ##          - read job data from database (job status, filename)
    ##          - read XML
    ##          - write data to database
    ##          - write status to database - job done (0) or error or "failed again"
    ##    while (jobs are running)
    ##       - if (jobs < max and more-files-to-read and more-space)
    ##          - break loop
    ##       - sleep for 10 minutes
