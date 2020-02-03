#!/bin/bash

wiki="enwiki/"
dump="20200101/"

# fastestMirror=$(python3 mirrors.py)
fastestMirror="http://dumps.wikimedia.freemirror.org/"
echo $fastestMirror
# ./download.sh $fastestMirror $wiki $dump

# ./extract.sh 
python3 parse.py
# python3 removeWikitext.py
# python3 selectFeatures.py
# python3 mysql.py
