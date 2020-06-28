"""
This script ...
"""
import argparse
import csv
import os
import time
from datetime import datetime as dt

import matplotlib
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
from cycler import cycler

import Database


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

    _, ax = plt.subplots()
    ax.set_title("Distribution of edits in main space")
    ax.set_xlabel("Number of edits by user")
    ax.set_ylabel("Percentage")
    ax.bar(columns, data)

    singlePlot(plt, ax, "y")
    ax.set_ylim(top=50)

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
        data = [47507862, 1585249, 1092331, 169984, 34658]

    total = sum(data)
    data = list(map(lambda x: x * 100 / total, data))

    _, ax = plt.subplots()
    ax.set_title("Distribution of edits in talk space")
    ax.set_xlabel("Talk Page Edits")
    ax.set_ylabel("Percentage")
    ax.bar(columns, data)

    singlePlot(plt, ax, "y")
    ax.set_ylim(top=100)

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

    data = mapNamespace(data)

    _, ax = plt.subplots()  # Create a figure and an axes.
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

    _, ax = plt.subplots()
    ax.set_title("Namespaces that users edit")
    ax.set_ylabel("Percentage")
    ax.bar(columns, data)

    singlePlot(plt, ax, "y")
    ax.set_ylim(top=100)

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
    axs[0].barh(*zip(*mainspaceData), color="gold")
    axs[0].set_ylabel("Usernames")  # Add an x-label to the axes.
    axs[0].set_xlabel("Number of edits (linear)")  # Add a y-label to the axes.
    axs[0].set_title("Main space edits")  # Add a title to the axes.
    axs[0].xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
    axs[1].barh(*zip(*talkspaceData), color="gold")
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
    axs[0].barh(*zip(*mainspaceData), color="mediumaquamarine")
    axs[0].set_ylabel("Usernames")  # Add an x-label to the axes.
    axs[0].set_xlabel("Number of edits (linear)")  # Add a y-label to the axes.
    axs[0].set_title("Main space edits")  # Add a title to the axes.
    axs[0].xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
    axs[1].barh(*zip(*talkspaceData), color="mediumaquamarine")
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
    axs[0].barh(*zip(*mainspaceData), color="skyblue")
    axs[0].set_ylabel("Usernames")  # Add an x-label to the axes.
    axs[0].set_xlabel("Number of edits (linear)")  # Add a y-label to the axes.
    axs[0].set_title("Main space edits")  # Add a title to the axes.
    axs[0].xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
    axs[1].barh(*zip(*talkspaceData), color="skyblue")
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
    (SELECT count(*) FROM user WHERE bot is null and ip_address is null and blocked is null
    and number_of_edits = 0),
    (SELECT count(*) FROM user WHERE bot is null and ip_address is null and blocked is null
    and number_of_edits = 1),
    (SELECT count(*) FROM user WHERE bot is null and ip_address is null and blocked is null
    and number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE bot is null and ip_address is null and blocked is null
    and number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE bot is null and ip_address is null and blocked is null
    and number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(mainspaceUser,)
        mainspaceUserData = cursor.fetchall()
        mainspaceUserData = list(*mainspaceUserData)
        with open(dataDir + str(i) + "-mainspace-user.txt", "w") as file:
            file.write(str(mainspaceUserData))
    else:
        mainspaceUserData = [187156, 3040977, 4133614, 1176582, 223369]

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
        mainspaceBotData = [4, 101, 272, 211, 996]

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
        mainspaceBlockedData = [3851, 95484, 123939, 37727, 6677]

    mainspaceIp = """SELECT
    (SELECT count(*) FROM user WHERE ip_address is true
    and number_of_edits = 0),
    (SELECT count(*) FROM user WHERE ip_address is true
    and number_of_edits = 1),
    (SELECT count(*) FROM user WHERE ip_address is true
    and number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE ip_address is true
    and number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE ip_address is true
    and number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(mainspaceIp,)
        mainspaceIpData = cursor.fetchall()
        mainspaceIpData = list(*mainspaceIpData)
        with open(dataDir + str(i) + "-mainspace-ip.txt", "w") as file:
            file.write(str(mainspaceIpData))
    else:
        mainspaceIpData = [872725, 20386443, 18001533, 2058493, 133467]

    talkspaceUser = """SELECT
    (SELECT count(*) FROM user WHERE bot is null and ip_address is null and blocked is null
    and talkpage_number_of_edits = 0),
    (SELECT count(*) FROM user WHERE bot is null and ip_address is null and blocked is null
    and  talkpage_number_of_edits = 1),
    (SELECT count(*) FROM user WHERE bot is null and ip_address is null and blocked is null
    and  talkpage_number_of_edits > 1 and talkpage_number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE bot is null and ip_address is null and blocked is null
    and  talkpage_number_of_edits > 10 and talkpage_number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE bot is null and ip_address is null and blocked is null
    and  talkpage_number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(talkspaceUser,)
        talkspaceUserData = cursor.fetchall()
        talkspaceUserData = list(*talkspaceUserData)
        with open(dataDir + str(i) + "-talkspace-user.txt", "w") as file:
            file.write(str(talkspaceUserData))
    else:
        talkspaceUserData = [7887493, 340977, 385875, 115498, 31855]

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
        talkspaceBotData = [1031, 63, 119, 103, 268]

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
        talkspaceBlockedData = [245284, 8522, 9849, 3235, 788]

    talkspaceIp = """SELECT
    (SELECT count(*) FROM user WHERE ip_address is true
    and talkpage_number_of_edits = 0),
    (SELECT count(*) FROM user WHERE ip_address is true
    and talkpage_number_of_edits = 1),
    (SELECT count(*) FROM user WHERE ip_address is true
    and talkpage_number_of_edits > 1 and talkpage_number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE ip_address is true
    and talkpage_number_of_edits > 10 and talkpage_number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE ip_address is true
    and talkpage_number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(talkspaceIp,)
        talkspaceIpData = cursor.fetchall()
        talkspaceIpData = list(*talkspaceIpData)
        with open(dataDir + str(i) + "-talkspace-ip.txt", "w") as file:
            file.write(str(talkspaceIpData))
    else:
        talkspaceIpData = [39464189, 1237805, 697702, 51210, 1755]

    _, axs = plt.subplots(4, 2)
    axs = axs.ravel()
    types = ["User", "User", "Bot", "Bot", "Blocked", "Blocked", "IP", "IP"]
    namespaces = ["main", "talk"]
    data = [
        mainspaceUserData,
        talkspaceUserData,
        mainspaceBotData,
        talkspaceBotData,
        mainspaceBlockedData,
        talkspaceBlockedData,
        mainspaceIpData,
        talkspaceIpData,
    ]

    # fig.suptitle("Distribution of edits across name spaces for bots and users")
    colors = [
        "mediumpurple",
        "mediumpurple",
        "mediumaquamarine",
        "mediumaquamarine",
        "orangered",
        "orangered",
        "skyblue",
        "skyblue",
    ]
    for i in range(8):
        axs[i].set_title(types[i] + " edits in " + namespaces[i % 2] + " space")
        axs[i].bar(columns, data[i], color=colors[i])
        axs[i].yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        removeSpines(axs[i])

    plt.gcf().set_size_inches(12, 18)

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
        userData = [1823459, 47502424, 1058210, 4407]

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
        botData = [549, 1031, 4, 0]

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
        blockedData = [18557, 245270, 3837, 14]

    ip = """SELECT
    (select count(*) as target from user
    WHERE talkpage_number_of_edits > 0 and number_of_edits > 0 and ip_address is true),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits = 0 and number_of_edits > 0 and ip_address is true),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits > 0 and number_of_edits = 0 and ip_address is true),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits = 0 and number_of_edits = 0 and ip_address is true);"""
    if not dryrun:
        cursor.execute(ip,)
        ipData = cursor.fetchall()
        ipData = list(*ipData)
        with open(dataDir + str(i) + "-ip.txt", "w") as file:
            file.write(str(ipData))
    else:
        ipData = [1116049, 39463887, 872423, 302]

    _, axs = plt.subplots(2, 2)
    axs = axs.ravel()
    types = ["users", "bots", "blocked users", "IP users"]
    colors = ["mediumpurple", "mediumaquamarine", "orangered", "skyblue"]
    data = [userData, botData, blockedData, ipData]

    for i in range(4):
        axs[i].set_title("Namespaces that " + types[i] + " edit")
        axs[i].bar(columns, data[i], color=colors[i])
        axs[i].yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        removeSpines(axs[i])

    # fig.tight_layout()
    plt.gcf().set_size_inches(14, 14)
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def editTimesUserBots(cursor, i, plotDir, dataDir, dryrun=False):
    groups = ["Special User", "User", "Blocked User", "IP", "IP Blocked", "Bot"]

    conditions = [
        "user_special is True",
        "bot is not True and blocked is not true and ip_address is not true and user_special is not True",
        "blocked is True and ip_address is not true",
        "ip_address is True and blocked is not true",
        "ip_address is True and blocked is true",
        "bot is True",
    ]

    data = []
    dataStd = []

    for j, group in enumerate(groups):
        if not dryrun:
            times = """select avg(min_time)/3600, avg(avg_time)/3600, avg(max_time)/3600,
            avg(duration)/3600, std(min_time)/3600, std(avg_time)/3600, std(max_time)/3600,
            std(duration)/3600
            from user_time_stats join user
            on user_time_stats.id = user.id
            where %s;"""
            cursor.execute(times % conditions[j],)
            timeData = cursor.fetchall()
            timeStd = list(*timeData)[4:]
            timeData = list(*timeData)[:4]

            data.append(timeData)
            dataStd.append(timeStd)
            writeCSV(dataDir + str(i) + "-" + group + ".csv", [timeData, timeStd])
        else:
            with open(dataDir + str(i) + "-" + group + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                temp = [list(map(float, line)) for line in reader]

            # print(groupData)
            data.append(temp[0])
            dataStd.append(temp[1])

    columns = [
        "Minimum time\nbetween edits",
        "Average time\nbetween edits",
        "Maximum time\nbetween edits",
        "Time between\nfirst and last edit",
    ]

    figname = plotDir + str(i) + "-1-" + "editTimesUserBots"
    plt.figure()
    fig, axs = plt.subplots(1, 2)

    # Position of bars on x-axis
    ind = list(range(len(columns)))

    # Width of a bar
    width = 0.14

    colors = [
        "gold",
        "mediumpurple",
        "orangered",
        "skyblue",
        "#F08EC1",
        "mediumaquamarine",
    ]

    # Plotting
    for j, group in enumerate(groups):
        axs[0].bar(
            list(map(lambda x: x + width * j, ind[:2])),
            data[j][:2],
            width,
            label=group,
            # yerr=dataStd[i][:2],
            color=colors[j],
        )
        axs[0].set_xticklabels(columns[:2])
        axs[0].set_xticks(list(map(lambda x: x + (width * 5) / 2, ind[:2])))
        axs[1].bar(
            list(map(lambda x: x + width * j, ind[2:])),
            data[j][2:],
            width,
            label=group,
            # yerr=dataStd[i][2:],
            color=colors[j],
        )
        axs[1].set_xticklabels(columns[2:])
        axs[1].set_xticks(list(map(lambda x: x + (width * 5) / 2, ind[2:])))

    fig.suptitle("Average time between talk page edits")
    for ax in axs:
        ax.set_ylim(bottom=0)
        ax.set_ylabel("Hours")
        ax.grid(color="#ccc", which="major", axis="y", linestyle="solid")
        ax.set_axisbelow(True)
        removeSpines(ax)
        ax.yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        ax.legend()

    plt.gcf().set_size_inches(15, 7)
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()

    figname = plotDir + str(i) + "-2-" + "editTimesUserBots"
    plt.figure()
    fig, axs = plt.subplots(2, 1)

    fig.suptitle("Average time between talk page edits", y=1.05)
    plotRange = range(0, 2)

    for k, ax in enumerate(axs):
        removeSpines(ax)
        ax.xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        ax.set_yticks(plotRange)
        ax.set_ylim(bottom=-0.5, top=1.5)
        ax.set_xlabel("Hours")

    for j, group in enumerate(groups):
        axs[0].scatter(data[j][:2], plotRange, color=colors[j], label=group)
        axs[1].scatter(data[j][2:], plotRange, color=colors[j], label=group)

    axs[0].hlines(
        y=plotRange,
        xmin=[min(x) for x in list(zip(*data))][:2],
        xmax=[max(x) for x in list(zip(*data))][:2],
        color="grey",
        alpha=0.4,
    )
    axs[0].set_yticklabels(columns[:2])
    axs[0].invert_yaxis()
    axs[1].hlines(
        y=plotRange,
        xmin=[min(x) for x in list(zip(*data))][2:],
        xmax=[max(x) for x in list(zip(*data))][2:],
        color="grey",
        alpha=0.4,
    )
    axs[1].set_yticklabels(columns[2:])
    axs[1].invert_yaxis()

    axs[0].legend(
        loc="lower center", bbox_to_anchor=(0.5, 1), ncol=3, fancybox=True, shadow=True,
    )

    plt.gcf().set_size_inches(9.5, 5.5)

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


def sentimentUserBotsBlockedIP(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i) + "-" + "sentimentUserBotsBlockedIP"
    plt.figure()

    columns = [
        "added sentiment",
        "deleted sentiment",
    ]

    users = """select avg(edit.added_sentiment),avg(edit.deleted_sentiment)
    from edit join user
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

    _, ax = plt.subplots()

    # Position of bars on x-axis
    ind = list(range(len(columns)))

    # Width of a bar
    width = 0.2

    # Plotting
    ax.bar(ind, userData, width, label="Non blocked users", color="mediumpurple")
    ax.bar(
        list(map(lambda x: x + width, ind)),
        blockedData,
        width,
        label="Blocked users",
        color="orangered",
    )
    ax.bar(
        list(map(lambda x: x + width * 2, ind)),
        botsData,
        width,
        label="Bots",
        color="mediumaquamarine",
    )
    ax.bar(
        list(map(lambda x: x + width * 3, ind)),
        ipAddressData,
        width,
        label="IP address",
        color="skyblue",
    )

    ax.set_ylabel("unit ?")
    ax.set_title("Average sentiment of different subsets of users")

    # xticks()
    # First argument - A list of positions at which ticks should be placed
    # Second argument -  A list of labels to place at the given locations
    plt.xticks(list(map(lambda x: x + (width * 3) / 2, ind)), columns)

    ax.set_ylim(bottom=0)
    removeSpines(ax)
    showGrid(plt, ax, "y")
    plt.gcf().set_size_inches(12, 7)

    plt.legend(loc="best")
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def sentimentGroups(cursor, i, plotDir, dataDir, dryrun=False):
    groups = ["User", "Blocked User", "IP", "IP Blocked", "Bot", "Special User"]

    conditions = [
        "bot is not True and blocked is not true and ip_address is not true and user_special is not True",
        "blocked is True and ip_address is not true",
        "ip_address is True and blocked is not true",
        "ip_address is True and blocked is true",
        "bot is True",
        "user_special is True",
    ]
    sentimentConditions = [
        "edit.added_sentiment > 0 and edit.deleted_length > 2",
        "edit.added_sentiment < 0 and edit.deleted_length > 2",
        "edit.deleted_sentiment > 0 and edit.added_length > 2",
        "edit.deleted_sentiment < 0 and edit.added_length > 2",
        "edit.added_sentiment != 0 and edit.deleted_sentiment != 0",
        "1",
    ]

    data = []

    for j, group in enumerate(groups):
        groupData = []

        if not dryrun:
            for sentimentCondition in sentimentConditions:
                sentiment = """select avg(edit.added_sentiment),avg(edit.deleted_sentiment)
                from edit join user
                on edit.user_table_id = user.id
                where %s and %s;"""
                cursor.execute(sentiment % (conditions[j], sentimentCondition),)
                sentimentData = cursor.fetchall()
                groupData.append(list(*sentimentData))

            data.append(groupData)
            writeCSV(dataDir + str(i) + "-" + group + ".csv", groupData)
        else:
            with open(dataDir + str(i) + "-" + group + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                for line in reader:
                    groupData.append([float(i) for i in line])

            # print(groupData)
            data.append(groupData)

    figname = plotDir + str(i) + "-1-" + "sentimentGroups"
    plt.figure()
    _, axs = plt.subplots(3, 2, sharey=True)
    axs = axs.ravel()

    columns = [
        "Added sentiment",
        "Deleted sentiment",
    ]

    labels = [
        "Added positive",
        "Added negative",
        "Deleted positive",
        "Deleted negative",
        "Both have sentiment",
        "All",
    ]

    ind = list(range(len(columns)))

    width = 0.15

    for j, group in enumerate(groups):
        axs[j].set_title(
            "Average sentiment for different\ntypes of " + group + " edits"
        )
        axs[j].set_ylabel("unit ?")
        axs[j].set_xticks(list(map(lambda x: x + (width * 5) / 2, ind)))
        axs[j].set_xticklabels(columns)
        removeSpines(axs[j])
        axs[j].grid(color="#ccc", which="major", axis="y", linestyle="solid")
        axs[j].set_axisbelow(True)

        for k, label in enumerate(labels):
            axs[j].bar(
                list(map(lambda x: x + width * k, ind)), data[j][k], width, label=label,
            )

    plt.gcf().set_size_inches(14, 17)
    # Finding the best position for legends and putting it
    plt.legend(loc="best")
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()

    colors = [
        "gold",
        "mediumpurple",
        "orangered",
        "mediumaquamarine",
        "skyblue",
        "#F08EC1",
    ]

    figname = plotDir + str(i) + "-2-" + "sentimentGroups"
    plt.figure()
    fig, axs = plt.subplots(1, 2, sharey=True)
    fig.suptitle("Average sentiment for different types of edits by groups", y=1.05)
    plotRange = range(0, 6)
    for k, ax in enumerate(axs):
        ax.hlines(
            y=plotRange,
            xmin=[min(list(zip(*x))[k]) for x in list(zip(*data))],
            xmax=[max(list(zip(*x))[k]) for x in list(zip(*data))],
            color="grey",
            alpha=0.4,
        )
        # ax.vlines(
        #     x=allData[:2],
        #     ymin=list(map(lambda x: x - 0.5, plotRange)),
        #     ymax=list(map(lambda x: x + 0.5, plotRange)),
        # color="grey",
        # alpha=0.4,
        # )
        for j, group in enumerate(groups):
            dataSlice = [x[k] for x in data[j]]
            ax.scatter(dataSlice, plotRange, color=colors[j], label=group)

        removeSpines(ax)
        ax.axvline(0, color="#ccc", linewidth=0.5, zorder=-1)
        ax.set_axisbelow(True)

    axs[0].set_xlabel("Added sentiment")
    axs[1].set_xlabel("Deleted sentiment")

    axs[0].set_yticklabels(labels)
    axs[0].set_yticks(plotRange)

    axs[0].legend(
        loc="lower center", bbox_to_anchor=(1, 1), ncol=3, fancybox=True, shadow=True,
    )

    plt.gcf().set_size_inches(9.5, 5.5)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


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

    colors = [
        "gold",
        "mediumpurple",
        "orangered",
        "mediumaquamarine",
        "skyblue",
        "#F08EC1",
    ]

    _, ax = plt.subplots()
    ax.set_title("Average profanity per type of user")
    ax.set_ylabel("Average profanity / %")
    ax.bar(*zip(*data), yerr=std, color=colors)
    ax.set_ylim(bottom=0)
    # plt.bar(*zip(*data))

    plt.grid(color="#ccc", which="major", axis="y", linestyle="solid")
    ax.set_axisbelow(True)
    removeSpines(ax)
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def averageAll(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "averageAll"
    plt.figure()

    query = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment), STD(added_length),STD(deleted_length),STD(del_words),STD(comment_length),
    STD(ins_longest_inserted_word),STD(ins_longest_character_sequence),STD(ins_internal_link),
    STD(ins_external_link),STD(blanking),STD(comment_copyedit),STD(comment_personal_life),
    STD(comment_special_chars),STD(ins_capitalization),STD(ins_digits),STD(ins_pronouns),
    STD(ins_special_chars),STD(ins_vulgarity),STD(ins_whitespace),STD(reverted),STD(added_sentiment),
    STD(deleted_sentiment)  from edit;"""
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
    axs[0].bar(columns[:3], data[:3], yerr=dataStd[:3])
    axs[0].tick_params(labelrotation=90)
    axs[0].set_ylim(bottom=0)
    axs[1].bar(columns[3:8], data[3:8], yerr=dataStd[3:8])
    axs[1].tick_params(labelrotation=90)
    axs[1].set_ylim(bottom=0)
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

    data = mapNamespace(data)

    _, ax = plt.subplots()
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

    _, axs = plt.subplots(2, 1)
    colors = ["gold", "mediumpurple", "orangered", "mediumaquamarine", "skyblue"]
    axs[0].bar(*zip(*internalData), color=colors)
    axs[0].set_title("Average added internal links per type of user")
    axs[1].bar(*zip(*externalData), color=colors)
    axs[1].set_title("Average added external links per type of user")
    plt.gcf().set_size_inches(5, 10)
    removeSpines(axs[0])
    removeSpines(axs[1])
    axs[0].grid(color="#ccc", which="major", axis="y", linestyle="solid")
    axs[0].set_axisbelow(True)
    axs[1].grid(color="#ccc", which="major", axis="y", linestyle="solid")
    axs[1].set_axisbelow(True)
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
    colors = (
        ["gold"] * 4
        + ["mediumaquamarine"]
        + ["gold"] * 2
        + ["mediumpurple"]
        + ["gold"] * 3
        + ["mediumpurple"]
        + ["gold"] * 15
    )
    _, ax = plt.subplots()  # Create a figure and an axes.
    ax.barh(*zip(*data), color=colors)
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

    query = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment)  FROM edit
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
            482.2263,
            384.6865,
            52.4005,
            37.8249,
            10.3969,
            1.8504,
            1.7145,
            0.1331,
            0.0024,
            0.0007,
            0.0003,
            0.11470288,
            0.10220409,
            0.02810473,
            0.00839849,
            0.11358946,
            0.0167,
            0.17759977,
            0.0243,
            0.048819411249298277,
            0.005998387005003988,
        ]

    special = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),
    AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),AVG(deleted_sentiment)  FROM edit
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
            440.9023,
            462.0706,
            60.3628,
            47.2563,
            10.3737,
            1.7691,
            1.7508,
            0.1538,
            0.0016,
            0.0006,
            0.0001,
            0.11234557,
            0.10580707,
            0.02121139,
            0.00586263,
            0.13506474,
            0.0100,
            0.15924664,
            0.0100,
            0.02477164276923664,
            0.0053575857156795016,
        ]

    ip = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment)  FROM edit
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

    ipBlocked = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment)  FROM edit
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

    blocked = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment)  FROM edit
    inner join user
    on user.id = edit.user_table_id
    where user.blocked is True and ip_address is not true;"""
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

    bot = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment)  FROM edit
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

    start = 0
    end = 2
    plotRange = range(start, end)

    fig.suptitle("Average of all integer edit fields")
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
    axs[0].scatter(data[:2], plotRange, color="mediumpurple", label="all users")
    axs[0].scatter(
        specialData[:2], plotRange, color="gold", label="users with privileges"
    )
    axs[0].scatter(botData[:2], plotRange, color="mediumaquamarine", label="bots")
    axs[0].scatter(ipData[:2], plotRange, color="skyblue", label="IP users")
    axs[0].scatter(
        ipBlockedData[:2], plotRange, color="#F08EC1", label="blocked IP users"
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
    axs[1].scatter(data[start:end], plotRange, color="mediumpurple")
    axs[1].scatter(specialData[start:end], plotRange, color="gold")
    axs[1].scatter(botData[start:end], plotRange, color="mediumaquamarine")
    axs[1].scatter(ipData[start:end], plotRange, color="skyblue")
    axs[1].scatter(ipBlockedData[start:end], plotRange, color="#F08EC1")
    axs[1].scatter(blockedData[start:end], plotRange, color="orangered")
    axs[1].set_yticklabels(columns[start:end])
    axs[1].set_yticks(plotRange)

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
    axs[2].scatter(data[start:end], plotRange, color="mediumpurple")
    axs[2].scatter(
        specialData[start:end], plotRange, color="gold", label="users with privileges"
    )
    axs[2].scatter(
        botData[start:end], plotRange, color="mediumaquamarine", label="bots"
    )
    axs[2].scatter(ipData[start:end], plotRange, color="skyblue")
    axs[2].scatter(ipBlockedData[start:end], plotRange, color="#F08EC1")
    axs[2].scatter(blockedData[start:end], plotRange, color="orangered")
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
    axs[3].scatter(data[start:], plotRange, color="mediumpurple")
    axs[3].scatter(specialData[start:], plotRange, color="gold")
    axs[3].scatter(botData[start:], plotRange, color="mediumaquamarine")
    axs[3].scatter(ipData[start:], plotRange, color="skyblue")
    axs[3].scatter(ipBlockedData[start:], plotRange, color="#F08EC1")
    axs[3].scatter(blockedData[start:], plotRange, color="orangered")
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
    colors = [["mediumpurple", "skyblue"], ["orangered", "#F08EC1"]]

    _, axs = plt.subplots(2, 1)
    axs[0].set_title("Comparison of blocked and unblocked\nusers and IPs")
    axs[0].set_ylabel("Number of Users")
    yPosOne = yPosTwo = 0
    for key, value in enumerate(data):
        absBottom = [yPosOne, yPosTwo]
        axs[0].bar(
            xticks, value, bottom=absBottom, label=labels[key], color=colors[key]
        )
        yPosOne += value[0]
        yPosTwo += value[1]

    axs[0].yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
    removeSpines(axs[0])

    data = proportinateData
    data = [data[i : i + 2] for i in range(0, len(data), 2)]
    axs[1].set_title("Proportional")
    axs[1].set_ylabel("Percent")
    yPosOne = yPosTwo = 0
    for key, value in enumerate(data):
        absBottom = [yPosOne, yPosTwo]
        axs[1].bar(
            xticks, value, bottom=absBottom, label=labels[key], color=colors[key]
        )
        yPosOne += value[0]
        yPosTwo += value[1]

    removeSpines(axs[1])
    plt.gcf().set_size_inches(5, 10)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def compositionOfUser(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "compositionOfUser"
    plt.figure()

    query = """SELECT
    (SELECT count(*) FROM user WHERE
    bot is not true and ip_address is not true and blocked is not true and user_special is not true),
    (SELECT count(*) FROM user WHERE
    bot is not true and ip_address is not true and blocked is true and user_special is not true),
    (SELECT count(*) FROM user WHERE
    bot is true and ip_address is not true and blocked is not true and user_special is not true),
    (SELECT count(*) FROM user WHERE
    bot is true and ip_address is not true and blocked is true and user_special is not true),
    (SELECT count(*) FROM user WHERE
    bot is not true and ip_address is true and blocked is not true and user_special is not true),
    (SELECT count(*) FROM user WHERE
    bot is not true and ip_address is true and blocked is true and user_special is not true),
    (SELECT count(*) FROM user WHERE
    bot is not true and ip_address is not true and blocked is not true and user_special is true),
    (SELECT count(*) FROM user WHERE
    bot is not true and ip_address is not true and blocked is true and user_special is true);"""
    columns = [
        "Users",
        "Blocked",
        "Bot",
        "Bot Blocked",
        "IP",
        "IP Blocked",
        "Special",
        "Special Blocked",
    ]
    colors = [
        "mediumpurple",
        "orangered",
        "mediumaquamarine",
        "C1",
        "skyblue",
        "#F08EC1",
        "gold",
        "C0",
    ]
    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        data = list(*data)
        with open(dataDir + str(i) + ".txt", "w") as file:
            file.write(str(data))
    else:
        data = [8747953, 173785, 1528, 15, 41358810, 93851, 14074, 27]

    total = sum(data)
    data = list(map(lambda x: x / total, data))

    edits = """SELECT
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id WHERE
    bot is not true and ip_address is not true and blocked is not true and user_special is not true),
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id WHERE
    bot is not true and ip_address is not true and blocked is true and user_special is not true),
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id WHERE
    bot is true and ip_address is not true and blocked is not true and user_special is not true),
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id WHERE
    bot is true and ip_address is not true and blocked is true and user_special is not true),
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id WHERE
    bot is not true and ip_address is true and blocked is not true and user_special is not true),
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id WHERE
    bot is not true and ip_address is true and blocked is true and user_special is not true),
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id WHERE
    bot is not true and ip_address is not true and blocked is not true and user_special is true),
    (SELECT count(*) FROM edit inner join user on user.id = edit.user_table_id WHERE
    bot is not true and ip_address is not true and blocked is true and user_special is true);"""
    if not dryrun:
        cursor.execute(edits,)
        editsData = cursor.fetchall()
        editsData = list(*editsData)
        with open(dataDir + str(i) + "-edits.txt", "w") as file:
            file.write(str(editsData))
    else:
        editsData = [17572071, 847162, 8804388, 195019, 5070606, 7926, 23548274, 23897]

    total = sum(editsData)
    editsData = list(map(lambda x: x / total, editsData))

    data = list(zip(data, editsData))
    labels = ["distribution\nof users", "distribution\nof edits"]
    _, ax = plt.subplots()
    ax.set_title("Distribution of users\nand how many edits on talkpages they make")
    yPosOne = yPosTwo = 0
    for key, value in enumerate(data):
        absBottom = [yPosOne, yPosTwo]
        ax.bar(labels, value, bottom=absBottom, label=columns[key], color=colors[key])
        yPosOne += value[0]
        yPosTwo += value[1]
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(reversed(handles), reversed(labels), loc="center left")

    ax.set_ylim([0, 1])
    plt.gcf().set_size_inches(5, 10)
    removeSpines(ax)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


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

    mins = """select MIN(added_length),MIN(deleted_length),MIN(del_words),MIN(comment_length),
    MIN(ins_longest_inserted_word),MIN(ins_longest_character_sequence),MIN(ins_internal_link),
    MIN(ins_external_link),MIN(blanking),MIN(comment_copyedit),MIN(comment_personal_life),
    MIN(comment_special_chars),MIN(ins_capitalization),MIN(ins_digits),MIN(ins_pronouns),
    MIN(ins_special_chars),MIN(ins_vulgarity),MIN(ins_whitespace),MIN(reverted),MIN(added_sentiment),
    MIN(deleted_sentiment) FROM edit;"""
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

    maxs = """select MAX(added_length),MAX(deleted_length),MAX(del_words),MAX(comment_length),
    MAX(ins_longest_inserted_word),MAX(ins_longest_character_sequence),MAX(ins_internal_link),
    MAX(ins_external_link),MAX(blanking),MAX(comment_copyedit),MAX(comment_personal_life),
    MAX(comment_special_chars),MAX(ins_capitalization),MAX(ins_digits),MAX(ins_pronouns),
    MAX(ins_special_chars),MAX(ins_vulgarity),MAX(ins_whitespace),MAX(reverted),MAX(added_sentiment),
    sMAX(deleted_sentiment)  FROM edit;"""
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

    means = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment) from edit;"""
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

    stds = """select STD(added_length),STD(deleted_length),STD(del_words),STD(comment_length),
    STD(ins_longest_inserted_word),STD(ins_longest_character_sequence),STD(ins_internal_link),
    STD(ins_external_link),STD(blanking),STD(comment_copyedit),STD(comment_personal_life),
    STD(comment_special_chars),STD(ins_capitalization),STD(ins_digits),STD(ins_pronouns),
    STD(ins_special_chars),STD(ins_vulgarity),STD(ins_whitespace),STD(reverted),STD(added_sentiment),
    STD(deleted_sentiment) from edit;"""
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
    axs[1].scatter(stdsData[start:end], plotRange, color="skyblue")
    axs[1].scatter(meansData[start:end], plotRange, color="black")
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
    axs[2].scatter(stdsData[start:end], plotRange, color="skyblue")
    invertedStds = list(
        map(
            lambda x: max(2 * x[0] - x[1], 0),
            zip(meansData[start:end], stdsData[start:end]),
        )
    )
    axs[2].scatter(invertedStds, plotRange, color="skyblue")
    axs[2].scatter(meansData[start:end], plotRange, color="black")
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
    axs[3].scatter(meansData[start:end], plotRange, color="black")
    axs[3].scatter(stdsData[start:end], plotRange, color="skyblue")
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

    query = """select count(*), sum(comment_copyedit = 1), sum(comment_personal_life = 1),
    sum(ins_vulgarity = 1), sum(reverted = 1), sum(blanking = 1) from edit;"""

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
    axs = axs.ravel()

    fig.suptitle("Ratios of boolean features")

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

    query = """select count(*), sum(confirmed = 1), sum(autoconfirmed = 1), sum(user_special = 1),
    sum(bot = 1), sum(blocked = 1) from user;"""

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

    query = "select cast(edit_date as date) as date, count(*) from edit group by date order by date;;"

    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()

        writeCSV(dataDir + str(i) + ".csv", data)
    else:
        with open(dataDir + str(i) + ".csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            data = [line for line in reader]

            data = list(map(lambda x: (dt.strptime(x[0], "%Y-%m-%d"), int(x[1])), data))

    dates = list(map(lambda x: matplotlib.dates.date2num(x[0]), data))
    values = [x[1] for x in data]
    _, ax = plt.subplots()

    ax.set_title("Talkpage edits over time")

    ax.plot_date(dates, values, "C0-")

    plt.gcf().set_size_inches(12, 7.5)
    singlePlot(plt, ax, "y")

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


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

    after = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment)  FROM edit
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
    axs[1].scatter(beforeData[start:end], plotRange, color="skyblue")
    axs[1].scatter(afterData[start:end], plotRange, color="orangered")
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
    axs[2].scatter(beforeData[start:end], plotRange, color="skyblue")
    axs[2].scatter(afterData[start:end], plotRange, color="orangered")
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
    axs[3].scatter(beforeData[start:], plotRange, color="skyblue")
    axs[3].scatter(afterData[start:], plotRange, color="orangered")
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

    query = """select YEAR(edit_date), MONTH(edit_date), AVG(added_length),AVG(deleted_length),
    AVG(del_words),AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),
    AVG(ins_internal_link),AVG(ins_external_link),AVG(comment_special_chars),AVG(blanking),
    AVG(comment_copyedit),AVG(comment_personal_life),AVG(ins_capitalization),AVG(ins_digits),
    AVG(ins_pronouns),AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),
    AVG(added_sentiment),AVG(deleted_sentiment)  FROM edit
    GROUP BY YEAR(edit_date), MONTH(edit_date)
    order by YEAR(edit_date), MONTH(edit_date) ;"""

    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()

        writeCSV(dataDir + str(i) + ".csv", data)
    else:
        with open(dataDir + str(i) + ".csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            data = [line for line in reader]

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

    _, axs = plt.subplots(4, 1, gridspec_kw={"height_ratios": [1, 1, 1, 2]})

    axs[0].set_title("Talkpage edits over time")

    colors = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]
    start = [0, 3, 5, 9]
    end = [3, 5, 9, 21]
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

    query = """select YEAR(edit_date), AVG(added_length),AVG(deleted_length),
    AVG(del_words),AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),
    AVG(ins_internal_link),AVG(ins_external_link),AVG(comment_special_chars),AVG(blanking),
    AVG(comment_copyedit),AVG(comment_personal_life),AVG(ins_capitalization),AVG(ins_digits),
    AVG(ins_pronouns),AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),
    AVG(added_sentiment),AVG(deleted_sentiment) FROM edit
    GROUP BY YEAR(edit_date)
    order by YEAR(edit_date) ;"""

    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()

        writeCSV(dataDir + str(i) + ".csv", data)
    else:
        with open(dataDir + str(i) + ".csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            data = [line for line in reader]

            data = list(map(lambda x: tuple(map(float, x)), data))

    dates = list(map(lambda x: matplotlib.dates.datestr2num(str(int(x[0]))), data,))

    values = list(map(lambda x: x[1:], data))

    _, axs = plt.subplots(4, 1, gridspec_kw={"height_ratios": [1, 1, 1, 2]})

    axs[0].set_title("Talkpage edits by averaged by year")

    colors = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]
    start = [0, 3, 5, 9]
    end = [3, 5, 9, 21]
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


def namespacesEditedByUserGroups(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "namespacesEditedByUserGroups"
    plt.figure()
    columns = [
        "Main",
        "Talk",
        "User",
        "User Talk",
        "Wikipedia",
        "Wikipedia Talk",
        "File",
        "FIle Talk",
        "MediaWiki",
        "MediaWiki Talk",
        "Template",
        "Template Talk",
        "Help",
        "Help Talk",
        "Category",
        "Category Talk",
        "Special",
        "Media",
        "Portal",
        "Portal Talk",
        "Draft",
        "Draft Talk",
        "TimedText",
        "TimedText Talk",
        "Module",
        "Module Talk",
        "Book",
        "Book Talk",
        "Education Program",
        "Education Program Talk",
        "Gadget",
        "Gadget Talk",
        "Gadget Definition",
        "Gadget Definition Talk",
    ]

    # https://stackoverflow.com/questions/28620904/how-to-count-unique-set-values-in-mysql
    count = "SELECT COUNT(*) FROM user"
    allUsers = """SELECT COUNT(user.namespaces) FROM
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
    LEFT OUTER JOIN (SELECT namespaces FROM user) user
    ON FIND_IN_SET(set_list.namespaces, user.namespaces) > 0
    GROUP BY set_list.namespaces
    ;"""
    if not dryrun:
        cursor.execute(allUsers,)
        allUsersData = cursor.fetchall()

        cursor.execute(count,)
        total = cursor.fetchall()[0][0]
        allUsersData = list(map(lambda x: x[0] / total, allUsersData))

        writeCSV(dataDir + str(i) + "-all.csv", [allUsersData])
    else:
        with open(dataDir + str(i) + "-all.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            allUsersData = [line for line in reader]
            allUsersData = allUsersData[0]
            allUsersData = list(map(float, allUsersData))

    count = "SELECT COUNT(*) FROM user where bot is null and blocked is null and ip_address is null"
    users = """SELECT COUNT(user.namespaces) FROM
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
        where bot is null and blocked is null and ip_address is null) user
    ON FIND_IN_SET(set_list.namespaces, user.namespaces) > 0
    GROUP BY set_list.namespaces
    ;"""
    if not dryrun:
        cursor.execute(users,)
        usersData = cursor.fetchall()
        cursor.execute(count,)
        total = cursor.fetchall()[0][0]
        usersData = list(map(lambda x: x[0] / total, usersData))

        writeCSV(dataDir + str(i) + "-user.csv", [usersData])
    else:
        with open(dataDir + str(i) + "-user.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            usersData = [line for line in reader]
            usersData = usersData[0]
            usersData = list(map(float, usersData))

    count = "SELECT COUNT(*) FROM user where user_special is true"
    specialUsers = """SELECT COUNT(user.namespaces) FROM
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
        where user_special is true) user
    ON FIND_IN_SET(set_list.namespaces, user.namespaces) > 0
    GROUP BY set_list.namespaces
    ;"""
    if not dryrun:
        cursor.execute(specialUsers,)
        specialUsersData = cursor.fetchall()
        cursor.execute(count,)
        total = cursor.fetchall()[0][0]
        specialUsersData = list(map(lambda x: x[0] / total, specialUsersData))

        writeCSV(dataDir + str(i) + "-special.csv", [specialUsersData])
    else:
        with open(dataDir + str(i) + "-special.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            specialUsersData = [line for line in reader]
            specialUsersData = specialUsersData[0]
            specialUsersData = list(map(float, specialUsersData))

    count = "SELECT COUNT(*) FROM user where bot is true"
    bots = """SELECT COUNT(user.namespaces) FROM
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
        where bot is true and (number_of_edits > 0 or
    talkpage_number_of_edits > 0)) user
    ON FIND_IN_SET(set_list.namespaces, user.namespaces) > 0
    GROUP BY set_list.namespaces
    ;"""
    if not dryrun:
        cursor.execute(bots,)
        botsData = cursor.fetchall()
        cursor.execute(count,)
        total = cursor.fetchall()[0][0]
        botsData = list(map(lambda x: x[0] / total, botsData))

        writeCSV(dataDir + str(i) + "-bots.csv", [botsData])
    else:
        with open(dataDir + str(i) + "-bots.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            botsData = [line for line in reader]
            botsData = botsData[0]
            botsData = list(map(float, botsData))

    count = "SELECT COUNT(*) FROM user where blocked is true and ip_address is null"
    blocked = """SELECT COUNT(user.namespaces) FROM
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
        where blocked is true and ip_address is null) user
    ON FIND_IN_SET(set_list.namespaces, user.namespaces) > 0
    GROUP BY set_list.namespaces
    ;"""
    if not dryrun:
        cursor.execute(blocked,)
        blockedData = cursor.fetchall()
        cursor.execute(count,)
        total = cursor.fetchall()[0][0]
        blockedData = list(map(lambda x: x[0] / total, blockedData))

        writeCSV(dataDir + str(i) + "-blocked.csv", [blockedData])
    else:
        with open(dataDir + str(i) + "-blocked.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            blockedData = [line for line in reader]
            blockedData = blockedData[0]
            blockedData = list(map(float, blockedData))

    count = "SELECT COUNT(*) FROM user where ip_address is true"
    ip = """SELECT COUNT(user.namespaces) FROM
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
        where ip_address is true) user
    ON FIND_IN_SET(set_list.namespaces, user.namespaces) > 0
    GROUP BY set_list.namespaces
    ;"""
    if not dryrun:
        cursor.execute(ip,)
        ipData = cursor.fetchall()
        cursor.execute(count,)
        total = cursor.fetchall()[0][0]
        ipData = list(map(lambda x: x[0] / total, ipData))
        writeCSV(dataDir + str(i) + "-ip.csv", [ipData])
    else:
        with open(dataDir + str(i) + "-ip.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            ipData = [line for line in reader]
            ipData = ipData[0]
            ipData = list(map(float, ipData))

    count = "SELECT COUNT(*) FROM user where blocked is true and ip_address is true"
    ipBlocked = """SELECT COUNT(user.namespaces) FROM
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
        where blocked is true and ip_address is true) user
    ON FIND_IN_SET(set_list.namespaces, user.namespaces) > 0
    GROUP BY set_list.namespaces
    ;"""
    if not dryrun:
        cursor.execute(ipBlocked,)
        ipBlockedData = cursor.fetchall()
        cursor.execute(count,)
        total = cursor.fetchall()[0][0]
        ipBlockedData = list(map(lambda x: x[0] / total, ipBlockedData))
        writeCSV(dataDir + str(i) + "-ip-blocked.csv", [ipBlockedData])
    else:
        with open(dataDir + str(i) + "-ip-blocked.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            ipBlockedData = [line for line in reader]
            ipBlockedData = ipBlockedData[0]
            ipBlockedData = list(map(float, ipBlockedData))

    _, ax = plt.subplots()

    start = 0
    end = len(usersData)
    plotRange = range(start, end)

    ax.set_title("Namespaces Edited By Different Groups of Users")
    ax.hlines(
        y=plotRange,
        xmin=[
            min(a, b, c, d)
            for a, b, c, d in zip(
                specialUsersData[start:end],
                botsData[start:end],
                blockedData[start:end],
                ipBlockedData[start:end],
            )
        ],
        xmax=specialUsersData[start:end],
        color="grey",
        alpha=0.4,
    )
    ax.vlines(
        x=allUsersData[start:end],
        ymin=list(map(lambda x: x - 0.5, plotRange)),
        ymax=list(map(lambda x: x + 0.5, plotRange)),
        color="grey",
        alpha=0.4,
    )
    ax.scatter(usersData, plotRange, color="mediumpurple", label="all users")
    ax.scatter(specialUsersData, plotRange, color="gold", label="users with privileges")
    ax.scatter(botsData, plotRange, color="mediumaquamarine", label="bots")
    ax.scatter(ipData, plotRange, color="skyblue", label="IP users")
    ax.scatter(blockedData, plotRange, color="orangered", label="blocked users")
    ax.scatter(ipBlockedData, plotRange, color="#F08EC1", label="blocked IP users")
    ax.set_yticklabels(columns[start:end])
    ax.set_yticks(plotRange)
    ax.legend(
        loc="upper center", bbox_to_anchor=(0.5, 1), ncol=3, fancybox=True, shadow=True,
    )

    plt.gcf().set_size_inches(9.5, 9.5)
    removeSpines(ax)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def talkpageEditsTimeAveraged(cursor, i, plotDir, dataDir, dryrun):
    yearConditions = [
        "where",
        "join user on edit.user_table_id = user.id where user.bot is not True and",
    ]
    monthConditions = [
        "",
        "join user on edit.user_table_id = user.id where user.bot is not True",
    ]
    names = ["withBots", "noBots"]

    for j, name in enumerate(names):
        figname = plotDir + str(i) + "-" + name + "-" + "talkpageEditsTimeAveraged"
        plt.figure()
        years = """select Year(edit_date) as date, count(*) from edit %s
         Year(edit_date) > 2001 and Year(edit_date) < 2020 GROUP BY YEAR(edit_date)
        order by YEAR(edit_date) ;"""

        if not dryrun:
            cursor.execute(years % yearConditions[j],)
            yearsData = cursor.fetchall()

            writeCSV(dataDir + str(i) + "-" + name + "-years.csv", yearsData)
        else:
            with open(dataDir + str(i) + "-" + name + "-years.csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                yearsData = [line for line in reader]

                yearsData = list(map(lambda x: tuple(map(float, x)), yearsData))

        months = """select Year(edit_date), Month(edit_date) as date, count(*) from edit %s
        GROUP BY YEAR(edit_date), Month(edit_date)
        order by YEAR(edit_date), Month(edit_date);"""

        if not dryrun:
            cursor.execute(months % monthConditions[j],)
            monthsData = cursor.fetchall()

            writeCSV(dataDir + str(i) + "-" + name + "-months.csv", monthsData)
        else:
            with open(dataDir + str(i) + "-" + name + "-months.csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                monthsData = [line for line in reader]

                monthsData = list(map(lambda x: tuple(map(float, x)), monthsData))

        datesYears = list(
            map(lambda x: matplotlib.dates.datestr2num(str(int(x[0]))), yearsData)
        )
        datesMonths = list(
            map(
                lambda x: matplotlib.dates.datestr2num(
                    str(int(x[0])) + "-" + str(int(x[1]))
                ),
                monthsData,
            )
        )
        valuesYears = [x[1] for x in yearsData]
        valuesMonths = [x[2] for x in monthsData]

        _, ax = plt.subplots()

        ax.set_title("Talkpage edits over time")
        ax.set_ylabel("Edits per Year")

        ax.plot_date(datesYears, valuesYears, "C0-")
        ax2 = ax.twinx()
        ax2.plot_date(datesMonths, valuesMonths, "C0-", alpha=0.4)
        ax2.set_ylabel("Edits per Month")

        plt.gcf().set_size_inches(12, 7.5)
        ax.spines["top"].set_visible(False)
        ax2.spines["top"].set_visible(False)
        ax.yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        ax2.yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))

        plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
        plt.close()


def talkpageEditsOverTimeNoBots(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "talkpageEditsOverTimeNoBots"
    plt.figure()

    query = """select cast(edit_date as date) as date, count(*) from edit join user
    on edit.user_table_id = user.id
    where user.bot is not True group by date order by date;"""

    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()

        writeCSV(dataDir, i, data)
    else:
        with open(dataDir + str(i) + ".csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            data = [line for line in reader]

            data = list(map(lambda x: (dt.strptime(x[0], "%Y-%m-%d"), int(x[1])), data))

    dates = list(map(lambda x: matplotlib.dates.date2num(x[0]), data))
    values = [x[1] for x in data]
    _, ax = plt.subplots()

    ax.set_title("Talkpage edits over time excluding bots")

    ax.plot_date(dates, values, "C0-")

    plt.gcf().set_size_inches(12, 7.5)
    singlePlot(plt, ax, "y")

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def averageBlockedLastEdits(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "averageBlockedLastEdits"
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

    blocked = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment)  FROM edit
    inner join user
    on user.id = edit.user_table_id
    where user.blocked is True and ip_address is not true;"""
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

    blockedLastFive = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
    AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
    AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment)  FROM blocked_last_five_edits;"""
    if not dryrun:
        cursor.execute(blockedLastFive,)
        blockedLastFiveData = cursor.fetchall()
        blockedLastFiveData = list(*blockedLastFiveData)
        with open(dataDir + str(i) + "-blockedLastFive.txt", "w") as file:
            file.write(str(blockedLastFiveData))
    else:
        blockedLastFiveData = [
            591.8531,
            313.1837,
            42.4830,
            39.3817,
            9.9740,
            1.7104,
            2.4844,
            0.1693,
            0.0056,
            0.0001,
            0.0004,
            0.12568949,
            0.10761438,
            0.03202700,
            0.00905484,
            0.10172546,
            0.0245,
            0.18894388,
            0.1336,
            0.044459942111849636,
            0.0062527888968363565,
        ]

    fig, axs = plt.subplots(4, 1, gridspec_kw={"height_ratios": [2, 2, 3, 11]})

    start = 0
    end = 2
    plotRange = range(start, end)

    fig.suptitle("Average of all integer edit fields")
    axs[0].hlines(
        y=plotRange,
        xmin=[min(a, b) for a, b in zip(blockedData[:end], blockedLastFiveData[:end],)],
        xmax=[max(a, b) for a, b in zip(blockedData[:end], blockedLastFiveData[:end],)],
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
        blockedLastFiveData[:2],
        plotRange,
        color="orangered",
        marker="D",
        label="Last five edits of blocked users",
    )
    axs[0].scatter(blockedData[:2], plotRange, color="orangered", label="Blocked users")
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
            min(a, b)
            for a, b in zip(blockedData[start:end], blockedLastFiveData[start:end],)
        ],
        xmax=[
            max(a, b)
            for a, b in zip(blockedData[start:end], blockedLastFiveData[start:end],)
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
    axs[1].scatter(
        blockedLastFiveData[start:end], plotRange, color="orangered", marker="D"
    )
    axs[1].scatter(blockedData[start:end], plotRange, color="orangered")
    axs[1].set_yticklabels(columns[start:end])
    axs[1].set_yticks(plotRange)

    start = 5
    end = 8
    plotRange = range(1, end - start + 1)
    axs[2].hlines(
        y=plotRange,
        xmin=[
            min(a, b)
            for a, b in zip(blockedData[start:end], blockedLastFiveData[start:end],)
        ],
        xmax=[
            max(a, b)
            for a, b in zip(blockedData[start:end], blockedLastFiveData[start:end],)
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
    axs[2].scatter(
        blockedLastFiveData[start:end], plotRange, color="orangered", marker="D"
    )
    axs[2].scatter(blockedData[start:end], plotRange, color="orangered")
    axs[2].set_yticklabels(columns[start:end])
    axs[2].set_yticks(plotRange)
    axs[2].set_xlim(left=0)

    start = 8
    end = 21
    plotRange = range(1, end - start + 1)
    axs[3].hlines(
        y=plotRange,
        xmin=[
            min(a, b) for a, b in zip(blockedData[start:], blockedLastFiveData[start:],)
        ],
        xmax=[
            max(a, b) for a, b in zip(blockedData[start:], blockedLastFiveData[start:],)
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
    axs[3].scatter(
        blockedLastFiveData[start:], plotRange, color="orangered", marker="D"
    )
    axs[3].scatter(blockedData[start:], plotRange, color="orangered")
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


def talkpageEditsTimeGroups(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "talkpageEditsTimeGroups"
    plt.figure()

    columns = [
        "Special",
        "Users",
        "Bot",
        "Blocked",
        "IP",
        "IP Blocked",
    ]

    colors = [
        "gold",
        "mediumpurple",
        "mediumaquamarine",
        "orangered",
        "skyblue",
        "#F08EC1",
    ]

    conditions = [
        "user_special is True",
        "bot is not True and blocked is not true and ip_address is not true and user_special is not True",
        "bot is True",
        "blocked is True and ip_address is not true and bot is not true and user_special is not True",
        "ip_address is True and blocked is not true",
        "ip_address is True and blocked is true",
    ]

    queryYear = """select count(*) from edit join user on edit.user_table_id = user.id
    where %s and Year(edit_date) > 2001 and Year(edit_date) < 2020
    GROUP BY YEAR(edit_date) order by YEAR(edit_date)"""

    queryMonth = """select Year(edit_date), Month(edit_date) as date, count(*) from edit
    join user on edit.user_table_id = user.id
    where %s
    GROUP BY YEAR(edit_date), Month(edit_date) order by YEAR(edit_date), Month(edit_date)"""

    dataYear = []
    dataMonth = []
    datesMonths = []

    for j, column in enumerate(columns):
        # print(conditions[i])
        if not dryrun:
            cursor.execute(queryYear % conditions[j],)
            yearsData = cursor.fetchall()
            dataYear.append(yearsData)
            writeCSV(dataDir + str(i) + "-years-" + column + ".csv", yearsData)
        else:
            with open(dataDir + str(i) + "-years-" + column + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                yearsData = [line for line in reader]

                yearsData = list(map(lambda x: tuple(map(float, x)), yearsData))
                dataYear.append(yearsData)

        if not dryrun:
            cursor.execute(queryMonth % conditions[j],)
            monthData = cursor.fetchall()
            dataMonth.append(monthData)
            writeCSV(dataDir + str(i) + "-month-" + column + ".csv", monthData)
        else:
            with open(dataDir + str(i) + "-month-" + column + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                monthData = [line for line in reader]

                monthData = list(map(lambda x: tuple(map(float, x)), monthData))
                monthDates = list(
                    map(
                        lambda x: matplotlib.dates.datestr2num(
                            str(int(x[0])) + "-" + str(int(x[1]))
                        ),
                        monthData,
                    )
                )
                dataMonth.append(monthData)
                datesMonths.append(monthDates)

    datesYears = list(range(2002, 2020))

    _, axs = plt.subplots(2, 1)

    axs[0].set_title("Talkpage edits over time by group")
    for i, column in enumerate(columns):
        axs[0].plot(
            datesYears,
            dataYear[i],
            color=colors[i],
            label=column,
            linestyle="-",
            marker=",",
        )
        axs[1].plot_date(
            datesMonths[i],
            [x[2] for x in dataMonth[i]],
            color=colors[i],
            label=column,
            linestyle="-",
            marker=",",
        )

    axs[0].set_ylabel("Edits per Year")
    axs[1].set_ylabel("Edits per Month")

    for ax in axs:
        ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        showGrid(plt, ax, "y")

    plt.gcf().set_size_inches(16, 12)
    plt.legend(loc="upper right")

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def averageFeaturesOverTimeGroups(cursor, i, plotDir, dataDir, dryrun):
    columns = [
        "Length of added content",
        "Length of deleted content",
        "Deleted words",
        "Length of comment",
        "Characters in Longest inserted word",
        "Longest Character Sequence",
        "Number of internal links inserted",
        "Number of external links inserted",
        "Blanking talkpage",
        "Comment contains 'copyedit'",
        "Special characters in comment",
        "Percent of capitalization in added",
        "Percent of digits in added",
        "Percent of pronouns in added",
        "Percent of special characters in added",
        "Added contains vulgarity",
        "Percent of whitespace in added",
        "Edit Reverted",
        "Added sentiment",
        "Deleted sentiment",
    ]

    groups = [
        "Special",
        "Users",
        "Bot",
        "Blocked",
        "IP",
        "IP Blocked",
    ]

    conditions = [
        "user_special is True",
        "bot is not True and blocked is not true and ip_address is not true and user_special is not True",
        "bot is True",
        "blocked is True and ip_address is not true and bot is not true and user_special is not True",
        "ip_address is True and blocked is not true",
        "ip_address is True and blocked is true",
    ]

    timeSpanConditions = ["YEAR(edit_date), MONTH(edit_date), ", "YEAR(edit_date),"]
    groupByConditions = [
        " GROUP BY YEAR(edit_date), MONTH(edit_date) order by YEAR(edit_date), MONTH(edit_date)",
        " GROUP BY YEAR(edit_date) order by YEAR(edit_date)",
    ]

    names = ["month", "year"]
    for m in range(2):
        data = []

        for j, condition in enumerate(conditions):
            query = """select %s AVG(added_length),AVG(deleted_length),
            AVG(del_words),AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),
            AVG(ins_internal_link),AVG(ins_external_link),AVG(comment_special_chars),AVG(blanking),
            AVG(comment_copyedit),AVG(ins_capitalization),AVG(ins_digits),
            AVG(ins_pronouns),AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),
            AVG(added_sentiment),AVG(deleted_sentiment)  FROM edit join user
            on edit.user_table_id = user.id
            where %s
            %s ;"""

            if not dryrun:
                cursor.execute(
                    query % (timeSpanConditions[m], condition, groupByConditions[m])
                )
                groupData = cursor.fetchall()
                data.append(groupData)
                writeCSV(
                    dataDir + str(i) + "-" + names[m] + "-" + groups[j] + ".csv",
                    groupData,
                )
            else:
                with open(
                    dataDir + str(i) + "-" + names[m] + "-" + groups[j] + ".csv", "r"
                ) as file:
                    reader = csv.reader(file, delimiter=",")
                    groupData = [line for line in reader]

                    groupData = list(map(lambda x: tuple(map(float, x)), groupData))
                    data.append(groupData)

        if m == 0:
            dates = [
                list(
                    map(
                        lambda x: matplotlib.dates.datestr2num(
                            str(int(x[0])) + "-" + str(int(x[1]))
                        ),
                        y,
                    )
                )
                for y in data
            ]
            values = [list(map(lambda x: x[2:], y)) for y in data]
        elif m == 1:
            dates = [
                list(map(lambda x: matplotlib.dates.datestr2num(str(int(x[0]))), y,))
                for y in data
            ]
            values = [list(map(lambda x: x[1:], y)) for y in data]

        colors = [
            "gold",
            "mediumpurple",
            "mediumaquamarine",
            "orangered",
            "skyblue",
            "#F08EC1",
        ]

        for j in range(4):
            figname = (
                plotDir
                + str(i)
                + "-"
                + names[m]
                + "-"
                + str(j)
                + "-"
                + "averageFeaturesOverTimeGroups"
            )
            plt.figure()
            _, axs = plt.subplots(5, 1)

            axs[0].set_title("Talkpage edits over time")
            for k, group in enumerate(groups):
                for l in range(0, 5):
                    axs[l].set_title(columns[(5 * j) + l])
                    axs[l].plot_date(
                        dates[k],
                        list(map(lambda x: x[(5 * j) + l], values[k])),
                        "C0-",
                        label=group,
                        c=colors[k],
                    )
                    removeSpines(axs[l])
            axs[0].legend(loc="best")
            plt.gcf().set_size_inches(20, 20)

            plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
            plt.close()


def talkpageEditorsTimeGroups(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "talkpageEditorsTimeGroups"
    plt.figure()

    columns = [
        "Special",
        "Users",
        "Bot",
        "Blocked",
        "IP",
        "IP Blocked",
    ]

    colors = [
        "gold",
        "mediumpurple",
        "mediumaquamarine",
        "orangered",
        "skyblue",
        "#F08EC1",
    ]

    conditions = [
        "user_special is True",
        "bot is not True and blocked is not true and ip_address is not true and user_special is not True",
        "bot is True",
        "blocked is True and ip_address is not true and bot is not true and user_special is not True",
        "ip_address is True and blocked is not true",
        "ip_address is True and blocked is true",
    ]

    queryYear = """SELECT count(years) FROM (
        SELECT Year(edit_date) as years FROM edit JOIN user ON edit.user_table_id = user.id     
        WHERE %s AND Year(edit_date) > 2001 AND Year(edit_date) < 2020     
        GROUP BY YEAR(edit_date), edit.user_table_id 
        ORDER BY YEAR(edit_date)
        ) AS innerQuery group by years"""

    # queryMonth = """select Year(edit_date), Month(edit_date) as date, count(*) from edit
    # join user on edit.user_table_id = user.id
    # where %s
    # GROUP BY YEAR(edit_date), Month(edit_date), edit.user_table_id order by YEAR(edit_date), Month(edit_date)"""

    dataYear = []
    # dataMonth = []
    # datesMonths = []

    for j, column in enumerate(columns):
        # print(conditions[i])
        if not dryrun:
            cursor.execute(queryYear % conditions[j],)
            yearsData = cursor.fetchall()
            dataYear.append(yearsData)
            writeCSV(dataDir + str(i) + "-years-" + column + ".csv", yearsData)
        else:
            with open(dataDir + str(i) + "-years-" + column + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                yearsData = [line for line in reader]

                yearsData = list(map(lambda x: tuple(map(float, x)), yearsData))
                dataYear.append(yearsData)

        # if not dryrun:
        #     cursor.execute(queryMonth % conditions[j],)
        #     monthData = cursor.fetchall()
        #     dataMonth.append(monthData)
        #     writeCSV(dataDir + str(i) + "-month-" + column + ".csv", monthData)
        # else:
        #     with open(dataDir + str(i) + "-month-" + column + ".csv", "r") as file:
        #         reader = csv.reader(file, delimiter=",")
        #         monthData = [line for line in reader]

        #         monthData = list(map(lambda x: tuple(map(float, x)), monthData))
        #         monthDates = list(
        #             map(
        #                 lambda x: matplotlib.dates.datestr2num(
        #                     str(int(x[0])) + "-" + str(int(x[1]))
        #                 ),
        #                 monthData,
        #             )
        #         )
        #         dataMonth.append(monthData)
        #         datesMonths.append(monthDates)

    datesYears = list(range(2002, 2020))

    _, axs = plt.subplots(2, 1)

    axs[0].set_title("Number of talkpage editors over time by group")
    for i, column in enumerate(columns):
        axs[0].plot(
            datesYears,
            dataYear[i],
            color=colors[i],
            label=column,
            linestyle="-",
            marker=",",
        )
        # axs[1].plot_date(
        #     datesMonths[i],
        #     [x[2] for x in dataMonth[i]],
        #     color=colors[i],
        #     label=column,
        #     linestyle="-",
        #     marker=",",
        # )

    axs[0].set_ylabel("Editors per Year")
    axs[1].set_ylabel("Editors per Month")

    for ax in axs:
        ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        showGrid(plt, ax, "y")

    plt.gcf().set_size_inches(16, 12)
    plt.legend(loc="upper right")

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


def compositionOfUserOverTime(cursor, i, plotDir, dataDir, dryrun):

    columns = [
        "Special",
        "Users",
        "Bot",
        "Blocked",
        "IP",
        "IP Blocked",
    ]

    colors = [
        "gold",
        "mediumpurple",
        "mediumaquamarine",
        "orangered",
        "skyblue",
        "#F08EC1",
    ]

    conditions = [
        "user_special is True",
        "bot is not True and blocked is not true and ip_address is not true and user_special is not True",
        "bot is True",
        "blocked is True and ip_address is not true and bot is not true and user_special is not True",
        "ip_address is True and blocked is not true",
        "ip_address is True and blocked is true",
    ]

    queryEditsYear = """select count(*) from edit join user on edit.user_table_id = user.id
    where %s and Year(edit_date) > 2001 and Year(edit_date) < 2020
    GROUP BY YEAR(edit_date) order by YEAR(edit_date)"""
    dataEditsYear = []

    queryEditorsYear = """SELECT count(years) FROM (
        SELECT Year(edit_date) as years FROM edit JOIN user ON edit.user_table_id = user.id     
        WHERE %s AND Year(edit_date) > 2001 AND Year(edit_date) < 2020     
        GROUP BY YEAR(edit_date), edit.user_table_id 
        ORDER BY YEAR(edit_date)
        ) AS innerQuery group by years"""
    dataEditorsYear = []

    for j, column in enumerate(columns):
        # print(conditions[i])
        if not dryrun:
            cursor.execute(queryEditsYear % conditions[j],)
            yearsData = cursor.fetchall()
            dataEditsYear.append(yearsData)
            writeCSV(dataDir + str(i) + "-edits-" + column + ".csv", yearsData)
        else:
            with open(dataDir + str(i) + "-edits-" + column + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                yearsData = [line for line in reader]
                yearsData = list(map(lambda x: float(x[0]), yearsData))
                dataEditsYear.append(yearsData)

    for j, column in enumerate(columns):
        if not dryrun:
            cursor.execute(queryEditorsYear % conditions[j],)
            yearsData = cursor.fetchall()
            dataEditorsYear.append(yearsData)
            writeCSV(dataDir + str(i) + "-editors-" + column + ".csv", yearsData)
        else:
            with open(dataDir + str(i) + "-editors-" + column + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                yearsData = [line for line in reader]

                yearsData = list(map(lambda x: float(x[0]), yearsData))
                dataEditorsYear.append(yearsData)

    datesYears = list(range(2002, 2020))

    figname = plotDir + str(i) + "-compositionOfUserOverTime"
    plt.figure()
    _, axs = plt.subplots(2, 1)
    axs[0].set_title("Number of talkpage editors over time by group")
    axs[1].set_title("Talkpage edits over time by group")
    axs[0].stackplot(
        datesYears,
        dataEditorsYear,
        colors=colors,
        labels=columns,
    )
    axs[1].stackplot(
        datesYears,
        dataEditsYear,
        colors=colors,
        labels=columns,
    )
    axs[0].set_ylabel("Editors per Year")
    axs[1].set_ylabel("Edits per Year")

    for ax in axs:
        ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))

    plt.gcf().set_size_inches(16, 12)
    plt.legend()

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()

    sums = [sum(x) for x in list(zip(*dataEditsYear))]
    dataEditsYear = [[z/sums[i] for i, z in enumerate(y)] for y in dataEditsYear]
    sums = [sum(x) for x in list(zip(*dataEditorsYear))]
    dataEditorsYear = [[z/sums[i] for i, z in enumerate(y)] for y in dataEditorsYear]
    
    figname = plotDir + str(i) + "-proportional-compositionOfUserOverTime"
    plt.figure()
    _, axs = plt.subplots(2, 1)
    axs[0].set_title("Number of talkpage editors over time by group")
    axs[1].set_title("Talkpage edits over time by group")
    axs[0].stackplot(
        datesYears,
        dataEditorsYear,
        colors=colors,
        labels=columns,
    )
    axs[1].stackplot(
        datesYears,
        dataEditsYear,
        colors=colors,
        labels=columns,
    )
    axs[0].set_ylabel("Editors per Year / %")
    axs[1].set_ylabel("Edits per Year / %")

    for ax in axs:
        ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    plt.gcf().set_size_inches(16, 12)
    plt.legend()

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.close()


# --------------------------------------------------------------------------------------


def writeCSV(fileName, data):
    with open(fileName, "w") as file:
        writer = csv.writer(file, delimiter=",")
        for line in data:
            writer.writerow(line)


def mapNamespace(data):
    mapping = {
        "0": "Main",
        "1": "Main Talk",
        "2": "User",
        "3": "User Talk",
        "4": "Wikipedia",
        "5": "Wikipedia Talk",
        "6": "File",
        "7": "FIle Talk",
        "8": "MediaWiki",
        "9": "MediaWiki Talk",
        "10": "Template",
        "11": "Template Talk",
        "12": "Help",
        "13": "Help Talk",
        "14": "Category",
        "15": "Category Talk",
        "-1": "Special",
        "-2": "Media",
        "100": "Portal",
        "101": "Portal Talk",
        "118": "Draft",
        "119": "Draft Talk",
        "710": "TimedText",
        "711": "TimedText Talk",
        "828": "Module",
        "829": "Module Talk",
        "108": "Book",
        "109": "Book Talk",
        "446": "Education Program",
        "447": "Education Program Talk",
        "2300": "Gadget",
        "2301": "Gadget Talk",
        "2302": "Gadget Definition",
        "2303": "Gadget Definition Talk",
    }

    data = list(map(lambda x: (mapping[x[0]], x[1]), data))
    return data


def singlePlot(pltObj, ax, axis):
    removeSpines(ax)

    if axis == "y":
        ax.yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        showGrid(pltObj, ax, "y")
    elif axis == "x":
        ax.xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        showGrid(pltObj, ax, "x")


# formatter function takes tick label and tick position
def threeFigureFormatter(x, pos):
    if pos:
        pass  # appeasing the linter
    s = "%d" % x
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ",".join(reversed(groups))


def removeSpines(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def showGrid(pltObj, ax, axis):
    pltObj.grid(color="#ccc", which="major", axis=axis, linestyle="solid")
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

    fontFiles = font_manager.findSystemFonts(fontpaths=["./"])
    for fontFile in fontFiles:
        font_manager.fontManager.addfont(fontFile)

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

    i = 0  # 0 - 5 seconds
    # partitionStatus(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 1 - 79 seconds
    # distributionOfMainEdits(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 2
    # distributionOfTalkEdits(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 3
    # numberOfPagesPerNamespace(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 4
    # editsMainTalkNeither(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 5
    # numMainTalkEditsForBiggestUsers(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 6
    # numMainTalkEditsForBiggestBots(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 7
    # numMainTalkEditsForBiggestIPs(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 8
    # distributionOfMainEditsUserBots(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 9
    # editsMainTalkNeitherUserBots(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 10 - 2 minutes
    # editTimesUserBots(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 11
    # distributionOfEditsPerNamespace(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 12
    # sentimentUserBotsBlockedIP(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 13 - 55 minutes
    # sentimentGroups(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 14
    # profanityAll(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 15
    # averageAll(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 16
    # namespacesEditedByTopFiveHundred(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 17
    # internalExternalLinks(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 18
    # specialUsersPlot(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 19
    # averageAllSpecial(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 20
    # compositionOfUserIP(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 21
    # compositionOfUser(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 22
    # aggregations(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 23 - 50 seconds
    # editBooleans(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 24 - 50 seconds
    # userBooleans(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 25
    # talkpageEditsOverTime(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 26
    # averageAllEpoch(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 27
    # averageFeaturesOverTime(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 28
    # averageFeaturesOverYear(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 29 - 26 minutes
    # namespacesEditedByUserGroups(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 30 - minutes
    # talkpageEditsTimeAveraged(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 31
    # talkpageEditsOverTimeNoBots(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 32 - 7 minutes
    # averageBlockedLastEdits(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 33

    i = i + 1  # 34 - 54 minutes
    # talkpageEditsTimeGroups(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 35 - 48 minutes
    # averageFeaturesOverTimeGroups(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 36 - 17 minutes
    # talkpageEditorsTimeGroups(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 37
    # compositionOfUserOverTime(cursor, i, plotDir, dataDir, dryrun)

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

    tick = time.time()
    plot(
        plotDir=clArgs.dir, dryrun=clArgs.dryrun,
    )
    print("--- %s seconds ---" % (time.time() - tick))
