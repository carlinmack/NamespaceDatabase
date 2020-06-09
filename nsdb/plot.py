"""
This script ....t
"""
import argparse
import os

import Database
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr


def partitionStatus(cursor, i, plotDir, dataDir):
    plt.figure()
    figname = plotDir + str(i)

    query = """SELECT status, count(id)
    FROM wikiactors.partition
    GROUP BY status;"""

    cursor.execute(query,)
    data = cursor.fetchall()
    with open(dataDir + str(i) + ".txt", "w") as file:
        file.write(str(data))
    plt.title("Status of parsing partitions")
    plt.xlabel("Status")
    plt.ylabel("Number of Partitions")
    plt.bar(*zip(*data))
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def distributionOfMainEdits(cursor, i, plotDir, dataDir):
    figname = plotDir + str(i)
    plt.figure()

    query = """SELECT
    (SELECT count(*) FROM user WHERE number_of_edits = 0),
    (SELECT count(*) FROM user WHERE number_of_edits = 1),
    (SELECT count(*) FROM user WHERE number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE number_of_edits > 100);"""
    columns = ["no edits", "1 edit", "2-10 edits", "11-100 edits", ">100 edits"]
    cursor.execute(query,)
    data = cursor.fetchall()
    data = list(*data)
    with open(dataDir + str(i) + ".txt", "w") as file:
        file.write(str(data))

    total = sum(data)
    data = list(map(lambda x: x * 100 / total, data))

    plt.title("Distribution of edits in main space")
    plt.xlabel("Number of edits by user")
    plt.ylabel("Percentage")
    plt.bar(columns, data)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def distributionOfTalkEdits(cursor, i, plotDir, dataDir):
    figname = plotDir + str(i)
    plt.figure()

    query = """SELECT
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits = 0),
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits = 1),
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 1 and talkpage_number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 10 and talkpage_number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 100);"""
    columns = ["no edits", "1 edit", "2-10 edits", "11-100 edits", ">100 edits"]
    cursor.execute(query,)
    data = cursor.fetchall()
    data = list(*data)
    with open(dataDir + str(i) + ".txt", "w") as file:
        file.write(str(data))

    total = sum(data)
    data = list(map(lambda x: x * 100 / total, data))

    plt.title("Distribution of edits in talk space")
    plt.xlabel("Talk Page Edits")
    plt.ylabel("Percentage")
    plt.bar(columns, data)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def numberOfPagesPerNamespace(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i)
    plt.figure()

    query = """SELECT namespace, count(page_id)
    AS 'count'
    FROM page
    GROUP BY namespace;"""
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
            ("4", 1064053),
            ("5", 145316),
            ("3", 13270254),
            ("100", 89259),
            ("13", 1051),
            ("12", 1934),
            ("118", 91670),
            ("6", 799880),
            ("7", 421780),
            ("101", 22247),
            ("11", 310669),
            ("8", 2119),
            ("9", 1308),
            ("119", 20586),
            ("10", 575245),
            ("14", 1668104),
            ("15", 1399806),
            ("829", 6564),
            ("828", 9691),
            ("108", 6893),
            ("109", 6196),
            ("710", 924),
            ("711", 40),
            ("447", 1323),
            ("2300", 1),
            ("2301", 1),
        ]

    plt.title("Number of Pages per namespace")
    plt.xticks(rotation=90)
    plt.xlabel("Namespace")
    plt.ylabel("Number of Pages (log)")
    plt.yscale("log")
    plt.bar(*zip(*data))
    plt.savefig(figname + "-log", bbox_inches="tight", pad_inches=0.25)

    plt.ylabel("Number of Pages (linear)")
    plt.yscale("linear")
    plt.bar(*zip(*data))
    plt.savefig(figname + "-linear", bbox_inches="tight", pad_inches=0.25)


