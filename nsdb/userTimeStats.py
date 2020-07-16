"""
This script ....
"""

import argparse
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

    query = """SELECT count(*) FROM user_time_stats where 
      first_edit is not null;"""
    cursor.execute(query,)
    found = cursor.fetchone()[0]

    cursor.close()
    database.close()

    print(found, total, found / total)

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

    # print(minimum, average / 86400, maximum / 86400, duration / 86400)
    # print(minimum, average, maximum, duration)

    query = """INSERT INTO user_time_stats
        (id, min_time, avg_time, max_time, duration)
        VALUES (%s, %s, %s, %s, %s);"""

    cursor.execute(query, (userId, minimum, average, maximum, duration,))


def firstLast(cursor, userId):
    query = """UPDATE user_time_stats
        SET first_edit = (SELECT MAX(edit_date) FROM edit where user_table_id = %s),
            last_edit  = (SELECT MIN(edit_date) FROM edit where user_table_id = %s)
        WHERE id = %s;"""

    cursor.execute(query, (userId, userId, userId))


def main():
    """A function"""
    tick = time.time()

    usersToDo = statsForAll()

    while usersToDo:
        print("remake cursors")
        database, cursor = Database.connect()
        generateDatabase, generateCursor = Database.connect()

        query = """SELECT user.id FROM user
        LEFT OUTER JOIN user_time_stats
        ON user.id = user_time_stats.id
        WHERE user_time_stats.first_edit is null
        and user.talkpage_number_of_edits > 1;"""

        cursor.execute(query,)
        while True:
            try:
                userId = cursor.fetchone()
            except:
                print('remake inner cursor')
                database, cursor = Database.connect()
                continue
            if userId:
                userId = userId[0]
                # generate(generateCursor, userId)
                firstLast(generateCursor, userId)
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

    return parser


if __name__ == "__main__":
    # argParser = defineArgParser()
    # clArgs = argParser.parse_args()
    main()
