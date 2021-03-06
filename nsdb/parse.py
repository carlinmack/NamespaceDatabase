"""
This script allows the user to parse a dump from a database connection
and extract features to a database table.

This tool uses a MySQL database that is configured in the Database() module.
"""
import argparse
import os
import re
import subprocess
import sys
import traceback
from datetime import datetime
from sys import argv
from typing import List, Tuple

import mwreverts
import mwxml
import tqdm
from profanity import profanity

import Database


def multiprocess(
    partitionsDir: str, namespaces: List[int], queue, jobId: str, dryRun: bool = False
):
    """Wrapper around process to call parse in a multiprocessing pool"""
    while True:
        partitionName = queue.get()

        parseId = str(jobId) + "_" + str(partitionName)
        parse(partitionsDir, namespaces, parseId, dryRun, partitionName)

    print("EXIT", flush=True)


class fileCursor:
    testFile = "../test-output.txt"
    lastrowid = -1

    def __init__(self, partitionName):
        self.testFile = "../test-output-" + partitionName + ".txt"

    def execute(self, *args):
        parameters = tuple(map(lambda x: '"' + str(x) + '"', args[1]))
        output = args[0] % parameters
        output = " ".join(output.split())
        with open(self.testFile, "a+") as file:
            file.write(output + "\n")


def markAsNotFound(fileName):
    query = """update partition 
        set status = 'failed', error = 'Not found' 
        where file_name = %s;"""

    database, cursor = Database.connect()
    cursor.execute(query, (fileName,))
    cursor.close()
    database.close()


def getDump(partitionsDir: str, cursor=0, partitionName: str = ""):
    """Returns the next dump to be parsed from the database

    Parameters
    ----------
    cursor: MySQLCursor - cursor allowing CRUD actions on the DB connections

    Returns
    -------
    dump: class 'mwxml.iteration.dump.Dump' - dump file iterator
    fileName: str - fileName of dump
    """

    if cursor:
        ## Read dump from database
        query = "SELECT file_name FROM partition WHERE status = 'todo' LIMIT 1"
        cursor.execute(query)
        todofile = cursor.fetchone()

        if not todofile:
            ## no files to run, close database connections and finish
            return None, None

        fileName = todofile[0]
        path = partitionsDir + fileName

        if not os.path.exists(path):
            markAsNotFound(fileName)
            raise IOError("file " + path + " not found on disk")

        print("Parsing", path)
        dump = mwxml.Dump.from_file(open(path))

        ## Change status of dump
        currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = """UPDATE partition
            SET
                status = "running",
                start_time_1 = %s
            WHERE file_name = %s;"""
        cursor.execute(query, (currentTime, fileName))
    else:
        path = partitionsDir + partitionName
        dump = mwxml.Dump.from_file(open(path))
        fileName = partitionName

    return dump, fileName


def parseNonTargetNamespace(
    page, title: str, namespace: str, cursor, parallel: str = ""
):
    """Counts the number of edits each user makes and inserts them to the database.

        Parameters
        ----------
        page: mwtypes.Page
        title: str - Title of the page
        namespace: str - Namespace of the page
        cursor: MySQLCursor - cursor allowing CRUD actions on the DB connections
        parallel: str - id of process, hides progress bars if present
    """
    userDict = {}

    undidRevision = re.compile(r"^Undid revision (\d+) by.*?\|(.*?)\]")

    detector = mwreverts.Detector()

    pageEdits = 0

    editIdToUserId = {}

    for revision in tqdm.tqdm(
        page, desc=title, unit=" edits", smoothing=0, disable=parallel
    ):
        if not revision.user:
            continue

        pageEdits = pageEdits + 1

        # Check if not None as there is a user 0, Larry Sanger
        if revision.user.id is not None:
            userId = revision.user.id
            username = revision.user.text

            editIdToUserId[revision.id] = userId

            if not username in userDict:
                userDict[username] = [1, 0, userId]
            else:
                userDict[username][0] += 1

        else:
            ipAddress = revision.user.text

            if not ipAddress in userDict:
                userDict[ipAddress] = [1, 0, -1]
            else:
                userDict[ipAddress][0] += 1

        revertedUsers = checkReverted(
            detector, revision, cursor, undidRevision, False, editIdToUserId
        )

        if revertedUsers:
            for user in revertedUsers:
                # it's naive to assume that the user will already be in userDict as
                # they could've been renamed or vanished
                if "userId" in user:
                    userId = user["userId"]
                    username = user["user"]

                    if not username in userDict:
                        userDict[username] = [0, 1, userId]
                    else:
                        userDict[username][1] += 1
                else:
                    ipAddress = user["user"]

                    if not ipAddress in userDict:
                        userDict[ipAddress] = [0, 1, -1]
                    else:
                        userDict[ipAddress][1] += 1

    for key, value in userDict.items():
        editCount = value[0]
        revertedCount = value[1]
        userId = value[2]

        if userId > -1:
            query = """INSERT INTO user 
            (user_id, username, namespaces, number_of_edits, reverted_edits)
            VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY
            UPDATE
                namespaces = CONCAT_WS(',', namespaces, %s),
                number_of_edits = number_of_edits + %s,
                reverted_edits = reverted_edits + %s;"""

            cursor.execute(
                query,
                (
                    userId,
                    key,
                    namespace,
                    editCount,
                    revertedCount,
                    namespace,
                    editCount,
                    revertedCount,
                ),
            )
        else:
            query = """INSERT INTO user 
            (ip_address, namespaces, number_of_edits, reverted_edits)
            VALUES (%s, %s, %s, %s) ON DUPLICATE KEY
            UPDATE
                namespaces = CONCAT_WS(',', namespaces, %s),
                number_of_edits = number_of_edits + %s,
                reverted_edits = reverted_edits + %s;"""

            cursor.execute(
                query,
                (
                    key,
                    namespace,
                    editCount,
                    revertedCount,
                    namespace,
                    editCount,
                    revertedCount,
                ),
            )

    query = """UPDATE page
                SET number_of_edits = %s 
                WHERE title=%s
                AND namespace = %s;"""
    cursor.execute(query, (pageEdits, title, namespace))


