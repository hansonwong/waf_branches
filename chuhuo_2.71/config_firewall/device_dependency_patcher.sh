#!/bin/bash
#
# Copyright (C) Bluedon, 2016
# Author: Linfan Hu (hlf@chinabluedon.cn)
# Date: 2016/11/24
#

# Check if it is in progress
VAR=`ps -ef | grep "$0" | grep -Ev "grep|$$" | wc -l`
if [ $VAR -gt 0 ]; then
    echo "Error: $0 in progress"
    exit 1
fi

# Determine working directory
WORK_DIR=$1

# Files which should not be overwritten
GRUB_CONFIG=/boot/grub2/grub.cfg
DPDK_INIT=/home/ng_platform/sh/dpdk_init.sh

RC_LOCAL=/etc/rc.d/rc.local
CRONTAB=/etc/crontab
SYSCTL_CONF=/etc/sysctl.conf
RUN_SERVER=/home/ng_platform/sh/run_server.sh
NGINX_CONF=/usr/local/bdwaf/conf/nginx.conf
PROXYNGINX_CONF=/usr/local/bdwaf/conf_proxy/nginx.conf
DPDK_SERVICE=/usr/local/bluedon/conf/systemctl/dpdk.service
DPDK_FRAME_H=/home/ng_platform/bd_dpdk_warper/include2/dpdk_frame.h
DPDK_FRAME_C=/home/ng_platform/bd_dpdk_warper/lib2/dpdk_frame.c
DPDK_CONFIG_H=/home/ng_platform/bd_dpdk_warper/include2/dpdk_config.h
SERVER_C=/home/ng_platform/bd_dpdk_warper/server/server.c
KNI_MISC_C=/home/ng_platform/dpdk-1.8.0/lib/librte_eal/linuxapp/kni/kni_misc.c

if [ -d "$WORK_DIR" ]; then
    if [ -d "$WORK_DIR/ngfw-sysconfig" ]; then
        RC_LOCAL=$WORK_DIR/ngfw-sysconfig/rc.local
        CRONTAB=$WORK_DIR/ngfw-sysconfig/crontab
        SYSCTL_CONF=$WORK_DIR/ngfw-sysconfig/sysctl.conf
        RUN_SERVER=$WORK_DIR/ngfw-sysconfig/sh/run_server.sh
    fi

    if [ -f "$WORK_DIR/waf-config/bdwaf/conf/nginx.conf" ]; then
        NGINX_CONF=$WORK_DIR/waf-config/bdwaf/conf/nginx.conf
    fi
    
    if [ -d "$WORK_DIR/firewall_python_1.1_product" ]; then
        DPDK_SERVICE=$WORK_DIR/firewall_python_1.1_product/conf/systemctl/dpdk.service
    fi

    if [ -d "$WORK_DIR/bd_dpdk_warper" ]; then
        DPDK_FRAME_H=$WORK_DIR/bd_dpdk_warper/include2/dpdk_frame.h
        DPDK_FRAME_C=$WORK_DIR/bd_dpdk_warper/lib2/dpdk_frame.c
        SERVER_C=$WORK_DIR/bd_dpdk_warper/server/server.c
    fi

    if [ -d "$WORK_DIR/dpdk-1.8.0" ]; then
        KNI_MISC_C=$WORK_DIR/dpdk-1.8.0/lib/librte_eal/linuxapp/kni/kni_misc.c
    fi
fi

IPS_CONF=/etc/suricata/ips
# Old device may place ips config file to the following path:
IPS_CONF_OLD=/usr/local/bluedon/template/ips

MGT_NIC=/etc/network_config/mgt_nic.txt
if [ ! -f "$MGT_NIC" ]; then
    # Old device may place mgt_nic.txt to the following path
    MGT_NIC=/usr/local/bluedon/conf/mgt_nic.txt
fi

# IPS configuration files location
[ -d "/etc/suricata" ] || mkdir -p /etc/suricata
[ -d "/usr/local/bluedon/template" ] || mkdir -p /usr/local/bluedon/template

# WAF configuration files location
[ -d "/usr/local/bdwaf/conf" ] || mkdir -p /usr/local/bdwaf/conf

function isolate_cpu()
{
    if [ ! -f "$GRUB_CONFIG" ]; then
        echo "No grub.cfg found"
        return 1
    fi

    isolcpus="isolcpus="
    nohz_full="nohz_full="
    rcu_nocbs="rcu_nocbs="

    # Check and set isolated cpus for grub
    CPUS=`cat /proc/cpuinfo | grep -i processor | wc -l`
    if [ $CPUS -le 4 ]; then
        isolcpus+="3"
        nohz_full+="3"
        rcu_nocbs+="3"
    else
        # DO NOT isolate core greater than 7
        [ $CPUS -gt 8 ] && CPUS=8;

        for (( i = $CPUS - 1; $i > 0 ; i-- )); do
            # DO NOT isolate core 6
            [ $i -eq 6 ] && continue;

            if [ $i -gt 1 ]; then
                isolcpus+="$i,"
                nohz_full+="$i,"
                rcu_nocbs+="$i,"
            else
                isolcpus+="$i"
                nohz_full+="$i"
                rcu_nocbs+="$i"
            fi
        done
    fi

    sed -i "s/^.*isolcpus.*$/\tlinux16 \/vmlinuz-3.10.0 root=\/dev\/sda2 ro vconsole.keymap=us crashkernel=auto  vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_US.UTF-8 $isolcpus $nohz_full $rcu_nocbs nmi_watchdog=0 selinux=0  intel_pstate=disable nosoftlockup console=tty0 console=ttyS0,115200n8/" $GRUB_CONFIG

    return 0
}

