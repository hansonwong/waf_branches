#! /bin/sh

#python /usr/local/bluedon/reportlog/mysql_log_daemon.py -s stop  > /dev/null 2>&1
#python /usr/local/bluedon/reportlog/mysql_log_daemon.py -s start > /dev/null 2>&1 &
python /usr/local/bluedon/reportlog/mysql_log_daemon.py -s restart > /dev/null 2>&1 &
