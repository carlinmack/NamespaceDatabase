Module [nsdb](nsdb/nsdb.py)
===========
This script finds the fastest mirror, downloads and splits one Wikipedia
dump.

This script relies on running in a bash environment. Windows users are
encouraged to install Windows Subsystem for Linux.

This tool uses a MySQL database.

Please run pip install -r requirements.txt before running this script.

Functions
---------

    
`countLines(file)`
:   Returns the number of lines in a file using wc from bash

    
`createDumpsFile(listOfDumps, wiki, dump)`
:   Creates dumps.txt if it doesn't exist

    
`downloadFirstDump(listOfDumps)`
:   Downloads the first dump in dumps.txt

    
`extractFile(fileName)`
:   Unzip and delete if successful

    
`main()`
:   Download a list of dumps if it doesn't exist. If there are no dumps,
    download one and split it, then process the dump on multiple threads

    
`markLongRunningJobsAsError(cursor)`
:   Marks jobs that take over 20 minutes as error.
    
    This doesn't halt execution but does allow the job to be requeued.

    
`outstandingJobs(cursor)`
:   Returns number of jobs with status 'todo' or 'failed'

    
`removeDoneJobs(cursor)`
:   Remove partitions that are completed

    
`restartJobs(namespaces, cursor)`
:   Restart jobs labelled failed, mark them as restarted

    
`splitFile()`
:   Split first dump into 40 partitions

    
`startJobs(namespaces, cursor)`
:   Start 40 concurrent jobs with python's multiprocessing

    
`writeJobIds(listOfPartitions, cursor)`
:   Write list of partitions to database, clears partitions.txt

-----


Module [parse](nsdb/parse.py)
============
This script allows the user to parse a dump from a database connection
and extract features to a database table.

This tool uses a MySQL database that is configured in the Database() module.

Functions
---------

    
`cleanString(string)`
:   Removes special characters and unnecessary whitespace from text

    
`containsVulgarity(string)`
:   Returns whether text contains profanity based on a simple wordlist approach

    
`getDiff(old, new, parallel)`
:   Returns the diff between two edits using wdiff
    
    Parameters
    ----------
    old : str - old revision
    new : str - new revision
    
    Returns
    -------
    added: str - all the text that is exclusively in the new revision
    deleted: str - all the text that is exclusively in the old revision
    parallel: int - id of the parallel process, 0 if not

    
`getDump(cursor)`
:   Returns the next dump to be parsed from the database
    
    Parameters
    ----------
    cursor: MySQLCursor - cursor allowing CRUD actions on the DB connections
    
    Returns
    -------
    dump: class 'mwxml.iteration.dump.Dump' - dump file iterator
    filename: str - filename of dump

    
`longestCharSequence(string)`
:   Returns the length of the longest repeated character sequence in text

    
`longestWord(string)`
:   Returns the length of the longest word in text

    
`parse(namespaces=[1], parallel=0)`
:   Selects the next dump from the database, extracts the features and
    imports them into several database tables.
    
    Detailed extraction of features is performed for namespaces of interest.
    Pages that are not in the namespace of choice will instead only have the edits
    counted per user.
    
    Parameters
    ----------
    namespaces : list[int] - Wikipedia namespaces of interest.
    parallel: Int - whether to parse with multiple cores

    
`parseNonTargetNamespace(page, title, namespace, cursor, parallel)`
:   Counts the number of edits each user makes and inserts them to the database.
    
    Parameters
    ----------
    page: mwtypes.Page
    title: str - Title of the page
    namespace: str - Namespace of the page
    cursor: MySQLCursor - cursor allowing CRUD actions on the DB connections
    parallel: Int - >0 if called from parallel, hides progress bars

    
`parseTargetNamespace(page, title, namespace, cursor, parallel)`
:   Extracts features from each revision of a page into a database
    
    Ignores edits that have been deleted like:
        https://en.wikipedia.org/w/index.php?oldid=614217720
    
    Parameters
    ----------
    page: mwtypes.Page
    title: str - Title of the page
    namespace: str - Namespace of the page
    cursor: MySQLCursor - cursor allowing CRUD actions on the DB connections
    parallel: Int - id number of parallel slurm process, >0 if called from parallel, 
      hides progress bars

    
`ratioCapitals(string)`
:   Returns the ratio of uppercase to lowercase characters in text

    
`ratioDigits(string)`
:   Returns the ratio of digits to all characters in text

    
`ratioPronouns(string)`
:   Returns the ratio of personal pronouns to all words in text

    
`ratioSpecial(string)`
:   Returns the ratio of special characters to all characters in text

    
`ratioWhitespace(string)`
:   Returns the ratio of whitespace to all characters in text

-----


Module [splitwiki](nsdb/splitwiki.py)
================
This script looks in the dumps/ directory and splits the first file into 40
partitions by default. This can be changed by adjusting the parameters to split()

Functions
---------

    
`countLines(file)`
:   Returns the estimated number of lines in a dump using wcle.sh

    
`split(number=40, inputFolder='../dumps', outputFolder='../partitions', deleteDump=True)`
:   Splits Wikipedia dumps into smaller partitions. Creates a file
    partitions.txt with the created partitions.

-----


Module [mirrors](nsdb/mirrors.py)
==============
This script finds the fastest mirror to download Wikipedia dumps from

Functions
---------

    
`fastest()`
:   Gets a list of the fastest mirrors, downloads a single file from each
    and returns the fastest one
    
    Returns
    -------
    fastestMirror: str - the url of the fastest mirror

-----


Module [Database](nsdb/Database.py)
===============
This module creates a database connection for other scripts to use.

The connection is configured in the private.cnf function. See public.cnf for an 
example configuration.

Functions
---------

    
`connect()`
:   Connect to MySQL database using password stored in options file
    
    Returns
    -------
    database: MySQLConnection - connection to the MySQL DB
    cursor: MySQLCursor - cursor allowing CRUD actions on the DB connections

-----
