"""
This script ....
"""
import argparse
import gzip
import json
import os
import re
import urllib
import urllib.request
import subprocess

import Database


def ipGlobalBlocks(dir="lists/"):
    url = "https://dumps.wikimedia.org/other/globalblocks/"

    content = urllib.request.urlopen(url).read().decode("utf-8")

    latest = list(re.findall(r'<a href="(\d+)', content))[-1]

    globalBlocksFile = dir + latest + "-globalblocks.sql"
    globalBlocksArchive = globalBlocksFile + ".gz"

    url = url + latest + "/" + latest + "-globalblocks.gz"

    urllib.request.urlretrieve(url, globalBlocksArchive)

    subprocess.run(["7z", "x", globalBlocksArchive, "-o" + dir, "-aos"], check=True)

    database, cursor = Database.connect()

    with open(globalBlocksFile) as file:
        for result in cursor.execute(file.read(), multi=True):
            if result.with_rows:
                print("Rows produced by statement '{}':".format(result.statement))
                # print(result.fetchall())
            else:
                if result.rowcount != 0:
                    print(
                        "Number of rows affected by statement: {}".format(
                            result.rowcount
                        )
                    )

    # Query OK, 93849 rows affected (3 days 6 hours 15 min 52.43 sec)
    # Rows matched: 93851  Changed: 93849  Warnings: 0
    query = """update user A
    inner join ( 
        select id from user, globalblocks 
        where Is_ipv4(ip_address)  
        and gb_range_start not REGEXP '^v'
        and INET_ATON(ip_address) 
            between Cast(CONV(globalblocks.gb_range_start, 16, 10) as unsigned)
            and Cast(CONV(globalblocks.gb_range_end, 16, 10) as unsigned)
            limit 100000
    ) as B on A.id = B.id
    set blocked = 1; """

    cursor.execute(query,)

    os.remove(globalBlocksFile)
    os.remove(globalBlocksArchive)

    cursor.close()
    database.close()


def goodUsers(dir="lists/"):
    # find latest
    url = "https://dumps.wikimedia.org/enwiki"
    userGroupsFile = dir + "userGroups.sql"
    userGroupsArchive = userGroupsFile + ".gz"

    if not os.path.exists(userGroupsArchive):
        content = urllib.request.urlopen(url).read().decode("utf-8")
        dumps = re.findall(r"(?<=href=\")\d+(?=/\">)", content)

        userGroupsUrl = "https://dumps.wikimedia.org"

        for i in reversed(dumps):
            url = "https://dumps.wikimedia.org/enwiki/" + i + "/dumpstatus.json"
            content = urllib.request.urlopen(url).read().decode("utf-8")
            usergroups = json.loads(content)["jobs"]["usergroupstable"]

            if usergroups["status"] == "done":
                userGroupsUrl = (
                    userGroupsUrl + list(usergroups["files"].values())[0]["url"]
                )
                break

        urllib.request.urlretrieve(userGroupsUrl, userGroupsArchive)

        subprocess.run(["7z", "x", userGroupsArchive, "-o" + dir, "-aos"], check=True)

        database, cursor = Database.connect()

        with open(userGroupsFile) as file:
            for result in cursor.execute(file.read(), multi=True):
                if result.with_rows:
                    print("Rows produced by statement '{}':".format(result.statement))
                    # print(result.fetchall())
                else:
                    if result.rowcount != 0:
                        print(
                            "Number of rows affected by statement: {}".format(
                                result.rowcount
                            )
                        )

        query = """UPDATE user A
        INNER JOIN user_groups B
        ON A.user_id = B.ug_user
        SET A.user_special = 1
        WHERE ug_group != "confirmed" 
        and ug_group != "extendedconfirmed"
        and ug_group != "bot";"""

        cursor.execute(query,)

        os.remove(userGroupsFile)
        os.remove(userGroupsArchive)

        cursor.close()
        database.close()


def allBlocked(dir="lists/"):
    url = "https://petscan.wmflabs.org/?categories=Blocked_Wikipedia_users&project=wikipedia&edits%5Bflagged%5D=both&depth=4&cb_labels_any_l=1&edits%5Bbots%5D=both&cb_labels_no_l=1&output_limit=5&edits%5Banons%5D=both&search_max_results=500&interface_language=en&cb_labels_yes_l=1&ns%5B3%5D=1&negcats=Suspected%20Wikipedia%20sockpuppets%E2%80%8E&language=en&active_tab=tab_output&ns%5B2%5D=1&doit="

    content = urllib.request.urlretrieve(url, dir + "Blocked_Wikipedia_users.csv")

    print(content)


def createBlockedLastFiveEdits(cursor):
    database, cursor = Database.connect()
    query = "DROP TABLE IF EXISTS blocked_last_five_edits ;"

    cursor.execute(query,)

    query = """create table blocked_last_five_edits
                    select * from 
                        (select *, rank() over (partition by user_table_id order by edit_date desc) as rnk 
                        from edit) as x where rnk <= 5;"""

    cursor.execute(query,)

    cursor.close()
    database.close()


def createBlockedIPLastFiveEdits(cursor):
    database, cursor = Database.connect()
    query = "DROP TABLE IF EXISTS blocked_ip_last_five_edits ;"

    cursor.execute(query,)

    query = """create table blocked_ip_last_five_edits
    select t1.* from edit t1 join user
    on t1.user_table_id = user.id where user.blocked is true 
    and ip_address is not null and t1.edit_date >= (select edit_date from edit t2
                        where t2.user_table_id = t1.user_table_id
                        and user.blocked is true and ip_address is not null
                        order by edit_date desc limit 4,1);"""

    cursor.execute(query,)

    cursor.close()
    database.close()


def main():
    """A function"""
    print("hello world")
    listDir = "lists/"

    if not os.path.exists(listDir):
        os.mkdir(listDir)

    # 4 days
    # ipGlobalBlocks(listDir)

    # allBlocked(listDir)

    # goodUsers(listDir)

    # 1 day, 17 hours
    # createBlockedLastFiveEdits()

    # 
    # createBlockedIPLastFiveEdits()

    # if os.path.exists(listDir):
    #     os.rmdir(listDir)


def defineArgParser():
    """Creates parser for command line arguments"""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    # parser.add_argument(
    #     "-d",
    #     "--dir",
    #     help="Output directory for figures",
    #     default="../plots/",
    # )
    return parser


if __name__ == "__main__":
    argParser = defineArgParser()
    clArgs = argParser.parse_args()
    main(
        # dir=clArgs.dir,
    )
