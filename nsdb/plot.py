"""
This script ....t
"""
import argparse
import csv
import datetime
import os
from datetime import datetime as dt

import Database
import matplotlib
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from cycler import cycler  # for mpl>2.2


def partitionStatus(cursor, i, plotDir, dataDir, dryrun):
    plt.figure()
    figname = plotDir + str(i) + "-" + "partitionStatus"

    query = """SELECT status, count(id)
    FROM wikiactors.partition
    GROUP BY status
    ORDER BY count(id) desc;"""

    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        with open(dataDir + str(i) + ".txt", "w") as file:
            file.write(str(data))
    else:
        data = [("done", 76988), ("failed", 1418), ("failed again", 59)]
    _, ax = plt.subplots()
    ax.set_title("Status of parsing partitions")
    ax.set_xlabel("Status")
    ax.set_ylabel("Number of Partitions")
    ax.bar(*zip(*data))

    singlePlot(plt, ax, "y")

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def distributionOfMainEdits(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "distributionOfMainEdits"
    plt.figure()

    query = """SELECT
    (SELECT count(*) FROM user WHERE number_of_edits = 0),
    (SELECT count(*) FROM user WHERE number_of_edits = 1),
    (SELECT count(*) FROM user WHERE number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE number_of_edits > 100);"""
    columns = ["no edits", "1 edit", "2-10 edits", "11-100 edits", ">100 edits"]
    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        data = list(*data)
        with open(dataDir + str(i) + ".txt", "w") as file:
            file.write(str(data))
    else:
        data = [1062957, 23477790, 22217924, 3267408, 364341]

    total = sum(data)
    data = list(map(lambda x: x * 100 / total, data))

    fig, ax = plt.subplots()
    ax.set_title("Distribution of edits in main space")
    ax.set_xlabel("Number of edits by user")
    ax.set_ylabel("Percentage")
    ax.bar(columns, data)

    singlePlot(plt, ax, "y")

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def distributionOfTalkEdits(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "distributionOfTalkEdits"
    plt.figure()

    query = """SELECT
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits = 0),
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits = 1),
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 1 and talkpage_number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 10 and talkpage_number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 100);"""
    columns = ["no edits", "1 edit", "2-10 edits", "11-100 edits", ">100 edits"]
    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        data = list(*data)
        with open(dataDir + str(i) + ".txt", "w") as file:
            file.write(str(data))
    else:
        data = [47508198, 1585249, 1092331, 169984, 34658]

    total = sum(data)
    data = list(map(lambda x: x * 100 / total, data))

    fig, ax = plt.subplots()
    ax.set_title("Distribution of edits in talk space")
    ax.set_xlabel("Talk Page Edits")
    ax.set_ylabel("Percentage")
    ax.bar(columns, data)

    singlePlot(plt, ax, "y")

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def numberOfPagesPerNamespace(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "numberOfPagesPerNamespace"
    plt.figure()

    query = """SELECT namespace, count(page_id)
    AS 'count'
    FROM page
    GROUP BY namespace
    ORDER BY namespace;"""
    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        data = list(map(lambda x: (str(x[0]), x[1]), data))

        with open(dataDir + str(i) + ".txt", "w") as file:
            file.write(str(data))
    else:
        data = [
            ("0", 13274486),
            ("1", 6973255),
            ("2", 2769259),
            ("3", 13270254),
            ("4", 1064053),
            ("5", 145316),
            ("6", 799880),
            ("7", 421780),
            ("8", 2119),
            ("9", 1308),
            ("10", 575245),
            ("11", 310669),
            ("12", 1934),
            ("13", 1051),
            ("14", 1668104),
            ("15", 1399806),
            ("100", 89259),
            ("101", 22247),
            ("108", 6893),
            ("109", 6196),
            ("118", 91670),
            ("119", 20586),
            ("447", 1323),
            ("710", 924),
            ("711", 40),
            ("828", 9691),
            ("829", 6564),
            ("2300", 1),
            ("2301", 1),
        ]

    fig, ax = plt.subplots()  # Create a figure and an axes.
    ax.barh(*zip(*data))
    ax.set_ylabel("Namespace")  # Add an x-label to the axes.
    ax.set_xlabel("Number of Pages (log)")  # Add a y-label to the axes.
    ax.set_xscale("log")
    ax.set_title("Number of Pages per namespace")  # Add a title to the axes.

    plt.gcf().set_size_inches(8, 8)
    singlePlot(plt, ax, "x")

    plt.savefig(figname + "-log", bbox_inches="tight", pad_inches=0.25, dpi=200)

    ax.set_xlabel("Number of Pages (linear)")
    ax.set_xscale("linear")
    singlePlot(plt, ax, "x")

    plt.savefig(figname + "-linear", bbox_inches="tight", pad_inches=0.25, dpi=200)


def editsMainTalkNeither(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "editsMainTalkNeither"
    plt.figure()

    if not dryrun:
        query = """SELECT count(*)
            FROM user;"""
        cursor.execute(query,)
        totalUsers = cursor.fetchone()[0]
    else:
        totalUsers = 50390420

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
    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        data = list(*data)
        with open(dataDir + str(i) + ".txt", "w") as file:
            file.write(str(data))
    else:
        data = [1824008, 47503455, 1058214, 4407]
    data = list(map(lambda x: x * 100 / totalUsers, data))

    fig, ax = plt.subplots()
    ax.set_title("Namespaces that users edit")
    ax.set_ylabel("Percentage")
    ax.bar(columns, data)
    
    singlePlot(plt, ax, "y")

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def numMainTalkEditsForBiggestUsers(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "numMainTalkEditsForBiggestUsers"
    plt.figure()

    mainspace = """SELECT username, number_of_edits FROM user
    where bot is null order by number_of_edits desc limit 10;"""
    talkspace = """SELECT username, talkpage_number_of_edits FROM user
    where bot is null order by talkpage_number_of_edits desc limit 10;"""
    if not dryrun:
        cursor.execute(mainspace,)
        mainspaceData = cursor.fetchall()

        with open(dataDir + str(i) + "-mainspace.txt", "w") as file:
            file.write(str(mainspaceData))

        cursor.execute(talkspace,)
        talkspaceData = cursor.fetchall()

        with open(dataDir + str(i) + "-talkspace.txt", "w") as file:
            file.write(str(talkspaceData))
    else:
        mainspaceData = [
            ("Ser Amantio di Nicolao", 2642285),
            ("Koavf", 1501381),
            ("BrownHairedGirl", 1486023),
            ("BD2412", 1358460),
            ("Rich Farmbrough", 1254142),
            ("Tom.Reding", 1210959),
            ("Waacstats", 1108188),
            ("Materialscientist", 1059053),
            ("Hmains", 1047292),
            ("Bearcat", 953537),
        ]
        talkspaceData = [
            ("Koavf", 432184),
            ("Ser Amantio di Nicolao", 324243),
            ("Rich Farmbrough", 270090),
            ("Dthomsen8", 265542),
            ("BetacommandBot", 253719),
            ("EP111", 246440),
            ("Johnsoniensis", 238420),
            ("Fortdj33", 168119),
            ("ChrisGualtieri", 167658),
            ("Meno25", 144943),
        ]

    fig, axs = plt.subplots(2, 1)  # Create a figure and an axes.
    fig.suptitle("Top 10 mainspace and talkpage editors")
    axs[0].barh(*zip(*mainspaceData))
    axs[0].set_ylabel("Usernames")  # Add an x-label to the axes.
    axs[0].set_xlabel("Number of edits (linear)")  # Add a y-label to the axes.
    axs[0].set_title("Main space edits")  # Add a title to the axes.
    axs[0].xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
    axs[1].barh(*zip(*talkspaceData))
    axs[1].set_ylabel("Usernames")  # Add an x-label to the axes.
    axs[1].set_xlabel("Number of edits (linear)")  # Add a y-label to the axes.
    axs[1].set_title("Talk space edits")  # Add a title to the axes.
    axs[1].xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))

    plt.gcf().set_size_inches(8, 11)
    removeSpines(axs[0])
    removeSpines(axs[1])

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def numMainTalkEditsForBiggestBots(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "numMainTalkEditsForBiggestBots"
    plt.figure()

    mainspace = """SELECT username, number_of_edits FROM user
    where bot is true order by number_of_edits desc limit 10;"""
    talkspace = """SELECT username, talkpage_number_of_edits FROM user
    where bot is true order by talkpage_number_of_edits desc limit 10;"""
    if not dryrun:
        cursor.execute(mainspace,)
        mainspaceData = cursor.fetchall()

        with open(dataDir + str(i) + "-mainspace.txt", "w") as file:
            file.write(str(mainspaceData))

        cursor.execute(talkspace,)
        talkspaceData = cursor.fetchall()

        with open(dataDir + str(i) + "-talkspace.txt", "w") as file:
            file.write(str(talkspaceData))
    else:
        mainspaceData = [
            ("WP 1.0 bot", 6589889),
            ("Cydebot", 6336698),
            ("ClueBot NG", 5196209),
            ("AnomieBOT", 4361942),
            ("SmackBot", 3171007),
            ("Yobot", 2823974),
            ("Addbot", 2712291),
            ("InternetArchiveBot", 2683840),
            ("EmausBot", 1961489),
            ("Monkbot", 1556995),
        ]
        talkspaceData = [
            ("Yobot", 1520000),
            ("SineBot", 1414852),
            ("InternetArchiveBot", 1066758),
            ("AnomieBOT", 483147),
            ("ListasBot", 428200),
            ("BattyBot", 418389),
            ("Kingbotk", 366118),
            ("Xenobot Mk V", 347264),
            ("Lowercase sigmabot III", 311482),
            ("MiszaBot I", 226159),
        ]

    fig, axs = plt.subplots(2, 1)  # Create a figure and an axes.
    fig.suptitle("Top 10 mainspace and talkpage bot editors")
    axs[0].barh(*zip(*mainspaceData))
    axs[0].set_ylabel("Usernames")  # Add an x-label to the axes.
    axs[0].set_xlabel("Number of edits (linear)")  # Add a y-label to the axes.
    axs[0].set_title("Main space edits")  # Add a title to the axes.
    axs[0].xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
    axs[1].barh(*zip(*talkspaceData))
    axs[1].set_ylabel("Usernames")  # Add an x-label to the axes.
    axs[1].set_xlabel("Number of edits (linear)")  # Add a y-label to the axes.
    axs[1].set_title("Talk space edits")  # Add a title to the axes.
    axs[1].xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))

    plt.gcf().set_size_inches(8, 11)
    removeSpines(axs[0])
    removeSpines(axs[1])

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def numMainTalkEditsForBiggestIPs(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "numMainTalkEditsForBiggestIPs"
    plt.figure()

    mainspace = """SELECT ip_address, number_of_edits FROM user
    where ip_address is not null order by number_of_edits desc limit 10;"""
    talkspace = """SELECT ip_address, talkpage_number_of_edits FROM user
    where ip_address is not null order by talkpage_number_of_edits desc limit 10;"""
    if not dryrun:
        cursor.execute(mainspace,)
        mainspaceData = cursor.fetchall()
        # data = list(*data)
        with open(dataDir + str(i) + "-mainspace.txt", "w") as file:
            file.write(str(mainspaceData))

        cursor.execute(talkspace,)
        talkspaceData = cursor.fetchall()

        with open(dataDir + str(i) + "-talkspace.txt", "w") as file:
            file.write(str(talkspaceData))
    else:
        mainspaceData = [
            ("84.90.219.128", 49897),
            ("24.143.224.15", 45221),
            ("208.81.184.4", 37762),
            ("2600:1700:7E31:5", 33067),
            ("2605:A000:140D:4", 24182),
            ("129.33.19.254", 23492),
            ("217.129.67.28", 23340),
            ("204.153.84.10", 23007),
            ("68.39.174.238", 21153),
            ("2001:569:7C07:26", 20859),
        ]
        talkspaceData = [
            ("208.81.184.4", 11671),
            ("204.153.84.10", 4248),
            ("64.6.124.31", 3862),
            ("129.33.19.254", 3661),
            ("98.113.248.40", 2575),
            ("72.228.177.92", 2165),
            ("208.245.87.2", 2063),
            ("69.22.98.162", 1965),
            ("66.234.33.8", 1913),
            ("2001:8A0:F23F:16", 1874),
        ]

    fig, axs = plt.subplots(2, 1)  # Create a figure and an axes.
    fig.suptitle("Top 10 mainspace and talkpage IP editors")
    axs[0].barh(*zip(*mainspaceData))
    axs[0].set_ylabel("Usernames")  # Add an x-label to the axes.
    axs[0].set_xlabel("Number of edits (linear)")  # Add a y-label to the axes.
    axs[0].set_title("Main space edits")  # Add a title to the axes.
    axs[0].xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
    axs[1].barh(*zip(*talkspaceData))
    axs[1].set_ylabel("Usernames")  # Add an x-label to the axes.
    axs[1].set_xlabel("Number of edits (linear)")  # Add a y-label to the axes.
    axs[1].set_title("Talk space edits")  # Add a title to the axes.
    axs[1].xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))

    plt.gcf().set_size_inches(8, 11)
    removeSpines(axs[0])
    removeSpines(axs[1])

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def distributionOfMainEditsUserBots(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i) + "-" + "distributionOfMainEditsUserBots"
    plt.figure()

    columns = ["no edits", "1 edit", "2-10 edits", "11-100 edits", ">100 edits"]
    mainspaceUser = """SELECT
    (SELECT count(*) FROM user WHERE bot is null
    and number_of_edits = 0),
    (SELECT count(*) FROM user WHERE bot is null
    and number_of_edits = 1),
    (SELECT count(*) FROM user WHERE bot is null
    and number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE bot is null
    and number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE bot is null
    and number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(mainspaceUser,)
        mainspaceUserData = cursor.fetchall()
        mainspaceUserData = list(*mainspaceUserData)
        with open(dataDir + str(i) + "-mainspace-user.txt", "w") as file:
            file.write(str(mainspaceUserData))
    else:
        mainspaceUserData = [1062617, 23477689, 22217652, 3267197, 363346]

    mainspaceBot = """SELECT
    (SELECT count(*) FROM user WHERE bot is true
    and number_of_edits = 0),
    (SELECT count(*) FROM user WHERE bot is true
    and number_of_edits = 1),
    (SELECT count(*) FROM user WHERE bot is true
    and number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE bot is true
    and number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE bot is true
    and number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(mainspaceBot,)
        mainspaceBotData = cursor.fetchall()
        mainspaceBotData = list(*mainspaceBotData)
        with open(dataDir + str(i) + "-mainspace-bot.txt", "w") as file:
            file.write(str(mainspaceBotData))
    else:
        mainspaceBotData = [340, 101, 272, 211, 995]

    mainspaceBlocked = """SELECT
    (SELECT count(*) FROM user WHERE blocked is true
    and number_of_edits = 0),
    (SELECT count(*) FROM user WHERE blocked is true
    and number_of_edits = 1),
    (SELECT count(*) FROM user WHERE blocked is true
    and number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE blocked is true
    and number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE blocked is true
    and number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(mainspaceBlocked,)
        mainspaceBlockedData = cursor.fetchall()
        mainspaceBlockedData = list(*mainspaceBlockedData)
        with open(dataDir + str(i) + "-mainspace-blocked.txt", "w") as file:
            file.write(str(mainspaceBlockedData))
    else:
        mainspaceBlockedData = [2432, 50266, 82503, 32119, 6513]

    talkspaceUser = """SELECT
    (SELECT count(*) FROM user WHERE bot is null
    and talkpage_number_of_edits = 0),
    (SELECT count(*) FROM user WHERE bot is null
    and  talkpage_number_of_edits = 1),
    (SELECT count(*) FROM user WHERE bot is null
    and  talkpage_number_of_edits > 1 and talkpage_number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE bot is null
    and  talkpage_number_of_edits > 10 and talkpage_number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE bot is null
    and  talkpage_number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(talkspaceUser,)
        talkspaceUserData = cursor.fetchall()
        talkspaceUserData = list(*talkspaceUserData)
        with open(dataDir + str(i) + "-talkspace-user.txt", "w") as file:
            file.write(str(talkspaceUserData))
    else:
        talkspaceUserData = [47506831, 1585186, 1092212, 169881, 34391]

    talkspaceBot = """SELECT
    (SELECT count(*) FROM user WHERE bot is true
    and talkpage_number_of_edits = 0),
    (SELECT count(*) FROM user WHERE bot is true
    and  talkpage_number_of_edits = 1),
    (SELECT count(*) FROM user WHERE bot is true
    and  talkpage_number_of_edits > 1 and talkpage_number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE bot is true
    and  talkpage_number_of_edits > 10 and talkpage_number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE bot is true
    and  talkpage_number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(talkspaceBot,)
        talkspaceBotData = cursor.fetchall()
        talkspaceBotData = list(*talkspaceBotData)
        with open(dataDir + str(i) + "-talkspace-bot.txt", "w") as file:
            file.write(str(talkspaceBotData))
    else:
        talkspaceBotData = [1367, 63, 119, 103, 267]

    talkspaceBlocked = """SELECT
    (SELECT count(*) FROM user WHERE blocked is true
    and talkpage_number_of_edits = 0),
    (SELECT count(*) FROM user WHERE blocked is true
    and  talkpage_number_of_edits = 1),
    (SELECT count(*) FROM user WHERE blocked is true
    and  talkpage_number_of_edits > 1 and talkpage_number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE blocked is true
    and  talkpage_number_of_edits > 10 and talkpage_number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE blocked is true
    and  talkpage_number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(talkspaceBlocked,)
        talkspaceBlockedData = cursor.fetchall()
        talkspaceBlockedData = list(*talkspaceBlockedData)
        with open(dataDir + str(i) + "-talkspace-blocked.txt", "w") as file:
            file.write(str(talkspaceBlockedData))
    else:
        talkspaceBlockedData = [154838, 6404, 8635, 3173, 783]

    fig, axs = plt.subplots(2, 3)
    threeFigures = tkr.FuncFormatter(threeFigureFormatter)
    fig.suptitle("Distribution of edits across name spaces for bots and users")
    axs[0, 0].set_title("user edits in main space")
    axs[0, 0].bar(columns, mainspaceUserData)
    axs[0, 0].yaxis.set_major_formatter(threeFigures)
    axs[0, 1].set_title("bot edits in main space")
    axs[0, 1].bar(columns, mainspaceBotData)
    axs[0, 1].yaxis.set_major_formatter(threeFigures)
    axs[0, 2].set_title("blocked edits in main space")
    axs[0, 2].bar(columns, mainspaceBlockedData)
    axs[0, 2].yaxis.set_major_formatter(threeFigures)
    axs[1, 0].set_title("user edits in talk space")
    axs[1, 0].bar(columns, talkspaceUserData)
    axs[1, 0].yaxis.set_major_formatter(threeFigures)
    axs[1, 1].set_title("bot edits in talk space")
    axs[1, 1].bar(columns, talkspaceBotData)
    axs[1, 1].yaxis.set_major_formatter(threeFigures)
    axs[1, 2].set_title("blocked edits in talk space")
    axs[1, 2].bar(columns, talkspaceBlockedData)
    axs[1, 2].yaxis.set_major_formatter(threeFigures)

    plt.gcf().set_size_inches(19, 9)
    removeSpines(axs[0, 0])
    removeSpines(axs[0, 1])
    removeSpines(axs[0, 2])
    removeSpines(axs[1, 0])
    removeSpines(axs[1, 1])
    removeSpines(axs[1, 2])

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def editsMainTalkNeitherUserBots(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i) + "-" + "editsMainTalkNeitherUserBots"
    plt.figure()

    columns = [
        "edits mainspace\nand talkspace",
        "edits mainspace\nnot talkspace",
        "edits talkspace\nnot mainspace",
        "edits neither",
    ]

    users = """SELECT
    (select count(*) as target from user
    WHERE talkpage_number_of_edits > 0 and number_of_edits > 0 and bot is null),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits = 0 and number_of_edits > 0 and bot is null),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits > 0 and number_of_edits = 0 and bot is null),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits = 0 and number_of_edits = 0 and bot is null);"""
    if not dryrun:
        cursor.execute(users,)
        userData = cursor.fetchall()
        userData = list(*userData)
        with open(dataDir + str(i) + "-user.txt", "w") as file:
            file.write(str(userData))
    else:
        userData = [1823460, 47502424, 1058210, 4407]

    bots = """SELECT
    (select count(*) as target from user
    WHERE talkpage_number_of_edits > 0 and number_of_edits > 0 and bot is true),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits = 0 and number_of_edits > 0 and bot is true),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits > 0 and number_of_edits = 0 and bot is true),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits = 0 and number_of_edits = 0 and bot is true);"""
    if not dryrun:
        cursor.execute(bots,)
        botData = cursor.fetchall()
        botData = list(*botData)
        with open(dataDir + str(i) + "-bot.txt", "w") as file:
            file.write(str(botData))
    else:
        botData = [548, 1031, 4, 336]

    blocked = """SELECT
    (select count(*) as target from user
    WHERE talkpage_number_of_edits > 0 and number_of_edits > 0 and blocked is true),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits = 0 and number_of_edits > 0 and blocked is true),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits > 0 and number_of_edits = 0 and blocked is true),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits = 0 and number_of_edits = 0 and blocked is true);"""
    if not dryrun:
        cursor.execute(blocked,)
        blockedData = cursor.fetchall()
        blockedData = list(*blockedData)
        with open(dataDir + str(i) + "-blocked.txt", "w") as file:
            file.write(str(blockedData))
    else:
        blockedData = [16578, 154823, 2417, 15]
    plt.title("Namespaces that users edit")

    fig, axs = plt.subplots(3)
    axs[0].set_title("Namespaces that users edit")
    axs[0].bar(columns, userData)
    axs[1].set_title("Namespaces that bots edit")
    axs[1].bar(columns, botData)
    axs[2].set_title("Namespaces that blocked edit")
    axs[2].bar(columns, blockedData)
    # fig.tight_layout()
    plt.gcf().set_size_inches(10, 17.5)

    axs[0].yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
    axs[1].yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
    axs[2].yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
    removeSpines(axs[0])
    removeSpines(axs[1])
    removeSpines(axs[2])
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def editTimesUserBots(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i) + "-" + "editTimesUserBots"
    plt.figure()

    columns = [
        "min time",
        "average time",
        "maximum time",
        "account duration",
    ]

    users = """select avg(min_time)/3600, avg(avg_time)/3600, avg(max_time)/3600,
    avg(duration)/3600, std(min_time)/3600, std(avg_time)/3600, std(max_time)/3600, std(duration)/3600
    from user_time_stats join user
    on user_time_stats.id = user.id
    where user.blocked is not True;"""
    if not dryrun:
        cursor.execute(users,)
        userData = cursor.fetchall()
        userStd = list(*userData)[4:]
        userData = list(*userData)[:4]
        with open(dataDir + str(i) + "-user.txt", "w") as file:
            file.write(str(userData) + "\n" + str(userStd))
    else:
        # userData = [554.73523706, 1895.69554062, 12669.22330022, 40912.15355312]
        userData = [585.04453404, 1353.55128065, 4190.04904727, 7496.67851755]
        userStd = [
            4173.818169075838,
            4945.720150565946,
            10877.852434682092,
            19318.9197993923,
        ]

    blocked = """select avg(min_time)/3600, avg(avg_time)/3600, avg(max_time)/3600,
    avg(duration)/3600, std(min_time)/3600, std(avg_time)/3600, std(max_time)/3600, std(duration)/3600
    from user_time_stats join user
    on user_time_stats.id = user.id
    where user.blocked is true;"""
    if not dryrun:
        cursor.execute(blocked,)
        blockedData = cursor.fetchall()
        blockedStd = list(*blockedData)[4:]
        blockedData = list(*blockedData)[:4]
        with open(dataDir + str(i) + "-blocked.txt", "w") as file:
            file.write(str(blockedData) + "\n" + str(blockedStd))
    else:
        # blockedData = [5.51123904, 215.49983126, 4457.78610197, 17759.69208272]
        blockedData = [104.89630128, 315.44417069, 1522.00393320, 3044.11047520]
        blockedStd = [
            1445.3397388692304,
            1813.6419287313036,
            5619.618614308308,
            10367.92683510656,
        ]

    specialUsers = """select avg(min_time)/3600, avg(avg_time)/3600, avg(max_time)/3600,
    avg(duration)/3600, std(min_time)/3600, std(avg_time)/3600, std(max_time)/3600, std(duration)/3600
    from user_time_stats join user
    on user_time_stats.id = user.id
    where user.user_special is true;"""
    if not dryrun:
        cursor.execute(specialUsers,)
        specialUsersData = cursor.fetchall()
        specialUsersStd = list(*specialUsersData)[4:]
        specialUsersData = list(*specialUsersData)[:4]
        with open(dataDir + str(i) + "-specialUsers.txt", "w") as file:
            file.write(str(specialUsersData) + "\n" + str(specialUsersStd))
    else:
        # specialUsersData = [147.03132949, 1124.02555881, 13976.81447445, 45119.61085901]
        specialUsersData = [75.23881283, 608.03894083, 14312.48619327, 68101.25732456]
        specialUsersStd = [
            1720.7292200635438,
            2310.760460431426,
            14440.439492053269,
            41412.40758456633,
        ]

    # Numbers of pairs of bars you want
    N = len(columns)

    # Position of bars on x-axis
    ind = list(range(N))

    _, ax = plt.subplots()

    # Width of a bar
    width = 0.3

    # Plotting
    ax.bar(
        ind,
        specialUsersData,
        width,
        label="Users with special privileges",
        yerr=specialUsersStd,
    )
    ax.bar(
        list(map(lambda x: x + width, ind)),
        userData,
        width,
        label="Non blocked users",
        yerr=userStd,
    )
    ax.bar(
        list(map(lambda x: x + width * 2, ind)),
        blockedData,
        width,
        label="Blocked users",
        yerr=blockedStd,
    )
    # First argument - A list of positions at which ticks should be placed
    # Second argument -  A list of labels to place at the given locations
    plt.xticks(list(map(lambda x: x + (width * 2) / 2, ind)), columns)

    ax.set_ylim(bottom=0)
    ax.set_title("Average time between talk page edits and account duration")
    ax.set_ylabel("Hours")
    plt.legend(loc="upper left")

    plt.gcf().set_size_inches(9, 7)
    singlePlot(plt, ax, "y")

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def distributionOfEditsPerNamespace(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i) + "-" + "distributionOfEditsPerNamespace"
    plt.figure()

    columns = ["1 edit", "2-10 edits", "11-100 edits", ">100 edits"]
    mainspace = """SELECT
    (SELECT count(*) FROM page WHERE namespace = 0
    and number_of_edits = 1),
    (SELECT count(*) FROM page WHERE namespace = 0
    and number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM page WHERE namespace = 0
    and number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM page WHERE namespace = 0
    and number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(mainspace,)
        mainspaceData = cursor.fetchall()
        mainspaceData = list(*mainspaceData)
        with open(dataDir + str(i) + "-mainspace.txt", "w") as file:
            file.write(str(mainspaceData))
    else:
        mainspaceData = [4778018, 4321490, 3307576, 866011]

    mainspaceTalk = """SELECT
    (SELECT count(*) FROM page WHERE namespace = 1
    and number_of_edits = 1),
    (SELECT count(*) FROM page WHERE namespace = 1
    and number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM page WHERE namespace = 1
    and number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM page WHERE namespace = 1
    and number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(mainspaceTalk,)
        mainspaceTalkData = cursor.fetchall()
        mainspaceTalkData = list(*mainspaceTalkData)
        with open(dataDir + str(i) + "-mainspace-talk.txt", "w") as file:
            file.write(str(mainspaceTalkData))
    else:
        mainspaceTalkData = [2016660, 4227840, 683342, 45133]

    user = """SELECT
    (SELECT count(*) FROM page WHERE namespace = 2
    and number_of_edits = 1),
    (SELECT count(*) FROM page WHERE namespace = 2
    and number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM page WHERE namespace = 2
    and number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM page WHERE namespace = 2
    and number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(user,)
        userData = cursor.fetchall()
        userData = list(*userData)
        with open(dataDir + str(i) + "-user.txt", "w") as file:
            file.write(str(userData))
    else:
        userData = [1284828, 1161523, 284302, 38574]

    userTalk = """SELECT
    (SELECT count(*) FROM page WHERE namespace = 3
    and  number_of_edits = 1),
    (SELECT count(*) FROM page WHERE namespace = 3
    and  number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM page WHERE namespace = 3
    and  number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM page WHERE  namespace = 3
    and  number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(userTalk,)
        userTalkData = cursor.fetchall()
        userTalkData = list(*userTalkData)
        with open(dataDir + str(i) + "-user-talk.txt", "w") as file:
            file.write(str(userTalkData))
    else:
        userTalkData = [7782495, 5047261, 406777, 33363]

    fig, axs = plt.subplots(2, 2, sharey=True)
    fig.suptitle("Distribution of number of edits per page across name spaces")
    axs[0, 0].set_title("page edits in main space")
    axs[0, 0].bar(columns, mainspaceData)
    axs[0, 0].grid(color="#ccc", which="major", axis="y", linestyle="solid")
    axs[0, 0].set_axisbelow(True)

    axs[0, 1].set_title("page edits in main talk space")
    axs[0, 1].bar(columns, mainspaceTalkData)
    axs[0, 1].grid(color="#ccc", which="major", axis="y", linestyle="solid")
    axs[0, 1].set_axisbelow(True)

    axs[1, 0].set_title("page edits in user space")
    axs[1, 0].bar(columns, userData)
    axs[1, 0].grid(color="#ccc", which="major", axis="y", linestyle="solid")
    axs[1, 0].set_axisbelow(True)

    axs[1, 1].set_title("page edits in user talk space")
    axs[1, 1].bar(columns, userTalkData)
    axs[1, 1].grid(color="#ccc", which="major", axis="y", linestyle="solid")
    axs[1, 1].set_axisbelow(True)

    # fig.tight_layout()
    plt.gcf().set_size_inches(11, 9)
    removeSpines(axs[0, 0])
    removeSpines(axs[0, 1])
    removeSpines(axs[1, 0])
    removeSpines(axs[1, 1])
    axs[0, 0].yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
    axs[1, 0].yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))

    # ax.set_axisbelow(True)
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


#
def sentimentUserBotsBlockedIP(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i) + "-" + "sentimentUserBotsBlockedIP"
    plt.figure()

    columns = [
        "added sentiment",
        "deleted sentiment",
    ]

    users = """select avg(edit.added_sentiment),avg(edit.deleted_sentiment)
    from edit
    join user
    on edit.user_table_id = user.id
    where user.blocked is null and user.ip_address is null and user.bot is null;"""
    if not dryrun:
        cursor.execute(users,)
        userData = cursor.fetchall()
        userData = list(*userData)
        with open(dataDir + str(i) + "-user.txt", "w") as file:
            file.write(str(userData))
    else:
        userData = [0.03575823190161788, 0.005590118354446301]

    blocked = """select avg(edit.added_sentiment),avg(edit.deleted_sentiment)
    from edit
    join user
    on edit.user_table_id = user.id
    where user.blocked is true;"""
    if not dryrun:
        cursor.execute(blocked,)
        blockedData = cursor.fetchall()
        blockedData = list(*blockedData)
        with open(dataDir + str(i) + "-blocked.txt", "w") as file:
            file.write(str(blockedData))
    else:
        blockedData = [0.027887433037106706, 0.00475190706470203]

    bots = """select avg(edit.added_sentiment),avg(edit.deleted_sentiment)
    from edit
    join user
    on edit.user_table_id = user.id
    where user.bot is true;"""
    if not dryrun:
        cursor.execute(bots,)
        botsData = cursor.fetchall()
        botsData = list(*botsData)
        with open(dataDir + str(i) + "-bot.txt", "w") as file:
            file.write(str(botsData))
    else:
        botsData = [0.005499846173827871, 0.004018131754929727]

    ipAddress = """select avg(edit.added_sentiment),avg(edit.deleted_sentiment)
    from edit
    join user
    on edit.user_table_id = user.id
    where user.ip_address is true;"""
    if not dryrun:
        cursor.execute(ipAddress,)
        ipAddressData = cursor.fetchall()
        ipAddressData = list(*ipAddressData)
        with open(dataDir + str(i) + "-ipAddress.txt", "w") as file:
            file.write(str(ipAddressData))
    else:
        ipAddressData = [0.05001974686845408, 0.008109401602654984]

    fig, ax = plt.subplots()

    # Numbers of pairs of bars you want
    N = len(columns)

    # Position of bars on x-axis
    ind = list(range(N))

    # Width of a bar
    width = 0.2

    # Plotting
    ax.bar(ind, userData, width, label="Non blocked users")
    ax.bar(
        list(map(lambda x: x + width, ind)), blockedData, width, label="Blocked users"
    )
    ax.bar(list(map(lambda x: x + width * 2, ind)), botsData, width, label="Bots")
    ax.bar(
        list(map(lambda x: x + width * 3, ind)),
        ipAddressData,
        width,
        label="IP address",
    )

    ax.set_ylabel("unit ?")
    ax.set_title("Average sentiment of different subsets of users")

    # xticks()
    # First argument - A list of positions at which ticks should be placed
    # Second argument -  A list of labels to place at the given locations
    plt.xticks(list(map(lambda x: x + (width * 3) / 2, ind)), columns)

    # Finding the best position for legends and putting it
    removeSpines(ax)
    showGrid(plt, ax, 'y')
    plt.gcf().set_size_inches(12, 7)

    plt.legend(loc="best")
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


#
def sentimentBots(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i) + "-" + "sentimentBots"
    plt.figure()

    columns = [
        "added sentiment",
        "deleted sentiment",
    ]

    botsAddedPos = """select avg(edit.added_sentiment),avg(edit.deleted_sentiment)
    from edit join user
    on edit.user_table_id = user.id
    where user.bot is true and edit.added_sentiment > 0 and edit.deleted_length > 2;"""
    if not dryrun:
        cursor.execute(botsAddedPos,)
        botsAddedPosData = cursor.fetchall()
        botsAddedPosData = list(*botsAddedPosData)
        with open(dataDir + str(i) + "-added-pos.txt", "w") as file:
            file.write(str(botsAddedPosData))
    else:
        botsAddedPosData = [0.14632212385263108, 0.009081743779086889]

    botsDelPos = """select avg(edit.added_sentiment),avg(edit.deleted_sentiment)
    from edit join user
    on edit.user_table_id = user.id
    where user.bot is true and edit.deleted_sentiment > 0 and edit.added_length > 2;"""
    if not dryrun:
        cursor.execute(botsDelPos,)
        botsDelPosData = cursor.fetchall()
        botsDelPosData = list(*botsDelPosData)
        with open(dataDir + str(i) + "-del-pos.txt", "w") as file:
            file.write(str(botsDelPosData))
    else:
        botsDelPosData = [0.015218654447829615, 0.14050409393497162]

    botsAddNeg = """select avg(edit.added_sentiment),avg(edit.deleted_sentiment)
    from edit join user
    on edit.user_table_id = user.id
    where user.bot is true and edit.added_sentiment < 0 and edit.deleted_length > 2;"""
    if not dryrun:
        cursor.execute(botsAddNeg,)
        botsAddNegData = cursor.fetchall()
        botsAddNegData = list(*botsAddNegData)
        with open(dataDir + str(i) + "-added-neg.txt", "w") as file:
            file.write(str(botsAddNegData))
    else:
        botsAddNegData = [-0.06679255441733645, -0.004087247193970783]

    botsDelNeg = """select avg(edit.added_sentiment),avg(edit.deleted_sentiment)
    from edit join user
    on edit.user_table_id = user.id
    where user.bot is true and edit.deleted_sentiment < 0 and edit.added_length > 2;"""
    if not dryrun:
        cursor.execute(botsDelNeg,)
        botsDelNegData = cursor.fetchall()
        botsDelNegData = list(*botsDelNegData)
        with open(dataDir + str(i) + "-del-neg.txt", "w") as file:
            file.write(str(botsDelNegData))
    else:
        botsDelNegData = [-0.0052931137240005395, -0.1429369148030895]

    botsBoth = """select avg(edit.added_sentiment),avg(edit.deleted_sentiment)
    from edit join user
    on edit.user_table_id = user.id
    where user.bot is true and edit.added_sentiment != 0 and edit.deleted_sentiment != 0;"""
    if not dryrun:
        cursor.execute(botsBoth,)
        botsBothData = cursor.fetchall()
        botsBothData = list(*botsBothData)
        with open(dataDir + str(i) + "-both.txt", "w") as file:
            file.write(str(botsBothData))
    else:
        botsBothData = [0.0840575952452897, 0.04664798862148708]

    bots = """select avg(edit.added_sentiment),avg(edit.deleted_sentiment)
    from edit join user
    on edit.user_table_id = user.id
    where user.bot is true;"""
    if not dryrun:
        cursor.execute(bots,)
        botsData = cursor.fetchall()
        botsData = list(*botsData)
        with open(dataDir + str(i) + "-bots.txt", "w") as file:
            file.write(str(botsData))
    else:
        botsData = [0.005499846173827871, 0.004018131754929727]

    fig, ax = plt.subplots()

    # Numbers of pairs of bars you want
    N = len(columns)

    # Position of bars on x-axis
    ind = list(range(N))

    # Width of a bar
    width = 0.15

    # Plotting
    ax.bar(ind, botsAddedPosData, width, label="added positive")
    ax.bar(
        list(map(lambda x: x + width, ind)),
        botsAddNegData,
        width,
        label="added negative",
    )
    ax.bar(
        list(map(lambda x: x + width * 2, ind)),
        botsDelPosData,
        width,
        label="deleted positive",
    )
    ax.bar(
        list(map(lambda x: x + width * 3, ind)),
        botsDelNegData,
        width,
        label="deleted negative",
    )
    ax.bar(
        list(map(lambda x: x + width * 4, ind)),
        botsBothData,
        width,
        label="both have sentiment",
    )
    ax.bar(
        list(map(lambda x: x + width * 5, ind)), botsData, width, label="all bots",
    )

    ax.set_ylabel("unit ?")
    ax.set_title("Average sentiment for different types of bot edits")

    # xticks()
    # First argument - A list of positions at which ticks should be placed
    # Second argument -  A list of labels to place at the given locations
    plt.xticks(list(map(lambda x: x + (width * 3) / 2, ind)), columns)

    removeSpines(ax)
    plt.grid(color="#ccc", which="major", axis="y", linestyle="solid")
    ax.set_axisbelow(True)
    plt.gcf().set_size_inches(12, 7)
    # Finding the best position for legends and putting it
    plt.legend(loc="best")
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


#
def profanityAll(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "profanityAll"
    plt.figure()

    data = []
    std = []

    specialUsers = """select avg(edit.ins_vulgarity), std(edit.ins_vulgarity)
    from edit inner join user
    on edit.user_table_id = user.id
    where user.blocked is null and user.bot is null and user_special is true;"""
    if not dryrun:
        cursor.execute(specialUsers,)
        specialUsersData = cursor.fetchall()
        specialUsersStd = specialUsersData[0][1]
        specialUsersData = specialUsersData[0][0]
        with open(dataDir + str(i) + "-specialUsers.txt", "w") as file:
            file.write(str(specialUsersData) + "\n" + str(specialUsersStd))
    else:
        specialUsersData = 0.0109
        specialUsersStd = 0.09959333924192307

    data.append(("users with\nspecial priviliges", specialUsersData))
    std.append(specialUsersStd)

    users = """select avg(edit.ins_vulgarity), std(edit.ins_vulgarity)
    from edit
    inner join user
    on edit.user_table_id = user.id
    where user.blocked is null and user.ip_address is null and user.bot is null;"""
    if not dryrun:
        cursor.execute(users,)
        userData = cursor.fetchall()
        userStd = userData[0][1]
        userData = userData[0][0]
        with open(dataDir + str(i) + "-user.txt", "w") as file:
            file.write(str(userData) + "\n" + str(userStd))
    else:
        userData = 0.0123
        userStd = 0.11028484312384287

    data.append(("users", userData))
    std.append(userStd)

    blocked = """select avg(edit.ins_vulgarity), std(edit.ins_vulgarity)
    from edit
    inner join user
    on edit.user_table_id = user.id
    where user.blocked is true
    and user.ip_address is not true;"""
    if not dryrun:
        cursor.execute(blocked,)
        blockedData = cursor.fetchall()
        blockedStd = blockedData[0][1]
        blockedData = blockedData[0][0]
        with open(dataDir + str(i) + "-blocked.txt", "w") as file:
            file.write(str(blockedData) + "\n" + str(blockedStd))
    else:
        blockedData = 0.0153
        blockedStd = 0.12255422751902714

    data.append(("blocked", blockedData))
    std.append(blockedStd)

    bots = """select avg(edit.ins_vulgarity), std(edit.ins_vulgarity)
    from edit
    inner join user
    on edit.user_table_id = user.id
    where user.bot is true;"""
    if not dryrun:
        cursor.execute(bots,)
        botsData = cursor.fetchall()
        botsStd = botsData[0][1]
        botsData = botsData[0][0]
        with open(dataDir + str(i) + "-bot.txt", "w") as file:
            file.write(str(botsData) + "\n" + str(botsStd))
    else:
        botsData = 0.0080
        botsStd = 0.08899117278773609

    data.append(("bots", botsData))
    std.append(botsStd)

    ipAddress = """select avg(edit.ins_vulgarity), std(edit.ins_vulgarity)
    from edit
    inner join user
    on edit.user_table_id = user.id
    where user.ip_address is true
    and user.blocked is not true;"""
    if not dryrun:
        cursor.execute(ipAddress,)
        ipAddressData = cursor.fetchall()
        ipAddressStd = ipAddressData[0][1]
        ipAddressData = ipAddressData[0][0]
        with open(dataDir + str(i) + "-ipAddress.txt", "w") as file:
            file.write(str(ipAddressData) + "\n" + str(ipAddressStd))
    else:
        ipAddressData = 0.0434
        ipAddressStd = 0.20379850302087404

    data.append(("ip", ipAddressData))
    std.append(ipAddressStd)

    ipAddressBlocked = """select avg(edit.ins_vulgarity), std(edit.ins_vulgarity)
    from edit
    inner join user
    on edit.user_table_id = user.id
    where user.ip_address is true
    and user.blocked is true;"""
    if not dryrun:
        cursor.execute(ipAddressBlocked,)
        ipAddressBlockedData = cursor.fetchall()
        ipAddressBlockedStd = ipAddressBlockedData[0][1]
        ipAddressBlockedData = ipAddressBlockedData[0][0]
        with open(dataDir + str(i) + "-ipAddressBlocked.txt", "w") as file:
            file.write(str(ipAddressBlockedData) + "\n" + str(ipAddressBlockedStd))
    else:
        ipAddressBlockedData = 0.0437
        ipAddressBlockedStd = 0.20432362462698245

    data.append(("ip blocked", ipAddressBlockedData))
    std.append(ipAddressBlockedStd)

    _, ax = plt.subplots()
    ax.set_title("Average profanity per type of user")
    ax.set_ylabel("Average profanity / %")
    ax.bar(*zip(*data), yerr=std)
    ax.set_ylim(bottom=0)
    # plt.bar(*zip(*data))
    
    plt.grid(color="#ccc", which="major", axis="y", linestyle="solid")
    ax.set_axisbelow(True)
    removeSpines(ax)
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


#
def averageAll(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "averageAll"
    plt.figure()

    query = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),AVG(deleted_sentiment), STD(added_length),STD(deleted_length),STD(del_words),STD(comment_length),STD(ins_longest_inserted_word),STD(ins_longest_character_sequence),STD(ins_internal_link),STD(ins_external_link),STD(blanking),STD(comment_copyedit),STD(comment_personal_life),STD(comment_special_chars),STD(ins_capitalization),STD(ins_digits),STD(ins_pronouns),STD(ins_special_chars),STD(ins_vulgarity),STD(ins_whitespace),STD(reverted),STD(added_sentiment),STD(deleted_sentiment)  from edit;"""
    columns = [
        "added_length",
        "deleted_length",
        "del_words",
        "comment_length",
        "ins_longest_inserted_word",
        "ins_longest_character_sequence",
        "ins_internal_link",
        "ins_external_link",
        "blanking",
        "comment_copyedit",
        "comment_personal_life",
        "comment_special_chars",
        "ins_capitalization",
        "ins_digits",
        "ins_pronouns",
        "ins_special_chars",
        "ins_vulgarity",
        "ins_whitespace",
        "reverted",
        "added_sentiment",
        "deleted_sentiment",
    ]
    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        dataStd = list(*data)[21:]
        data = list(*data)[:21]
        with open(dataDir + str(i) + ".txt", "w") as file:
            file.write(str(data) + "\n" + str(dataStd))
    else:
        data = [
            442.0422,
            439.0867,
            58.0321,
            49.1949,
            10.6587,
            1.8952,
            1.6529,
            0.1304,
            0.0022,
            0.0005,
            0.0002,
            0.11972271,
            0.10387291,
            0.02747601,
            0.00610185,
            0.12846018,
            0.0143,
            0.16946286,
            0.0293,
            0.03135975155021137,
            0.0055170703440406196,
        ]
        dataStd = [
            4654.176162916367,
            6176.346864990649,
            951.2080429740175,
            39.922080083596796,
            72.77314313715188,
            45.67935596915416,
            17.34742048576987,
            5.371908826641828,
            0.047305664882096865,
            0.022598233982907077,
            0.014979221561754661,
            0.09649544409376277,
            0.13556309951733453,
            0.0529137673082975,
            0.018949801230515435,
            0.07763594209856826,
            0.11881033215053255,
            0.18192642687661204,
            0.16869769991099628,
            0.14008787360862252,
            0.0690388085081368,
        ]

    fig, axs = plt.subplots(1, 3, gridspec_kw={"width_ratios": [3, 5, 13]})

    fig.suptitle("Average of all integer edit fields")
    # axs[0, 0].set_title("user edits in main space")
    axs[0].bar(columns[:3], data[:3], yerr=dataStd[:3])
    axs[0].tick_params(labelrotation=90)
    axs[0].set_ylim(bottom=0)
    # axs[1].set_title("bot edits in main space")
    axs[1].bar(columns[3:8], data[3:8], yerr=dataStd[3:8])
    axs[1].tick_params(labelrotation=90)
    axs[1].set_ylim(bottom=0)
    # axs[0, 2].set_title("blocked edits in main space")
    axs[2].bar(columns[8:], data[8:], yerr=dataStd[8:])
    axs[2].tick_params(labelrotation=90)
    axs[2].set_ylim(bottom=0)
    plt.gcf().set_size_inches(10, 7.5)
    removeSpines(axs[0])
    removeSpines(axs[1])
    removeSpines(axs[2])

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def namespacesEditedByTopFiveHundred(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "namespacesEditedByTopFiveHundred"
    plt.figure()
    # https://stackoverflow.com/questions/28620904/how-to-count-unique-set-values-in-mysql
    query = """SELECT set_list.namespaces, COUNT(user.namespaces) FROM
    (SELECT TRIM("'" FROM SUBSTRING_INDEX(SUBSTRING_INDEX(
    (SELECT TRIM(')' FROM SUBSTR(column_type, 5)) FROM information_schema.columns
    WHERE table_name = 'user' AND column_name = 'namespaces'),
    ',', @r:=@r+1), ',', -1)) AS namespaces
    FROM (SELECT @r:=0) deriv1,
    (SELECT ID FROM information_schema.COLLATIONS) deriv2
    HAVING @r <=
    (SELECT LENGTH(column_type) - LENGTH(REPLACE(column_type, ',', ''))
    FROM information_schema.columns
    WHERE table_name = 'user' AND column_name = 'namespaces')) set_list
    LEFT OUTER JOIN (SELECT namespaces FROM user
        where bot is null order by number_of_edits desc limit 500) user
    ON FIND_IN_SET(set_list.namespaces, user.namespaces) > 0
    GROUP BY set_list.namespaces
    ;"""
    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        data = list(map(lambda x: (str(x[0]), x[1]), data))
        with open(dataDir + str(i) + ".txt", "w") as file:
            file.write(str(data))
    else:
        data = [
            ("0", 500),
            ("1", 500),
            ("2", 499),
            ("3", 500),
            ("4", 499),
            ("5", 494),
            ("6", 475),
            ("7", 351),
            ("8", 102),
            ("9", 266),
            ("10", 497),
            ("11", 481),
            ("12", 280),
            ("13", 292),
            ("14", 492),
            ("15", 450),
            ("-1", 0),
            ("-2", 0),
            ("100", 444),
            ("101", 267),
            ("118", 439),
            ("119", 258),
            ("710", 31),
            ("711", 9),
            ("828", 169),
            ("829", 159),
            ("108", 229),
            ("109", 117),
            ("446", 0),
            ("447", 31),
            ("2300", 0),
            ("2301", 2),
            ("2302", 0),
            ("2303", 0),
        ]
    fig, ax = plt.subplots()
    ax.set_title("Namespaces that the top 500 users have edited")
    labels = list(map(lambda x: x[0], data))
    ax.set_xticklabels(labels=labels, rotation=90)
    # plt.ylabel("? (log)")
    # # plt.yscale("log")
    ax.bar(*zip(*data))
    removeSpines(ax)
    plt.grid(color="#ccc", which="major", axis="y", linestyle="solid")
    ax.set_axisbelow(True)
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


#
def internalExternalLinks(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "internalExternalLinks"
    plt.figure()

    internalData = []
    externalData = []

    specialUsers = """select avg(edit.ins_internal_link), avg(edit.ins_external_link)
    from edit join user
    on edit.user_table_id = user.id
    where user.user_special is true;"""
    # where user.user_special is true
    if not dryrun:
        cursor.execute(specialUsers,)
        specialUsersData = cursor.fetchall()
        specialUsersInternalData = specialUsersData[0][0]
        specialUsersExternalData = specialUsersData[0][1]
        with open(dataDir + str(i) + "-specialUsers.txt", "w") as file:
            file.write(str([specialUsersInternalData, specialUsersExternalData]))
    else:
        specialUsersInternalData = 1.6357
        specialUsersExternalData = 0.1278

    internalData.append(("users with\nspecial priviliges", specialUsersInternalData))
    externalData.append(("users with\nspecial priviliges", specialUsersExternalData))

    users = """select avg(edit.ins_internal_link), avg(edit.ins_external_link)
    from edit
    join user
    on edit.user_table_id = user.id
    where user.blocked is null and user.ip_address is null and user.bot is null;"""
    if not dryrun:
        cursor.execute(users,)
        userData = cursor.fetchall()
        userInternalData = userData[0][0]
        userExternalData = userData[0][1]
        with open(dataDir + str(i) + "-user.txt", "w") as file:
            file.write(str([userInternalData, userExternalData]))
    else:
        userInternalData = 1.5574
        userExternalData = 0.1189

    internalData.append(("users", userInternalData))
    externalData.append(("users", userExternalData))

    blocked = """select avg(edit.ins_internal_link), avg(edit.ins_external_link)
    from edit
    join user
    on edit.user_table_id = user.id
    where user.blocked is true;"""
    if not dryrun:
        cursor.execute(blocked,)
        blockedData = cursor.fetchall()
        blockedInternalData = blockedData[0][0]
        blockedExternalData = blockedData[0][1]
        with open(dataDir + str(i) + "-blocked.txt", "w") as file:
            file.write(str([blockedInternalData, blockedExternalData]))
    else:
        blockedInternalData = 1.3400
        blockedExternalData = 0.1222

    internalData.append(("blocked", blockedInternalData))
    externalData.append(("blocked", blockedExternalData))

    bots = """select avg(edit.ins_internal_link), avg(edit.ins_external_link)
    from edit
    join user
    on edit.user_table_id = user.id
    where user.bot is true;"""
    if not dryrun:
        cursor.execute(bots,)
        botsData = cursor.fetchall()
        botsInternalData = botsData[0][0]
        botsExternalData = botsData[0][1]
        with open(dataDir + str(i) + "-bot.txt", "w") as file:
            file.write(str([botsInternalData, botsExternalData]))
    else:
        botsInternalData = 2.3044
        botsExternalData = 0.1800

    internalData.append(("bots", botsInternalData))
    externalData.append(("bots", botsExternalData))

    ipAddress = """select avg(edit.ins_internal_link), avg(edit.ins_external_link)
    from edit
    join user
    on edit.user_table_id = user.id
    where user.ip_address is true;"""
    if not dryrun:
        cursor.execute(ipAddress,)
        ipAddressData = cursor.fetchall()
        ipAddressInternalData = ipAddressData[0][0]
        ipAddressExternalData = ipAddressData[0][1]
        with open(dataDir + str(i) + "-ipAddress.txt", "w") as file:
            file.write(str([ipAddressInternalData, ipAddressExternalData]))
    else:
        ipAddressInternalData = 1.0504
        ipAddressExternalData = 0.1154

    internalData.append(("ip", ipAddressInternalData))
    externalData.append(("ip", ipAddressExternalData))

    fig, axs = plt.subplots(2, 1)

    axs[0].bar(*zip(*internalData))
    axs[0].set_title("Average added internal links per type of user")
    axs[1].bar(*zip(*externalData))
    axs[1].set_title("Average added external links per type of user")
    plt.gcf().set_size_inches(5, 10)
    removeSpines(axs[0])
    removeSpines(axs[1])
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def specialUsersPlot(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "specialUsersPlot"
    plt.figure()

    query = """SELECT ug_group, count(ug_user)
    AS 'count'
    FROM user_groups
    GROUP BY ug_group;"""
    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        data = list(map(lambda x: (str(x[0]), x[1]), data))

        with open(dataDir + str(i) + ".txt", "w") as file:
            file.write(str(data))
    else:
        data = [
            ("abusefilter", 150),
            ("abusefilter-helper", 19),
            ("accountcreator", 35),
            ("autoreviewer", 4092),
            ("bot", 309),
            ("bureaucrat", 19),
            ("checkuser", 43),
            ("confirmed", 428),
            ("copyviobot", 1),
            ("epadmin", 2),
            ("eventcoordinator", 131),
            ("extendedconfirmed", 50792),
            ("extendedmover", 309),
            ("filemover", 403),
            ("flow-bot", 1),
            ("founder", 1),
            ("import", 2),
            ("interface-admin", 11),
            ("ipblock-exempt", 418),
            ("massmessage-sender", 59),
            ("oversight", 45),
            ("patroller", 724),
            ("researcher", 3),
            ("reviewer", 7370),
            ("rollbacker", 6281),
            ("sysop", 1140),
            ("templateeditor", 184),
        ]

    fig, ax = plt.subplots()  # Create a figure and an axes.
    ax.barh(*zip(*data))
    ax.invert_yaxis()
    ax.set_ylabel("User groups")  # Add an x-label to the axes.
    ax.set_xlabel("Number of Users (log)")  # Add a y-label to the axes.
    ax.set_xscale("log")
    ax.set_title("Number of Users per User Group")  # Add a title to the axes.
    ax.xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
    plt.gcf().set_size_inches(7, 7)
    singlePlot(plt, ax, "x")
    plt.savefig(figname + "-log", bbox_inches="tight", pad_inches=0.25, dpi=200)

    ax.set_xlabel("Number of Users (linear)")
    ax.set_xscale("linear")

    plt.gcf().set_size_inches(7, 7)
    singlePlot(plt, ax, "x")
    plt.savefig(figname + "-linear", bbox_inches="tight", pad_inches=0.25, dpi=200)


#
def averageAllSpecial(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "averageAllSpecial"
    plt.figure()

    columns = [
        "added_length",
        "deleted_length",
        "del_words",
        "comment_length",
        "ins_longest_inserted_word",
        "ins_longest_character_sequence",
        "ins_internal_link",
        "ins_external_link",
        "blanking",
        "comment_copyedit",
        "comment_personal_life",
        "comment_special_chars",
        "ins_capitalization",
        "ins_digits",
        "ins_pronouns",
        "ins_special_chars",
        "ins_vulgarity",
        "ins_whitespace",
        "reverted",
        "added_sentiment",
        "deleted_sentiment",
    ]

    allEdits = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment)  FROM edit;"""
    if not dryrun:
        cursor.execute(allEdits,)
        allData = cursor.fetchall()
        allData = list(*allData)
        with open(dataDir + str(i) + "-all.txt", "w") as file:
            file.write(str(allData))
    else:
        allData = [
            442.0422,
            439.0867,
            58.0321,
            49.1949,
            10.6587,
            1.8952,
            1.6529,
            0.1304,
            0.0022,
            0.0005,
            0.0002,
            0.11972271,
            0.10387291,
            0.02747601,
            0.00610185,
            0.12846018,
            0.0143,
            0.16946286,
            0.0293,
            0.03135975155021137,
            0.0055170703440406196,
        ]

    query = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),AVG(deleted_sentiment)  FROM edit
    inner join user
    on user.id = edit.user_table_id
    where user.blocked is null
    and user.user_special is null
    and user.ip_address is null
    and user.bot is null;"""
    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        data = list(*data)
        with open(dataDir + str(i) + "-user.txt", "w") as file:
            file.write(str(data))
    else:
        data = [
            525.9844,
            427.2599,
            58.6059,
            37.0737,
            10.5163,
            1.8895,
            1.7960,
            0.1359,
            0.0029,
            0.0005,
            0.0003,
            0.11632597,
            0.10173668,
            0.02940640,
            0.00933118,
            0.10858162,
            0.0192,
            0.18442976,
            0.0325,
            0.05423712919836253,
            0.006679179803724929,
        ]

    special = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),AVG(deleted_sentiment)  FROM edit
    inner join user
    on user.id = edit.user_table_id
    where user.user_special is True;"""
    if not dryrun:
        cursor.execute(special,)
        specialData = cursor.fetchall()
        specialData = list(*specialData)
        with open(dataDir + str(i) + "-special.txt", "w") as file:
            file.write(str(specialData))
    else:
        specialData = [
            398.5122,
            392.4957,
            50.8446,
            52.4496,
            10.5209,
            1.7682,
            1.6357,
            0.1278,
            0.0016,
            0.0006,
            0.0002,
            0.11922957,
            0.10697243,
            0.02570266,
            0.00522568,
            0.13717350,
            0.0093,
            0.15875237,
            0.0148,
            0.02470609377917194,
            0.004687928593039355,
        ]

    ip = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),AVG(deleted_sentiment)  FROM edit
    inner join user
    on user.id = edit.user_table_id
    where user.ip_address is True
    and user.blocked is not true;"""
    if not dryrun:
        cursor.execute(ip,)
        ipData = cursor.fetchall()
        ipData = list(*ipData)
        with open(dataDir + str(i) + "-ip.txt", "w") as file:
            file.write(str(ipData))
    else:
        ipData = [
            478.6787,
            540.9392,
            75.8385,
            25.4024,
            12.7483,
            2.9722,
            1.0498,
            0.1154,
            0.0066,
            0.0002,
            0.0005,
            0.10915781,
            0.09348089,
            0.04645136,
            0.00952301,
            0.08899232,
            0.0434,
            0.22379311,
            0.1437,
            0.05003652881927706,
            0.008112887395128948,
        ]

    ipBlocked = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),AVG(deleted_sentiment)  FROM edit
    inner join user
    on user.id = edit.user_table_id
    where user.ip_address is True
    and user.blocked is true;"""
    if not dryrun:
        cursor.execute(ipBlocked,)
        ipBlockedData = cursor.fetchall()
        ipBlockedData = list(*ipBlockedData)
        with open(dataDir + str(i) + "-ipBlocked.txt", "w") as file:
            file.write(str(ipBlockedData))
    else:
        ipBlockedData = [
            574.6621,
            321.4382,
            42.5342,
            32.2950,
            11.4884,
            2.4286,
            1.4061,
            0.1595,
            0.0406,
            0.0004,
            0.0010,
            0.10968559,
            0.08657087,
            0.05258113,
            0.00762512,
            0.09092609,
            0.0437,
            0.20707933,
            0.2118,
            0.039283604989237844,
            0.005879388956523799,
        ]

    blocked = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),AVG(deleted_sentiment)  FROM edit
    inner join user
    on user.id = edit.user_table_id
    where user.blocked is True;"""
    if not dryrun:
        cursor.execute(blocked,)
        blockedData = cursor.fetchall()
        blockedData = list(*blockedData)
        with open(dataDir + str(i) + "-blocked.txt", "w") as file:
            file.write(str(blockedData))
    else:
        blockedData = [
            376.9058,
            374.0861,
            49.9100,
            48.6153,
            9.6661,
            1.7168,
            1.3400,
            0.1222,
            0.0022,
            0.0005,
            0.0002,
            0.12568887,
            0.10028163,
            0.01931273,
            0.00505370,
            0.12080836,
            0.0153,
            0.16692144,
            0.0281,
            0.027887433037106706,
            0.00475190706470203,
        ]

    bot = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),AVG(deleted_sentiment)  FROM edit
    inner join user
    on user.id = edit.user_table_id
    where user.bot is True;"""
    if not dryrun:
        cursor.execute(bot,)
        botData = cursor.fetchall()
        botData = list(*botData)
        with open(dataDir + str(i) + "-bot.txt", "w") as file:
            file.write(str(botData))
    else:
        botData = [
            549.0619,
            487.8700,
            62.0877,
            87.5882,
            12.1183,
            1.8673,
            2.3044,
            0.1800,
            0.0011,
            0.0000,
            0.0001,
            0.14624979,
            0.09998104,
            0.03534354,
            0.00527977,
            0.15460378,
            0.0080,
            0.15773835,
            0.0248,
            0.005518091804445644,
            0.004024606970162133,
        ]

    fig, axs = plt.subplots(4, 1, gridspec_kw={"height_ratios": [2, 2, 3, 11]})

    fig.suptitle("Average of all integer edit fields")

    start = 0
    end = 2
    plotRange = range(start, end)

    axs[0].hlines(
        y=plotRange,
        xmin=[
            min(a, b, c, d, e, f)
            for a, b, c, d, e, f in zip(
                data[:end],
                specialData[:end],
                blockedData[:end],
                ipData[:end],
                ipBlockedData[:end],
                botData[:end],
            )
        ],
        xmax=[
            max(a, b, c, d, e, f)
            for a, b, c, d, e, f in zip(
                data[:end],
                specialData[:end],
                blockedData[:end],
                ipData[:end],
                ipBlockedData[:end],
                botData[:end],
            )
        ],
        color="grey",
        alpha=0.4,
    )
    axs[0].vlines(
        x=allData[:2],
        ymin=list(map(lambda x: x - 0.5, plotRange)),
        ymax=list(map(lambda x: x + 0.5, plotRange)),
        color="grey",
        alpha=0.4,
    )
    axs[0].scatter(data[:2], plotRange, color="navy", label="all users")
    axs[0].scatter(
        specialData[:2], plotRange, color="gold", label="users with privileges"
    )
    axs[0].scatter(botData[:2], plotRange, color="mediumaquamarine", label="bots")
    axs[0].scatter(ipData[:2], plotRange, color="skyblue", label="ip users")
    axs[0].scatter(
        ipBlockedData[:2], plotRange, color="hotpink", label="blocked56 ip users"
    )
    axs[0].scatter(blockedData[:2], plotRange, color="orangered", label="blocked users")
    axs[0].set_yticklabels(columns[:2])
    axs[0].set_yticks(plotRange)
    axs[0].legend(
        loc="upper center", bbox_to_anchor=(0.5, 2), ncol=3, fancybox=True, shadow=True,
    )
    # axs[0].set_ylim([start - 0.5, end + 0.5])

    start = 3
    end = 5
    plotRange = range(1, end - start + 1)
    axs[1].hlines(
        y=plotRange,
        xmin=[
            min(a, b, c, d, e, f)
            for a, b, c, d, e, f in zip(
                data[start:end],
                specialData[start:end],
                blockedData[start:end],
                ipData[start:end],
                ipBlockedData[start:end],
                botData[start:end],
            )
        ],
        xmax=[
            max(a, b, c, d, e, f)
            for a, b, c, d, e, f in zip(
                data[start:end],
                specialData[start:end],
                blockedData[start:end],
                ipData[start:end],
                ipBlockedData[start:end],
                botData[start:end],
            )
        ],
        color="grey",
        alpha=0.4,
    )
    axs[1].vlines(
        x=allData[start:end],
        ymin=list(map(lambda x: x - 0.5, plotRange)),
        ymax=list(map(lambda x: x + 0.5, plotRange)),
        color="grey",
        alpha=0.4,
    )
    axs[1].scatter(data[start:end], plotRange, color="navy", label="all users")
    axs[1].scatter(
        specialData[start:end], plotRange, color="gold", label="users with privileges"
    )
    axs[1].scatter(
        botData[start:end], plotRange, color="mediumaquamarine", label="bots"
    )
    axs[1].scatter(ipData[start:end], plotRange, color="skyblue", label="ip users")
    axs[1].scatter(
        ipBlockedData[start:end], plotRange, color="hotpink", label="blocked ip users"
    )
    axs[1].scatter(
        blockedData[start:end], plotRange, color="orangered", label="blocked users"
    )
    axs[1].set_yticklabels(columns[start:end])
    axs[1].set_yticks(plotRange)
    # axs[1].set_ylim([0.5, 2.25])

    start = 5
    end = 8
    plotRange = range(1, end - start + 1)
    axs[2].hlines(
        y=plotRange,
        xmin=[
            min(a, b, c, d, e, f)
            for a, b, c, d, e, f in zip(
                data[start:end],
                specialData[start:end],
                blockedData[start:end],
                ipData[start:end],
                ipBlockedData[start:end],
                botData[start:end],
            )
        ],
        xmax=[
            max(a, b, c, d, e, f)
            for a, b, c, d, e, f in zip(
                data[start:end],
                specialData[start:end],
                blockedData[start:end],
                ipData[start:end],
                ipBlockedData[start:end],
                botData[start:end],
            )
        ],
        color="grey",
        alpha=0.4,
    )
    axs[2].vlines(
        x=allData[start:end],
        ymin=list(map(lambda x: x - 0.5, plotRange)),
        ymax=list(map(lambda x: x + 0.5, plotRange)),
        color="grey",
        alpha=0.4,
    )
    axs[2].scatter(data[start:end], plotRange, color="navy", label="all users")
    axs[2].scatter(
        specialData[start:end], plotRange, color="gold", label="users with privileges"
    )
    axs[2].scatter(
        botData[start:end], plotRange, color="mediumaquamarine", label="bots"
    )
    axs[2].scatter(ipData[start:end], plotRange, color="skyblue", label="ip users")
    axs[2].scatter(
        ipBlockedData[start:end], plotRange, color="hotpink", label="blocked ip users"
    )
    axs[2].scatter(
        blockedData[start:end], plotRange, color="orangered", label="blocked users"
    )
    axs[2].set_yticklabels(columns[start:end])
    axs[2].set_yticks(plotRange)
    axs[2].set_xlim(left=0)

    start = 8
    end = 21
    plotRange = range(1, end - start + 1)
    axs[3].hlines(
        y=plotRange,
        xmin=[
            min(a, b, c, d, e, f)
            for a, b, c, d, e, f in zip(
                data[start:],
                specialData[start:],
                blockedData[start:],
                ipData[start:],
                ipBlockedData[start:],
                botData[start:],
            )
        ],
        xmax=[
            max(a, b, c, d, e, f)
            for a, b, c, d, e, f in zip(
                data[start:],
                specialData[start:],
                blockedData[start:],
                ipData[start:],
                ipBlockedData[start:],
                botData[start:],
            )
        ],
        color="grey",
        alpha=0.4,
    )
    axs[3].vlines(
        x=allData[start:],
        ymin=list(map(lambda x: x - 0.5, plotRange)),
        ymax=list(map(lambda x: x + 0.5, plotRange)),
        color="grey",
        alpha=0.4,
    )
    axs[3].scatter(data[start:], plotRange, color="navy", label="all users")
    axs[3].scatter(
        specialData[start:], plotRange, color="gold", label="users with privileges"
    )
    axs[3].scatter(botData[start:], plotRange, color="mediumaquamarine", label="bots")
    axs[3].scatter(ipData[start:], plotRange, color="skyblue", label="ip users")
    axs[3].scatter(
        ipBlockedData[start:], plotRange, color="hotpink", label="blocked ip users"
    )
    axs[3].scatter(
        blockedData[start:], plotRange, color="orangered", label="blocked users"
    )
    axs[3].set_yticklabels(columns[start:])
    axs[3].set_yticks(plotRange)
    axs[3].set_xlim(left=0)

    plt.gcf().set_size_inches(9.5, 9.5)
    removeSpines(axs[0])
    removeSpines(axs[1])
    removeSpines(axs[2])
    removeSpines(axs[3])

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def compositionOfUserIP(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "compositionOfUserIP"
    plt.figure()

    query = """SELECT
    (SELECT count(*) FROM user
    WHERE bot is not true and ip_address is not true and blocked is not true),
    (SELECT count(*) FROM user
    WHERE bot is not true and ip_address is true and blocked is not true),
    (SELECT count(*) FROM user
    WHERE bot is not true and ip_address is not true and blocked is true),
    (SELECT count(*) FROM user
    WHERE bot is not true and ip_address is true and blocked is true);"""
    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        data = list(*data)
        with open(dataDir + str(i) + ".txt", "w") as file:
            file.write(str(data))
    else:
        data = [8762027, 41358810, 173812, 93851]

    sumUser = data[0] + data[2]
    sumIP = data[1] + data[3]
    proportinateData = [
        data[0] / sumUser,
        data[1] / sumIP,
        data[2] / sumUser,
        data[3] / sumIP,
    ]

    data = [data[i : i + 2] for i in range(0, len(data), 2)]

    xticks = ["users", "ip"]
    labels = ["non-blocked", "blocked"]

    fig, axs = plt.subplots(2, 1)
    axs[0].set_title("Comparison of blocked and unblocked\nusers and IPs")
    axs[0].set_ylabel("Number of Users")
    y_pos_1 = y_pos_2 = 0
    for k, v in enumerate(data):
        abs_bottom = [y_pos_1, y_pos_2]
        axs[0].bar(xticks, v, bottom=abs_bottom, label=labels[k])
        y_pos_1 += v[0]
        y_pos_2 += v[1]

    axs[0].yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
    removeSpines(axs[0])

    data = proportinateData
    data = [data[i : i + 2] for i in range(0, len(data), 2)]
    axs[1].set_title("Proportional")
    axs[1].set_ylabel("Percent")
    y_pos_1 = y_pos_2 = 0
    for k, v in enumerate(data):
        abs_bottom = [y_pos_1, y_pos_2]
        axs[1].bar(xticks, v, bottom=abs_bottom, label=labels[k])
        y_pos_1 += v[0]
        y_pos_2 += v[1]

    removeSpines(axs[1])
    plt.gcf().set_size_inches(5, 10)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def compositionOfUser(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "compositionOfUser"
    plt.figure()

    query = """SELECT
    (SELECT count(*) FROM user
    WHERE bot is not true and ip_address is not true and blocked is not true and user_special is not true),
    (SELECT count(*) FROM user
    WHERE bot is not true and ip_address is not true and blocked is true and user_special is not true),
    (SELECT count(*) FROM user
    WHERE bot is true and ip_address is not true and blocked is not true and user_special is not true),
    (SELECT count(*) FROM user
    WHERE bot is true and ip_address is not true and blocked is true and user_special is not true),
    (SELECT count(*) FROM user
    WHERE bot is not true and ip_address is true and blocked is not true and user_special is not true),
    (SELECT count(*) FROM user
    WHERE bot is not true and ip_address is true and blocked is true and user_special is not true),
    (SELECT count(*) FROM user
    WHERE bot is not true and ip_address is not true and blocked is not true and user_special is true),
    (SELECT count(*) FROM user
    WHERE bot is not true and ip_address is not true and blocked is true and user_special is true);"""
    columns = [
        "users",
        "blocked",
        "bot",
        "bot blocked",
        "ip",
        "ip blocked",
        "special",
        "special blocked",
    ]
    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        data = list(*data)
        with open(dataDir + str(i) + ".txt", "w") as file:
            file.write(str(data))
    else:
        data = [8747943, 173785, 1596, 21, 41358810, 93851, 14084, 27]

    total = sum(data)
    data = list(map(lambda x: x / total, data))

    edits = """SELECT
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id
    WHERE bot is not true and ip_address is not true and blocked is not true and user_special is not true),
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id
    WHERE bot is not true and ip_address is not true and blocked is true and user_special is not true),
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id
    WHERE bot is true and ip_address is not true and blocked is not true and user_special is not true),
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id
    WHERE bot is true and ip_address is not true and blocked is true and user_special is not true),
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id
    WHERE bot is not true and ip_address is true and blocked is not true and user_special is not true),
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id
    WHERE bot is not true and ip_address is true and blocked is true and user_special is not true),
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id
    WHERE bot is not true and ip_address is not true and blocked is not true and user_special is true),
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id
    WHERE bot is not true and ip_address is not true and blocked is true and user_special is true);"""
    columns = [
        "users",
        "blocked",
        "bot",
        "bot blocked",
        "ip",
        "ip blocked",
        "special",
        "special blocked",
    ]
    if not dryrun:
        cursor.execute(edits,)
        editsData = cursor.fetchall()
        editsData = list(*editsData)
        with open(dataDir + str(i) + "-edits.txt", "w") as file:
            file.write(str(editsData))
    else:
        editsData = [17536089, 847162, 2929584, 195019, 5070606, 7926, 23584256, 23897]

    total = sum(editsData)
    editsData = list(map(lambda x: x / total, editsData))

    data = list(zip(data, editsData))
    labels = ["distribution\nof users", "distribution\nof edits"]
    fig, ax = plt.subplots()
    ax.set_title("Distribution of users\nand how many edits on talkpages they make")
    y_pos_1 = y_pos_2 = 0
    for k, v in enumerate(data):
        abs_bottom = [y_pos_1, y_pos_2]
        ax.bar(labels, v, bottom=abs_bottom, label=columns[k])
        y_pos_1 += v[0]
        y_pos_2 += v[1]
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(reversed(handles), reversed(labels), loc="center left")

    ax.set_ylim([0, 1])
    plt.gcf().set_size_inches(5, 10)
    removeSpines(ax)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


#
def aggregations(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "aggregations"
    plt.figure()

    columns = [
        "added_length",
        "deleted_length",
        "del_words",
        "comment_length",
        "ins_longest_inserted_word",
        "ins_longest_character_sequence",
        "ins_internal_link",
        "ins_external_link",
        "blanking",
        "comment_copyedit",
        "comment_personal_life",
        "comment_special_chars",
        "ins_capitalization",
        "ins_digits",
        "ins_pronouns",
        "ins_special_chars",
        "ins_vulgarity",
        "ins_whitespace",
        "reverted",
        "added_sentiment",
        "deleted_sentiment",
    ]

    if not dryrun:
        modesData = []
        for i in columns:
            query = "SELECT {i} FROM edit GROUP BY {i} ORDER BY count(*) DESC LIMIT 1".format(
                i=i
            )
            cursor.execute(query,)
            modesData.append(cursor.fetchall()[0][0])

        with open(dataDir + str(i) + "-modes.txt", "w") as file:
            file.write(str(modesData))
    else:
        modesData = [0, 2, 1, 0, 11, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    mins = """select MIN(added_length),MIN(deleted_length),MIN(del_words),MIN(comment_length),MIN(ins_longest_inserted_word),MIN(ins_longest_character_sequence),MIN(ins_internal_link),MIN(ins_external_link),MIN(blanking),MIN(comment_copyedit),MIN(comment_personal_life),MIN(comment_special_chars),MIN(ins_capitalization),MIN(ins_digits),MIN(ins_pronouns),MIN(ins_special_chars),MIN(ins_vulgarity),MIN(ins_whitespace),MIN(reverted),MIN(added_sentiment),MIN(deleted_sentiment) FROM edit;"""
    if not dryrun:
        cursor.execute(mins,)
        minsData = cursor.fetchall()
        minsData = list(*minsData)
        with open(dataDir + str(i) + "-mins.txt", "w") as file:
            file.write(str(minsData))
    else:
        minsData = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0.0000,
            0.0000,
            0.0000,
            0.0000,
            0.0000,
            0,
            0.0000,
            0,
            -1.0,
            -1.0,
        ]

    maxs = """select MAX(added_length),MAX(deleted_length),MAX(del_words),MAX(comment_length),MAX(ins_longest_inserted_word),MAX(ins_longest_character_sequence),MAX(ins_internal_link),MAX(ins_external_link),MAX(blanking),MAX(comment_copyedit),MAX(comment_personal_life),MAX(comment_special_chars),MAX(ins_capitalization),MAX(ins_digits),MAX(ins_pronouns),MAX(ins_special_chars),MAX(ins_vulgarity),MAX(ins_whitespace),MAX(reverted),MAX(added_sentiment),MAX(deleted_sentiment)  FROM edit;"""
    if not dryrun:
        cursor.execute(maxs,)
        maxsData = cursor.fetchall()
        maxsData = list(*maxsData)
        with open(dataDir + str(i) + "-maxs.txt", "w") as file:
            file.write(str(maxsData))
    else:
        maxsData = [
            8388607,
            8388607,
            2426845,
            127,
            32767,
            32767,
            24365,
            32767,
            1,
            1,
            1,
            0.9999,
            0.9999,
            0.9999,
            0.9999,
            0.9999,
            1,
            0.9999,
            1,
            1.0,
            1.0,
        ]

    means = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),AVG(deleted_sentiment) from edit;"""
    if not dryrun:
        cursor.execute(means,)
        meansData = cursor.fetchall()
        meansData = list(*meansData)
        with open(dataDir + str(i) + "-means.txt", "w") as file:
            file.write(str(meansData))
    else:
        meansData = [
            442.0422,
            439.0867,
            58.0321,
            49.1949,
            10.6587,
            1.8952,
            1.6529,
            0.1304,
            0.0022,
            0.0005,
            0.0002,
            0.11972271,
            0.10387291,
            0.02747601,
            0.00610185,
            0.12846018,
            0.0143,
            0.16946286,
            0.0293,
            0.03135975155021137,
            0.0055170703440406196,
        ]

    stds = """select STD(added_length),STD(deleted_length),STD(del_words),STD(comment_length),STD(ins_longest_inserted_word),STD(ins_longest_character_sequence),STD(ins_internal_link),STD(ins_external_link),STD(blanking),STD(comment_copyedit),STD(comment_personal_life),STD(comment_special_chars),STD(ins_capitalization),STD(ins_digits),STD(ins_pronouns),STD(ins_special_chars),STD(ins_vulgarity),STD(ins_whitespace),STD(reverted),STD(added_sentiment),STD(deleted_sentiment) from edit;"""
    if not dryrun:
        cursor.execute(stds,)
        stdsData = cursor.fetchall()
        stdsData = list(*stdsData)
        with open(dataDir + str(i) + "-stds.txt", "w") as file:
            file.write(str(stdsData))
    else:
        stdsData = [
            4654.176162916367,
            6176.346864990649,
            951.2080429740175,
            39.922080083596796,
            72.77314313715188,
            45.67935596915416,
            17.34742048576987,
            5.371908826641828,
            0.047305664882096865,
            0.022598233982907077,
            0.014979221561754661,
            0.09649544409376277,
            0.13556309951733453,
            0.0529137673082975,
            0.018949801230515435,
            0.07763594209856826,
            0.11881033215053255,
            0.18192642687661204,
            0.16869769991099628,
            0.14008787360862252,
            0.0690388085081368,
        ]

    stdsData = list(map(sum, zip(stdsData, meansData)))

    fig, axs = plt.subplots(4, 1, gridspec_kw={"height_ratios": [3, 4, 12, 2]})

    fig.suptitle("Min, max, mean and standard deviation of all fields")

    start = 0
    end = 3
    plotRange = range(start, end)

    axs[0].hlines(
        y=plotRange, xmin=minsData[:end], xmax=maxsData[:end], color="grey", alpha=0.4,
    )
    axs[0].vlines(
        x=[*minsData[:end], *maxsData[:end]],
        ymin=list(map(lambda x: x - 0.5, plotRange)),
        ymax=list(map(lambda x: x + 0.5, plotRange)),
        color="black",
    )
    axs[0].scatter(
        stdsData[:end], plotRange, color="skyblue", label="Standard Deviation"
    )
    axs[0].scatter(meansData[:end], plotRange, color="black", label="Mean")
    axs[0].set_yticklabels(columns[:end])
    axs[0].set_yticks(plotRange)
    axs[0].xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
    axs[0].legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.5),
        ncol=3,
        fancybox=True,
        shadow=True,
    )

    start = 4
    end = 8
    plotRange = range(1, end - start + 1)

    axs[1].hlines(
        y=plotRange,
        xmin=minsData[start:end],
        xmax=maxsData[start:end],
        color="grey",
        alpha=0.4,
    )
    axs[1].vlines(
        x=[*minsData[start:end], *maxsData[start:end]],
        ymin=list(map(lambda x: x - 0.5, plotRange)),
        ymax=list(map(lambda x: x + 0.5, plotRange)),
        color="black",
    )
    axs[1].scatter(
        stdsData[start:end], plotRange, color="skyblue", label="Standard Deviation"
    )
    axs[1].scatter(meansData[start:end], plotRange, color="black", label="Mode")
    axs[1].set_yticklabels(columns[start:end])
    axs[1].set_yticks(plotRange)
    axs[1].xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))

    start = 8
    end = 19
    plotRange = range(1, end - start + 1)

    axs[2].hlines(
        y=plotRange,
        xmin=minsData[start:end],
        xmax=maxsData[start:end],
        color="grey",
        alpha=0.4,
    )
    axs[2].vlines(
        x=[*minsData[start:end], *maxsData[start:end]],
        ymin=list(map(lambda x: x - 0.5, plotRange)),
        ymax=list(map(lambda x: x + 0.5, plotRange)),
        color="black",
    )
    axs[2].scatter(
        stdsData[start:end], plotRange, color="skyblue", label="Standard Deviation"
    )
    invertedStds = list(
        map(
            lambda x: max(2 * x[0] - x[1], 0),
            zip(meansData[start:end], stdsData[start:end]),
        )
    )
    axs[2].scatter(invertedStds, plotRange, color="skyblue")
    axs[2].scatter(meansData[start:end], plotRange, color="black", label="Mode")
    axs[2].set_yticklabels(columns[start:end])
    axs[2].set_yticks(plotRange)

    start = 19
    end = 21
    plotRange = range(1, end - start + 1)

    axs[3].hlines(
        y=plotRange,
        xmin=minsData[start:end],
        xmax=maxsData[start:end],
        color="grey",
        alpha=0.4,
    )
    axs[3].vlines(
        x=[*minsData[start:end], *maxsData[start:end]],
        ymin=list(map(lambda x: x - 0.5, plotRange)),
        ymax=list(map(lambda x: x + 0.5, plotRange)),
        color="black",
    )
    axs[3].scatter(meansData[start:end], plotRange, color="black", label="Mode")
    axs[3].scatter(
        stdsData[start:end], plotRange, color="skyblue", label="Standard Deviation"
    )
    invertedStds = list(
        map(lambda x: 2 * x[0] - x[1], zip(meansData[start:end], stdsData[start:end]))
    )
    axs[3].scatter(invertedStds, plotRange, color="skyblue")
    axs[3].set_yticklabels(columns[start:end])
    axs[3].set_yticks(plotRange)

    plt.gcf().set_size_inches(9.5, 9.5)
    removeSpines(axs[0])
    removeSpines(axs[1])
    removeSpines(axs[2])
    removeSpines(axs[3])

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def editBooleans(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "booleanPieCharts"
    plt.figure()

    query = """select count(*), sum(comment_copyedit = 1), sum(comment_personal_life = 1), sum(ins_vulgarity = 1), sum(reverted = 1), sum(blanking = 1) from edit;"""

    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        data = list(*data)

        population = data.pop(0)
        with open(dataDir + str(i) + ".txt", "w") as file:
            file.write(str(data) + "\n" + str(population))
    else:
        data = [29544, 12977, 828078, 1695274, 129688]
        population = 57822696

    columns = [
        "comment_copyedit",
        "comment_personal_life",
        "ins_vulgarity",
        "reverted",
        "blanking",
    ]

    # create a figure with two subplots
    fig, axs = plt.subplots(2, 3)

    fig.suptitle("Ratios of boolean features")

    axs = axs.ravel()

    # plot each pie chart in a separate subplot
    for key, value in enumerate(columns):
        axs[key].set_title(value)
        axs[key].pie([population, data[key]])

    axs[-1].axis("off")

    plt.gcf().set_size_inches(8, 6)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def userBooleans(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "userBooleans"
    plt.figure()

    query = """select count(*), sum(confirmed = 1), sum(autoconfirmed = 1), sum(user_special = 1), sum(bot = 1), sum(blocked = 1) from user;"""

    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        data = list(*data)

        population = data.pop(0)
        with open(dataDir + str(i) + ".txt", "w") as file:
            file.write(str(data) + "\n" + str(population))
    else:
        data = [74469, 1603322, 14414, 1584, 267678]
        population = 50390084

    columns = ["confirmed", "autoconfirmed", "user_special", "bot", "blocked"]

    # create a figure with two subplots
    fig, axs = plt.subplots(2, 3)

    fig.suptitle("Ratios of boolean features")

    axs = axs.ravel()

    # plot each pie chart in a separate subplot
    for key, value in enumerate(columns):
        axs[key].set_title(value)
        axs[key].pie([population, data[key]])

    axs[-1].axis("off")

    plt.gcf().set_size_inches(8, 6)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def talkpageEditsOverTime(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "talkpageEditsOverTime"
    plt.figure()

    query = "select cast(edit_date as date) as date, count(*) from edit group by date;"

    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()

        with open(dataDir + str(i) + ".csv", "w") as file:
            writer = csv.writer(file, delimiter=",")
            for line in data:
                writer.writerow(line)
    else:
        with open(dataDir + str(i) + ".csv", "r") as file:
            data = []
            reader = csv.reader(file, delimiter=",")
            for line in reader:
                data.append(line)

            data = list(map(lambda x: (dt.strptime(x[0], "%Y-%m-%d"), int(x[1])), data))

    dates = list(map(lambda x: matplotlib.dates.date2num(x[0]), data))
    values = [x[1] for x in data]
    fig, ax = plt.subplots()

    ax.set_title("Talkpage edits over time")

    ax.plot_date(dates, values, "C0-")

    plt.gcf().set_size_inches(12, 7.5)
    
    singlePlot(plt, ax, "y")

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


#
def averageAllEpoch(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "averageAllEpoch"
    plt.figure()

    columns = [
        "added_length",
        "deleted_length",
        "del_words",
        "comment_length",
        "ins_longest_inserted_word",
        "ins_longest_character_sequence",
        "ins_internal_link",
        "ins_external_link",
        "blanking",
        "comment_copyedit",
        "comment_personal_life",
        "comment_special_chars",
        "ins_capitalization",
        "ins_digits",
        "ins_pronouns",
        "ins_special_chars",
        "ins_vulgarity",
        "ins_whitespace",
        "reverted",
        "added_sentiment",
        "deleted_sentiment",
    ]

    allEdits = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment)  FROM edit;"""
    if not dryrun:
        cursor.execute(allEdits,)
        allData = cursor.fetchall()
        allData = list(*allData)
        with open(dataDir + str(i) + "-all.txt", "w") as file:
            file.write(str(allData))
    else:
        allData = [
            442.0422,
            439.0867,
            58.0321,
            49.1949,
            10.6587,
            1.8952,
            1.6529,
            0.1304,
            0.0022,
            0.0005,
            0.0002,
            0.11972271,
            0.10387291,
            0.02747601,
            0.00610185,
            0.12846018,
            0.0143,
            0.16946286,
            0.0293,
            0.03135975155021137,
            0.0055170703440406196,
        ]

    before = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment)  FROM edit
    where cast(edit_date as date) < '2010-09-01';"""
    if not dryrun:
        cursor.execute(before,)
        beforeData = cursor.fetchall()
        beforeData = list(*beforeData)
        with open(dataDir + str(i) + "-before.txt", "w") as file:
            file.write(str(beforeData))
    else:
        beforeData = [
            479.8468,
            576.8820,
            78.3332,
            44.2190,
            10.3822,
            1.9279,
            1.7219,
            0.1206,
            0.0031,
            0.0005,
            0.0002,
            0.12086085,
            0.10419313,
            0.02750613,
            0.00671131,
            0.12564456,
            0.0182,
            0.17842393,
            0.0342,
            0.0406774523917268,
            0.0076446326158984374,
        ]

    after = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),AVG(deleted_sentiment)  FROM edit
    where cast(edit_date as date) >= '2010-09-01';"""
    if not dryrun:
        cursor.execute(after,)
        afterData = cursor.fetchall()
        afterData = list(*afterData)
        with open(dataDir + str(i) + "-after.txt", "w") as file:
            file.write(str(afterData))
    else:
        afterData = [
            409.2529,
            319.5716,
            40.4241,
            53.5107,
            10.8985,
            1.8669,
            1.5930,
            0.1389,
            0.0015,
            0.0005,
            0.0003,
            0.11873556,
            0.10359516,
            0.02744988,
            0.00557324,
            0.13090228,
            0.0110,
            0.16169059,
            0.0251,
            0.023278155069148418,
            0.0036717546312976914,
        ]

    fig, axs = plt.subplots(4, 1, gridspec_kw={"height_ratios": [2, 2, 3, 11]})

    fig.suptitle("Average of edit fields before and after the midpoint of the dataset")

    start = 0
    end = 2
    plotRange = range(start, end)

    axs[0].hlines(
        y=plotRange,
        xmin=[min(a, b) for a, b in zip(beforeData[:end], afterData[:end],)],
        xmax=[max(a, b) for a, b in zip(beforeData[:end], afterData[:end],)],
        color="grey",
        alpha=0.4,
    )
    axs[0].vlines(
        x=allData[:2],
        ymin=list(map(lambda x: x - 0.5, plotRange)),
        ymax=list(map(lambda x: x + 0.5, plotRange)),
        color="grey",
        alpha=0.4,
    )
    axs[0].scatter(
        beforeData[:2], plotRange, color="skyblue", label="before 1st September 2010"
    )
    axs[0].scatter(
        afterData[:2], plotRange, color="orangered", label="after 1st September 2010"
    )
    axs[0].set_yticklabels(columns[:2])
    axs[0].set_yticks(plotRange)
    axs[0].legend(
        loc="upper center", bbox_to_anchor=(0.5, 2), ncol=3, fancybox=True, shadow=True,
    )

    start = 3
    end = 5
    plotRange = range(1, end - start + 1)
    axs[1].hlines(
        y=plotRange,
        xmin=[min(a, b) for a, b in zip(beforeData[start:end], afterData[start:end],)],
        xmax=[max(a, b) for a, b in zip(beforeData[start:end], afterData[start:end],)],
        color="grey",
        alpha=0.4,
    )
    axs[1].vlines(
        x=allData[start:end],
        ymin=list(map(lambda x: x - 0.5, plotRange)),
        ymax=list(map(lambda x: x + 0.5, plotRange)),
        color="grey",
        alpha=0.4,
    )
    axs[1].scatter(beforeData[start:end], plotRange, color="skyblue", label="ip users")
    axs[1].scatter(
        afterData[start:end], plotRange, color="orangered", label="blocked users"
    )
    axs[1].set_yticklabels(columns[start:end])
    axs[1].set_yticks(plotRange)

    start = 5
    end = 8
    plotRange = range(1, end - start + 1)
    axs[2].hlines(
        y=plotRange,
        xmin=[min(a, b) for a, b in zip(beforeData[start:end], afterData[start:end],)],
        xmax=[max(a, b) for a, b in zip(beforeData[start:end], afterData[start:end],)],
        color="grey",
        alpha=0.4,
    )
    axs[2].vlines(
        x=allData[start:end],
        ymin=list(map(lambda x: x - 0.5, plotRange)),
        ymax=list(map(lambda x: x + 0.5, plotRange)),
        color="grey",
        alpha=0.4,
    )
    axs[2].scatter(beforeData[start:end], plotRange, color="skyblue", label="ip users")
    axs[2].scatter(
        afterData[start:end], plotRange, color="orangered", label="blocked users"
    )
    axs[2].set_yticklabels(columns[start:end])
    axs[2].set_yticks(plotRange)
    axs[2].set_xlim(left=0)

    start = 8
    end = 21
    plotRange = range(1, end - start + 1)
    axs[3].hlines(
        y=plotRange,
        xmin=[min(a, b) for a, b in zip(beforeData[start:end], afterData[start:end],)],
        xmax=[max(a, b) for a, b in zip(beforeData[start:end], afterData[start:end],)],
        color="grey",
        alpha=0.4,
    )
    axs[3].vlines(
        x=allData[start:],
        ymin=list(map(lambda x: x - 0.5, plotRange)),
        ymax=list(map(lambda x: x + 0.5, plotRange)),
        color="grey",
        alpha=0.4,
    )
    axs[3].scatter(beforeData[start:], plotRange, color="skyblue", label="ip users")
    axs[3].scatter(
        afterData[start:], plotRange, color="orangered", label="blocked users"
    )
    axs[3].set_yticklabels(columns[start:])
    axs[3].set_yticks(plotRange)
    axs[3].set_xlim(left=0)

    plt.gcf().set_size_inches(9.5, 9.5)
    removeSpines(axs[0])
    removeSpines(axs[1])
    removeSpines(axs[2])
    removeSpines(axs[3])

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def averageFeaturesOverTime(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "averageFeaturesOverTime"
    plt.figure()

    columns = [
        "added_length",
        "deleted_length",
        "del_words",
        "comment_length",
        "ins_longest_inserted_word",
        "ins_longest_character_sequence",
        "ins_internal_link",
        "ins_external_link",
        "blanking",
        "comment_copyedit",
        "comment_personal_life",
        "comment_special_chars",
        "ins_capitalization",
        "ins_digits",
        "ins_pronouns",
        "ins_special_chars",
        "ins_vulgarity",
        "ins_whitespace",
        "reverted",
        "added_sentiment",
        "deleted_sentiment",
    ]

    query = """select YEAR(edit_date), MONTH(edit_date), AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment)  FROM edit
    GROUP BY YEAR(edit_date), MONTH(edit_date) 
    order by YEAR(edit_date), MONTH(edit_date) ;"""

    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()

        with open(dataDir + str(i) + ".csv", "w") as file:
            writer = csv.writer(file, delimiter=",")
            for line in data:
                writer.writerow(line)
    else:
        with open(dataDir + str(i) + ".csv", "r") as file:
            data = []
            reader = csv.reader(file, delimiter=",")
            for line in reader:
                data.append(line)

            data = list(map(lambda x: tuple(map(float, x)), data))

    dates = list(
        map(
            lambda x: matplotlib.dates.datestr2num(
                str(int(x[0])) + "-" + str(int(x[1]))
            ),
            data,
        )
    )

    values = list(map(lambda x: x[2:], data))

    fig, axs = plt.subplots(4, 1)

    axs[0].set_title("Talkpage edits over time")

    colors = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]
    start = [0, 3, 5, 8]
    end = [3, 5, 8, 21]
    for j in range(4):
        for i in range(start[j], end[j]):
            axs[j].plot_date(
                dates,
                list(map(lambda x: x[i], values)),
                "C0-",
                label=columns[i],
                c=colors[i % 10],
            )
        axs[j].legend(loc="best")
        removeSpines(axs[j])
    plt.gcf().set_size_inches(20, 15)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def averageFeaturesOverYear(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "averageFeaturesOverYear"
    plt.figure()

    columns = [
        "added_length",
        "deleted_length",
        "del_words",
        "comment_length",
        "ins_longest_inserted_word",
        "ins_longest_character_sequence",
        "ins_internal_link",
        "ins_external_link",
        "blanking",
        "comment_copyedit",
        "comment_personal_life",
        "comment_special_chars",
        "ins_capitalization",
        "ins_digits",
        "ins_pronouns",
        "ins_special_chars",
        "ins_vulgarity",
        "ins_whitespace",
        "reverted",
        "added_sentiment",
        "deleted_sentiment",
    ]

    query = """select YEAR(edit_date), AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment)  FROM edit
    GROUP BY YEAR(edit_date) 
    order by YEAR(edit_date) ;"""

    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()

        with open(dataDir + str(i) + ".csv", "w") as file:
            writer = csv.writer(file, delimiter=",")
            for line in data:
                writer.writerow(line)
    else:
        with open(dataDir + str(i) + ".csv", "r") as file:
            data = []
            reader = csv.reader(file, delimiter=",")
            for line in reader:
                data.append(line)

            data = list(map(lambda x: tuple(map(float, x)), data))

    dates = list(map(lambda x: matplotlib.dates.datestr2num(str(int(x[0]))), data,))

    values = list(map(lambda x: x[1:], data))

    fig, axs = plt.subplots(4, 1)

    axs[0].set_title("Talkpage edits by averaged by year")

    colors = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]
    start = [0, 3, 5, 8]
    end = [3, 5, 8, 21]
    for j in range(4):
        for i in range(start[j], end[j]):
            axs[j].plot_date(
                dates,
                list(map(lambda x: x[i], values)),
                "C0-",
                label=columns[i],
                c=colors[i % 10],
            )
        axs[j].legend(loc="best")
        removeSpines(axs[j])
    plt.gcf().set_size_inches(20, 15)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


# --------------------------------------------------------------------------------------


def singlePlot(plt, ax, axis):
    removeSpines(ax)

    if axis == "y":
        ax.yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        showGrid(plt, ax, "y")
    elif axis == "x":
        ax.xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        showGrid(plt, ax, "x")


def threeFigureFormatter(
    x, pos
):  # formatter function takes tick label and tick position
    s = "%d" % x
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ",".join(reversed(groups))


def removeSpines(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def showGrid(plt, ax, axis):
    plt.grid(color="#ccc", which="major", axis=axis, linestyle="solid")
    ax.set_axisbelow(True)


def plot(plotDir: str = "../plots/", dryrun=False):
    """A function"""
    if not os.path.exists(plotDir):
        os.mkdir(plotDir)

    dataDir = plotDir + "data/"
    if not os.path.exists(dataDir):
        os.mkdir(dataDir)

    if not dryrun:
        database, cursor = Database.connect()
    else:
        cursor = 0

    font_files = font_manager.findSystemFonts(fontpaths=["./"])
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    if "Inter" in [f.name for f in font_manager.fontManager.ttflist]:
        matplotlib.rcParams["font.family"] = "Inter"

    # cycle_colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    matplotlib.rcParams["axes.prop_cycle"] = cycler(
        color=[
            "#2271d3",
            "#f88b12",
            "#198424",
            "#db2b19",
            "#7e69d2",
            "#83361b",
            "#e051ac",
            "#727272",
            "#bcbd22",
            "#17becf",
        ]
    )

    # 0
    i = 0
    # partitionStatus(cursor, i, plotDir, dataDir, dryrun)

    # 1
    i = i + 1
    # distributionOfMainEdits(cursor, i, plotDir, dataDir, dryrun)

    # 2
    i = i + 1
    # distributionOfTalkEdits(cursor, i, plotDir, dataDir, dryrun)

    # 3
    i = i + 1
    # numberOfPagesPerNamespace(cursor, i, plotDir, dataDir, dryrun)

    # 4
    i = i + 1
    # editsMainTalkNeither(cursor, i, plotDir, dataDir, dryrun)

    # 5
    i = i + 1
    # numMainTalkEditsForBiggestUsers(cursor, i, plotDir, dataDir, dryrun)

    # 6
    i = i + 1
    # numMainTalkEditsForBiggestBots(cursor, i, plotDir, dataDir, dryrun)

    # 7
    i = i + 1
    # numMainTalkEditsForBiggestIPs(cursor, i, plotDir, dataDir, dryrun)

    # 8
    i = i + 1
    # distributionOfMainEditsUserBots(cursor, i, plotDir, dataDir, dryrun)

    # 9
    i = i + 1
    # editsMainTalkNeitherUserBots(cursor, i, plotDir, dataDir, dryrun)

    # 10
    i = i + 1
    # editTimesUserBots(cursor, i, plotDir, dataDir, dryrun)

    # 11
    i = i + 1
    # distributionOfEditsPerNamespace(cursor, i, plotDir, dataDir, dryrun)

    # 12
    i = i + 1
    # sentimentUserBotsBlockedIP(cursor, i, plotDir, dataDir, dryrun)

    # 13
    i = i + 1
    # sentimentBots(cursor, i, plotDir, dataDir, dryrun)

    # 14
    i = i + 1
    # profanityAll(cursor, i, plotDir, dataDir, dryrun)

    # 15
    i = i + 1
    # averageAll(cursor, i, plotDir, dataDir, dryrun)

    # 16
    i = i + 1
    # namespacesEditedByTopFiveHundred(cursor, i, plotDir, dataDir, dryrun)

    # 17
    i = i + 1
    # internalExternalLinks(cursor, i, plotDir, dataDir, dryrun)

    # 18
    i = i + 1
    # specialUsersPlot(cursor, i, plotDir, dataDir, dryrun)

    # 19
    i = i + 1
    # averageAllSpecial(cursor, i, plotDir, dataDir, dryrun)

    # 20
    i = i + 1
    # compositionOfUserIP(cursor, i, plotDir, dataDir, dryrun)

    # 21
    i = i + 1
    # compositionOfUser(cursor, i, plotDir, dataDir, dryrun)

    # 22
    i = i + 1
    # aggregations(cursor, i, plotDir, dataDir, dryrun)

    # 23
    i = i + 1
    # editBooleans(cursor, i, plotDir, dataDir, dryrun)

    # 24
    i = i + 1
    # userBooleans(cursor, i, plotDir, dataDir, dryrun)

    # 25
    i = i + 1
    # talkpageEditsOverTime(cursor, i, plotDir, dataDir, dryrun)

    # 26
    i = i + 1
    # averageAllEpoch(cursor, i, plotDir, dataDir, dryrun)

    # 27
    i = i + 1
    # averageFeaturesOverTime(cursor, i, plotDir, dataDir, dryrun)

    # 28
    i = i + 1
    # averageFeaturesOverYear(cursor, i, plotDir, dataDir, dryrun)

    if not dryrun:
        cursor.close()
        database.close()


def defineArgParser():
    """Creates parser for command line arguments"""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--dryrun",
        help="Don't use a database, no partitions will be deleted",
        action="store_true",
    )

    parser.add_argument(
        "-d", "--dir", help="Output plotDirectory for figures", default="../plots/",
    )

    return parser


if __name__ == "__main__":

    argParser = defineArgParser()
    clArgs = argParser.parse_args()

    plot(
        plotDir=clArgs.dir, dryrun=clArgs.dryrun,
    )
