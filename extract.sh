#!/bin/bash

start=`date +%s`

for i in *.7z; do
    tick=`date +%s`;
    7z e "$i"; 
    tock=`date +%s`;

    runtime=$((end-start));
    echo "$i $runtime";
done
end=`date +%s`

runtime=$((end-start))
echo $runtime


start=`date +%s`

for i in *.bz2; do
    tick=`date +%s`;
    7z e "$i"; 
    tock=`date +%s`;

    runtime=$((end-start));
    echo "$i $runtime";
done

end=`date +%s`

runtime=$((end-start))
echo $runtime
