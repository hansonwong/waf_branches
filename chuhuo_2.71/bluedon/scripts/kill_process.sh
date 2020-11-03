#!/bin/bash

#kill bdwaf
killall -9 bdwaf

#kill fp-debug
ID=`ps -ef | grep fp-debug | grep -v grep | awk '{print $2}'`
for pid in $ID
do
kill -9 $pid
done

#kill snort
ID=`ps -ef | grep snort | grep -v grep | awk '{print $2}'`
for pid in $ID
do
kill -9 $pid
done

