#!/bin/sh
#if [ $# -lt 1 ]
#then
#   echo "need procedure_name"
    #exit 1
#fi

PROCESS=`ps -ef|grep second_firewall_daemon.py|grep -v grep|grep -v PPID|awk '{ print $2}'`
for i in $PROCESS
do
    echo "Kill the $1 process [ $i ]"
    kill -9 $i
done

python /usr/local/bluedon/second_firewall_daemon.py -s stop
python /usr/local/bluedon/second_firewall_daemon.py -s start

ps -ef | grep second_firewall_daemon.py

#./log_daemon_restart.sh
