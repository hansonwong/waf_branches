#!/bin/bash
#
# Copyright (C) 2016 Bluedon. All rights reserved.
# Author: Linfan Hu (hlf@chinabluedon.cn)
# Date: 2016/12/21
#

# Check if configuration is in progress
VAR=`ps -ef | grep "$0" | grep -Ev "grep|$$" | wc -l`
if [ $VAR -gt 0 ]; then
    echo "错误：本配置脚本已在执行"
    exit 1
fi

# Constant data definition
USR_SEL_MGTPORT=1
USR_SEL_HAPORT=2
USR_SEL_SVRPORT=3
USR_SEL_WEBPORT=4
USR_SEL_SAVE=5
USR_SEL_RESET=6
USR_SEL_EXIT=7

# NIC that driven by kernel
MGT1=""
MGT2=""
HA_PORT=""

RC_LOCAL=/etc/rc.d/rc.local
CRONTAB=/etc/crontab
ENABLE_SERVICE=/usr/local/bluedon/scripts/enable_services.sh
DPDK_NIC_BIND=/home/ng_platform/dpdk-1.8.0/tools/dpdk_nic_bind.py
DPDK_INIT=/home/ng_platform/sh/dpdk_init.sh
PCI_CONF=/etc/network_config/pci.conf
MGT_NIC=/etc/network_config/mgt_nic.txt
WEB_PORTS=/etc/network_config/network_interface.cfg
HA_SCRIPT=/etc/sysconfig/network-scripts/ha_port
SERVER_DIR=/home/ng_platform/bd_dpdk_warper/server

OPERATION_LOG=/var/log/config_firewall.log

echo "//////////////////////////" >> $OPERATION_LOG
echo $(date '+%Y-%m-%d %H:%M:%S') >> $OPERATION_LOG
echo "//////////////////////////" >> $OPERATION_LOG

function init()
{
    # change password
    #./ch_passwd

    # allow backspace
    stty erase ^h

    ifup_all_ports;

    # Lookup default mgt ports
    MGT1=`ls /etc/sysconfig/network-scripts | grep ifcfg | grep -v lo | awk 'NR==1{print}' | sed 's/ifcfg-//'`
    MGT2=`ls /etc/sysconfig/network-scripts | grep ifcfg | grep -v lo | awk 'NR==2{print}' | sed 's/ifcfg-//'`

    check_mgt_port;
    if [ $? -ne 0 ]; then
        MGT1=""
        MGT2=""
    fi

    touch $HA_SCRIPT
    HA_PORT=`cat $HA_SCRIPT | sed 's/ //g'`
    if [ -n "$HA_PORT" ]; then
        VAR=`ifconfig -a | grep $HA_PORT`
        [ -z "$VAR" ] && HA_PORT=""
    fi
}

function reset()
{
    rm -f $PCI_CONF
    rm -f $MGT_NIC
    rm -f $WEB_PORTS
    rm -f $HA_SCRIPT

    init;
}

# Backward compat for previous version
function backward_compat()
{
    cp -f $PCI_CONF /home/ng_platform/bd_dpdk_warper/config/pci.conf
    cp -f $MGT_NIC /usr/local/bluedon/conf/mgt_nic.txt
}

function check_mgt_port()
{
    [ -z "$MGT1" ] && return 1

    VAR=`ifconfig -a | grep $MGT1`
    [ -z "$VAR" ] && return 1

    if [ -n "$MGT2" ]; then
        VAR=`ifconfig -a | grep $MGT2`
        if [ -z "$VAR" ]; then
            return 1
        fi
    fi

    return 0
}

