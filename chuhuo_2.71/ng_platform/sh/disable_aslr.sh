#!/bin/bash

flag=0

while [[ $flag -ne 1 ]]
do
	server_status=`ps -ef | grep mp_server | grep  -v grep  | wc -l`
	kni_status=`ps -ef | grep kni | grep -v grep | wc -l`
	if [ $server_status -ne 0 -a $kni_status -ne 0 ]; then
		sleep 1
		echo 0 > /proc/sys/kernel/randomize_va_space
		flag=1
	else
		sleep 1
	fi 
done
