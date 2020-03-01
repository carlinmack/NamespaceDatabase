import datetime
import re

import mwxml
import mysql.connector as sql
from mysql.connector import errorcode

##	IMPORT FILE
# test_dump = "enwiki-20200101-pages-meta-history1.xml-p10p1036"
# dump = mwxml.Dump.from_file(open(test_dump))

test_dump = "test.xml"
dump = mwxml.Dump.from_page_xml(open(test_dump))

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
    for page in dump:
        query = "INSERT IGNORE INTO page (page_id, title) VALUES (%s, %s)"
        cursor.execute(query, (page.id, page.title))

        database.commit()
        for revision in page:

            ## Page Features
            diff = revision.text
            query = """
            INSERT INTO edit (
                namespace, user_id, ip_address, edit_date, edit_id, page_id,
                ins_internal_link, ins_external_link, ins_longest_inserted_word, 
                ins_longest_character_sequence, ins_capitalization, ins_digits, 
                ins_special_chars, comment_personal_life, comment_copyedit, 
                comment_length, comment_special_chars
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s
            );
            """

            namespace = revision.page.namespace

            if revision.user.id:
                user_id = revision.user.id
                ip_address = "NULL"
            else:
                user_id = "NULL"
                ip_address = revision.user.text

            edit_date = datetime.datetime.strptime(
                str(revision.timestamp), "%Y-%m-%dT%H:%M:%SZ"
            )

            edit_id = revision.id
            page_id = revision.page.id

            ins_internal_link = len(re.findall("\[\[.*?\]\]", diff))
            ins_external_link = len(re.findall("[^\[]\[[^\[].*?[^\]]\][^\]]", diff))

            ins_longest_inserted_word = longestWord(diff)
            ins_longest_character_sequence = longestCharSequence(diff)

            ins_capitalization = ratioCapitals(diff)
            ins_digits = ratioDigits(diff)
            ins_special_chars = ratioSpecial(diff)

            if revision.comment:
                comment = revision.comment.lower()
                comment_copyedit = "copyedit" in comment
                comment_personal_life = "personal life" in comment
                comment_length = len(comment)
                comment_special_chars = ratioSpecial(comment)
            else:
                comment_copyedit = False
                comment_personal_life = False
                comment_length = -1
                comment_special_chars = -1

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
            )

            ## Insert page features into database
            cursor.execute(query, editTuple)
            database.commit()

    cursor.close()
    database.close()
