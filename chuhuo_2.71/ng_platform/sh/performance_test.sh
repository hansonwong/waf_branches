#!/bin/bash

if [ $# -eq 1 ]; then
        if [ $1 == "on" ]; then
                /home/ng_platform/bd_dpdk_warper/clients/performance_test on > /dev/null 2>&1
        elif [ $1 == "off" ]; then
                /home/ng_platform/bd_dpdk_warper/clients/performance_test off > /dev/null 2>&1
        else
                echo "error"
        fi
elif [ $# -eq 3 ]; then
        if [ $1 == "on" ]; then
                /home/ng_platform/bd_dpdk_warper/clients/performance_test on $2 $3 > /dev/null 2>&1
        elif [ $1 == "off" ]; then
                /home/ng_platform/bd_dpdk_warper/clients/performance_test off $2 $3 > /dev/null 2>&1
        else
                echo "error"
        fi
else
        echo "error"
fi
