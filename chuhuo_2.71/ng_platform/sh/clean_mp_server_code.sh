#!/bin/bash

#clean client
cd /home/ng_platform/bd_dpdk_warper/clients
rm *.c -f

#clean fp-debug
cd /home/ng_platform/bd_dpdk_warper/fp/fpdebug
rm *.cpp -f
rm *.h -f
cd /home/ng_platform/bd_dpdk_warper/fp/fpdebug/readline
rm *.h -f

#clean lib2
cd /home/ng_platform/bd_dpdk_warper/lib2
rm *.c -f
rm filter -rf
rm ndpi -rf

#clean server
cd /home/ng_platform/bd_dpdk_warper/server
rm *.c -f

#clean IPS
cd /home/suricata/src/
rm -rf *.c *.h *.o

#clean WAF
cd /home/bdwaf/
rm -rf nginx-1.4.4

#clean snort
cd /home/tools
rm -rf snort-2.9.8.0
rm -rf daq-2.0.6

#clean user authentication
cd /home/ng_platform
rm -rf user_authentication

#go to root
cd /
