#!/bin/bash


cd /home/ng_platform/dpdk-1.8.0/
tools/dpdk_nic_bind.py --status | grep drv=i |grep ixgbe | awk '{print $1}' | xargs ./tools/dpdk_nic_bind.py -b ixgbe
tools/dpdk_nic_bind.py --status | grep drv=i | grep -v ixgbe | awk '{print $1}' | xargs ./tools/dpdk_nic_bind.py -b igb
#> /dev/null 2>&1