function patch_cpu()
{
    if [ ! -f "$RC_LOCAL" ]; then
        echo "No rc.local found"
        return 1
    fi

    if [ ! -f "$RUN_SERVER" ]; then
        echo "No run_server.sh found"
        return 1
    fi

    if [ ! -f "$NGINX_CONF" ]; then
        echo "No nginx.conf found"
        return 1
    fi
    
    if [ ! -f "$PROXYNGINX_CONF" ]; then
        echo "No proxy nginx.conf found"
        return 1
    fi
    

    if [ ! -f "$DPDK_INIT" ]; then
        echo "No dpdk_init.sh found"
        return 1
    fi

    if [ ! -f "$DPDK_FRAME_H" ]; then
        echo "No dpdk_frame.h found"
        return 1
    fi

    if [ ! -f "$DPDK_FRAME_C" ]; then
        echo "No dpdk_frame.c found"
        return 1
    fi

    if [ ! -f "$KNI_MISC_C" ]; then
        echo "No kin_misc.c found"
        return 1
    fi

    # Get number of cpus
    CPUS=`cat /proc/cpuinfo | grep -i processor | wc -l`
    if [ $CPUS -ge 8 ]; then
        if [ -n "$WORK_DIR" ]; then
            \cp -f $WORK_DIR/ips-config/yaml/ips $IPS_CONF
        fi

        # new dpdk is running as system service
        [ -f "$DPDK_SERVICE" ] && sed -i "/mp_server/s/0x09/0x81/g" $DPDK_SERVICE

    elif [ $CPUS -ge 4 ]; then
        if [ -z "$WORK_DIR" ]; then
            mv -f $IPS_CONF $IPS_CONF-8
            mv -f $IPS_CONF-4 $IPS_CONF
        else
            \cp -f $WORK_DIR/ips-config/yaml/ips-4 $IPS_CONF
        fi

        # new dpdk is running as system service
        [ -f "$DPDK_SERVICE" ] && sed -i "/mp_server/s/0x81/0x09/g" $DPDK_SERVICE

        sed -i "/mp_server/s/0x81/0x09/g" $RC_LOCAL
        sed -i "/mp_server/s/0x81/0x09/g" $RUN_SERVER
        sed -i "s/^worker_processes.*$/worker_processes 2;/g" $NGINX_CONF
        sed -i "s/^worker_processes.*$/worker_processes 2;/g" $PROXYNGINX_CONF
        sed -i "s/^worker_cpu_affinity.*$/worker_cpu_affinity   0100 1000;/g" $NGINX_CONF
        sed -i "s/^worker_cpu_affinity.*$/worker_cpu_affinity   0100 1000;/g" $PROXYNGINX_CONF
        sed -i "/kthread_mode=single/s/#//g" $DPDK_INIT
        commented=`cat $DPDK_INIT | grep "kthread_mode=multiple" | grep "#"`
        if [ -z "$commented" ] ; then
            sed -i "/kthread_mode=multiple/s/^/#/" $DPDK_INIT
        fi
        sed -i "/ONE_G_PORT_RX_QUEUES/s/2/1/g" $DPDK_FRAME_H
        sed -i "/ONE_G_PORT_TX_QUEUES/s/2/1/g" $DPDK_FRAME_H
        sed -i "/TEN_G_PORT_RX_QUEUES/s/2/1/g" $DPDK_FRAME_H
        sed -i "/TEN_G_PORT_TX_QUEUES/s/2/1/g" $DPDK_FRAME_H
        sed -i "/kthread_bind/s/1/0/g" $KNI_MISC_C

        commented=`cat $DPDK_FRAME_C | grep "conf.core_id = 0;"| awk '{print $1}'`
        if [ "$commented" != "conf.core_id" ]; then
            sed -i "/conf.core_id = 0;/s/\/\///" $DPDK_FRAME_C
        fi

        commented=`cat $DPDK_FRAME_C | grep "conf.force_bind" | awk '{print $1}'`
        if [ "$commented" == "conf.force_bind" ]; then
            sed -i "/conf.force_bind/,+4s/^/\/\//" $DPDK_FRAME_C
        fi
    elif [ $CPUS -lt 4 ]; then
        echo "Error: Less than 4 CPU cores. Hyper-Threading NOT enable?"
        return 1
    fi

    # Backward compat
    cp -f $IPS_CONF $IPS_CONF_OLD 

    return 0
}

