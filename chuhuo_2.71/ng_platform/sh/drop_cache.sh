#!/bin/sh


while true; do

free_mem=`free -m | awk 'NR == 2 {printf $4}'`
cache_mem=`free -m | awk 'NR == 2 {printf $7}'`

#if free memory is <= 1024MB or cache >= 1024MB,then drop the caches
if [ $free_mem -le 1024 -o $cache_mem -ge 1024 ]; then
    sync && echo 3 > /proc/sys/vm/drop_caches
fi

sleep 10

done
