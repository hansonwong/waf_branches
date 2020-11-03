#!/bin/bash


while true
do
        sleep 3
        count='ps -ef| grep mp_server| grep -v "grep" |wc -l'
        if [ 0 == $count ]; then
                killall -9 bdwaf
                killall -9 bdwaf
                sleep 3 
                /home/ng_platform/bd_dpdk_warper/server/mp_server -c 0x03 -n 4  --file-prefix "program1" --proc-type primary > /dev/null 2>&1 &
                sleep 20
                /usr/local/bluedon/bdwaf/sbin/bdwaf
                echo $(date) >> /usr/local/bluedon/bdwaf/logs/mp_server.log
                echo "restart mp_server" >> /usr/local/bluedon/bdwaf/logs/mp_server.log
                python /usr/local/bluedon/bdwafd/bdreconfigbridge.py
        fi
done