# Modify management port(s) ifcfg script(s)
function modify_network_scripts()
{
    WORK_DIR=$(pwd)
    cd /etc/sysconfig/network-scripts

    ETH_SCRIPTS1=`ls | grep ifcfg | grep -v lo | awk 'NR==1{print}'`
    ETH_SCRIPTS2=`ls | grep ifcfg | grep -v lo | awk 'NR==2{print}'`

    if [ -z "$ETH_SCRIPTS1" ]; then
        echo "错误：未找到管理口的配置脚本" | tee -a $OPERATION_LOG
        cd $WORK_DIR
        return 1
    fi

    # Rename MGT1 if needed
    if [ "$ETH_SCRIPTS1" != "ifcfg-$MGT1" ]; then
        mv -f $ETH_SCRIPTS1 ifcfg-$MGT1
    fi

    # Rename or create MGT2 if needed
    if [ -n "$ETH_SCRIPTS2" ]; then
        if [ -z "$MGT2" ]; then
            rm -f $ETH_SCRIPTS2
        elif [ "$ETH_SCRIPTS2" != "ifcfg-$MGT2" ]; then
            mv -f $ETH_SCRIPTS2 ifcfg-$MGT2
        fi
    else
        if [ -n "$MGT2" ]; then
            cp -f ifcfg-$MGT1 ifcfg-$MGT2
        fi
    fi

    # Modify management port(s) ifcfg script(s)
    if [ -n "$MGT1" ]; then
        MACADDR=`ifconfig $MGT1 | grep ether | awk '{print toupper($2)}'`
        eval sed -i 's/^HWADDR.*$/HWADDR=$MACADDR/g' ifcfg-$MGT1
        eval sed -i 's/^NAME.*$/NAME=$MGT1/g' ifcfg-$MGT1
        sed -i 's/^IPADDR.*$/IPADDR=192.168.0.1/g' ifcfg-$MGT1
    fi

    if [ -n "$MGT2" ]; then
        MACADDR=`ifconfig $MGT2 | grep ether | awk '{print toupper($2)}'`
        eval sed -i 's/^HWADDR.*$/HWADDR=$MACADDR/g' ifcfg-$MGT2
        eval sed -i 's/^NAME.*$/NAME=$MGT2/g' ifcfg-$MGT2
        sed -i 's/^IPADDR.*$/IPADDR=192.168.1.1/g' ifcfg-$MGT2
    fi

    cd $WORK_DIR

    return 0
}

# Management port(s) configuration for Python 
function change_python_mgt_nic()
{
    if [ -z "$MGT1" ]; then
        echo "错误：未设置管理口" | tee -a $OPERATION_LOG
    elif [ -z "$MGT2" ]; then
        echo "{\"$MGT1\": \"192.168.0.1/24\"}" > $MGT_NIC
    else
        echo "{\"$MGT1\": \"192.168.0.1/24\",\"$MGT2\": \"192.168.1.1/24\"}" > $MGT_NIC
    fi
}

function ifup_all_ports()
{
    for i in `ifconfig -a | grep flags | grep -Ev "lo|vir" | awk '{print $1}' | sed 's/://g'`
    do
        ifconfig $i up
    done
}

function set_ha_ports()
{
    read -p  "请先将网线插入HA口，后按回车键" ignored

    HA_PORT=""
    for i in `ifconfig -a | grep flags | grep -Ev "lo|vir" | awk '{print $1}' | sed 's/://g'`
    do
        if [ $(ethtool $i | grep "Link detected" | awk '{print $3}') == "yes" ]; then
            if [ "$MGT1" != "$i" ] && [ "$MGT2" != "$i" ]; then
                HA_PORT=$i && break
            fi
		fi
    done

    if [ -z "$HA_PORT" ]; then
        echo "错误：HA口未连接到网络" | tee -a $OPERATION_LOG
        return 1
    fi

    if [ -n "$HA_PORT" ]; then
        echo "HA口是 $HA_PORT" | tee -a $OPERATION_LOG
        echo $HA_PORT > $HA_SCRIPT
    fi

    return 0
}

function set_one_mgt_port()
{
    read -p "请先将网线插入管理口，后按回车键" ignored

    for i in `ifconfig -a | grep flags | grep -Ev "lo|vir" | awk '{print $1}' | sed 's/://g'`
    do
        if [ $(ethtool $i | grep "Link detected" | awk '{print $3}') == "yes" ]; then
            if [ -z "$MGT1" ]; then
                MGT1=$i && break
            elif [ -z "$MGT2" ] && [ "$MGT1" != "$i" ]; then
                MGT2=$i && break
            fi
		fi
    done

    if [ -z "$MGT1" ] && [ -z "$MGT2" ]; then
        echo "错误：管理口未连接到网络" | tee -a $OPERATION_LOG
        return 1
    fi

    [ -n "$MGT1" ] && echo "管理口1是 $MGT1" | tee -a $OPERATION_LOG
    [ -n "$MGT2" ] && echo "管理口2是 $MGT2" | tee -a $OPERATION_LOG

    return 0
}