def parseTargetNamespace(
    page, title: str, namespace: str, cursor, parallel: str, partitionsDir
):
    """Extracts features from each revision of a page into a database

    Ignores edits that have been deleted like:
        https://en.wikipedia.org/w/index.php?oldid=614217720

    Parameters
    ----------
    page: mwtypes.Page
    title: str - Title of the page
    namespace: str - Namespace of the page
    cursor: MySQLCursor - cursor allowing CRUD actions on the DB connections
    parallel: str - id name of parallel slurm process, present if called from parallel,
      hides progress bars
    """
    blankText = re.compile(r"^\s+$")
    internalLink = re.compile(r"\[\[.*?\]\]")
    externalLink = re.compile(r"[^\[]\[[^\[].*?[^\]]\][^\]]")
    undidRevision = re.compile(r"^Undid revision (\d+) by.*?\|(.*?)\]")

    oldText = ""

    detector = mwreverts.Detector()

    pageEdits = 0

    editIdToUserId = {}

    ## Extract page features from each revision
    for revision in tqdm.tqdm(
        page, desc=title, unit=" edits", smoothing=0, disable=parallel
    ):
        if not revision.user:
            continue

        pageEdits = pageEdits + 1

        # Check if not None as there is a user 0, Larry Sanger
        if revision.user.id is not None:
            userId = revision.user.id
            username = revision.user.text

            editIdToUserId[revision.id] = userId

            query = """INSERT INTO user (user_id, username, namespaces, talkpage_number_of_edits)
                VALUES (%s, %s, %s, 1) ON DUPLICATE KEY
                UPDATE
                    namespaces = CONCAT_WS(',', namespaces, %s),
                    talkpage_number_of_edits = talkpage_number_of_edits + 1;"""
            cursor.execute(query, (userId, username, namespace, namespace))
        else:
            ipAddress = revision.user.text

            query = """INSERT INTO user (ip_address, namespaces, talkpage_number_of_edits)
                VALUES (%s, %s, 1) ON DUPLICATE KEY
                UPDATE
                    namespaces = CONCAT_WS(',', namespaces, %s),
                    talkpage_number_of_edits = talkpage_number_of_edits + 1;"""
            cursor.execute(query, (ipAddress, namespace, namespace))

        userTableId = cursor.lastrowid

        editDate = datetime.strptime(str(revision.timestamp), "%Y-%m-%dT%H:%M:%SZ")

        editId = revision.id
        pageId = revision.page.id

        # if revision has text and the text isn't whitespace
        if revision.text and not blankText.search(revision.text):
            blanking = False
            (added, deleted) = getDiff(oldText, revision.text, parallel, partitionsDir)
            blankAddition = blankText.search(added)

            addedLength = len(added)
            deletedLength = len(deleted)

            if added and not blankAddition:
                insInternalLink = len(internalLink.findall(added))
                insExternalLink = len(externalLink.findall(added))

                insLongestInsertedWord = longestWord(added)
                insLongestCharacterSequence = longestCharSequence(added)

                insCapitalization = ratioCapitals(added)
                insDigits = ratioDigits(added)
                insSpecialChars = ratioSpecial(added)
                insWhitespace = ratioWhitespace(added)

                insPronouns = ratioPronouns(added)
                insVulgarity = containsVulgarity(added)
            else:
                insInternalLink = 0
                insExternalLink = 0

                insLongestInsertedWord = 0
                insLongestCharacterSequence = 0

                insCapitalization = 0
                insDigits = 0
                insSpecialChars = 0
                if blankAddition:
                    insWhitespace = 1
                else:
                    insWhitespace = 0

                insPronouns = 0
                insVulgarity = 0

            delWords = len(deleted.split(" "))

            added = added[:65535]
            deleted = deleted[:65535]

            oldText = revision.text
        else:
            blanking = True

            added = "NULL"
            deleted = "NULL"

            addedLength = 0
            deletedLength = 0
            delWords = 0

            insInternalLink = "NULL"
            insExternalLink = "NULL"
            insLongestInsertedWord = "NULL"
            insLongestCharacterSequence = "NULL"
            insCapitalization = "NULL"
            insDigits = "NULL"
            insSpecialChars = "NULL"
            insWhitespace = "NULL"
            insPronouns = "NULL"
            insVulgarity = "NULL"

        if revision.comment:
            comment = revision.comment.lower()
            commentCopyedit = "copyedit" in comment
            commentPersonalLife = "personal life" in comment
            commentLength = len(comment)
            commentSpecialChars = ratioSpecial(comment)
        else:
            commentCopyedit = "NULL"
            commentPersonalLife = "NULL"
            commentLength = "NULL"
            commentSpecialChars = "NULL"

        checkReverted(detector, revision, cursor, undidRevision, True, editIdToUserId)

        query = """
        INSERT INTO edit (added, deleted, added_length, deleted_length, edit_date, 
            edit_id, page_id, ins_internal_link, ins_external_link, 
            ins_longest_inserted_word, ins_longest_character_sequence, 
            ins_pronouns, ins_capitalization, ins_digits, ins_special_chars, 
            ins_vulgarity, ins_whitespace, del_words, comment_personal_life, 
            comment_copyedit, comment_length, comment_special_chars, blanking, 
            user_table_id
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, 
            %s, %s, %s, %s, 
            %s, %s, %s, %s, 
            %s, %s, %s, %s,
            %s
        );
        """

        editTuple = (
            added,
            deleted,
            addedLength,
            deletedLength,
            editDate,
            editId,
            pageId,
            insInternalLink,
            insExternalLink,
            insLongestInsertedWord,
            insLongestCharacterSequence,
            insPronouns,
            insCapitalization,
            insDigits,
            insSpecialChars,
            insVulgarity,
            insWhitespace,
            delWords,
            commentPersonalLife,
            commentCopyedit,
            commentLength,
            commentSpecialChars,
            blanking,
            userTableId,
        )

        ## Insert page features into database
        cursor.execute(query, editTuple)

    query = """UPDATE page
                SET number_of_edits = %s 
                WHERE title=%s
                AND namespace = %s;"""
    cursor.execute(query, (pageEdits, title, namespace))


