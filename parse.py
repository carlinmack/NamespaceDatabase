import datetime
import re

import mwxml
import mysql.connector as sql
from mysql.connector import errorcode
import tqdm


##  FUNCTIONS TO EXTRACT FEATURES
def cleanString(string):
    removeSymbols = re.sub(r'[$-/:-?{-~!"^_`\[\]]', " ", string)
    removeDoubleSpaces = re.sub(r"\s\s+", " ", removeSymbols)
    return removeDoubleSpaces


def longestWord(string):
    string = cleanString(string)
    arr = string.split()
    longestWord = max(arr, key=len)
    # print(longestWord)
    return len(longestWord)


def longestCharSequence(string):
    string = cleanString(string)
    # print(string)
    previous = ""
    current = 0
    max = 0
    temp = []

    for char in string:
        if char == previous:
            current += 1
            temp.append(char)
        else:
            if current > max:
                max = current
            current = 1
            previous = char

    return max


def ratioCapitals(string):
    uppercase = 0
    lowercase = 1  # to avoid infinity

    # print(string)

    for char in string:
        if ord(char) >= 65 and ord(char) <= 90:
            uppercase = uppercase + 1
        elif ord(char) >= 97 and ord(char) <= 122:
            lowercase = lowercase + 1

    return uppercase / lowercase


def ratioDigits(string):
    digits = 0

    # print(string)

    for char in string:
        if char.isdigit():
            digits = digits + 1

    return digits / len(string)


def ratioSpecial(string):
    return len(re.findall(r'[!-/:-?{-~!"^_`\[\]]', string)) / len(string)


##	PRINT FEATURES FOR EVERY PAGE

try:
    database = sql.connect(
        host="wikiactors.cs.virginia.edu",
        database="wikiactors",
        username="wikiactors",
        option_files="private.cnf",
        option_groups="wikiactors",
    )

    cursor = database.cursor()

except sql.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    ## Read dump from database
    query = "SELECT file_name FROM partition WHERE status = 'todo' LIMIT 1"
    cursor.execute(query)
    filename = cursor.fetchone()[0]
    path = "partitions/" + filename
    dump = mwxml.Dump.from_page_xml(open(path))

    ## Change status of dump

    ## Parse
    for page in dump:
        query = "INSERT IGNORE INTO page (page_id, title) VALUES (%s, %s)"
        cursor.execute(query, (page.id, page.title))

        database.commit()
        for revision in tqdm.tqdm(page):
            ## Page Features
            namespace = revision.page.namespace

            if revision.user:
                if revision.user.id:
                    user_id = revision.user.id
                    ip_address = "NULL"
                else:
                    user_id = "NULL"
                    ip_address = revision.user.text
            else:
                print(revision)
                user_id = "NULL"
                ip_address = "NULL"

            edit_date = datetime.datetime.strptime(
                str(revision.timestamp), "%Y-%m-%dT%H:%M:%SZ"
            )

            edit_id = revision.id
            page_id = revision.page.id

            if revision.text:
                blanking = False
                diff = revision.text

                ins_internal_link = len(re.findall("\[\[.*?\]\]", diff))
                ins_external_link = len(re.findall("[^\[]\[[^\[].*?[^\]]\][^\]]", diff))

                ins_longest_inserted_word = longestWord(diff)
                ins_longest_character_sequence = longestCharSequence(diff)

                ins_capitalization = ratioCapitals(diff)
                ins_digits = ratioDigits(diff)
                ins_special_chars = ratioSpecial(diff)
            else:
                blanking = True

                ins_internal_link = "NULL"
                ins_external_link = "NULL"
                ins_longest_inserted_word = "NULL"
                ins_longest_character_sequence = "NULL"
                ins_capitalization = "NULL"
                ins_digits = "NULL"
                ins_special_chars = "NULL"

            if revision.comment:
                comment = revision.comment.lower()
                comment_copyedit = "copyedit" in comment
                comment_personal_life = "personal life" in comment
                comment_length = len(comment)
                comment_special_chars = ratioSpecial(comment)
            else:
                comment_copyedit = "NULL"
                comment_personal_life = "NULL"
                comment_length = "NULL"
                comment_special_chars = "NULL"

            query = """
            INSERT INTO edit (
                namespace, user_id, ip_address, edit_date, edit_id, page_id,
                ins_internal_link, ins_external_link, ins_longest_inserted_word, 
                ins_longest_character_sequence, ins_capitalization, ins_digits, 
                ins_special_chars, comment_personal_life, comment_copyedit, 
                comment_length, comment_special_chars, blanking
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s
            );
            """

            editTuple = (
                namespace,
                user_id,
                ip_address,
                edit_date,
                edit_id,
                page_id,
                ins_internal_link,
                ins_external_link,
                ins_longest_inserted_word,
                ins_longest_character_sequence,
                ins_capitalization,
                ins_digits,
                ins_special_chars,
                comment_personal_life,
                comment_copyedit,
                comment_length,
                comment_special_chars,
                blanking,
            )

            ## Insert page features into database
            cursor.execute(query, editTuple)
            database.commit()

            # oldrevision = revision

    cursor.close()
    database.close()
