#!/bin/bash

server_status=`ps -ef | grep mp_server | grep  -v grep  | wc -l`
if [ $server_status -eq 0 ]; then
	dpdk_init_status=`lsmod | grep igb_uio | wc -l`
	if [ $dpdk_init_status -eq 0 ]; then
		sh /home/ng_platform/sh/dpdk_init.sh
	fi

	sh /home/ng_platform/sh/kill_process.sh	
	sh /home/ng_platform/sh/run_server.sh
	sleep 20
	sh /home/ng_platform/sh/kill_process.sh	
	python /usr/local/bluedon/core/second_firewall_init.py > /var/log/restart.log 2>&1 &
	python /usr/local/bluedon/reportlog/mysql_log_daemon.py -s start > /var/log/mysql.log 2>&1 &
fi

