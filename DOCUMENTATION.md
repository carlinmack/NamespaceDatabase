Module talkpages
================
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

    
`main()`
:   Download a list of dumps if it doesn't exist. If there are no dumps,
    download one and split it, then process the dump on multiple threads


Module parse
============
This script allows the user to parse a dump from a database connection
and extract features to a database table.

This tool uses a MySQL database that is configured in the parse() function.

Please run pip install -r requirements.txt before running this script.

Functions
---------

    
`cleanString(string)`
:   Removes special characters and unnecessary whitespace from text

    
`databaseConnect()`
:   Connect to MySQL database using password stored in options file
    
    Returns
    -------
    database: MySQLConnection - connection to the MySQL DB
    cursor: MySQLCursor - cursor allowing CRUD actions on the DB connections

    
`getDiff(old, new)`
:   Returns the diff between two edits using wdiff
    
    Parameters
    ----------
    old : str - old revision
    new : str - new revision
    
    Returns
    -------
    added: str - all the text that is exclusively in the new revision
    deleted: str - all the text that is exclusively in the old revision

    
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

    
`parse()`
:   Selects the next dump from the database, extracts the features and
    imports them into several database tables.

    
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


Module splitwiki
================
This script looks in the dumps/ directory and splits the first file into 40
partitions by default. This can be changed by adjusting the parameters to split()

Please run pip install -r requirements.txt before running this script.

Functions
---------

    
`countLines(file)`
:   Returns the estimated number of lines in a dump using wcle.sh

    
`split(number=40, inputFolder='dumps', outputFolder='partitions', deleteDump=True)`
:   Splits Wikipedia dumps into smaller partitions. Creates a file
    partitions.txt with the created partitions.


Module mirrors
==============
This script finds the fastest mirror to download Wikipedia dumps from

Please run pip install -r requirements.txt before running this script.

Functions
---------

    
`fastest()`
:   Gets a list of the fastest mirrors, downloads a single file from each
    and returns the fastest one
    
    Returns
    -------
    fastestMirror: str - the url of the fastest mirror