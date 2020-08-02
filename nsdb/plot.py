import argparse
import csv
import os
import time
from datetime import datetime as dt
from math import floor

import matplotlib
import matplotlib.dates as mdates
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import pandas as pd
from cycler import cycler
from matplotlib import cm

import Database

# Plots --------------------------------------------------------------------------------


def partitionStatus(cursor, i, plotDir, dataDir, dryrun):
    plt.figure()
    figname = plotDir + str(i) + "-" + "partitionStatus"

    query = """SELECT status, count(id) FROM wikiactors.partition
    GROUP BY status ORDER BY count(id) desc;"""

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

    savePlot(figname)


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

    savePlot(figname)


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

    savePlot(figname)


def numberOfPagesPerNamespace(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "numberOfPagesPerNamespace"
    plt.figure()

    query = """SELECT namespace, count(page_id) AS 'count' FROM page
    GROUP BY namespace ORDER BY namespace;"""
    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        data = list(map(lambda x: (str(x[0]), x[1]), data))

        writeCSV(dataDir + str(i) + ".csv", data)
    else:
        with open(dataDir + str(i) + ".csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            data = [[str(line[0]), int(line[1])] for line in reader]

    data = mapNamespace(data)

    scales = ["log", "linear"]
    for scale in scales:
        _, ax = plt.subplots()  # Create a figure and an axes.
        ax.barh(*zip(*data))
        ax.set_ylabel("Namespace")  # Add an x-label to the axes.
        ax.set_xlabel("Number of Pages (%s)" % scale)  # Add a y-label to the axes.
        ax.set_xscale(scale)
        ax.set_title("Number of Pages per namespace")  # Add a title to the axes.

        plt.gcf().set_size_inches(8, 8)
        singlePlot(plt, ax, "x")

        savePlot(figname + "-%s" % scale)


def editsMainTalkNeither(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "editsMainTalkNeither"
    plt.figure()

    if not dryrun:
        query = """SELECT count(*) FROM user;"""
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

    savePlot(figname)


def numMainTalkEditsForBiggestEditors(cursor, i, plotDir, dataDir, dryrun):
    groups, conditions, colors = groupInfo()

    selectConditions = [
        "username",
        "username",
        "username",
        "ip_address",
        "ip_address",
        "username",
    ]

    dataMainspace = []
    dataTalkspace = []

    for j, group in enumerate(groups):
        mainspace = """SELECT %s, number_of_edits FROM user
        where %s order by number_of_edits desc limit 10;"""
        talkspace = """SELECT %s, talkpage_number_of_edits FROM user
        where %s order by talkpage_number_of_edits desc limit 10;"""
        if not dryrun:
            cursor.execute(mainspace % (selectConditions[j], conditions[j]),)
            mainspaceData = cursor.fetchall()

            writeCSV(dataDir + str(i) + "-" + group + "-mainspace.csv", mainspaceData)
            dataMainspace.append(mainspaceData)

            cursor.execute(talkspace % (selectConditions[j], conditions[j]),)
            talkspaceData = cursor.fetchall()
            dataTalkspace.append(talkspaceData)

            writeCSV(dataDir + str(i) + "-" + group + "-talkspace.csv", talkspaceData)
        else:
            with open(dataDir + str(i) + "-" + group + "-mainspace.csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                mainspaceData = [[str(line[0]), int(line[1])] for line in reader]
                dataMainspace.append(mainspaceData)

            with open(dataDir + str(i) + "-" + group + "-talkspace.csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                talkspaceData = [[str(line[0]), int(line[1])] for line in reader]
                dataTalkspace.append(talkspaceData)

    for j, group in enumerate(groups):
        figname = plotDir + str(i) + "-" + group + "-numMainTalkEditsForBiggestEditors"
        plt.figure()
        fig, axs = plt.subplots(2, 1)  # Create a figure and an axes.
        fig.suptitle("Top 10 mainspace and talkpage %s editors" % group)
        axs[0].barh(*zip(*dataMainspace[j]), color=colors[j])
        axs[0].set_title("Main space edits")  # Add a title to the axes.
        axs[1].barh(*zip(*dataTalkspace[j]), color=colors[j])
        axs[1].set_title("Talk space edits")  # Add a title to the axes.

        plt.gcf().set_size_inches(8, 11)
        for ax in axs:
            removeSpines(ax)
            ax.xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
            ax.set_xlabel("Number of edits (linear)")  # Add a y-label to the axes.

        savePlot(figname)


def distributionOfMainEditsUserBots(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i) + "-" + "distributionOfMainEditsUserBots"
    plt.figure()

    groups, conditions, colors = groupInfo()
    data = []

    columns = ["no edits", "1 edit", "2-10 edits", "11-100 edits", ">100 edits"]
    for j, condition in enumerate(conditions):
        conditionTuple = (condition,) * 5
        mainspaceGroup = """SELECT
        (SELECT count(*) FROM user WHERE %s and number_of_edits = 0),
        (SELECT count(*) FROM user WHERE %s and number_of_edits = 1),
        (SELECT count(*) FROM user WHERE %s and number_of_edits > 1 and number_of_edits <= 10),
        (SELECT count(*) FROM user WHERE %s and number_of_edits > 10 and number_of_edits <= 100),
        (SELECT count(*) FROM user WHERE %s and number_of_edits > 100);"""
        if not dryrun:
            cursor.execute(mainspaceGroup % conditionTuple,)
            mainspaceGroupData = cursor.fetchall()
            mainspaceGroupData = list(*mainspaceGroupData)
            writeCSV(
                dataDir + str(i) + "-mainspace-%s.csv" % groups[j], [mainspaceGroupData]
            )
        else:
            with open(dataDir + str(i) + "-mainspace-%s.csv" % groups[j], "r") as file:
                reader = csv.reader(file, delimiter=",")
                mainspaceGroupData = list(reader)[0]
                mainspaceGroupData = [int(x) for x in mainspaceGroupData]

        data.append(mainspaceGroupData)

        talkspaceUser = """SELECT
        (SELECT count(*) FROM user WHERE %s and talkpage_number_of_edits = 0),
        (SELECT count(*) FROM user WHERE %s and talkpage_number_of_edits = 1),
        (SELECT count(*) FROM user WHERE %s and talkpage_number_of_edits > 1 and talkpage_number_of_edits <= 10),
        (SELECT count(*) FROM user WHERE %s and talkpage_number_of_edits > 10 and talkpage_number_of_edits <= 100),
        (SELECT count(*) FROM user WHERE %s and talkpage_number_of_edits > 100);"""
        if not dryrun:
            cursor.execute(talkspaceUser % conditionTuple,)
            talkspaceGroupData = cursor.fetchall()
            talkspaceGroupData = list(*talkspaceGroupData)
            writeCSV(
                dataDir + str(i) + "-talkspace-%s.csv" % groups[j], [talkspaceGroupData]
            )
        else:
            with open(dataDir + str(i) + "-talkspace-%s.csv" % groups[j], "r") as file:
                reader = csv.reader(file, delimiter=",")
                talkspaceGroupData = list(reader)[0]
                talkspaceGroupData = [int(x) for x in talkspaceGroupData]

        data.append(talkspaceGroupData)

    _, axs = plt.subplots(3, 4)
    axs = axs.ravel()
    namespaces = ["main", "talk"]

    # fig.suptitle("Distribution of edits across name spaces for bots and users")

    for j, ax in enumerate(axs):
        ax.set_title(groups[floor(j / 2)] + " edits in " + namespaces[j % 2] + " space")
        ax.bar(columns, data[j], color=colors[floor(j / 2)])
        ax.yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        removeSpines(ax)

    plt.gcf().set_size_inches(25, 13)

    savePlot(figname)


def editsMainTalkNeitherUserBots(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i) + "-" + "editsMainTalkNeitherUserBots"
    plt.figure()

    columns = [
        "edits mainspace\nand talkspace",
        "edits mainspace\nnot talkspace",
        "edits talkspace\nnot mainspace",
        "edits neither",
    ]

    groups, conditions, colors = groupInfo()

    data = []
    for j, condition in enumerate(conditions):
        groupQuery = """SELECT
        (select count(*) as target from user
        WHERE talkpage_number_of_edits > 0 and number_of_edits > 0 and %s),
        (select count(*) as target from user
        WHERE talkpage_number_of_edits = 0 and number_of_edits > 0 and %s),
        (select count(*) as target from user
        WHERE talkpage_number_of_edits > 0 and number_of_edits = 0 and %s),
        (select count(*) as target from user
        WHERE talkpage_number_of_edits = 0 and number_of_edits = 0 and %s);"""
        if not dryrun:
            cursor.execute(groupQuery % (condition, condition, condition, condition),)
            groupData = cursor.fetchall()
            groupData = list(*groupData)
            writeCSV(dataDir + str(i) + "-%s.csv" % groups[j], [groupData])
        else:
            with open(dataDir + str(i) + "-%s.csv" % groups[j]) as file:
                reader = csv.reader(file, delimiter=",")
                groupData = [line for line in reader][0]
                groupData = [int(x) for x in groupData]

        data.append(groupData)

    _, axs = plt.subplots(2, 3)
    axs = axs.ravel()

    for j, ax in enumerate(axs):
        ax.set_title("Namespaces that " + groups[j] + "s edit")
        ax.bar(columns, data[j], color=colors[j])
        ax.yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        removeSpines(ax)

    plt.gcf().set_size_inches(22.5, 12)
    savePlot(figname)


def editTimesUserBots(cursor, i, plotDir, dataDir, dryrun=False):
    groups, conditions, colors = groupInfo()

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
    savePlot(figname)

    figname = plotDir + str(i) + "-2-" + "editTimesUserBots"
    plt.figure()
    fig, axs = plt.subplots(2, 1)

    fig.suptitle("Average time between talk page edits", y=1.05)
    plotRange = range(0, 2)

    for ax in axs:
        removeSpines(ax)
        ax.xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        ax.set_yticks(plotRange)
        ax.set_ylim(bottom=-0.5, top=1.5)
        ax.set_xlabel("Hours")

    for j, group in enumerate(groups):
        axs[0].scatter(data[j][:2], plotRange, color=colors[j], label=group, s=75)
        axs[1].scatter(data[j][2:], plotRange, color=colors[j], label=group, s=75)

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

    savePlot(figname)


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
    and number_of_edits = 1),
    (SELECT count(*) FROM page WHERE namespace = 3
    and number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM page WHERE namespace = 3
    and number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM page WHERE namespace = 3
    and number_of_edits > 100);"""
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
    savePlot(figname)


def sentimentUserBotsBlockedIP(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i) + "-" + "sentimentUserBotsBlockedIP"
    plt.figure()

    groups, conditions, colors = groupInfo()

    columns = [
        "added sentiment",
        "deleted sentiment",
    ]

    data = []

    for j, condition in enumerate(conditions):
        groupQuery = """select avg(edit.added_sentiment),avg(edit.deleted_sentiment)
        from edit join user
        on edit.user_table_id = user.id
        where %s;"""
        if not dryrun:
            cursor.execute(groupQuery % condition,)
            groupData = cursor.fetchall()
            groupData = list(*groupData)
            writeCSV(dataDir + str(i) + "-" + groups[j] + ".csv", [groupData])
        else:
            with open(dataDir + str(i) + "-" + groups[j] + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                groupData = []
                for line in reader:
                    groupData.append([float(k) for k in line])
                groupData = groupData[0]

        data.append(groupData)

    _, ax = plt.subplots()

    # Position of bars on x-axis
    ind = list(range(len(columns)))

    # Width of a bar
    width = 0.15

    # Plotting
    for j, groupData in enumerate(data):
        ax.bar(
            list(map(lambda x: x + width * j, ind)),
            groupData,
            width,
            label=groups[j],
            color=colors[j],
        )

    ax.set_ylabel("unit ?")
    ax.set_title("Average sentiment of different subsets of users")

    # xticks()
    # First argument - A list of positions at which ticks should be placed
    # Second argument -  A list of labels to place at the given locations
    plt.xticks(list(map(lambda x: x + (width * 5) / 2, ind)), columns)

    ax.set_ylim(bottom=0)
    removeSpines(ax)
    showGrid(plt, ax, "y")
    plt.gcf().set_size_inches(12, 7)

    plt.legend(loc="best")
    savePlot(figname)


def sentimentGroups(cursor, i, plotDir, dataDir, dryrun=False):
    groups, conditions, colors = groupInfo()

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
                    groupData.append([float(k) for k in line])

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
    plt.legend(loc="best")
    savePlot(figname)

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

    savePlot(figname)

    figname = plotDir + str(i) + "-3-" + "sentimentGroups"
    plt.figure()
    _, axs = plt.subplots(3, 2)
    axs = axs.ravel()

    for j, label in enumerate(labels):
        ax = axs[j]
        ax.set_title(label)
        ax.set_ylabel("unit ?")
        ax.set_xticks(range(0, 6))
        ax.set_xticklabels(groups)
        removeSpines(ax)
        ax.grid(color="#ccc", which="major", axis="y", linestyle="solid")
        ax.set_axisbelow(True)

        for k, group in enumerate(groups):
            if j in [2, 3]:
                value = data[k][j][1] - data[k][j][0]
            else:
                value = data[k][j][0] - data[k][j][1]
            ax.bar(k, value, label=group, color=colors[k])

    plt.gcf().set_size_inches(14, 17)
    savePlot(figname)


def profanityAll(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "profanityAll"
    plt.figure()

    groups, conditions, colors = groupInfo()

    data = []
    std = []

    for j, condition in enumerate(conditions):
        groupQuery = """select avg(edit.ins_vulgarity), std(edit.ins_vulgarity)
        from edit join user
        on edit.user_table_id = user.id
        where %s;"""
        if not dryrun:
            cursor.execute(groupQuery % condition,)
            groupData = cursor.fetchall()
            writeCSV(dataDir + str(i) + "-" + groups[j] + ".csv", groupData)
        else:
            with open(dataDir + str(i) + "-" + groups[j] + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                groupData = []
                for line in reader:
                    groupData.append([float(k) for k in line])

        data.append(groupData[0][0])
        std.append(groupData[0][1])

    _, ax = plt.subplots()
    ax.set_title("Average profanity per type of user")
    ax.set_ylabel("Average profanity / %")
    ax.bar(groups, data, yerr=std, color=colors)
    ax.set_ylim(bottom=0)

    plt.grid(color="#ccc", which="major", axis="y", linestyle="solid")
    ax.set_axisbelow(True)
    removeSpines(ax)
    savePlot(figname)


def averageAll(cursor, i, plotDir, dataDir, dryrun, columns):
    figname = plotDir + str(i) + "-" + "averageAll"
    plt.figure()

    query = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(ins_avg_word_length),AVG(del_avg_word_length),AVG(blanking),
    AVG(comment_copyedit),AVG(comment_personal_life),AVG(comment_special_chars),AVG(ins_capitalization),
    AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),
    AVG(reverted),AVG(added_sentiment),AVG(deleted_sentiment),STD(added_length),
    STD(deleted_length),STD(del_words),STD(comment_length),STD(ins_longest_inserted_word),
    STD(ins_longest_character_sequence),STD(ins_internal_link),STD(ins_external_link),
    STD(ins_avg_word_length), STD(del_avg_word_length),STD(blanking),STD(comment_copyedit),
    STD(comment_personal_life),STD(comment_special_chars),STD(ins_capitalization),STD(ins_digits),
    STD(ins_pronouns),STD(ins_special_chars),STD(ins_vulgarity),STD(ins_whitespace),STD(reverted),
    STD(added_sentiment),STD(deleted_sentiment) from edit;"""
    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        dataStd = list(*data)[23:]
        data = list(*data)[:23]
        writeCSV(dataDir + str(i) + ".csv", [data])
        writeCSV(dataDir + str(i) + "-std.csv", [dataStd])
    else:
        with open(dataDir + str(i) + ".csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            data = [list(map(float, line)) for line in reader][0]
        with open(dataDir + str(i) + "-std.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            dataStd = [list(map(float, line)) for line in reader][0]

    fig, axs = plt.subplots(1, 3, gridspec_kw={"width_ratios": [3, 7, 13]})

    start = [0, 3, 10]
    end = [3, 10, 23]

    fig.suptitle("Average of all integer edit fields")
    for j, ax in enumerate(axs):
        ax.bar(
            columns[start[j] : end[j]],
            data[start[j] : end[j]],
            yerr=dataStd[start[j] : end[j]],
        )
        ax.tick_params(labelrotation=90)
        ax.set_ylim(bottom=0)
        removeSpines(ax)

    plt.gcf().set_size_inches(10, 7.5)

    savePlot(figname)


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
        writeCSV(dataDir + str(i) + ".csv", data)
    else:
        with open(dataDir + str(i) + ".csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            data = [(str(line[0]), int(line[1])) for line in reader]

    data = mapNamespace(data)

    _, ax = plt.subplots()
    ax.set_title("Namespaces that the top 500 users have edited")
    labels = list(map(lambda x: x[0], data))
    ax.set_xticklabels(labels=labels, rotation=90)
    ax.bar(*zip(*data))
    removeSpines(ax)
    plt.grid(color="#ccc", which="major", axis="y", linestyle="solid")
    ax.set_axisbelow(True)
    plt.gcf().set_size_inches(9, 5)
    savePlot(figname)


def internalExternalLinks(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "internalExternalLinks"
    plt.figure()

    groups, conditions, colors = groupInfo()

    internalData = []
    externalData = []

    for j, condition in enumerate(conditions):
        userGroup = """select avg(edit.ins_internal_link), avg(edit.ins_external_link)
        from edit join user
        on edit.user_table_id = user.id
        where %s;"""
        if not dryrun:
            cursor.execute(userGroup % condition,)
            userGroupData = cursor.fetchall()
            writeCSV(dataDir + str(i) + "-%s.csv" % groups[j], userGroupData)
        else:
            with open(dataDir + str(i) + "-%s.csv" % groups[j], "r") as file:
                reader = csv.reader(file, delimiter=",")
                userGroupData = [(float(line[0]), float(line[1])) for line in reader]

        userGroupInternalData = userGroupData[0][0]
        userGroupExternalData = userGroupData[0][1]

        internalData.append(userGroupInternalData)
        externalData.append(userGroupExternalData)

    _, axs = plt.subplots(2, 1)
    axs[0].bar(groups, internalData, color=colors)
    axs[0].set_title("Average added internal links per type of user")
    axs[1].bar(groups, externalData, color=colors)
    axs[1].set_title("Average added external links per type of user")
    plt.gcf().set_size_inches(6.5, 12)
    for ax in axs:
        removeSpines(ax)
        ax.grid(color="#ccc", which="major", axis="y", linestyle="solid")
        ax.set_axisbelow(True)

    savePlot(figname)


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

    scales = ["log", "linear"]
    for scale in scales:
        _, ax = plt.subplots()  # Create a figure and an axes.
        ax.barh(*zip(*data), color=colors)
        ax.invert_yaxis()
        ax.set_ylabel("User groups")  # Add an x-label to the axes.
        ax.set_xlabel("Number of Users (%s)" % scale)  # Add a y-label to the axes.
        ax.set_xscale(scale)
        ax.set_title("Number of Users per User Group")  # Add a title to the axes.
        ax.xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        plt.gcf().set_size_inches(7, 7)
        singlePlot(plt, ax, "x")
        savePlot(figname + "-%s" % scale)


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
        "ins_avg_word_length",
        "del_avg_word_length",
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

    groups, conditions, colors = groupInfo(all=True)

    data = []

    for j, condition in enumerate(conditions):
        query = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
        AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
        AVG(ins_external_link),AVG(ins_avg_word_length),AVG(del_avg_word_length),AVG(blanking),
        AVG(comment_copyedit),AVG(comment_personal_life),AVG(comment_special_chars),
        AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),
        AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
        AVG(deleted_sentiment)  FROM edit
        inner join user
        on user.id = edit.user_table_id
        where %s;"""
        if not dryrun:
            cursor.execute(query % condition,)
            groupData = cursor.fetchall()
            groupData = list(*groupData)

            writeCSV(dataDir + str(i) + "-" + groups[j] + ".csv", [groupData])
        else:
            with open(dataDir + str(i) + "-" + groups[j] + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                groupData = [list(map(float, line)) for line in reader][0]

        data.append(groupData)

    fig, axs = plt.subplots(3, 1, gridspec_kw={"height_ratios": [4, 6, 13]})

    fig.suptitle("Average of all integer edit fields")

    start = [0, 4, 10]
    end = [4, 10, 23]

    labels = [
        "none",
        "users with privileges",
        "all users",
        "blocked users",
        "IP users",
        "blocked IP users",
        "bots",
    ]

    for j, ax in enumerate(axs):
        plotRange = range(start[j], end[j])

        ax.hlines(
            y=plotRange,
            xmin=[
                min(a, b, c, d, e, f)
                for a, b, c, d, e, f in list(zip(*data[1:]))[start[j] : end[j]]
            ],
            xmax=[
                max(a, b, c, d, e, f)
                for a, b, c, d, e, f in list(zip(*data[1:]))[start[j] : end[j]]
            ],
            color="grey",
            alpha=0.4,
        )
        ax.vlines(
            x=data[0][start[j] : end[j]],
            ymin=list(map(lambda x: x - 0.5, plotRange)),
            ymax=list(map(lambda x: x + 0.5, plotRange)),
            color="grey",
            alpha=0.4,
        )

        for k, group in enumerate(data):
            if k == 0:
                continue
            ax.scatter(
                group[start[j] : end[j]],
                plotRange,
                color=colors[k],
                label=labels[k],
                alpha=0.75,
                edgecolors="none",
                s=100,
            )
        ax.set_yticklabels(columns[start[j] : end[j]])
        ax.set_yticks(plotRange)
        removeSpines(ax)
        ax.invert_yaxis()
        if j > 1:
            ax.set_xlim(left=0)

    axs[0].legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.6),
        ncol=3,
        fancybox=True,
        shadow=True,
    )

    plt.gcf().set_size_inches(9.5, 9.5)

    savePlot(figname)


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

    data = [data[j : j + 2] for j in range(0, len(data), 2)]

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
    data = [data[j : j + 2] for j in range(0, len(data), 2)]
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

    savePlot(figname)


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

    savePlot(figname)


def aggregations(cursor, i, plotDir, dataDir, dryrun, columns):
    figname = plotDir + str(i) + "-" + "aggregations"
    plt.figure()

    if not dryrun:
        modesData = []
        for j in columns:
            query = "SELECT %s FROM edit GROUP BY %s ORDER BY count(*) DESC LIMIT 1" % (
                j,
                j,
            )
            cursor.execute(query,)
            modesData.append(cursor.fetchall()[0][0])

        writeCSV(dataDir + str(i) + "-modes.csv", [modesData])
    else:
        with open(dataDir + str(i) + "-modes.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            modesData = [list(map(float, line)) for line in reader][0]

    mins = """select MIN(added_length),MIN(deleted_length),MIN(del_words),MIN(comment_length),
    MIN(ins_longest_inserted_word),MIN(ins_longest_character_sequence),MIN(ins_internal_link),
    MIN(ins_external_link),MIN(ins_avg_word_length), MIN(del_avg_word_length),MIN(blanking),
    MIN(comment_copyedit),MIN(comment_personal_life),MIN(comment_special_chars),
    MIN(ins_capitalization),MIN(ins_digits),MIN(ins_pronouns),MIN(ins_special_chars),
    MIN(ins_vulgarity),MIN(ins_whitespace),MIN(reverted),MIN(added_sentiment),
    MIN(deleted_sentiment) FROM edit;"""
    if not dryrun:
        cursor.execute(mins,)
        minsData = cursor.fetchall()
        minsData = list(*minsData)

        writeCSV(dataDir + str(i) + "-mins.csv", [minsData])
    else:
        with open(dataDir + str(i) + "-mins.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            minsData = [list(map(float, line)) for line in reader][0]

    maxs = """select MAX(added_length),MAX(deleted_length),MAX(del_words),MAX(comment_length),
    MAX(ins_longest_inserted_word),MAX(ins_longest_character_sequence),MAX(ins_internal_link),
    MAX(ins_external_link),MAX(ins_avg_word_length), MAX(del_avg_word_length),MAX(blanking),
    MAX(comment_copyedit),MAX(comment_personal_life),MAX(comment_special_chars),
    MAX(ins_capitalization),MAX(ins_digits),MAX(ins_pronouns),MAX(ins_special_chars),
    MAX(ins_vulgarity),MAX(ins_whitespace),MAX(reverted),MAX(added_sentiment),
    MAX(deleted_sentiment)  FROM edit;"""
    if not dryrun:
        cursor.execute(maxs,)
        maxsData = cursor.fetchall()
        maxsData = list(*maxsData)

        writeCSV(dataDir + str(i) + "-maxs.csv", [maxsData])
    else:
        with open(dataDir + str(i) + "-maxs.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            maxsData = [list(map(float, line)) for line in reader][0]

    means = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(ins_avg_word_length),AVG(del_avg_word_length),AVG(blanking),
    AVG(comment_copyedit),AVG(comment_personal_life),AVG(comment_special_chars),
    AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),
    AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment) from edit;"""
    if not dryrun:
        cursor.execute(means,)
        meansData = cursor.fetchall()
        meansData = list(*meansData)
        meansData = list(map(float, meansData))

        writeCSV(dataDir + str(i) + "-means.csv", [meansData])
    else:
        with open(dataDir + str(i) + "-means.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            meansData = [list(map(float, line)) for line in reader][0]

    stds = """select STD(added_length),STD(deleted_length),STD(del_words),STD(comment_length),
    STD(ins_longest_inserted_word),STD(ins_longest_character_sequence),STD(ins_internal_link),
    STD(ins_external_link),STD(ins_avg_word_length),STD(del_avg_word_length),STD(blanking),
    STD(comment_copyedit),STD(comment_personal_life),STD(comment_special_chars),
    STD(ins_capitalization),STD(ins_digits),STD(ins_pronouns),STD(ins_special_chars),
    STD(ins_vulgarity),STD(ins_whitespace),STD(reverted),STD(added_sentiment),
    STD(deleted_sentiment) from edit;"""
    if not dryrun:
        cursor.execute(stds,)
        stdsData = cursor.fetchall()
        stdsData = list(*stdsData)

        writeCSV(dataDir + str(i) + "-stds.csv", [stdsData])
    else:
        with open(dataDir + str(i) + "-stds.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            stdsData = [list(map(float, line)) for line in reader][0]

    stdsData = list(map(sum, zip(stdsData, meansData)))

    fig, axs = plt.subplots(6, 1, gridspec_kw={"height_ratios": [3, 1, 5, 2, 11, 2]})

    fig.suptitle("Min, max, mean and standard deviation of all fields")

    start = [0, 3, 4, 8, 10, 21]
    end = [3, 4, 8, 10, 21, 23]

    for j, ax in enumerate(axs):
        plotRange = range(start[j], end[j])

        ax.hlines(
            y=plotRange,
            xmin=minsData[start[j] : end[j]],
            xmax=maxsData[start[j] : end[j]],
            color="grey",
            alpha=0.4,
        )
        ax.vlines(
            x=[*minsData[start[j] : end[j]], *maxsData[start[j] : end[j]]],
            ymin=list(map(lambda x: x - 0.5, plotRange)),
            ymax=list(map(lambda x: x + 0.5, plotRange)),
            color="black",
        )
        ax.scatter(
            stdsData[start[j] : end[j]],
            plotRange,
            color="skyblue",
            label="Standard Deviation",
        )
        if j < 3:
            ax.xaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))
        if j in [1, 4]:
            invertedStds = list(
                map(
                    lambda x: max(2 * x[0] - x[1], 0),
                    zip(meansData[start[j] : end[j]], stdsData[start[j] : end[j]]),
                )
            )
            ax.scatter(invertedStds, plotRange, color="skyblue")
        elif j == 5:
            invertedStds = list(
                map(
                    lambda x: 2 * x[0] - x[1],
                    zip(meansData[start[j] : end[j]], stdsData[start[j] : end[j]]),
                )
            )
            ax.scatter(invertedStds, plotRange, color="skyblue")
        ax.scatter(meansData[start[j] : end[j]], plotRange, color="black", label="Mean")
        ax.set_yticklabels(columns[start[j] : end[j]])
        ax.set_yticks(plotRange)
        ax.invert_yaxis()
        removeSpines(ax)

    axs[0].legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.5),
        ncol=3,
        fancybox=True,
        shadow=True,
    )

    plt.gcf().set_size_inches(9.5, 9.5)

    savePlot(figname)


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

    savePlot(figname)


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

    savePlot(figname)


def talkpageEditsOverTime(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "talkpageEditsOverTime"
    plt.figure()

    query = "select cast(edit_date as date) as date, count(*) from edit group by date order by date;"

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

    savePlot(figname)


def averageAllEpoch(cursor, i, plotDir, dataDir, dryrun, columns):
    figname = plotDir + str(i) + "-" + "averageAllEpoch"
    plt.figure()

    groups = ["all", "before", "after"]
    conditions = [
        "1",
        "cast(edit_date as date) < '2010-09-01'",
        "cast(edit_date as date) >= '2010-09-01'",
    ]

    data = []

    for j, condition in enumerate(conditions):
        query = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
        AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
        AVG(ins_external_link),AVG(ins_avg_word_length), AVG(del_avg_word_length),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
        AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
        AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
        AVG(deleted_sentiment)  FROM edit
        where %s;"""
        if not dryrun:
            cursor.execute(query % condition,)
            condData = cursor.fetchall()
            condData = list(*condData)

            writeCSV(dataDir + str(i) + "-" + groups[j] + ".csv", [condData])
        else:
            with open(dataDir + str(i) + "-" + groups[j] + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                condData = [list(map(float, line)) for line in reader][0]

        data.append(condData)

    fig, axs = plt.subplots(3, 1, gridspec_kw={"height_ratios": [4, 6, 13]})

    fig.suptitle("Average of edit fields before and after the midpoint of the dataset")

    start = [0, 4, 10]
    end = [4, 10, 23]

    colors = [
        "skyblue",
        "orangered",
    ]

    labels = [
        "before 1st September 2010",
        "after 1st September 2010",
    ]

    for j, ax in enumerate(axs):
        plotRange = range(start[j], end[j])

        ax.hlines(
            y=plotRange,
            xmin=[min(a, b) for a, b in list(zip(*data[1:]))[start[j] : end[j]]],
            xmax=[max(a, b) for a, b in list(zip(*data[1:]))[start[j] : end[j]]],
            color="grey",
            alpha=0.4,
        )
        ax.vlines(
            x=data[0][start[j] : end[j]],
            ymin=list(map(lambda x: x - 0.5, plotRange)),
            ymax=list(map(lambda x: x + 0.5, plotRange)),
            color="grey",
            alpha=0.4,
        )

        for k, group in enumerate(data):
            if k == 0:
                continue
            ax.scatter(
                group[start[j] : end[j]],
                plotRange,
                color=colors[k - 1],
                label=labels[k - 1],
            )
        ax.set_yticklabels(columns[start[j] : end[j]])
        ax.set_yticks(plotRange)
        removeSpines(ax)
        ax.invert_yaxis()
        if j > 1:
            ax.set_xlim(left=0)

    axs[0].legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.6),
        ncol=3,
        fancybox=True,
        shadow=True,
    )

    plt.gcf().set_size_inches(9.5, 9.5)

    savePlot(figname)


def averageFeaturesOverTime(cursor, i, plotDir, dataDir, dryrun, columns):
    conditions = [", MONTH(edit_date)", ""]
    names = ["Month", "Year"]

    for l, condition in enumerate(conditions):
        figname = plotDir + str(i) + "-" + "averageFeaturesOver" + names[l]
        plt.figure()

        query = """select YEAR(edit_date)%s, AVG(added_length),AVG(deleted_length),
        AVG(del_words),AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),
        AVG(ins_internal_link),AVG(ins_external_link),AVG(ins_avg_word_length), AVG(del_avg_word_length)
        ,AVG(comment_special_chars),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
        AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),
        AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),AVG(deleted_sentiment)
        FROM edit
        GROUP BY YEAR(edit_date)%s
        order by YEAR(edit_date)%s;"""

        if not dryrun:
            cursor.execute(query % (condition, condition, condition),)
            data = cursor.fetchall()

            writeCSV(dataDir + str(i) + "-" + names[l] + ".csv", data)
        else:
            with open(dataDir + str(i) + "-" + names[l] + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                data = [line for line in reader]

                data = list(map(lambda x: tuple(map(float, x)), data))

        if l == 0:
            dates = list(
                map(
                    lambda x: matplotlib.dates.datestr2num(
                        str(int(x[0])) + "-" + str(int(x[1]))
                    ),
                    data,
                )
            )

            values = list(map(lambda x: x[2:], data))
        elif l == 1:
            dates = list(
                map(lambda x: matplotlib.dates.datestr2num(str(int(x[0]))), data,)
            )

            values = list(map(lambda x: x[1:], data))

        _, axs = plt.subplots(
            5, 1, gridspec_kw={"height_ratios": [1, 1, 1, 2, 1]}, sharex=True
        )

        axs[0].set_title("Talkpage edits over time")

        colors = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]
        start = [0, 3, 5, 11, 21]
        end = [3, 5, 11, 21, 23]
        for j, ax in enumerate(axs):
            for k in range(start[j], end[j]):
                ax.plot_date(
                    dates,
                    list(map(lambda x: x[k], values)),
                    "C0-",
                    label=columns[k],
                    c=colors[k % 10],
                )
            ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
            removeSpines(ax)
            ax.set_xlim(
                matplotlib.dates.datestr2num("2000-12"),
                matplotlib.dates.datestr2num("2020-05"),
            )
        plt.gcf().set_size_inches(20, 15)

        savePlot(figname)


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
        "File Talk",
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

    groups, conditions, colors = groupInfo(all=True)

    data = []
    for j, condition in enumerate(conditions):
        # https://stackoverflow.com/questions/28620904/how-to-count-unique-set-values-in-mysql
        count = "SELECT COUNT(*) FROM user where %s"
        group = """SELECT COUNT(user.namespaces) FROM
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
            where %s) user
        ON FIND_IN_SET(set_list.namespaces, user.namespaces) > 0
        GROUP BY set_list.namespaces
        ;"""
        if not dryrun:
            cursor.execute(group % condition,)
            groupData = cursor.fetchall()
            cursor.execute(count % condition,)
            total = cursor.fetchall()[0][0]
            groupData = list(map(lambda x: x[0] / total, groupData))

            writeCSV(dataDir + str(i) + "-%s.csv" % groups[j], [groupData])
        else:
            with open(dataDir + str(i) + "-%s.csv" % groups[j], "r") as file:
                reader = csv.reader(file, delimiter=",")
                groupData = [line for line in reader]
                groupData = groupData[0]
                groupData = list(map(float, groupData))

        data.append(groupData)

    _, ax = plt.subplots()
    plotRange = range(0, len(data[0]))
    ax.set_title("Namespaces Edited By Different Groups of Users")
    ax.hlines(
        y=plotRange,
        xmin=[min(a, b, c, d, e, f, g) for a, b, c, d, e, f, g in list(zip(*data))],
        xmax=[max(a, b, c, d, e, f, g) for a, b, c, d, e, f, g in list(zip(*data))],
        color="grey",
        alpha=0.4,
    )
    ax.vlines(
        x=data[0],
        ymin=list(map(lambda x: x - 0.5, plotRange)),
        ymax=list(map(lambda x: x + 0.5, plotRange)),
        color="grey",
        alpha=0.4,
    )

    for j, group in enumerate(data):
        if j == 0:
            continue
        ax.scatter(group, plotRange, color=colors[j], label=groups[j], s=75)
        ax.set_yticklabels(columns)
        ax.set_yticks(plotRange)
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1),
            ncol=3,
            fancybox=True,
            shadow=True,
        )

    plt.gcf().set_size_inches(9.5, 9.5)
    removeSpines(ax)

    savePlot(figname)


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

        savePlot(figname)


def talkpageEditsOverTimeNoBots(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "talkpageEditsOverTimeNoBots"
    plt.figure()

    query = """select cast(edit_date as date) as date, count(*) from edit join user
    on edit.user_table_id = user.id
    where user.bot is not True group by date order by date;"""

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

    ax.set_title("Talkpage edits over time excluding bots")

    ax.plot_date(dates, values, "C0-")
    ax.set_xlim(
        matplotlib.dates.datestr2num("2001-01"), matplotlib.dates.datestr2num("2019-12")
    )

    plt.gcf().set_size_inches(12, 7.5)
    singlePlot(plt, ax, "y")

    savePlot(figname)


def averageBlockedLastEdits(cursor, i, plotDir, dataDir, dryrun, columns):
    allEdits = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
    AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
    AVG(ins_external_link),AVG(ins_avg_word_length), AVG(del_avg_word_length),AVG(blanking),
    AVG(comment_copyedit),AVG(comment_personal_life),AVG(comment_special_chars),
    AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),
    AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
    AVG(deleted_sentiment) FROM edit
    inner join user
    on user.id = edit.user_table_id
    where ip_address is not true;"""
    if not dryrun:
        cursor.execute(allEdits,)
        allData = cursor.fetchall()
        allData = list(*allData)
        writeCSV(dataDir + str(i) + "-all.csv", [allData])
    else:
        with open(dataDir + str(i) + "-all.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            allData = [list(map(float, line)) for line in reader][0]

    optionNames = ["users", "IPs"]
    options = [["not", "blocked_last_five_edits"], ["", "blocked_ip_last_five_edits"]]
    optionColors = ["orangered", "#F08EC1"]

    excel = []

    for k in range(len(options)):
        blocked = """select AVG(added_length),AVG(deleted_length),AVG(del_words),AVG(comment_length),
        AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),AVG(ins_internal_link),
        AVG(ins_external_link),AVG(ins_avg_word_length), AVG(del_avg_word_length),AVG(blanking),
        AVG(comment_copyedit),AVG(comment_personal_life),AVG(comment_special_chars),
        AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),
        AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
        AVG(deleted_sentiment) FROM edit
        inner join user
        on user.id = edit.user_table_id
        where user.blocked is True and ip_address is %s true;"""
        if not dryrun:
            cursor.execute(blocked % options[k][0],)
            blockedData = cursor.fetchall()
            blockedData = list(*blockedData)
            writeCSV(dataDir + str(i) + "-" + optionNames[k] + ".csv", [blockedData])
        else:
            with open(dataDir + str(i) + "-" + optionNames[k] + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                blockedData = [list(map(float, line)) for line in reader][0]

        data = blockedData

        blockedLastFive = """select AVG(added_length),AVG(deleted_length),AVG(del_words),
        AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_longest_character_sequence),
        AVG(ins_internal_link),AVG(ins_external_link),AVG(ins_avg_word_length),
        AVG(del_avg_word_length),AVG(blanking),AVG(comment_copyedit),AVG(comment_personal_life),
        AVG(comment_special_chars),AVG(ins_capitalization),AVG(ins_digits),AVG(ins_pronouns),
        AVG(ins_special_chars),AVG(ins_vulgarity),AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),
        AVG(deleted_sentiment) FROM %s;"""
        if not dryrun:
            cursor.execute(blockedLastFive % options[k][1],)
            blockedLastFiveData = cursor.fetchall()
            blockedLastFiveData = list(*blockedLastFiveData)
            writeCSV(
                dataDir + str(i) + "-" + optionNames[k] + "-lastFive.csv",
                [blockedLastFiveData],
            )
        else:
            with open(
                dataDir + str(i) + "-" + optionNames[k] + "-lastFive.csv", "r"
            ) as file:
                reader = csv.reader(file, delimiter=",")
                blockedLastFiveData = [list(map(float, line)) for line in reader][0]

        lastFiveData = blockedLastFiveData

        plt.figure()
        figname = plotDir + str(i) + "-" + optionNames[k] + "-averageBlockedLastEdits"

        fig, axs = plt.subplots(3, 1, gridspec_kw={"height_ratios": [4, 6, 13]})
        fig.suptitle("Average of all integer edit fields")

        start = [0, 4, 10]
        end = [4, 10, 23]

        for j, ax in enumerate(axs):
            plotRange = range(start[j], end[j])
            ax.hlines(
                y=plotRange,
                xmin=[
                    min(a, b)
                    for a, b in zip(
                        data[start[j] : end[j]], lastFiveData[start[j] : end[j]]
                    )
                ],
                xmax=[
                    max(a, b)
                    for a, b in zip(
                        data[start[j] : end[j]], lastFiveData[start[j] : end[j]]
                    )
                ],
                color="grey",
                alpha=0.4,
            )
            ax.vlines(
                x=allData[start[j] : end[j]],
                ymin=list(map(lambda x: x - 0.5, plotRange)),
                ymax=list(map(lambda x: x + 0.5, plotRange)),
                color="grey",
                alpha=0.4,
            )
            ax.scatter(
                lastFiveData[start[j] : end[j]],
                plotRange,
                color=optionColors[k],
                marker="D",
                label="Last five edits of blocked %s" % optionNames[k],
                s=75,
            )
            ax.scatter(
                data[start[j] : end[j]],
                plotRange,
                color=optionColors[k],
                label="Blocked %s" % optionNames[k],
                s=75,
            )
            ax.set_yticklabels(columns[start[j] : end[j]])
            ax.set_yticks(plotRange)
            removeSpines(ax)
            ax.invert_yaxis()

        axs[0].legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.6),
            ncol=2,
            fancybox=True,
            shadow=True,
        )
        axs[1].set_xlim(left=0)
        axs[2].set_xlim(left=0)

        plt.gcf().set_size_inches(9.5, 9.5)

        savePlot(figname)
    writeCSV(dataDir + "excel.csv", excel)


def talkpageEditsTimeGroups(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "talkpageEditsTimeGroups"
    plt.figure()

    columns, conditions, colors = groupInfo()

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
    for j, column in enumerate(columns):
        axs[0].plot(
            datesYears,
            dataYear[j],
            color=colors[j],
            label=column,
            linestyle="-",
            marker=",",
        )
        axs[1].plot_date(
            datesMonths[j],
            [x[2:] for x in dataMonth[j]],
            color=colors[j],
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

    savePlot(figname)


def averageFeaturesOverTimeGroups(cursor, i, plotDir, dataDir, dryrun):
    columns = [
        "Length of added content",
        "Length of deleted content",
        "Deleted words",
        "Length of comment",
        "Characters in Longest inserted word",
        "Number of internal links inserted",
        "Number of external links inserted",
        "Average word length in added",
        "Average word length in deleted",
        "Blanking talkpage",
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

    groups, conditions, colors = groupInfo()

    timeSpanConditions = ["YEAR(edit_date), MONTH(edit_date), ", "YEAR(edit_date),"]
    groupByConditions = [
        " GROUP BY YEAR(edit_date), MONTH(edit_date) order by YEAR(edit_date), MONTH(edit_date)",
        " GROUP BY YEAR(edit_date) order by YEAR(edit_date)",
    ]

    names = ["month", "year"]
    for m in range(2):
        data = []

        for j, condition in enumerate(conditions):
            query = """select %s AVG(added_length),AVG(deleted_length),AVG(del_words),
            AVG(comment_length),AVG(ins_longest_inserted_word),AVG(ins_internal_link),
            AVG(ins_external_link),AVG(ins_avg_word_length),AVG(del_avg_word_length),
            AVG(comment_special_chars),AVG(blanking),AVG(ins_capitalization),
            AVG(ins_digits),AVG(ins_pronouns),AVG(ins_special_chars),AVG(ins_vulgarity),
            AVG(ins_whitespace),AVG(reverted),AVG(added_sentiment),AVG(deleted_sentiment)  
            FROM edit join user
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
                    "%s%s-%s-%s.csv" % (dataDir, str(i), names[m], groups[j]),
                    groupData,
                )
            else:
                with open(
                    "%s%s-%s-%s.csv" % (dataDir, str(i), names[m], groups[j]), "r"
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
            _, axs = plt.subplots(5, 1, sharex=True)

            axs[0].set_title("Talkpage edits over time")
            for k, group in enumerate(groups):
                for l, ax in enumerate(axs):
                    ax.set_title(columns[(5 * j) + l])
                    ax.plot_date(
                        dates[k],
                        list(map(lambda x: x[(5 * j) + l], values[k])),
                        "C0-",
                        label=group,
                        c=colors[k],
                    )
                    removeSpines(ax)
                    if m == 1:
                        ax.set_xlim(
                            matplotlib.dates.datestr2num("2001-01"),
                            matplotlib.dates.datestr2num("2019-12"),
                        )
            axs[0].legend(loc="best")
            plt.gcf().set_size_inches(20, 20)

            savePlot(figname)


def talkpageEditorsTimeGroups(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-" + "talkpageEditorsTimeGroups"
    plt.figure()

    columns, conditions, colors = groupInfo()

    queryYear = """SELECT count(years) FROM (
            SELECT Year(edit_date) as years FROM edit JOIN user 
                ON edit.user_table_id = user.id 
            WHERE %s AND Year(edit_date) > 2001 AND Year(edit_date) < 2020 
            GROUP BY YEAR(edit_date), edit.user_table_id 
            ORDER BY YEAR(edit_date)
        ) AS innerQuery GROUP BY years;"""

    queryMonth = """SELECT Concat(year, "-", month), count(user_table_id) FROM (
            SELECT Year(edit_date) as year, Month(edit_date) as month, user_table_id FROM edit JOIN user 
                ON edit.user_table_id = user.id 
            WHERE %s
            GROUP BY YEAR(edit_date), Month(edit_date), edit.user_table_id
            order by YEAR(edit_date), Month(edit_date)
        ) AS innerQuery GROUP BY year, month;"""

    dataYear = []
    dataMonth = []
    datesMonths = []

    for j, column in enumerate(columns):
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

            writeCSV(dataDir + str(i) + "-month-" + column + ".csv", monthData)
        else:
            with open(dataDir + str(i) + "-month-" + column + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                monthData = [line for line in reader]
                monthData = list(
                    map(lambda x: (dt.strptime(x[0], "%Y-%m"), int(x[1])), monthData)
                )

        dates = list(map(lambda x: x[0], monthData))
        values = [x[1] for x in monthData]
        datesMonths.append(dates)
        dataMonth.append(values)

    datesYears = [dt.strptime(str(x), "%Y") for x in range(2002, 2020)]

    _, axs = plt.subplots(2, 1, sharex=True)
    axs[0].set_title("Number of talkpage editors over time by group")

    for j, column in enumerate(columns):
        axs[0].plot_date(
            datesYears,
            dataYear[j],
            color=colors[j],
            label=column,
            linestyle="-",
            marker=",",
        )
        axs[1].plot_date(
            datesMonths[j],
            dataMonth[j],
            color=colors[j],
            label=column,
            linestyle="-",
            marker=",",
        )

    axs[0].set_ylabel("Editors per Year")
    axs[1].set_ylabel("Editors per Month")

    for ax in axs:
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.xaxis.set_tick_params(labelbottom=True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))

    plt.gcf().set_size_inches(16, 12)
    plt.legend(loc="upper right")

    savePlot(figname)


def compositionOfUserOverTime(cursor, i, plotDir, dataDir, dryrun):
    columns, conditions, colors = groupInfo()

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

    if not dryrun:
        for j, column in enumerate(columns):
            cursor.execute(queryEditsYear % conditions[j],)
            editorsData = cursor.fetchall()
            editorsData = [y[0] for y in editorsData]
            dataEditsYear.append(editorsData)

            cursor.execute(queryEditorsYear % conditions[j],)
            editsData = cursor.fetchall()
            editsData = [y[0] for y in editsData]
            dataEditorsYear.append(editsData)

        writeCSV(dataDir + str(i) + "-dataEditsYear.csv", dataEditsYear)
        writeCSV(dataDir + str(i) + "-dataEditorsYear.csv", dataEditorsYear)
    else:
        with open(dataDir + str(i) + "-dataEditorsYear.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            dataEditorsYear = [line for line in reader]
            dataEditorsYear = [[int(y) for y in x] for x in dataEditorsYear]

        with open(dataDir + str(i) + "-dataEditsYear.csv", "r") as file:
            reader = csv.reader(file, delimiter=",")
            dataEditsYear = [line for line in reader]
            dataEditsYear = [[int(y) for y in x] for x in dataEditsYear]

    datesYears = list(range(2002, 2020))

    figname = plotDir + str(i) + "-compositionOfUserOverTime"
    plt.figure()
    _, axs = plt.subplots(2, 1)
    axs[0].set_title("Number of talkpage editors over time by group")
    axs[0].set_ylabel("Editors per Year")
    axs[0].stackplot(
        datesYears, dataEditorsYear, colors=colors, labels=columns,
    )
    axs[1].set_title("Talkpage edits over time by group")
    axs[1].set_ylabel("Edits per Year")
    axs[1].stackplot(
        datesYears, dataEditsYear, colors=colors, labels=columns,
    )

    for ax in axs:
        ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.set_major_formatter(tkr.FuncFormatter(threeFigureFormatter))

    plt.gcf().set_size_inches(16, 12)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(reversed(handles), reversed(labels))

    savePlot(figname)

    sums = [sum(x) for x in list(zip(*dataEditsYear))]
    dataEditsYear = [[z / sums[j] for j, z in enumerate(y)] for y in dataEditsYear]
    sums = [sum(x) for x in list(zip(*dataEditorsYear))]
    dataEditorsYear = [[z / sums[j] for j, z in enumerate(y)] for y in dataEditorsYear]

    figname = plotDir + str(i) + "-proportional-compositionOfUserOverTime"
    plt.figure()
    _, axs = plt.subplots(2, 1)
    axs[0].set_title("Number of talkpage editors over time by group")
    axs[1].set_title("Talkpage edits over time by group")
    axs[0].stackplot(datesYears, dataEditorsYear, colors=colors, labels=columns)
    axs[1].stackplot(datesYears, dataEditsYear, colors=colors, labels=columns)
    axs[0].set_ylabel("Editors per Year / %")
    axs[1].set_ylabel("Edits per Year / %")

    for ax in axs:
        ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    plt.gcf().set_size_inches(16, 12)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(reversed(handles), reversed(labels))

    savePlot(figname)


def timespanOfContributorEngagement(cursor, i, plotDir, dataDir, dryrun):
    columns, conditions, _ = groupInfo(all=True)

    markerSizes = [5, 9, 5, 9, 5, 9, 9]

    for j, condition in enumerate(conditions):
        figname = (
            plotDir + str(i) + "-" + columns[j] + "-timespanOfContributorEngagement"
        )
        plt.figure()
        query = """SELECT cast(first_edit as date), cast(last_edit as date),
        number_of_edits + talkpage_number_of_edits AS total_edits
        FROM user join edit_times on user.id = edit_times.id WHERE %s"""
        if not dryrun:
            cursor.execute(query % condition,)
            tick = time.time()
            data = cursor.fetchall()
            writeCSV(dataDir + str(i) + "-" + columns[j] + ".csv", data)
        else:
            with open(dataDir + str(i) + "-" + columns[j] + ".csv", "r") as file:
                reader = csv.reader(file, delimiter=",")
                data = [
                    [
                        matplotlib.dates.datestr2num(line[0]),
                        matplotlib.dates.datestr2num(line[1]),
                        int(line[2]),
                    ]
                    for line in reader
                ]

        df = pd.DataFrame(data)
        df.columns = ["first_edit", "last_edit", "total_edits"]

        plt.figure(num=None, figsize=(15, 15))
        plt.xlim([dt(2001, 1, 1), dt(2020, 1, 4)])
        plt.ylim([dt(2001, 1, 1), dt(2020, 1, 4)])
        plt.xlabel("Date of First Edit", fontsize=16)
        plt.ylabel("Date of Most Recent Edit", fontsize=16)
        plt.title(
            "Timespan of Wikipedia Talkpage %s Editor Engagement" % columns[j],
            fontsize=16,
        )
        few_edits = df[df.total_edits < 10]
        some_edits = df[((df.total_edits >= 10) & (df.total_edits < 50))]
        many_edits = df[((df.total_edits >= 50) & (df.total_edits < 1000))]
        most_edits = df[df.total_edits >= 1000]

        data = [most_edits, many_edits, some_edits, few_edits]
        # colors = [cm.plasma(x) for x in [0.16, 0.42333333, 0.68666667, 0.95]]
        colors = ["purple", "red", "orange", "yellow"]

        for k, color in enumerate(colors):
            plt.plot(
                data[k]["first_edit"],
                data[k]["last_edit"],
                ".",
                markersize=markerSizes[j],
                alpha=0.1,
                color=color,
                markeredgewidth=0,
            )

        # plt.plot([dt(2001, 1, 1), dt(2015, 1, 4)], [dt(2006, 1, 1), dt(2020, 1, 4)], ls="--", c=".3")

        lgnd = plt.legend(
            [
                "Talkpage editors with more than 1000 edits",
                "Talkpage editors with between 50 and 1000 edits",
                "Talkpage editors with between 10 and 50 edits",
                "Talkpage editors with less than 10 edits",
            ],
            fontsize=16,
            loc="lower right",
        )
        # change the marker size manually for both lines
        for lg in lgnd.legendHandles:
            lg._legmarker.set_markersize(9)
            lg._legmarker.set_alpha(1)

        ax = plt.axes()
        # ax.set_facecolor('#292722')
        removeSpines(ax)

        savePlot(figname)


def firstLastEditsGroups(cursor, i, plotDir, dataDir, dryrun):
    figname = plotDir + str(i) + "-firstLastEditsGroups"
    plt.figure()

    columns, conditions, colors = groupInfo()

    tableColumns = ["first_edit", "last_edit"]

    data = []

    for j, condition in enumerate(conditions):
        groupData = []

        for k, t in enumerate(tableColumns):
            tableData = []
            query = """SELECT YEAR(%s), MONTH(%s), count(*)
            FROM user join edit_times on user.id = edit_times.id WHERE %s
            group by YEAR(%s), MONTH(%s) order by YEAR(%s), MONTH(%s)"""
            if not dryrun:
                cursor.execute(query % (t, t, condition, t, t, t, t,),)
                tick = time.time()
                tableData = cursor.fetchall()
                tableData = list(
                    map(lambda x: (str(x[0]) + "-" + str(x[1]), x[2]), tableData)
                )
                writeCSV("%s%s-%s-%s.csv" % (dataDir, str(i), columns[j], t), tableData)
            else:
                with open(
                    "%s%s-%s-%s.csv" % (dataDir, str(i), columns[j], t), "r"
                ) as file:
                    reader = csv.reader(file, delimiter=",")
                    tableData = [
                        [matplotlib.dates.datestr2num(line[0]), int(line[1]),]
                        for line in reader
                    ]
            groupData.append(list(zip(*tableData)))
        data.append(groupData)

    fig, axs = plt.subplots(4, 3)
    axs = axs.ravel(order="F")

    fig.suptitle(
        "How many users made their first and last talkpage edit per day in each group"
    )
    for j, ax in enumerate(axs):
        if not j % 2:
            ax.set_title("%s first edit" % columns[floor(j / 2)])
        else:
            ax.set_title("%s last edit" % columns[floor(j / 2)])
        ax.plot_date(
            x=data[floor(j / 2)][j % 2][0],
            y=data[floor(j / 2)][j % 2][1],
            linestyle="-",
            marker=",",
            color=colors[floor(j / 2)],
        )

        ax.set_xlim(right=matplotlib.dates.datestr2num("2020-03"))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    plt.gcf().set_size_inches(20, 15)

    savePlot(figname)


# Helpers ------------------------------------------------------------------------------


def savePlot(figname):
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25, dpi=200)
    plt.cla()
    plt.close()


def writeCSV(fileName, data):
    with open(fileName, "w") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerows(data)


def groupInfo(all=False):
    groups = ["Special User", "User", "Blocked User", "IP", "Blocked IP", "Bot"]

    conditions = [
        "user_special is True",
        "bot is not True and blocked is not true and ip_address is not true and user_special is not True",
        "blocked is True and ip_address is not true and bot is not true and user_special is not true",
        "ip_address is True and blocked is not true",
        "ip_address is True and blocked is true",
        "bot is True",
    ]

    colors = [
        "gold",
        "mediumpurple",
        "orangered",
        "skyblue",
        "#F08EC1",
        "mediumaquamarine",
    ]

    if all == True:
        groups.insert(0, "All")
        conditions.insert(0, "1")
        colors.insert(0, "black")

    return groups, conditions, colors


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


# Main ---------------------------------------------------------------------------------


def plot(plotDir: str = "../plots/", dryrun=False):
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

    columns = [
        "added_length",
        "deleted_length",
        "del_words",
        "comment_length",
        "ins_longest_inserted_word",
        "ins_longest_character_sequence",
        "ins_internal_link",
        "ins_external_link",
        "ins_avg_word_length",
        "del_avg_word_length",
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

    i = 0  # 0 - 5 seconds
    # partitionStatus(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 1 - 1 minute
    # distributionOfMainEdits(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 2 - 1 minute
    # distributionOfTalkEdits(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 3 - 30 seconds
    # numberOfPagesPerNamespace(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 4 - 1 minute
    # editsMainTalkNeither(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 5 - 5 minutes
    # numMainTalkEditsForBiggestEditors(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 6

    i = i + 1  # 7

    i = i + 1  # 8 - 20 minutes
    # distributionOfMainEditsUserBots(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 9 - 7 minutes
    # editsMainTalkNeitherUserBots(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 10 - 2 minutes
    # editTimesUserBots(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 11 - 4 minutes
    # distributionOfEditsPerNamespace(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 12 - 20 minutes
    # sentimentUserBotsBlockedIP(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 13 - 52 minutes
    # sentimentGroups(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 14 - 17 minutes
    # profanityAll(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 15 - 4 minutes
    # averageAll(cursor, i, plotDir, dataDir, dryrun, columns)

    i = i + 1  # 16 - 20 seconds
    # namespacesEditedByTopFiveHundred(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 17 - 18 minutes
    # internalExternalLinks(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 18 - 4 seconds
    # specialUsersPlot(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 19 - 37 minutes
    # averageAllSpecial(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 20 - 2 minutes
    # compositionOfUserIP(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 21 - 12 minutes
    # compositionOfUser(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 22 - 37 minutes
    # aggregations(cursor, i, plotDir, dataDir, dryrun, columns)

    i = i + 1  # 23 - 50 seconds
    # editBooleans(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 24 - 50 seconds
    # userBooleans(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 25 - 26 seconds
    # talkpageEditsOverTime(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 26 - 6 minutes
    # averageAllEpoch(cursor, i, plotDir, dataDir, dryrun, columns)

    i = i + 1  # 27 - 8 minutes
    # averageFeaturesOverTime(cursor, i, plotDir, dataDir, dryrun, columns)

    i = i + 1  # 28

    i = i + 1  # 29 - 12 minutes
    # namespacesEditedByUserGroups(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 30 - 7 minutes
    # talkpageEditsTimeAveraged(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 31 - 4 minutes
    # talkpageEditsOverTimeNoBots(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 32 - 11 minutes
    # averageBlockedLastEdits(cursor, i, plotDir, dataDir, dryrun, columns)

    i = i + 1  # 33 -

    i = i + 1  # 34 - 54 minutes
    # talkpageEditsTimeGroups(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 35 - 48 minutes
    # averageFeaturesOverTimeGroups(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 36 - 17 minutes
    # talkpageEditorsTimeGroups(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 37 - 36 minutes
    # compositionOfUserOverTime(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 38 - 20 minutes
    # timespanOfContributorEngagement(cursor, i, plotDir, dataDir, dryrun)

    i = i + 1  # 39 - 17 minutes
    # firstLastEditsGroups(cursor, i, plotDir, dataDir, dryrun)

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
        help="Don't use a database connection, takes 12 minutes to generate all plots",
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