def editsMainTalkNeither(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i)
    plt.figure()

    query = """SELECT count(*)
        FROM user;"""
    cursor.execute(query,)
    totalUsers = cursor.fetchone()[0]

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

    plt.title("Namespaces that users edit")
    plt.ylabel("Percentage")
    plt.bar(columns, data)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def numMainTalkEditsForBiggestUsers(cursor, i, plotDir, dataDir):
    figname = plotDir + str(i)
    plt.figure()

    mainspace = """SELECT username, number_of_edits FROM user
    where bot is null order by number_of_edits desc limit 10;"""
    talkspace = """SELECT username, talkpage_number_of_edits FROM user
    where bot is null order by talkpage_number_of_edits desc limit 10;"""
    cursor.execute(mainspace,)
    mainspaceData = cursor.fetchall()

    with open(dataDir + str(i) + "-mainspace.txt", "w") as file:
        file.write(str(mainspaceData))

    cursor.execute(talkspace,)
    talkspaceData = cursor.fetchall()

    with open(dataDir + str(i) + "-talkspace.txt", "w") as file:
        file.write(str(talkspaceData))

    plt.title("Number of main and talk edits for the biggest editors")
    plt.bar(*zip(*mainspaceData), label="mainspace edits")
    plt.bar(*zip(*talkspaceData), label="talkspace edits")
    plt.xticks(rotation=90)
    plt.legend(loc="upper right")
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def numMainTalkEditsForBiggestBots(cursor, i, plotDir, dataDir):
    figname = plotDir + str(i)
    plt.figure()

    mainspace = """SELECT username, number_of_edits FROM user
    where bot is true order by number_of_edits desc limit 10;"""
    talkspace = """SELECT username, talkpage_number_of_edits FROM user
    where bot is true order by talkpage_number_of_edits desc limit 10;"""
    cursor.execute(mainspace,)
    mainspaceData = cursor.fetchall()

    with open(dataDir + str(i) + "-mainspace.txt", "w") as file:
        file.write(str(mainspaceData))

    cursor.execute(talkspace,)
    talkspaceData = cursor.fetchall()

    with open(dataDir + str(i) + "-talkspace.txt", "w") as file:
        file.write(str(talkspaceData))

    plt.title("Number of main and talk edits for the biggest bots")
    plt.bar(*zip(*mainspaceData), label="mainspace edits")
    plt.bar(*zip(*talkspaceData), label="talkspace edits")
    plt.xticks(rotation=90)
    plt.legend(loc="upper right")
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def numMainTalkEditsForBiggestIPs(cursor, i, plotDir, dataDir):
    figname = plotDir + str(i)
    plt.figure()

    mainspace = """SELECT ip_address, number_of_edits FROM user
    where ip_address is not null order by number_of_edits desc limit 10;"""
    talkspace = """SELECT ip_address, talkpage_number_of_edits FROM user
    where ip_address is not null order by talkpage_number_of_edits desc limit 10;"""
    cursor.execute(mainspace,)
    mainspaceData = cursor.fetchall()
    # data = list(*data)
    with open(dataDir + str(i) + "-mainspace.txt", "w") as file:
        file.write(str(mainspaceData))

    cursor.execute(talkspace,)
    talkspaceData = cursor.fetchall()

    with open(dataDir + str(i) + "-talkspace.txt", "w") as file:
        file.write(str(talkspaceData))

    plt.title("Number of main and talk edits for the biggest IP editors")
    plt.bar(*zip(*mainspaceData), label="mainspace edits")
    plt.bar(*zip(*talkspaceData), label="talkspace edits")
    plt.xticks(rotation=90)
    plt.legend(loc="upper right")
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def distributionOfMainEditsUserBots(cursor, i, plotDir, dataDir, dryrun=False):
    def formatter(x, pos):  # formatter function takes tick label and tick position
        s = "%d" % x
        groups = []
        while s and s[-1].isdigit():
            groups.append(s[-3:])
            s = s[:-3]
        return s + ",".join(reversed(groups))

    figname = plotDir + str(i)
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
    threeFigures = tkr.FuncFormatter(formatter)
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
    plt.gcf().set_size_inches(20, 10)
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def editsMainTalkNeitherUserBots(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i)
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
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def editTimesUserBots(cursor, i, plotDir, dataDir, dryrun=False):

    figname = plotDir + str(i)
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
        userData = [584.68424387, 1352.63700297, 4186.79704245, 7490.39812962]
        userStd = [
            4172.026442852001,
            4943.701153194956,
            10873.528895162885,
            19310.972230041192,
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
        blockedData = [92.79879749, 303.09142600, 1582.28911081, 3231.75859999]
        blockedStd = [
            1437.4337418350062,
            1804.4136287010265,
            5778.304638286785,
            10743.635287170524,
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
        specialUsersData = [192.15421342, 1462.58485847, 17093.34624816, 55476.52302954]
        specialUsersStd = [
            2590.0629314313774,
            3788.0370304857165,
            17440.14473037299,
            40756.72616459319,
        ]

    # Numbers of pairs of bars you want
    N = len(columns)

    # Position of bars on x-axis
    ind = list(range(N))

    # Figure size
    plt.figure(figsize=(9, 7))

    # Width of a bar
    width = 0.3

    # Plotting
    plt.bar(
        ind,
        specialUsersData,
        width,
        label="Users with special privileges",
        yerr=specialUsersStd,
    )
    plt.bar(
        list(map(lambda x: x + width, ind)),
        userData,
        width,
        label="Non blocked users",
        yerr=userStd,
    )
    plt.bar(
        list(map(lambda x: x + width * 2, ind)),
        blockedData,
        width,
        label="Blocked users",
        yerr=blockedStd,
    )
    plt.ylim(bottom=0)
    plt.ylabel("Hours")
    plt.title("")

    # xticks()
    # First argument - A list of positions at which ticks should be placed
    # Second argument -  A list of labels to place at the given locations
    plt.xticks(list(map(lambda x: x + (width * 2) / 2, ind)), columns)

    # Finding the best position for legends and putting it
    plt.legend(loc="best")
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)

    # fig, axs = plt.subplots(1, 2, gridspec_kw={"width_ratios": [3, 1]})

    # fig.suptitle("Time between talkpage edits and duration between first and last edit")

    # axs[0].bar(columns[:2], data[:2])
    # axs[0].set_xticks
    # axs[0].tick_params(labelrotation=90)
    # axs[0].ylabel("Hours")

    # axs[1].bar(columns[2:7], data[2:7])
    # axs[1].tick_params(labelrotation=90)
    # axs[1].ylabel("Hours")

    # plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def distributionOfEditsPerNamespace(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i)
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
    axs[0, 1].set_title("page edits in main talk space")
    axs[0, 1].bar(columns, mainspaceTalkData)
    axs[1, 0].set_title("page edits in user space")
    axs[1, 0].bar(columns, userData)
    axs[1, 1].set_title("page edits in user talk space")
    axs[1, 1].bar(columns, userTalkData)
    # fig.tight_layout()
    plt.gcf().set_size_inches(11, 9)
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


#
def sentimentUserBotsBlockedIP(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i)
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

    # Numbers of pairs of bars you want
    N = len(columns)

    # Position of bars on x-axis
    ind = list(range(N))

    # Figure size
    plt.figure(figsize=(12, 7))

    # Width of a bar
    width = 0.2

    # Plotting
    plt.bar(ind, userData, width, label="Non blocked users")
    plt.bar(
        list(map(lambda x: x + width, ind)), blockedData, width, label="Blocked users"
    )
    plt.bar(list(map(lambda x: x + width * 2, ind)), botsData, width, label="Bots")
    plt.bar(
        list(map(lambda x: x + width * 3, ind)),
        ipAddressData,
        width,
        label="IP address",
    )

    plt.ylabel("unit ?")
    plt.title("Average sentiment of different subsets of users")

    # xticks()
    # First argument - A list of positions at which ticks should be placed
    # Second argument -  A list of labels to place at the given locations
    plt.xticks(list(map(lambda x: x + (width * 3) / 2, ind)), columns)

    # Finding the best position for legends and putting it
    plt.legend(loc="best")
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


#
def sentimentBots(cursor, i, plotDir, dataDir, dryrun=False):

    figname = plotDir + str(i)
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

    # Numbers of pairs of bars you want
    N = len(columns)

    # Position of bars on x-axis
    ind = list(range(N))

    # Figure size
    plt.figure(figsize=(12, 7))

    # Width of a bar
    width = 0.15

    # Plotting
    plt.bar(ind, botsAddedPosData, width, label="added positive")
    plt.bar(
        list(map(lambda x: x + width, ind)),
        botsAddNegData,
        width,
        label="added negative",
    )
    plt.bar(
        list(map(lambda x: x + width * 2, ind)),
        botsDelPosData,
        width,
        label="deleted positive",
    )
    plt.bar(
        list(map(lambda x: x + width * 3, ind)),
        botsDelNegData,
        width,
        label="deleted negative",
    )
    plt.bar(
        list(map(lambda x: x + width * 4, ind)),
        botsBothData,
        width,
        label="both have sentiment",
    )
    plt.bar(
        list(map(lambda x: x + width * 5, ind)), botsData, width, label="all bots",
    )

    plt.ylabel("unit ?")
    plt.title("Average sentiment for different types of bot edits")

    # xticks()
    # First argument - A list of positions at which ticks should be placed
    # Second argument -  A list of labels to place at the given locations
    plt.xticks(list(map(lambda x: x + (width * 3) / 2, ind)), columns)

    # Finding the best position for legends and putting it
    plt.legend(loc="best")
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


#
def profanityAll(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i)
    plt.figure()

    data = []

    specialUsers = """select avg(edit.ins_vulgarity)
    from edit join user
    on edit.user_table_id = user.id
    where user.blocked is null and user.bot is null and confirmed is true;"""
    if not dryrun:
        cursor.execute(specialUsers,)
        specialUsersData = cursor.fetchall()
        specialUsersData = specialUsersData[0][0]
        with open(dataDir + str(i) + "-specialUsers.txt", "w") as file:
            file.write(str(specialUsersData))
    else:
        specialUsersData = 0.0187

    data.append(("users with\nspecial priviliges", specialUsersData))

    users = """select avg(edit.ins_vulgarity)
    from edit
    join user
    on edit.user_table_id = user.id
    where user.blocked is null and user.ip_address is null and user.bot is null;"""
    if not dryrun:
        cursor.execute(users,)
        userData = cursor.fetchall()
        userData = userData[0][0]
        with open(dataDir + str(i) + "-user.txt", "w") as file:
            file.write(str(userData))
    else:
        userData = 0.0187

    data.append(("users", userData))

    blocked = """select avg(edit.ins_vulgarity)
    from edit
    join user
    on edit.user_table_id = user.id
    where user.blocked is true;"""
    if not dryrun:
        cursor.execute(blocked,)
        blockedData = cursor.fetchall()
        blockedData = blockedData[0][0]
        with open(dataDir + str(i) + "-blocked.txt", "w") as file:
            file.write(str(blockedData))
    else:
        blockedData = 0.0209

    data.append(("blocked", blockedData))

    bots = """select avg(edit.ins_vulgarity)
    from edit
    join user
    on edit.user_table_id = user.id
    where user.bot is true;"""
    if not dryrun:
        cursor.execute(bots,)
        botsData = cursor.fetchall()
        botsData = botsData[0][0]
        with open(dataDir + str(i) + "-bot.txt", "w") as file:
            file.write(str(botsData))
    else:
        botsData = 0.0108

    data.append(("bots", botsData))

    ipAddress = """select avg(edit.ins_vulgarity)
    from edit
    join user
    on edit.user_table_id = user.id
    where user.ip_address is true;"""
    if not dryrun:
        cursor.execute(ipAddress,)
        ipAddressData = cursor.fetchall()
        ipAddressData = ipAddressData[0][0]
        with open(dataDir + str(i) + "-ipAddress.txt", "w") as file:
            file.write(str(ipAddressData))
    else:
        ipAddressData = 0.0418

    data.append(("ip", ipAddressData))

    plt.title("Average profanity per type of user")
    plt.ylabel("Average profanity / %")
    plt.bar(*zip(*data))
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


#
def averageAll(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i)
    plt.figure()

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
        userData = [584.68424387, 1352.63700297, 4186.79704245, 7490.39812962]
        userStd = [
            4172.026442852001,
            4943.701153194956,
            10873.528895162885,
            19310.972230041192,
        ]

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

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def namespacesEditedByTopFiveHundred(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i)
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

    plt.title("Namespaces that the top 500 users have edited")
    plt.xticks(rotation=90)
    plt.ylabel("? (log)")
    # plt.yscale("log")
    plt.bar(*zip(*data))
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


#
def internalExternalLinks(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i)
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

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


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

    # 0
    i = 0
    # partitionStatus(cursor, i, plotDir, dataDir)

    # 1
    i = i + 1
    # distributionOfMainEdits(cursor, i, plotDir, dataDir)

    # 2
    i = i + 1
    # distributionOfTalkEdits(cursor, i, plotDir, dataDir)

    # 3
    i = i + 1
    # numberOfPagesPerNamespace(cursor, i, plotDir, dataDir, dryrun)

    # 4
    i = i + 1
    # editsMainTalkNeither(cursor, i, plotDir, dataDir, dryrun)

    # 5
    i = i + 1
    # numMainTalkEditsForBiggestUsers(cursor, i, plotDir, dataDir)

    # 6
    i = i + 1
    # numMainTalkEditsForBiggestBots(cursor, i, plotDir, dataDir)

    # 7
    i = i + 1
    # numMainTalkEditsForBiggestIPs(cursor, i, plotDir, dataDir)

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