def getDiff(old: str, new: str, parallel: str, partitionsDir) -> Tuple[str, str]:
    """Returns the diff between two edits using wdiff

    Parameters
    ----------
    old : str - old revision
    new : str - new revision

    Returns
    -------
    added: str - all the text that is exclusively in the new revision
    deleted: str - all the text that is exclusively in the old revision
    parallel: str - id of the parallel process, 0 if not
    """
    oldrevision = "revision/old" + parallel + ".txt"
    newrevision = "revision/new" + parallel + ".txt"

    with open(newrevision, "w") as newFile:
        newFile.writelines(new)

    lineSeperators = re.compile(
        r"======================================================================"
    )

    added = (
        subprocess.run(["wdiff", "-13", oldrevision, newrevision], capture_output=True)
        .stdout.decode("utf-8")
        .strip()
    )

    added = lineSeperators.sub("", added)

    deleted = (
        subprocess.run(["wdiff", "-23", oldrevision, newrevision], capture_output=True)
        .stdout.decode("utf-8")
        .strip()
    )

    deleted = lineSeperators.sub("", deleted)

    os.rename(newrevision, oldrevision)
    open(partitionsDir + "revision/new" + parallel + ".txt", "w").close()

    return added, deleted


def checkReverted(
    detector, revision, cursor, undidRevision, target: bool, editIdToUserId
):
    """Inserts reverted edits into the database for target namespace, otherwise 
    returns the user that was reverted"""
    reverted = detector.process(
        revision.sha1,
        [
            {
                "revisionId": revision.id,
                "user": revision.user.text,
                "userId": revision.user.id,
            }
        ],
    )

    # check with mwreverts first as it is a source of truth, comments may lie
    # however check the comment anyway as they may make additional edits that
    # will bypass mwreverts
    if reverted:
        users = []
        # usually performs 1 loop, not really O(n^2)
        for reversion in reverted.reverteds:
            for revert in reversion:
                revisionId = revert["revisionId"]
                user = revert["user"]
                if revert["userId"] is None:
                    userId = -1
                else:
                    userId = revert["userId"]

                if target:
                    query = """UPDATE edit
                        SET reverted = True
                        WHERE edit_id = %s;"""
                    cursor.execute(query, (revisionId,))

                    if userId != -1:
                        query = """
                        INSERT INTO user (user_id, username, talkpage_reverted_edits)
                            VALUES (%s, %s, 1) ON DUPLICATE KEY
                            UPDATE
                                talkpage_reverted_edits = talkpage_reverted_edits + 1;"""
                        cursor.execute(query, (userId, user))
                    else:
                        query = """INSERT INTO user (ip_address, talkpage_reverted_edits)
                            VALUES (%s, 1) ON DUPLICATE KEY
                            UPDATE
                                talkpage_reverted_edits = talkpage_reverted_edits + 1;"""
                        cursor.execute(query, (user,))

                else:
                    user = {"user": user, "userId": userId}
                    users.append(user)
        return users
    elif revision.comment:
        reverted = undidRevision.match(revision.comment)

        if reverted:
            revisionId = int(reverted.groups(0)[0])
            user = reverted.groups(0)[1]

            if revisionId in editIdToUserId:
                userId = editIdToUserId[revisionId]
            else:
                userId = -1

            if target:
                query = """UPDATE edit
                        SET reverted = True
                        WHERE edit_id = %s;"""
                cursor.execute(query, (revisionId,))

                if userId != -1:
                    query = """INSERT INTO user
                        (user_id, username, talkpage_reverted_edits)
                        VALUES (%s, %s, 1) ON DUPLICATE KEY
                        UPDATE
                            talkpage_reverted_edits = talkpage_reverted_edits + 1;"""
                    cursor.execute(query, (userId, user))
                else:
                    query = """INSERT INTO user
                        (ip_address, talkpage_reverted_edits)
                        VALUES (%s, 1) ON DUPLICATE KEY
                        UPDATE
                            talkpage_reverted_edits = talkpage_reverted_edits + 1;"""
                    cursor.execute(query, (user,))

            else:
                return [{"user": user, "userId": userId}]


