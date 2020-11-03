#!/bin/sh

echo 'Serching LOG Files...'
LOG_PATH="/var/log"
FILES=`find "$LOG_PATH" -name '*.log' -size +1024M -exec ls -lh {} \; | sort -k 5 -n -r | awk '{print $9}'`
for file in $FILES
do
    echo "" > $file
    echo 'COVER LOG:'$file
done


echo 'DONE !'
