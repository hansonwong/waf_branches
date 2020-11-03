#!/bin/bash

ps -ef | grep mp_server | grep -v grep
mp_server_exist=$?
if [ $mp_server_exist -eq 1 ]; then
	cp /usr/local/bluedon/bdwaf/conf/nginx.conf.new /usr/local/bluedon/bdwaf/conf/nginx.conf
	killall bdwaf > /dev/null 2>&1
	sleep 2
	cp /usr/local/bluedon/bdwaf/sbin/bdwaf.new /usr/local/bluedon/bdwaf/sbin/bdwaf
    cd /home/ng_platform/dpdk-1.8.0/
	tools/dpdk_nic_bind.py --bind=igb_uio $(tools/dpdk_nic_bind.py --status | sed -rn 's,.* if=([^ ]*).*igb_uio *$,\1,p') > /dev/null 2>&1
	/home/ng_platform/bd_dpdk_warper/server/mp_server -c 0x01 -n 4  --file-prefix "program1" --proc-type primary > /dev/null 2>&1 &
	sleep 8
	/usr/local/bluedon/bdwaf/sbin/bdwaf > /dev/null
fi

