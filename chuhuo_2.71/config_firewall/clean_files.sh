#!/bin/bash

VAR=`ps -ef | grep "$0" | grep -Ev "grep|$$" | wc -l`
if [ $VAR -gt 0 ]; then
    echo "Error: $0 in progress"
    exit 1
fi

#----------------------------------------------------------
# wifi审计
rm -rf /home/wifi_audit

#----------------------------------------------------------
# /home/perf_up.sh
rm -f  /home/perf_up.sh
#----------------------------------------------------------

# /home/tools
rm -f  /home/tools/*.tar.gz
rm -f  /home/tools/*.tar.bz2
rm -f  /home/tools/*.tar
rm -f  /home/tools/*.zip

# 反向拍照
rm -rf /home/tools/antidetect-rec

# 反扫描
rm -rf /home/tools/AntiScan
rm -rf /home/tools/daq-2.0.6
rm -rf /home/tools/snort-2.9.8.0

# 病毒引擎
rm -rf /home/tools/av_install_package
rm -rf /home/cyren/checkfile

# suricata
rm -rf /home/tools/sc

# syslog-ng
rm -rf /home/tools/syslog-ng-3.6.4
rm -rf /home/tools/eventlog-0.2.12

# dpi
rm -rf /home/tools/ndpi-netfilter-master

# ha
rm -rf /home/tools/updata_ha
rm -f  /home/rsync/send/sync_safe_tactics
rm -f  /home/rsync/recv/sync_safe_tactics

# vpn
rm -rf /home/tools/vpn

# 新版ssl vpn不需要这个目录
rm -rf /etc/openvpn

rm -rf /home/vpn_source

# 工具
rm -rf /home/tools/automake-1.13.4
rm -rf /home/tools/automake-1.15
rm -rf /home/tools/file-5.11
rm -rf /home/tools/hiredis-master
rm -rf /home/tools/ipset-6.27
rm -rf /home/tools/jansson-2.6
rm -rf /home/tools/libevent-2.1.8-stable
rm -rf /home/tools/libiconv-1.14
rm -rf /home/tools/libnet-1.1.6
rm -rf /home/tools/libol-0.3.18
rm -rf /home/tools/libpcap-1.4.0
rm -rf /home/tools/ncurses-5.9
rm -rf /home/tools/pcre-8.32
rm -rf /home/tools/pimd-2.1.8
rm -rf /home/tools/redis-3.2.3
rm -rf /home/tools/rp-pppoe-3.12
rm -rf /home/tools/yaml-0.1.5
rm -rf /home/tools/rsync_updata
rm -f  /home/tools/fix_systemd.sh
rm -rf /home/tools/n2n-master
#----------------------------------------------------------

# move_irq
rm -f  /home/.move_irq.sh.swp
rm -f  /home/move_irq.sh
#----------------------------------------------------------

# suicata
# 新版本sc可以删除整个目录
rm /home/suricata -rf
#----------------------------------------------------------

# bdwaf
rm -f  /home/bdwaf/*.tar.gz
rm -rf /home/bdwaf/conf
rm -rf /home/bdwaf/ModSecurity
rm -rf /home/bdwaf/URLs
#----------------------------------------------------------

# htop工具
rm -rf /home/htop-1.0.2
#----------------------------------------------------------

# 蜜罐
rm -rf /home/dionaea
rm -f  /opt/dionaea241bak.zip
rm -rf /opt/dionaealib
rm -rf /opt/ecdysis-nat64-20140422
rm -f  /opt/ecdysis-nat64-20140422.tar.gz
rm -rf /opt/rh
rm -rf /opt/dionaea/netifaces-0.10.4
rm -f  /opt/dionaea/netifaces-0.10.4.tar.gz
rm -rf /opt/dionaea/p0f-master
rm -f  /opt/dionaea/p0f-master.zip
rm -rf /opt/dionaea/PyMySQL-0.6.6
rm -f  /opt/dionaea/PyMySQL-0.6.6.tar.gz
#----------------------------------------------------------

# 测试文件
rm -f  /home/SystemController.php
rm -f  /home/virtual_traffic.py
#----------------------------------------------------------

# 串口服务程序
if [ -d "/home/admin/bd_cli" ]; then
    cd /home/admin/bd_cli
    rm -rf `ls | grep -v -w bdcli | grep -v -w passwd | grep -v config`
fi
#----------------------------------------------------------

# /home/ng_platform
rm -f  /home/ng_platform/*.log

# dpdk

# 删除dpdk源码，只保留编译后的文件和工具
if [ -d "/home/ng_platform/dpdk-1.8.0" ]; then
    cd /home/ng_platform/dpdk-1.8.0
    rm -rf `ls | grep -v -w tools | grep -v -w x86_64-native-linuxapp-gcc`
    rm -f tools/setup.sh
fi

# 删除dpdk编译后的文件，只保留网卡驱动和kni驱动
if [ -d "/home/ng_platform/dpdk-1.8.0/x86_64-native-linuxapp-gcc" ]; then
    cd /home/ng_platform/dpdk-1.8.0/x86_64-native-linuxapp-gcc
    rm -rf `ls | grep -v -w kmod`
fi
#----------------------------------------------------------

# 系统升级备份文件
rm -f  /home/bluedon/bdfw_backup.tar.gz
rm -f  /home/bluedon/restore_system.sh
#----------------------------------------------------------

# PHP工具
rm -rf /home/mallor
#----------------------------------------------------------

# 系统自带内核
rm -f  /usr/src/linux-2.6.34.tar.gz
rm -rf /usr/src/kernels/3.10.0-123.el7.x86_64
#----------------------------------------------------------

# 内核C文件
if [ -d "/usr/src/kernels/linux-3.10.0-123.el7" ]; then
    cd /usr/src/kernels/linux-3.10.0-123.el7
    rm -f  `find ./ ! -path "./scripts/*" -name *.c`
fi
#----------------------------------------------------------

# /root
rm -f  /root/*.txt
rm -f  /root/*.pcap
rm -f  /root/update_firewall_product.sh
#----------------------------------------------------------

# /boot
rm -f  /boot/config-3.10.0-123.el7.x86_64
rm -f  /boot/initramfs-0-rescue-d52eb5c6850342fea85624a5bb163671.img
rm -f  /boot/initramfs-0-rescue-e1e543a305d641c29fd82b4aba900f40.img
rm -f  /boot/initramfs-3.10.0-123.el7.x86_64.img
rm -f  /boot/symvers-3.10.0-123.el7.x86_64.gz
rm -f  /boot/System.map-3.10.0-123.el7.x86_64
rm -f  /boot/System.map-3.10.0.old
rm -f  /boot/vmlinuz-0-rescue-d52eb5c6850342fea85624a5bb163671
rm -f  /boot/vmlinuz-0-rescue-e1e543a305d641c29fd82b4aba900f40
rm -f  /boot/vmlinuz-3.10.0-123.el7.x86_64
rm -f  /boot/vmlinuz-3.10.0.old
#----------------------------------------------------------

# /lib/modules
rm -rf /lib/modules/3.10.0-123.el7.x86_64
#----------------------------------------------------------

# /etc/sysconfig
rm -rf /etc/sysconfig/network-scripts-bak

# iptable_log
rm -f /var/log/iptable_log/Makefile
rm -f /var/log/iptable_log/Read-kmsg.c

# clone and config firwall
rm -rf /root/clone_disk
rm -rf /root/config_firewall
rm -f  update_firewall_product.sh

cd /root



