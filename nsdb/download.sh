#!/bin/bash

mirror=$1
wiki=$2
dump=$3

url="$mirror$wiki$dump"
file="../index.html"

wget -O $file "$url"

grep -oP '(?<=href=").*pages-meta-history.*7z(?=")' $file > ../dumps.txt

rm $file
# while read line; do 
#         wget "$mirror$line"; 
#     done <dumps.txt

# read -r line<dumps.txt
# wget -P archives/ "$mirror$line"

# change to write file names to database