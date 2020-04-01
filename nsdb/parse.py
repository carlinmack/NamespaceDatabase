"""
This script allows the user to parse a dump from a database connection
and extract features to a database table.

This tool uses a MySQL database that is configured in the Database() module.
"""
import os
import re
import subprocess
import sys
import traceback
from datetime import datetime
import time
from typing import Tuple

import mwreverts
import mwxml
import tqdm
from profanity import profanity

import Database

from multiprocessing import Queue


def multiprocess(partitionsDir, namespaces, queue, id):
    """Wrapper around process to call parse correctly"""
    while True:
        i = queue.get()

        delay = int(i[-1:])
        time.sleep(delay / 3)

        id = str(id) + "_" + str(i)
        parse(partitionsDir, namespaces, id)

        time.sleep(10)


def getDump(partitionsDir, cursor):
    """Returns the next dump to be parsed from the database

    Parameters
    ----------
    cursor: MySQLCursor - cursor allowing CRUD actions on the DB connections

    Returns
    -------
    dump: class 'mwxml.iteration.dump.Dump' - dump file iterator
    filename: str - filename of dump
    """
    ## Read dump from database
    query = "SELECT file_name FROM partition WHERE status = 'todo' LIMIT 1"
    cursor.execute(query)
    todofile = cursor.fetchone()

    if not todofile:
        ## no files to run, close database connections and finish
        return None, None

    filename = todofile[0]
    path = partitionsDir + filename

    if not os.path.exists(path):
        raise IOError("file not found on disk")

    print(path)
    dump = mwxml.Dump.from_file(open(path))

    ## Change status of dump
    currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = """UPDATE partition
        SET
            status = "running",
            start_time_1 = %s
        WHERE file_name = %s;"""
    cursor.execute(query, (currenttime, filename))

    return dump, filename


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

    for revision in tqdm.tqdm(
        page, desc=title, unit=" edits", smoothing=0, disable=parallel
    ):
        if not revision.user:
            continue

        # Check if not None as there is a user 0, Larry Sanger
        if revision.user.id is not None:
            userId = revision.user.id
            username = revision.user.text

            if not username in userDict:
                userDict[username] = [1, userId]
            else:
                userDict[username][0] += 1

        else:
            ipAddress = revision.user.text

            if not ipAddress in userDict:
                userDict[ipAddress] = [1, -1]
            else:
                userDict[ipAddress][0] += 1

    for key, value in userDict.items():
        editCount = value[0]
        userId = value[1]

        if userId > -1:
            query = """INSERT INTO user (user_id, username, namespaces, number_of_edits)
            VALUES (%s, %s, %s, %s) ON DUPLICATE KEY
            UPDATE
                namespaces = CONCAT_WS(',', namespaces, %s),
                number_of_edits = number_of_edits + %s;"""

            cursor.execute(
                query, (userId, key, namespace, editCount, namespace, editCount),
            )
        else:
            query = """INSERT INTO user (ip_address, namespaces, number_of_edits)
            VALUES (%s, %s, %s) ON DUPLICATE KEY
            UPDATE
                namespaces = CONCAT_WS(',', namespaces, %s),
                number_of_edits = number_of_edits + %s;"""

            cursor.execute(query, (key, namespace, editCount, namespace, editCount))


def parseTargetNamespace(page, title: str, namespace: str, cursor, parallel: str):
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

    ## Extract page features from each revision
    for revision in tqdm.tqdm(
        page, desc=title, unit=" edits", smoothing=0, disable=parallel
    ):
        if not revision.user:
            continue

        # Check if not None as there is a user 0, Larry Sanger
        if revision.user.id is not None:
            userId = revision.user.id
            username = revision.user.text

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
            (added, deleted) = getDiff(oldText, revision.text, parallel)
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

            insInternalLink = "NULL"
            insExternalLink = "NULL"
            insLongestInsertedWord = "NULL"
            insLongestCharacterSequence = "NULL"
            insCapitalization = "NULL"
            insDigits = "NULL"
            insSpecialChars = "NULL"

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

        reverted = detector.process(
            revision.sha1, [{"revisionId": editId, "user": revision.user.text}]
        )

        # check with mwreverts first as it is a source of truth, comments may lie
        # however check the comment anyway as they may make additional edits that
        # will bypass mwreverts
        if reverted:
            # usually performs 1 loop, not really O(n^2)
            for reversion in reverted.reverteds:
                for revert in reversion:
                    revisionId = revert["revisionId"]
                    user = revert["user"]

                    query = """UPDATE edit
                        SET reverted = True
                        WHERE edit_id = %s;"""
                    cursor.execute(query, (revisionId,))

                    query = """UPDATE user
                        SET reverted_edits = reverted_edits + 1
                        WHERE username = %s or ip_address = %s;"""
                    cursor.execute(query, (user, user))

        elif revision.comment:
            reverted = undidRevision.match(revision.comment)

            if reverted:
                revisionId = reverted.groups(0)[0]
                user = reverted.groups(0)[1]

                query = """UPDATE edit
                    SET reverted = True
                    WHERE edit_id = %s;"""
                cursor.execute(query, (revisionId,))

                query = """UPDATE user
                    SET reverted_edits = reverted_edits + 1
                    WHERE username = %s or ip_address = %s;"""
                cursor.execute(query, (user, user))

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


