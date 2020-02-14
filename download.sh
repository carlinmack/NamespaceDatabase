#!/bin/bash

mirror=$1
wiki=$2
dump=$3

url="${1}${2}${3}"
file="index.html"

wget -O $file $url

grep -oP '(?<=href=").*pages-meta-history.*7z(?=")' index.html > dumps.txt

# while read line; do 
#         wget "$mirror$line"; 
#     done <dumps.txt

read -r line<dumps.txt
wget -P archives/ "$mirror$line"