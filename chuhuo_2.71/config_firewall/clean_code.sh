#!/bin/bash

# Check if it is in progress
VAR=`ps -ef | grep "$0" | grep -Ev "grep|$$" | wc -l`
if [ $VAR -gt 0 ]; then
    echo "Error: $0 in progress"
    exit 1
fi

#clean client
if [ -d "/home/ng_platform/bd_dpdk_warper/clients" ]; then
    cd /home/ng_platform/bd_dpdk_warper/clients
    rm -f *.c
    rm -f Makefile
fi

#clean fp-debug
if [ -d "/home/ng_platform/bd_dpdk_warper/fp/fpdebug" ]; then
    cd /home/ng_platform/bd_dpdk_warper/fp/fpdebug
    rm -f *.cpp
    rm -f *.h
    rm -f Makefile
fi

if [ -d "/home/ng_platform/bd_dpdk_warper/fp/fpdebug/readline" ]; then
    cd /home/ng_platform/bd_dpdk_warper/fp/fpdebug/readline
    rm -f *.h
fi

#clean lib2
if [ -d "/home/ng_platform/bd_dpdk_warper/lib2" ]; then
    cd /home/ng_platform/bd_dpdk_warper/lib2
    rm -f *.c
    rm -rf filter
    rm -rf ndpi
fi

#clean server
if [ -d "/home/ng_platform/bd_dpdk_warper/server" ]; then
    cd /home/ng_platform/bd_dpdk_warper/server
    rm -f *.c
    rm -f *.h
fi

#clean include and include2
if [ -d "/home/ng_platform/bd_dpdk_warper" ]; then
    cd /home/ng_platform/bd_dpdk_warper
    rm -rf include
    rm -rf include2
fi

#clean policyevolve
if [ -d "/home/ng_platform/policyevolve" ]; then
    cd /home/ng_platform/policyevolve
    rm -f *.c
    rm -f *.h
    rm -f Makefile
    rm -f tse.sql
fi

#clean ips
if [ -d "/home/suricata/src" ]; then
    cd /home/suricata/src
    rm -f *.c
    rm -f *.h
    rm -f *.o
fi

#clean waf
if [ -d "/home/bdwaf" ]; then
    cd /home/bdwaf
    rm -rf nginx-1.4.4
fi

#clean snort
if [ -d "/home/tools" ]; then
    cd /home/tools
    rm -rf snort-2.9.8.0
    rm -rf daq-2.0.6
fi

#clean user authentication
if [ -d "/home/ng_platform" ]; then
    cd /home/ng_platform
    rm -rf user_authentication
fi

#clean av scan
rm -rf /home/tools/av_install_package

#clean anti-detect
rm -rf /home/tools/antidetect-rec

#clean ipsec vpn
rm -rf /home/tools/vpn/ipsec-guomi

cd /root

#clean files
sh /root/config_firewall/clean_files.sh

exit 0
