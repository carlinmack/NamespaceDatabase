# Outputs in the format
# Namespace
# User(id)
# Date
# Page (id)
# --Added-----
# --Deleted---
# --Blanking--
# Ins Internal Link
# Ins External Link
# Longest Inserted Word
# Ins Longest Character Sequence
# Ins Capitalization
# Ins Digits
# Ins Special Chars
# Copyedit
# Personal Life
# Comment Length
# Comment Special Chars
#
# User name

import mwxml
import re

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
for page in dump:
    for revision in page:
        diff = revision.text
        print(revision.page.namespace)
        print(revision.user.id)
        print(revision.timestamp)
        print(revision.id)
        # print(diff)
        # print(revision.comment)
        print(len(re.findall("\[\[.*?\]\]", diff)))
        print(len(re.findall("[^\[]\[[^\[].*?[^\]]\][^\]]", diff)))
        print(longestWord(diff))
        print(longestCharSequence(diff))
        print(ratioCapitals(diff))
        print(ratioDigits(diff))
        print(ratioSpecial(diff))
        if revision.comment:
            comment = revision.comment.lower()
            print("copyedit" in comment)
            print("personal life" in comment)
            print(len(comment))
            print(ratioSpecial(comment))
        else:
            print(False)
            print(False)
            print(-1)
            print(-1)
        print(" ")
        print(revision.user.text)
        print(" ")
        print(" ")
