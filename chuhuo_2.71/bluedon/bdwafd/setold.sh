#!/bin/bash

ps -ef | grep mp_server| grep -v grep
mp_server_exit=$?
if [ $mp_server_exit -eq 0 ]; then
	killall bdwaf > /dev/null 2>&1
	killall mp_server
	sleep 3
    cd /home/ng_platform/dpdk-1.8.0/
	tools/dpdk_nic_bind.py --status | grep drv=i | awk '{print $1}' | xargs ./tools/dpdk_nic_bind.py -b igb > /dev/null 2>&1
	cp /usr/local/bluedon/bdwaf/conf/nginx.conf.old /usr/local/bluedon/bdwaf/conf/nginx.conf
	cp /usr/local/bluedon/bdwaf/sbin/bdwaf.old /usr/local/bluedon/bdwaf/sbin/bdwaf
	/usr/local/bluedon/bdwaf/sbin/bdwaf
fi