function set_mgt_ports()
{
    MGT1=""
    MGT2=""

    while true
    do
        echo "[1] 继续设置管理口" | tee -a $OPERATION_LOG
        echo "[2] 返回上一级菜单" | tee -a $OPERATION_LOG
        read -p "请选择：" OPT
        echo  "请选择：$OPT" >> $OPERATION_LOG

        [ -z "$OPT" ] && continue

        VAR=`echo $OPT | grep "[^0-9]"`
        [ -n "$VAR" ] && continue

        if [ $OPT -eq 1 ]; then
            set_one_mgt_port;
        elif [ $OPT -eq 2 ]; then
            break
        fi
    done

    modify_network_scripts;

    change_python_mgt_nic;

    return 0
}

function set_one_service_port()
{
    read -p "请先将网线插入业务口，后按回车键" ignored

    $DPDK_NIC_BIND --status | sed -rn 's, .* if=([^ ]*).*,\1,p' | sed 's,\(.\{12\}\),\1 ,' | while read i
    do
        PCI_ADDR=`echo $i | awk '{print $1}'`
        IF_NAME=`echo $i | awk '{print $2}'`

        if [ "$IF_NAME" == "$MGT1" ] || [ "$IF_NAME" == "$MGT2" ] || [ "$IF_NAME" == "$HA_PORT" ]; then
            continue;
        fi

        if [ $(ethtool $IF_NAME | grep "Link detected" | awk '{print $3}') == "yes" ]; then
            if [ -z $(cat $PCI_CONF | grep "$PCI_ADDR") ]; then
                echo "$PCI_ADDR" >> $PCI_CONF
                echo "第$(cat $PCI_CONF | wc -l)个业务口是 $IF_NAME ，设置完成" | tee -a $OPERATION_LOG
            fi
        fi
    done

    return 0
}

function set_service_ports()
{
    # check if mp_server is running
    VAR=`ps -ef | grep mp_server | grep -v grep`
    if [ -n "$VAR" ]; then
        echo "错误：部分业务口已启用无法进行设置"
        return 1
    fi

    # Clear pci.conf
    rm -f $PCI_CONF
    touch $PCI_CONF

    while true
    do
        echo "[1] 继续设置业务口" | tee -a $OPERATION_LOG
        echo "[2] 返回上一级菜单" | tee -a $OPERATION_LOG
        read -p "请选择：" OPT
        echo  "请选择：$OPT" >> $OPERATION_LOG

        [ -z "$OPT" ] && continue

        VAR=`echo $OPT | grep "[^0-9]"`
        [ -n "$VAR" ] && continue

        if [ $OPT -eq 1 ]; then
            set_one_service_port;
        elif [ $OPT -eq 2 ]; then
            break
        fi
    done

    VAR=`cat $PCI_CONF | wc -l`
    echo "共设置了 $VAR 个业务口" | tee -a $OPERATION_LOG

    return 0
}