##  FUNCTIONS TO EXTRACT FEATURES
def cleanString(string: str) -> str:
    """Removes special characters and unnecessary whitespace from text"""
    removeSymbols = re.sub(r'[$-/:-?{-~!"^_`\[\]]', " ", string)
    removeDoubleSpaces = re.sub(r"\s\s+", " ", removeSymbols)
    return removeDoubleSpaces


def longestWord(string: str) -> int:
    """Returns the length of the longest word in text"""
    string = cleanString(string)
    arr = string.split()
    if len(arr) > 0:
        longestWord = max(arr, key=len)
        # print(longestWord)
        return len(longestWord)
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


def getDiff(old: str, new: str, parallel: str) -> Tuple[str, str]:
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
    open("revision/new" + parallel + ".txt", "w").close()

    return added, deleted


def parse(partitionsDir:str="../partitions/", namespaces=[1], parallel=""):
    """Selects the next dump from the database, extracts the features and
    imports them into several database tables.

    Detailed extraction of features is performed for namespaces of interest.
    Pages that are not in the namespace of choice will instead only have the edits
    counted per user.

    Parameters
    ----------
    namespaces : list[int] - Wikipedia namespaces of interest.
    parallel: str - whether to parse with multiple cores
    """
    database, cursor = Database.connect()

    if not os.path.exists("revision"):
        os.mkdir("revision")

    open("revision/old" + parallel + ".txt", "w").close()
    open("revision/new" + parallel + ".txt", "w").close()

    try:
        dump, filename = getDump(partitionsDir, cursor)

        if dump is None:
            cursor.close()
            database.close()
            return

        # for development, disable namespace check
        # filename = "../test.xml"
        # dump = mwxml.Dump.from_page_xml(open(filename))

        for page in dump:
            open("revision/old" + parallel + ".txt", "w").close()
            open("revision/new" + parallel + ".txt", "w").close()

            namespace = page.namespace
            title = page.title
            query = """INSERT IGNORE INTO page (page_id, namespace, title, file_name)
                VALUES (%s, %s, %s, %s)"""
            cursor.execute(query, (page.id, namespace, title, filename))

            if namespace not in namespaces:
                parseNonTargetNamespace(page, title, str(namespace), cursor, parallel)

                continue

            parseTargetNamespace(page, title, str(namespace), cursor, parallel)

        ## Change status of dump
        currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = """UPDATE partition
            SET status = "done", end_time_1 = %s 
            WHERE file_name = %s;"""
        cursor.execute(query, (currenttime, filename))

    except OSError as e:
        err = str(sys.exc_info()[1])

        if not parallel:
            print(err)

        raise
    except Exception as e:
        err = str(sys.exc_info()[1])

        currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not parallel:
            print(err)

        if not os.path.exists("error"):
            os.mkdir("error")

        with open("error/" + filename, "a") as file:
            file.write(currenttime + "\n\n")
            file.write(str(e) + "\n\n")
            file.write(traceback.format_exc() + "\n\n")

        query = """UPDATE partition
            SET
                status = "failed",
                end_time_1 = %s,
                error = %s
            WHERE
                file_name = %s;"""
        cursor.execute(query, (currenttime, err, filename))

        raise

    os.remove("revision/old" + parallel + ".txt")
    os.remove("revision/new" + parallel + ".txt")

    cursor.close()
    database.close()


if __name__ == "__main__":
    parse()
