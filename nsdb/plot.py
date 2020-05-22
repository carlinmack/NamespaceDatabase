"""
This script ....
"""
import argparse
import os
import matplotlib.pyplot as plt

import Database


def plot(dir: str = "../plots/",):
    """A function"""
    if not os.path.exists(dir):
        os.mkdir(dir)

    dataDir = dir + "data/"
    if not os.path.exists(dataDir):
        os.mkdir(dataDir)

    database, cursor = Database.connect()

    # Constants
    query = """SELECT count(*)
    FROM user;"""
    cursor.execute(query,)
    totalUsers = cursor.fetchone()[0]

    i = 0
    figname = dir + str(i)
    plt.figure()

    query = """SELECT status, count(id)
    FROM partition
    GROUP BY status;"""

    # cursor.execute(query,)
    # data = cursor.fetchall()
    # with open(dataDir + str(i) + ".txt", "w") as file:
    #     file.write(str(data))
    # plt.xlabel('Status')
    # plt.ylabel('Number of Partitions')
    # plt.bar(*zip(*data))
    # plt.savefig(figname, bbox_inches = "tight")

    #1
    i = i + 1
    figname = dir + str(i) 
    plt.figure()

    query = """SELECT 
    (SELECT count(*) FROM user WHERE number_of_edits = 0), 
    (SELECT count(*) FROM user WHERE number_of_edits = 1), 
    (SELECT count(*) FROM user WHERE number_of_edits > 1 and number_of_edits <= 10), 
    (SELECT count(*) FROM user WHERE number_of_edits > 10 and number_of_edits <= 100), 
    (SELECT count(*) FROM user WHERE number_of_edits > 100);"""
    columns = ["no edits", "1 edit", "2-10 edits", "11-100 edits", ">100 edits"]
    # cursor.execute(query,)
    # data = cursor.fetchall()
    # data = list(*data)
    # with open(dataDir + str(i) + ".txt", "w") as file:
    #     file.write(str(data))

    # total = sum(data)
    # data = list(map(lambda x: x*100/total, data))

    # plt.xlabel('Main space edits')
    # plt.ylabel('Percentage')
    # plt.bar(columns,data)

    # plt.savefig(figname, bbox_inches = "tight")

    #2
    i = i + 1
    figname = dir + str(i)   
    plt.figure()

    query = """SELECT 
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits = 0), 
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits = 1), 
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 1 and talkpage_number_of_edits <= 10), 
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 10 and talkpage_number_of_edits <= 100), 
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 100);"""
    columns = ["no edits", "1 edit", "2-10 edits", "11-100 edits", ">100 edits"]
    # cursor.execute(query,)
    # data = cursor.fetchall()
    # data = list(*data)
    # with open(dataDir + str(i) + ".txt", "w") as file:
    #     file.write(str(data))

    # total = sum(data)
    # data = list(map(lambda x: x*100/total, data))

    # plt.xlabel('Talk Page Edits')
    # plt.ylabel('Percentage')
    # plt.bar(columns,data)

    # plt.savefig(figname, bbox_inches = "tight")

    #3
    i = i + 1
    figname = dir + str(i) 
    plt.figure()

    query = """SELECT namespace, count(page_id) 
    AS 'count' 
    FROM page 
    GROUP BY namespace;"""
    # cursor.execute(query,)
    # data = cursor.fetchall()
    # data = list(map(lambda x: (str(x[0]), x[1]), data))

    # with open(dataDir + str(i) + ".txt", "w") as file:
    #     file.write(str(data))

    # plt.xlabel('Namespace')
    # plt.ylabel('Number of Pages (log)')
    # plt.yscale('log')
    # plt.bar(*zip(*data))
    # plt.savefig(figname +"-log", bbox_inches = "tight")
    # plt.ylabel('Number of Pages (linear)')
    # plt.yscale('linear')
    # plt.bar(*zip(*data))
    # plt.savefig(figname +"-linear", bbox_inches = "tight")

    #4
    i = i + 1
    figname = dir + str(i) 
    plt.figure()

    query = """SELECT 
    (select count(*) as target from user 
    WHERE talkpage_number_of_edits > 0 and number_of_edits > 0), 
    (select count(*) as target from user 
    WHERE talkpage_number_of_edits = 0 and number_of_edits > 0), 
    (select count(*) as target from user 
    WHERE talkpage_number_of_edits > 0 and number_of_edits = 0), 
    (select count(*) as target from user 
    WHERE talkpage_number_of_edits = 0 and number_of_edits = 0);"""
    columns = [
        "edits mainspace\nand talkspace",
        "edits mainspace\nnot talkspace",
        "edits talkspace\nnot mainspace",
        "edits neither",
    ]
    # cursor.execute(query,)
    # data = cursor.fetchall()
    # data = list(*data)
    # with open(dataDir + str(i) + ".txt", "w") as file:
    #     file.write(str(data))

    # data = [1824008, 47503455, 1058214, 4407]
    # data = list(map(lambda x: x*100/totalUsers, data))

    # plt.ylabel('Percentage')
    # plt.bar(columns,data)

    # plt.savefig(figname, bbox_inches = "tight")

    #5
    i = i + 1
    figname = dir + str(i) 
    plt.figure()

    mainspace = """SELECT username, number_of_edits FROM user 
    where bot is null order by number_of_edits desc limit 10;"""
    talkspace = """SELECT username, talkpage_number_of_edits FROM user 
    where bot is null order by talkpage_number_of_edits desc limit 10;"""
    # cursor.execute(mainspace,)
    # mainspaceData = cursor.fetchall()
    
    # with open(dataDir + str(i) + "-mainspace.txt", "w") as file:
    #     file.write(str(mainspaceData))

    # cursor.execute(talkspace,)
    # talkspaceData = cursor.fetchall()
    
    # with open(dataDir + str(i) + "-talkspace.txt", "w") as file:
    #     file.write(str(talkspaceData))

    # # plt.ylabel('Percentage')
    # plt.bar(*zip(*mainspaceData), label='mainspace edits')
    # plt.bar(*zip(*talkspaceData), label='talkspace edits')
    # plt.xticks(rotation= 45)
    # plt.legend(loc="upper right")
    # plt.savefig(figname, bbox_inches = "tight")

    #6
    i = i + 1
    figname = dir + str(i) 
    plt.figure()

    mainspace = """SELECT username, number_of_edits FROM user 
    where bot is true order by number_of_edits desc limit 10;"""
    talkspace = """SELECT username, talkpage_number_of_edits FROM user 
    where bot is true order by talkpage_number_of_edits desc limit 10;"""
    # cursor.execute(mainspace,)
    # mainspaceData = cursor.fetchall()
    
    # with open(dataDir + str(i) + "-mainspace.txt", "w") as file:
    #     file.write(str(mainspaceData))

    # cursor.execute(talkspace,)
    # talkspaceData = cursor.fetchall()
    
    # with open(dataDir + str(i) + "-talkspace.txt", "w") as file:
    #     file.write(str(talkspaceData))

    # plt.ylabel('Percentage')
    # plt.bar(*zip(*mainspaceData), label='mainspace edits')
    # plt.bar(*zip(*talkspaceData), label='talkspace edits')
    # plt.xticks(rotation= 45)
    # plt.legend(loc="upper right")
    # plt.savefig(figname, bbox_inches = "tight")

    #7
    i = i + 1
    figname = dir + str(i) 
    plt.figure()

    mainspace = """SELECT ip_address, number_of_edits FROM user 
    where ip_address is not null order by number_of_edits desc limit 10;"""
    talkspace = """SELECT ip_address, talkpage_number_of_edits FROM user 
    where ip_address is not null order by talkpage_number_of_edits desc limit 10;"""
    # cursor.execute(mainspace,)
    # mainspaceData = cursor.fetchall()
    # # data = list(*data)
    # with open(dataDir + str(i) + "-mainspace.txt", "w") as file:
    #     file.write(str(mainspaceData))

    # cursor.execute(talkspace,)
    # talkspaceData = cursor.fetchall()
    
    # with open(dataDir + str(i) + "-talkspace.txt", "w") as file:
    #     file.write(str(talkspaceData))

    # plt.ylabel('Percentage')
    # plt.bar(*zip(*mainspaceData), label='mainspace edits')
    # plt.bar(*zip(*talkspaceData), label='talkspace edits')
    # plt.xticks(rotation= 45)
    # plt.legend(loc="upper right")
    # plt.savefig(figname, bbox_inches = "tight")

    cursor.close()
    database.close()


def defineArgParser():
    """Creates parser for command line arguments"""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "-d", "--dir", help="Output directory for figures", default="../plots/",
    )

    return parser


if __name__ == "__main__":

    argParser = defineArgParser()
    clArgs = argParser.parse_args()

    plot(dir=clArgs.dir,)
