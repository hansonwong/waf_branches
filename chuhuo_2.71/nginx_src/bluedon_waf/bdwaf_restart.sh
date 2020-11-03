#!/bin/bash

FILENAME="/usr/local/bdwaf/conf/waf_on.conf"

head -1 $FILENAME|while read line
do
   if [ $line == "1" ]
   then 
       killall -9 bdwaf
       killall -9 bdwaf
       /usr/local/bdwaf/sbin/bdwaf
       break
   fi
done 



