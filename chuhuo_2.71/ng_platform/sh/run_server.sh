#!/bin/bash

#enable ASLR
echo 2 > /proc/sys/kernel/randomize_va_space

#start mp_server
(/home/ng_platform/bd_dpdk_warper/server/mp_server  -c 0x81 -n 4  --file-prefix "program1" --proc-type primary > /var/log/mp_server/mp_server.log 2>&1 &)

#disable ASLR
sh /home/ng_platform/sh/disable_aslr.sh > /dev/null 2>&1 & 
