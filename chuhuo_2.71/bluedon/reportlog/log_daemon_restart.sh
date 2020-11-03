#!/bin/sh
#if [ $# -lt 1 ]
#then
#	echo "need procedure_name"
	#exit 1
#fi
python mysql_log_daemon.py -s stop
python mysql_log_daemon.py -s start

exit

if [ "$1" = 'stop' ]; then
    PROCESS=`ps -ef|grep 'python mysql_log_daemon.py'|grep -v grep|grep -v PPID|awk '{ print $2}'`
    for i in $PROCESS
    do
        echo "Kill the $1 process [ $i ]"
        kill -9 $i
    done

    PROCESS=`ps -ef|grep 'python /usr/local/bluedon/mysql_log_daemon.py'|grep -v grep|grep -v PPID|awk '{ print $2}'`
    for i in $PROCESS
    do
        echo "Kill the $1 process [ $i ]"
        kill -9 $i
    done
    python mysql_log_daemon.py -s stop

else
    PROCESS=`ps -ef|grep 'python mysql_log_daemon.py'|grep -v grep|grep -v PPID|awk '{ print $2}'`
    for i in $PROCESS
    do
        echo "Kill the $1 process [ $i ]"
        kill -9 $i
    done
    
    PROCESS=`ps -ef|grep 'python /usr/local/bluedon/mysql_log_daemon.py'|grep -v grep|grep -v PPID|awk '{ print $2}'`
    for i in $PROCESS
    do
        echo "Kill the $1 process [ $i ]"
        kill -9 $i
    done


    python mysql_log_daemon.py -s stop
    python mysql_log_daemon.py -s start
fi

ps -ef | grep mysql_log_daemon.py | grep -v grep 