##  FUNCTIONS TO EXTRACT FEATURES
def cleanString(string: str) -> str:
    """Removes special characters and unnecessary whitespace from text"""
    removeSymbols = re.sub(r'[$-/:?{}~!"^_`\[\]]', " ", string)
    removeDoubleSpaces = re.sub(r"\s\s+", " ", removeSymbols)
    return removeDoubleSpaces


def longestWord(string: str) -> int:
    """Returns the length of the longest word in text"""
    string = cleanString(string)
    arr = string.split()
    if len(arr) > 0:
        maxLength = max(arr, key=len)
        # print(longestWord)
        return len(maxLength)
    else:
        return 0


def longestCharSequence(string: str) -> int:
    """Returns the length of the longest repeated character sequence in text"""
    string = cleanString(string)
    # print(string)
    previous = ""
    current = 0
    maxLength = 0
    temp = []

    for char in string:
        if char == previous:
            current += 1
            temp.append(char)
        else:
            if current > maxLength:
                maxLength = current
            current = 1
            previous = char

    return maxLength


def ratioCapitals(string: str) -> int:
    """Returns the ratio of uppercase to lowercase characters in text"""
    uppercase = 0
    lowercase = 1  # to avoid infinity

    # print(string)

    for char in string:
        if ord(char) >= 65 and ord(char) <= 90:
            uppercase = uppercase + 1
        elif ord(char) >= 97 and ord(char) <= 122:
            lowercase = lowercase + 1

    return uppercase / lowercase


def ratioDigits(string: str) -> int:
    """Returns the ratio of digits to all characters in text"""
    digits = 0

    for char in string:
        if char.isdigit():
            digits = digits + 1

    return digits / len(string)


def ratioSpecial(string: str) -> int:
    """Returns the ratio of special characters to all characters in text"""
    return len(re.findall(r'[!-/:-?{-~!"^_`\[\]]', string)) / len(string)


