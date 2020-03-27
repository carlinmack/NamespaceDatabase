"""
This module creates a database connection for other scripts to use.

The connection is configured in the private.cnf function. See public.cnf for an 
example configuration.
"""

import mysql.connector as sql
from mysql.connector import errorcode

def connect():
    """Connect to MySQL database using password stored in options file

    Returns
    -------
    database: MySQLConnection - connection to the MySQL DB
    cursor: MySQLCursor - cursor allowing CRUD actions on the DB connections
    """
    try:
        database = sql.connect(
            host="wikiactors.cs.virginia.edu",
            database="wikiactors",
            username="wikiactors",
            option_files="private.cnf",
            option_groups="wikiactors",
            autocommit="true",
        )

        cursor = database.cursor()

    except sql.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        raise
    else:
        return database, cursor