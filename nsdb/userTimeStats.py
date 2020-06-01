"""
This script ....
"""

import argparse
import os
import sys
import time
from datetime import datetime
from statistics import mean

import Database


def statsForAll():
    database, cursor = Database.connect()

    query = """SELECT count(*) FROM user
    WHERE talkpage_number_of_edits > 1;"""
    cursor.execute(query,)
    total = cursor.fetchone()[0]

    query = """SELECT count(*) FROM user_time_stats;"""
    cursor.execute(query,)
    found = cursor.fetchone()[0]

    cursor.close()
    database.close()

    return found < total


def generate(cursor, userId):
    query = """Select edit_date
    from edit 
    where user_table_id = %s
    order by edit_date;"""

    cursor.execute(query, (userId,))

    first = old = cursor.fetchone()[0]

    editTimes = []

    while old:
        new = cursor.fetchone()
        if new:
            new = new[0]
            editTimes.append((new - old).total_seconds())
            old = new
        else:
            break

    last = old

    minimum = min(editTimes)
    maximum = max(editTimes)
    average = mean(editTimes)
    duration = (last - first).total_seconds()

    query = """INSERT INTO user_time_stats
        (id, min_time, avg_time, max_time, duration)
        VALUES (%s, %s, %s, %s, %s);"""

    cursor.execute(
        query, (userId, minimum, average, maximum, duration,),
    )


def main(namespaces=[1]):
    """A function"""
    tick = time.time()

    usersToDo = statsForAll()

    while usersToDo:
        database, cursor = Database.connect()
        generateDatabase, generateCursor = Database.connect()

        query = """SELECT user.id FROM user
        LEFT OUTER JOIN user_time_stats
        ON user.id = user_time_stats.id
        WHERE user_time_stats.id IS null
        and user.namespaces & %s
        and user.talkpage_number_of_edits > 1;"""

        # to fix, won't work if multiple namespaces are targets
        cursor.execute(query, (namespaces[0],))
        while True:
            try:
                userId = cursor.fetchone()
            except:
                database, cursor = Database.connect()
                continue
            if userId:
                userId = userId[0]
                generate(generateCursor, userId)
            else:
                break

        generateCursor.close()
        generateDatabase.close()
        cursor.close()
        database.close()
        usersToDo = statsForAll()

    print("--- %s seconds ---" % (time.time() - tick))


def defineArgParser():
    """Creates parser for command line arguments"""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "-n",
        "--namespaces",
        help="""Same namespaces which you parsed for [default: 1]""",
        default=[1],
        type=int,
        nargs="+",
    )

    return parser


if __name__ == "__main__":
    argParser = defineArgParser()
    clArgs = argParser.parse_args()
    # plot(dir=clArgs.dir,)
    main(namespaces=clArgs.namespaces,)
