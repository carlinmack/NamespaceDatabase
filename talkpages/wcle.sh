#!/bin/bash

# wcle – word count line estimate
# Fast line-count estimate for huge files
# By Nathan Sheffield, 2014

file=$1

nsample=100000

headbytes=$(head -q -n $nsample "$file" | wc -c)

filesize=$(ls -sH --block-size=1 "$file" | cut -f1 -d" ")

echo $((filesize * nsample / (headbytes) ))