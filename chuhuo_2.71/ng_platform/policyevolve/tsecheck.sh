#!/bin/bash

while true
do
	return=0
	return=`ps -ef | grep "nftse" | grep -v "grep" | wc -l`
	if [ $return -eq 0 ]
	then
		iptables -t filter -F NF_QUEUE_CHAIN
		exit
	fi
	sleep 1
done