# input format: mgt | service ports     | service ports...
# example:      1,2 | 1,2,3,4 / 5,6,7,8 | 9,10
#                   |<-     socket    ->|
#                   |<- slot->|
#                   |port 1234|port 5678|                  
function set_web_ports()
{
    check_mgt_port
    if [ $? -ne 0 ]; then
        echo "必须先配置好管理口" | tee -a $OPERATION_LOG
        return 1
    fi

    read -p "请输入web首页网口排布：" OPT
    [ -z "$OPT" ] && return 1

    echo  "请输入web首页网口排布：$OPT" >> $OPERATION_LOG

    # figure out number of pci sockets
    VAR=`echo $OPT | tr -cd "|" | wc -c`
    if [ $VAR -eq 0 ]; then
        echo "错误：至少要有两个PCI插槽" && return 1
    fi
    let VAR++;

    TOTAL_PORTS=`ifconfig -a | grep flags | grep -Ev "lo|vir" | wc -l`

    echo "[{" > $WEB_PORTS

    for ((i = 1; i <= $VAR; i++))
    do
        ONE_LINE="\"$i\":{"

        PCI_SOCKET=`echo $OPT | awk -F"|" '{print $'$i'}'`
        if [ -z "$PCI_SOCKET" ]; then
            echo "错误：输入的PCI插槽格式有误" | tee -a $OPERATION_LOG
            return 1
        fi

        # the first pci socket holds mgt ports
        if [ $i -eq 1 ]; then
            # port must be integer
            if [ -n "$(echo $PCI_SOCKET | awk -F"," '{print $1$2}' | grep "[^0-9]")" ]; then
                echo "错误：网口号必须是整数" && return 1
            fi

            [ -n "$MGT1" ] && ONE_LINE+="\"1\":\"$MGT1\""
            [ -n "$MGT2" ] && ONE_LINE+=",\"3\":\"$MGT2\""
            [ -n "$HA_PORT" ] && ONE_LINE+=",\"3\":\"$HA_PORT\""
            ONE_LINE+="},"
            echo $ONE_LINE >> $WEB_PORTS
            continue
        fi

        # figure out number of pci slots
        VAR2=`echo $PCI_SOCKET | tr -cd "/" | wc -c`
        let VAR2++

        for ((j = 1; j <= $VAR2; j++))
        do
            PCI_SLOT=`echo $PCI_SOCKET | awk -F"/" '{print $'$j'}'`
            if [ -z "$PCI_SLOT" ]; then
                echo "错误：输入的PCI子槽格式有误" | tee -a $OPERATION_LOG
                return 1
            fi

            # figure out number of ports
            NR_PORTS=`echo $PCI_SLOT | tr -cd "," | wc -c`
            let NR_PORTS++

            # Currently we support only two slots for one socket
            n=1
            [ $j -gt 1 ] && n=2

            for ((k = 1; k <= $NR_PORTS; k++))
            do
                PORT=`echo $PCI_SLOT | awk -F"," '{print $'$k'}' | sed 's/ //g'`
                if [ -z "$PORT" ]; then
                    echo "错误：输入的网口格式不对" | tee -a $OPERATION_LOG
                    return 1
                fi

                # port must be integer
                if [ -n "$(echo $PORT | grep "[^0-9]")" ]; then
                    echo "错误：网口号必须是整数" && return 1
                fi

                let PORT--
                if [ $PORT -lt 0 ] || [ $PORT -gt $TOTAL_PORTS ]; then
                    echo "错误：输入的网口序号超出范围" | tee -a $OPERATION_LOG
                    return 1
                fi

                ONE_LINE+="\"$n\":\"vEth$PORT\","
                let n=n+2
            done
        done

        # remove the last comma ','
        ONE_LINE=`echo $ONE_LINE | sed 's/.$//'`
        ONE_LINE+="},"
        echo $ONE_LINE >> $WEB_PORTS
    done

    echo "}]" >> $WEB_PORTS
    echo "完成" | tee -a $OPERATION_LOG

    return 0
}

