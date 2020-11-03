#!/bin/bash

#systemctl stop ips.service

#kill bdips
ID=`ps -ef | grep bdips | grep -v grep | awk '{print $2}'`
for pid in $ID
do
kill -9 $pid
done

#kill suricata
ID=`ps -ef | grep suricata | grep -v grep | awk '{print $2}'`
for pid in $ID
do
kill -9 $pid
done

#kill bdwaf
#ID=`ps -ef | grep bdwaf | grep -v grep | awk '{print $2}'`
#for pid in $ID
#do
#kill -9 $pid
#done
killall -9 bdwaf

#kill get_statistics_data
ID=`ps -ef | grep get_statistics_data | grep -v grep | awk '{print $2}'`
for pid in $ID
do
kill -9 $pid
done

#kill fp-debug
ID=`ps -ef | grep fp-debug | grep -v grep | awk '{print $2}'`
for pid in $ID
do
kill -9 $pid
done

#kill second_firewall_init.py
ID=`ps -ef | grep second_firewall_init.py | grep -v grep | awk '{print $2}'`
for pid in $ID
do
kill -9 $pid
done

#kill mysql_log_daemon.py
ID=`ps -ef | grep mysql_log_daemon.py | grep -v grep | awk '{print $2}'`
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

