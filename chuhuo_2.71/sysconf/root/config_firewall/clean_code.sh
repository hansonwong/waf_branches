#!/bin/bash

# Check if it is in progress
VAR=`ps -ef | grep "$0" | grep -Ev "grep|$$" | wc -l`
if [ $VAR -gt 0 ]; then
    echo "Error: $0 in progress"
    exit 1
fi

#clean client
cd /home/ng_platform/bd_dpdk_warper/clients
rm -f *.c

#clean fp-debug
cd /home/ng_platform/bd_dpdk_warper/fp/fpdebug
rm -f *.cpp
rm -f *.h
cd /home/ng_platform/bd_dpdk_warper/fp/fpdebug/readline
rm -f *.h

#clean lib2
cd /home/ng_platform/bd_dpdk_warper/lib2
rm -f *.c
rm -rf filter
rm -rf ndpi

#clean server
cd /home/ng_platform/bd_dpdk_warper/server
rm -f *.c
rm -f *.h

#clean policyevolve
cd /home/ng_platform/policyevolve
rm -f *.c

#clean ips
cd /home/suricata/src
rm -f *.c
rm -f *.h
rm -f *.o

#clean waf
cd /home/bdwaf
rm -rf nginx-1.4.4

#clean snort
cd /home/tools
rm -rf snort-2.9.8.0
rm -rf daq-2.0.6

#clean user authentication
cd /home/ng_platform
rm -rf user_authentication

#clean av scan
rm -rf /home/tools/av_install_package

#clean anti-detect
rm -rf /home/tools/antidetect-rec

#clean ipsec vpn
rm -rf /home/tools/vpn/ipsec-guomi

exit 0
