#!/bin/bash

count=`ps -ef|grep -v 'grep' |grep $0 |wc -l`
if [ $count -gt 3 ]; then
    #echo "$count" >> /tmp/test.log
    exit 0
fi

while true; do
ps -ef | grep python | grep -v grep | grep bdwafd.py

if [ $? -eq 1 ]; then
    python /usr/local/bluedon/bdwafd/bdwafd.py -s restart
    echo 'CMD_NGINX' >> /tmp/bdwaf.fifo
fi

ps -ef | grep python | grep -v 'grep' | grep bdauditd.py
if [ $? -eq 1 ]; then
    python /usr/local/bluedon/bdwafd/bdauditd.py -s restart
fi

sleep 5
done