def ratioWhitespace(string: str) -> int:
    """Returns the ratio of whitespace to all characters in text"""
    return len(re.findall(r"\s", string)) / len(string)


def ratioPronouns(string: str) -> int:
    """Returns the ratio of personal pronouns to all words in text"""
    return len(re.findall(r"(\sI\s|\sme\s|\smy\s|\smine\s|\smyself\s)", string)) / len(
        string.split(" ")
    )


def containsVulgarity(string: str) -> bool:
    """Returns whether text contains profanity based on a simple wordlist approach"""
    return profanity.contains_profanity(string)


def parse(
    partitionName: str = "",
    partitionsDir: str = "../partitions/",
    namespaces: List[int] = [1],
    parallel: str = "",
    dryRun: bool = False,
):
    """Selects the next dump from the database, extracts the features and
    imports them into several database tables.

    Detailed extraction of features is performed for namespaces of interest.
    Pages that are not in the namespace of choice will instead only have the edits
    counted per user.

    Parameters
    ----------
    partitionsDir: str - where the partitions are stored
    namespaces : list[int] - Wikipedia namespaces of interest.
    parallel: str - whether to parse with multiple cores
    """
    if not dryRun:
        database, cursor = Database.connect()
    else:
        cursor = fileCursor(partitionName)

    if not os.path.exists(partitionsDir + "revision"):
        os.mkdir(partitionsDir + "revision")

    open(partitionsDir + "revision/old" + parallel + ".txt", "w").close()
    open(partitionsDir + "revision/new" + parallel + ".txt", "w").close()

    try:
        if not dryRun:
            dump, fileName = getDump(partitionsDir, cursor=cursor)

            if dump is None:
                cursor.close()
                database.close()
                return
        else:
            dump, fileName = getDump(partitionsDir, partitionName=partitionName)

        # for development, disable namespace check
        # fileName = "../test.xml"
        # dump = mwxml.Dump.from_page_xml(open(fileName))

        for page in dump:
            open(partitionsDir + "revision/old" + parallel + ".txt", "w").close()
            open(partitionsDir + "revision/new" + parallel + ".txt", "w").close()

            namespace = page.namespace
            title = page.title
            query = """INSERT IGNORE INTO page (page_id, namespace, title, file_name)
                VALUES (%s, %s, %s, %s)"""
            cursor.execute(query, (page.id, namespace, title, fileName))

            if namespace not in namespaces:
                parseNonTargetNamespace(page, title, str(namespace), cursor, parallel)

                continue

            parseTargetNamespace(
                page, title, str(namespace), cursor, parallel, partitionsDir
            )

        ## Change status of dump
        currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = """UPDATE partition
            SET status = "done", end_time_1 = %s 
            WHERE file_name = %s;"""
        cursor.execute(query, (currentTime, fileName))

    except OSError:
        err = str(sys.exc_info()[1])

        if not parallel:
            print(err)

        raise
    except Exception as e:
        err = str(sys.exc_info()[1])

        currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not parallel:
            print(err)

        if not os.path.exists("error"):
            os.mkdir("error")

        with open("error/" + fileName, "a") as file:
            file.write(currentTime + "\n\n")
            file.write(str(e) + "\n\n")
            file.write(traceback.format_exc() + "\n\n")

        query = """UPDATE partition
            SET
                status = "failed",
                end_time_1 = %s,
                error = %s
            WHERE
                file_name = %s;"""
        cursor.execute(query, (currentTime, err, fileName))

        raise

    os.remove(partitionsDir + "revision/old" + parallel + ".txt")
    os.remove(partitionsDir + "revision/new" + parallel + ".txt")

    if not dryRun:
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
        "-p",
        "--partitionName",
        help="Set when called from the slurm script [default: 0]",
        default="",
        type=str,
    )

    parser.add_argument(
        "-d",
        "--partitionsDir",
        help="Where the partitions are stored [default: ../partitions/]",
        default="../partitions/",
        type=str,
    )

    parser.add_argument(
        "-n",
        "--namespaces",
        help="Namespaces of interest [default: 1]",
        default=[1],
        type=int,
        nargs="+",
    )

    parser.add_argument(
        "-i",
        "--parallelID",
        help="Set when called from the slurm script [default: '']",
        default="",
        type=str,
    )

    return parser


if __name__ == "__main__":

    argParser = defineArgParser()
    clArgs = argParser.parse_args()

    parse(
        partitionName=clArgs.partitionName,
        partitionsDir=clArgs.partitionsDir,
        namespaces=clArgs.namespaces,
        parallel=clArgs.parallel,
        dryRun=clArgs.dryRun,
    )