# Jobs that done automatically, which must follow after manual jobs
function auto_jobs()
{
    check_mgt_port
    if [ $? -ne 0 ]; then
        echo "必须先配置好管理口" | tee -a $OPERATION_LOG
        return 1
    fi

    KERNEL_PORT="lo|vir"
    [ -n "$MGT1" ] && KERNEL_PORT+="|$MGT1"
    [ -n "$MGT2" ] && KERNEL_PORT+="|$MGT2"
    [ -n "$HA_PORT" ] && KERNEL_PORT+="|$HA_PORT"
    eval sed -i 's/^KERNEL_PORT.*$/KERNEL_PORT=\"$KERNEL_PORT\"/g' $DPDK_INIT

    VAR=`ls $SERVER_DIR | grep "\.c"`
    if [ -n "$VAR" ]; then
        # Patch device and modify source code if needed
        sh device_dependency_patcher.sh >> $OPERATION_LOG 2>&1 
        if [ $? -ne 0 ]; then
            echo "错误：设备硬件依赖性检查失败" | tee -a $OPERATION_LOG
            return 1
        fi

        # Some platform must be rebuilt, or dpdk will not work
sh build_platform.sh >> $OPERATION_LOG 2>&1 << _EOT
1
2
19
_EOT
        if [ $? -ne 0 ]; then
            echo "错误：平台代码编译失败" | tee -a $OPERATION_LOG
            return 1
        fi
    fi

    # Backward compat for previous version
    backward_compat;

    # Uncomment rc.local
    commented=`cat $RC_LOCAL | grep touch | awk 'NR==1{print $1}'`
    if [ "$commented" != "touch" ]; then
        if [ -f "$ENABLE_SERVICE" ]; then
            sed -i "/touch/,+20s/#//" $RC_LOCAL
            sed -i "/ids-ipt/,+1s/#//" $RC_LOCAL
        else
            sed -i "/touch/,+100s/#//" $RC_LOCAL
        fi
    fi

    # Uncomment crontab
    commented=`cat $CRONTAB | grep disable | awk 'NR==1{print $1}'`
    if [ "$commented" != "#disable" ]; then
        if [ -f "$ENABLE_SERVICE" ]; then
            sed -i "/bd_dpdk_warper/s/#//" $CRONTAB
            sed -i "/bdwaf_restart/s/#//" $CRONTAB
        else
            sed -i "/disable/,+100s/#//" $CRONTAB
        fi
    fi

    # Save hardware informations
    cat /proc/cpuinfo > /root/cpuinfo.txt
    cat /proc/meminfo > /root/meminfo.txt
    lspci | grep Eth  > /root/ethinfo.txt

    return 0
}

function factory_reset()
{
    mysqld_multi start 1-2 > /dev/null 2>&1 &

    for ((i = 0; i < 5; i++))
    do
        sleep 1
        VAR=`ps -ef | grep mysql3306 | grep -v grep`
        [ -n "$VAR" ] && break
    done
    
    python /usr/local/bluedon/core/second_firewall_reset.py firewall > /dev/null 2>&1
}

function show_help()
{
    echo "============================== " | tee -a $OPERATION_LOG
    echo "[$USR_SEL_MGTPORT] 设置管理口" | tee -a $OPERATION_LOG
    echo "[$USR_SEL_HAPORT] 设置HA口" | tee -a $OPERATION_LOG
    echo "[$USR_SEL_SVRPORT] 设置业务口" | tee -a $OPERATION_LOG
    echo "[$USR_SEL_WEBPORT] 设置web首页网口排版" | tee -a $OPERATION_LOG
    echo "[$USR_SEL_SAVE] 保存设置" | tee -a $OPERATION_LOG
    echo "[$USR_SEL_RESET] 复位设置" | tee -a $OPERATION_LOG
    echo "[$USR_SEL_EXIT] 退出" | tee -a $OPERATION_LOG
    echo -e "请选择 : \c "

    read OPT
    echo "请选择 : $OPT" >> $OPERATION_LOG

    # User input must be an integer
    if [[ $OPT =~ ^[0-9]{1,}$ ]]; then
        return $OPT
    fi

    return 0
}

#########################################################

# Do initialization
init;

while true
do
    show_help
    USER_SEL=$?
	
    if [ $USER_SEL -eq $USR_SEL_RESET ]; then
        reset;
    elif [ $USER_SEL -eq $USR_SEL_EXIT ]; then
        break;
    elif [ $USER_SEL -eq $USR_SEL_MGTPORT ]; then
        set_mgt_ports;
    elif [ $USER_SEL -eq $USR_SEL_HAPORT ]; then
        set_ha_ports;
    elif [ $USER_SEL -eq $USR_SEL_SVRPORT ]; then
        set_service_ports;
    elif [ $USER_SEL -eq $USR_SEL_WEBPORT ]; then
        set_web_ports;
    elif [ $USER_SEL -eq $USR_SEL_SAVE ]; then
        echo "正在保存配置，请稍后。。。" | tee -a $OPERATION_LOG
        auto_jobs;
        if [ $? -eq 0 ]; then 
            #sh clean_code.sh >> $OPERATION_LOG 2>&1
            [ -f "$ENABLE_SERVICE" ] && sh $ENABLE_SERVICE
            echo "配置完成等待设备重启，请稍后。。。" | tee -a $OPERATION_LOG
            factory_reset;
        fi
    else
        echo "输入错误，请重新选择。"
        continue;
    fi

done

