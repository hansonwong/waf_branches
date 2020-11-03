#!/bin/bash

cd /home/ng_platform/dpdk-1.8.0
#rmmod i40e
#modprobe i40e
modprobe uio
insmod x86_64-native-linuxapp-gcc/kmod/igb_uio.ko
#tools/dpdk_nic_bind.py --bind=igb_uio $(tools/dpdk_nic_bind.py --status | sed -rn 's,.* if=([^ ]*).*igb_uio *$,\1,p')

#KERNEL_PORT="lo|vir|enp8s0|enp9s0"
#PCIE_ADDR=$(tools/dpdk_nic_bind.py --s | grep -E "Connection|Ethernet" | grep -Ev "$KERNEL_PORT" | awk '{print $1}')
#python tools/dpdk_nic_bind.py --bind=igb_uio $PCIE_ADDR
for addr in `cat /etc/network_config/pci.conf`
do
tools/dpdk_nic_bind.py --bind=igb_uio $addr
done

#tools/dpdk_nic_bind.py --bind=igb_uio 0000:05:00.0
#tools/dpdk_nic_bind.py --bind=igb_uio 0000:05:00.1
#tools/dpdk_nic_bind.py --bind=igb_uio 0000:07:00.0
#tools/dpdk_nic_bind.py --bind=igb_uio 0000:07:00.1
#tools/dpdk_nic_bind.py --bind=igb_uio 0000:07:00.2
#tools/dpdk_nic_bind.py --bind=igb_uio 0000:07:00.3
#tools/dpdk_nic_bind.py --bind=igb_uio 0000:08:00.0
#tools/dpdk_nic_bind.py --bind=igb_uio 0000:08:00.1
#tools/dpdk_nic_bind.py --bind=igb_uio 0000:08:00.2
#tools/dpdk_nic_bind.py --bind=igb_uio 0000:08:00.3

mkdir -p /mnt/huge
mount -t hugetlbfs nodev /mnt/huge
echo 3072 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
#echo 3500 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
#for gov in /sys/devices/system/cpu/*/cpufreq/scaling_governor ; do echo performance >$gov ; done
#insmod ./x86_64-native-linuxapp-gcc/kmod/rte_kni.ko kthread_mode=single
insmod ./x86_64-native-linuxapp-gcc/kmod/rte_kni.ko kthread_mode=multiple