function patch_memory()
{
    if [ ! -f "$DPDK_INIT" ]; then
        echo "NO dpdk_init.sh found"
        return 1
    fi

    if [ ! -f "$DPDK_FRAME_H" ]; then
        echo "No dpdk_frame.h found"
        return 1
    fi

    # Get memory size. Memory size varies from different platform or OS.
    # Moreover, many manufacturers regard 1GB as 1,000,000,000B. To deal with
    # this issue, we determine 16G/8G/4G approximately
    MEMS=`cat /proc/meminfo | grep -i memtotal | awk '{print $2}'`
    if [ $MEMS -lt 15000000 ]; then
        if [ $MEMS -gt 7600000 ]; then
            sed -i "/nr_hugepages/s/\<3072\>/2048/" $DPDK_INIT
            sed -i "/DPDK_NB_MBUFS/s/1500000/700000/g" $DPDK_FRAME_H
        elif [ $MEMS -gt 3700000 ]; then
            sed -i "/nr_hugepages/s/\<3072\>/700/" $DPDK_INIT
            sed -i "/DPDK_NB_MBUFS/s/1500000/200000/g" $DPDK_FRAME_H
            sed -i "/MAX_FLOW_BUCKET/s/65536/16384/g" $DPDK_CONFIG_H
	    sed -i "/MAX_NDPI_FLOW/s/65535/16383/g" $DPDK_CONFIG_H
	    
            dd if=/dev/zero of=/var/local/swapfile bs=1k count=4096000
            mkswap /var/local/swapfile
            swapon /var/local/swapfile
            echo "/var/local/swapfile  swap  swap    defaults 0 0" >> /etc/fstab
        else
            echo "Error: Memory size too small"
            return 1
        fi
    fi

    return 0
}

# 82574L network interface must use poll mode to check port status
function patch_nic()
{
    if [ ! -f "$SERVER_C" ]; then
        echo "No server.c found"
        return 1
    fi

    if [ ! -f "$DPDK_FRAME_H" ]; then
        echo "No dpdk_frame.h found"
        return 1
    fi

    # Network devices using kernel driver
    MGT_PORT1=`cat $MGT_NIC | awk -F"\"" '{print $2}'`
    MGT_PORT2=`cat $MGT_NIC | awk -F"," '{print $2}' | awk -F"\"" '{print $2}'`
    KERNEL_PORT=$MGT_PORT1
    if [ -n "$MGT_PORT2" ]; then
        KERNEL_PORT+="|$MGT_PORT1"
    fi

    ETH82574L=`/home/ng_platform/dpdk-1.8.0/tools/dpdk_nic_bind.py --s | grep "82574L" | grep -Ev "$KERNEL_PORT"`
    if [ -n "$ETH82574L" ]; then
        # Commented intr registration
        commented=`cat $DPDK_FRAME_C | grep ".intr_conf" | awk '{print $1}'`
        if [ "$commented" == ".intr_conf" ]; then
            sed -i "/intr_conf/,+2s/^/\/\//g" $DPDK_FRAME_C
            sed -i "/rte_eth_dev_callback_register/s/^/\/\//g" $DPDK_FRAME_C
        fi

        # Add port check function
        port_check=`cat $SERVER_C | grep port_check`
        if [ -z "$port_check" ]; then
sed -i "/do_manager_task(__attribute__((unused))/i\
static void port_check(void)\n\
{\n\
\tuint8_t portid,flag=0;\n\
\tuint8_t port_num=portinfos->portn;\n\
\tstruct rte_eth_link  link;\n\
\n\
\tfor (portid = 0; portid < port_num; portid++) {\n\
\t\tupdate_port_status(portid);\n\
\t}\n\
}\n" $SERVER_C
            sed -i "/detect_client(server_tx)/a\\\t\tport_check();" $SERVER_C
        fi
    fi
}

#################################################################
isolate_cpu;
if [ $? -ne 0 ]; then
    echo "Warning: Cannot isolate cpus"
fi

patch_cpu;
if [ $? -ne 0 ]; then
    echo "Warning: Cannot patch cpus"
fi

patch_memory;
if [ $? -ne 0 ]; then
    echo "Warning: Cannot patch memory"
fi

patch_nic;
if [ $? -ne 0 ]; then
    echo "Warning: Cannot patch network interface card"
fi

if [ -f "$RUN_SERVER" ]; then 
    cp -f $RUN_SERVER /home/ng_platform/sh/run_server.sh > /dev/null 2>&1
    chmod a+x /home/ng_platform/sh/*.sh
fi

if [ -f "$NGINX_CONF" ]; then 
    cp -f $NGINX_CONF /usr/local/bdwaf/conf/nginx.conf > /dev/null 2>&1
fi

if [ -f "$SYSCTL_CONF" ]; then 
    cp -f $SYSCTL_CONF /etc/sysctl.conf > /dev/null 2>&1
fi

if [ -f "$RC_LOCAL" ]; then
    cp -f $RC_LOCAL /etc/rc.d/rc.local > /dev/null 2>&1
    chmod a+x /etc/rc.d/rc.local
fi

if [ -f "$CRONTAB" ]; then 
    cp -f $CRONTAB /etc/crontab > /dev/null 2>&1
fi

exit 0
