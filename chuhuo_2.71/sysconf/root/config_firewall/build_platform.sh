#!/bin/bash
#
# Copyright (C) Bluedon, 2016
# Author: Linfan Hu (hlf@chinabluedon.cn)
# Date: 2016/11/17
#

# Check if update is in progress
VAR=`ps -ef | grep "$0" | grep -Ev "grep|$$" | wc -l`
if [ $VAR -gt 0 ]; then
    echo "Error: $0 in progress"
    exit 1
fi

# constant data definition
USR_SEL_DPDK=1
USR_SEL_DPDK_WARPER=2
USR_SEL_POLICY=3
USR_SEL_AVSCAN=4
USR_SEL_IPS=5
USR_SEL_WAF=6
USR_SEL_SNORT=7
USR_SEL_USR_AUTH=8
USR_SEL_ANTI_DETECT=9
USR_SEL_IPSECVPN=10
USR_SEL_SSLVPN=11
USR_SEL_ALL=12
USR_SEL_EXIT=19

#
# Source packages default directories
# You can specify these through script parameters
# packages functionality:
# suricata => ips engine
# nginx-1.4.4 => waf engine
# snort => anti-scan engine
#
DPDK_DIR=/home/ng_platform/dpdk-1.8.0/
DPDK_WARPER_DIR=/home/ng_platform/bd_dpdk_warper/
POLICY_DIR=/home/ng_platform/policyevolve/
IPS_DIR=/home/suricata/
WAF_DIR=/home/bdwaf/nginx-1.4.4/
SNORT_DIR=/home/tools/snort-2.9.8.0/
DAQ_DIR=/home/tools/daq-2.0.6/
USR_AUTHEN_DIR=/home/ng_platform/user_authentication/
AVSCAN_DIR=/home/tools/av_install_package/
ANTI_DETECT_DIR=/home/tools/antidetect-rec/
IPSECVPN_DIR=/home/tools/vpn/ipsec-guomi/
SSLVPN_DIR=

# log file path
BUILD_LOG=/home/ng_platform/build_platform.log
STATUS=/dev/null

# Signal handler: do cleanup
trap "exit 1" INT QUIT TERM STOP TSTP KILL

# Parse command line and redirect source pakages if needed
for i in $@
do
    VAR=`echo $i | awk -F"=" '{print $1}'`
    if [ "$VAR" == "dpdk" ]; then
        DPDK_DIR=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "dpdk_warper" ]; then
        DPDK_WARPER_DIR=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "policy" ]; then
        POLICY_DIR=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "ips" ]; then
        IPS_DIR=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "waf" ]; then
        WAF_DIR=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "snort" ]; then
        SNORT_DIR=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "daq" ]; then
        DAQ_DIR=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "user_auth" ]; then
        USR_AUTHEN_DIR=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "avscan" ]; then
        AVSCAN_DIR=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "anti_detect" ]; then
        ANTI_DETECT_DIR=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "ipsecvpn" ]; then
        IPSECVPN_DIR=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "sslvpn" ]; then
        SSLVPN_DIR=`echo $i | awk -F"=" '{print $2}'`
    elif [ "$VAR" == "status" ]; then
        STATUS=`echo $i | awk -F"=" '{print $2}'`
    fi
done

# export DPDK environment
unset RTE_SDK
export RTE_SDK=$DPDK_DIR

# build dpdk target
function build_dpdk()
{
    if [ ! -d "$DPDK_DIR" ]; then
        echo "Error: DPDK souce package not found"
        return 1
    fi

    cd $DPDK_DIR

    echo "Building DPDK SDK..."

    make -j4 install T=x86_64-native-linuxapp-gcc > /dev/null 2>$BUILD_LOG
    cat $BUILD_LOG

    VAR=`cat $BUILD_LOG | grep -iw error`
    [ -n "$VAR" ] && return 1

    echo "Done."

    return 0
}

# build dpdk warper
function build_dpdk_warper()
{
    if [ ! -d "$DPDK_WARPER_DIR" ]; then
        echo "Error: DPDK warper souce package not found"
        return 1
    fi

    cd $DPDK_WARPER_DIR

    echo "Building DPDK WARPER..."

    \cp -rf lib2/ndpi/pem /etc/
    \cp -rf lib2/ndpi/lib/* /lib/
    ldconfig

    sh dpdk_warper.sh > /dev/null 2>$BUILD_LOG
    cat $BUILD_LOG

    VAR=`cat $BUILD_LOG | grep -iw error`
    [ -n "$VAR" ] && return 1

    # sanity check
    [ ! -x "/home/ng_platform/bd_dpdk_warper/server/mp_server" ] && return 1

    echo "Done."

    return 0
}

function build_policy_evolve()
{
    if [ ! -d "$POLICY_DIR" ]; then
        echo "Error: policy evolve souce package not found"
        return 1
    fi

    cd $POLICY_DIR

    echo "Building policy evolve..."

    chmod a+x *.sh

    make > /dev/null 2>$BUILD_LOG
    cat $BUILD_LOG

    VAR=`cat $BUILD_LOG | grep -iw error`
    [ -n "$VAR" ] && return 1

    # sanity check
    [ ! -x "/home/ng_platform/policyevolve/nftse" ] && return 1

    echo "Done."

    return 0
}

# build ips
function build_ips()
{
    if [ ! -d "$IPS_DIR" ]; then
        echo "Error: IPS souce package not found"
        return 1
    fi

    cd $IPS_DIR
    chmod a+x -R *

    echo "Building IPS..."

    if [ -e "/home/suricata/install-ips" ]; then
        \cp -f configure-bdpi configure
        sh /home/suricata/install-ips > /dev/null 2>$BUILD_LOG
    else
        # check directories(provided by Libing)
        [ -d "/var/suricata/fw/http" ] || mkdir -p /var/suricata/fw/http
        [ -d "/var/suricata/fw/ftp" ] || mkdir -p /var/suricata/fw/ftp
        [ -d "/var/suricata/fw/mail" ] || mkdir -p /var/suricata/fw/mail
        [ -d "/var/suricata/audit/http" ] || mkdir -p /var/suricata/audit/http
        [ -d "/var/suricata/audit/ftp" ] || mkdir -p /var/suricata/audit/ftp
        [ -d "var/suricata/audit/mail" ] || mkdir -p /var/suricata/audit/mail

        make clean > /dev/null 2>&1
        sh cpl.sh  > /dev/null 2>&1
        make -j4 > /dev/null 2>$BUILD_LOG
    fi

    cat $BUILD_LOG
    VAR=`cat $BUILD_LOG | grep -iw error`
    [ -n "$VAR" ] && return 1

    # sanity check
    if [ -e "/home/suricata/install-ips" ]; then
        [ ! -x "/usr/local/bdips/bin/bdips" ] && return 1
    else
        [ ! -x "/home/suricata/src/suricata" ] && return 1
    fi

    echo "Done."

    return 0
}

# build waf
function build_waf()
{
    if [ ! -d "$WAF_DIR" ]; then
        echo "Error: WAF souce package not found"
        return 1
    fi

    cd $WAF_DIR

    echo "Building WAF..."

    chmod 777 -R *
    make clean  > /dev/null 2>&1
    sh premake.sh > /dev/null 2>&1

    make -j4 install > /dev/null 2>$BUILD_LOG
    cat $BUILD_LOG

    VAR=`cat $BUILD_LOG | grep -iw error`
    [ -n "$VAR" ] && return 1

    killall -9 bdwaf  > /dev/null 2>&1
    cd /usr/local/bdwaf/sbin
    \cp -f nginx bdwaf

    # sanity check
    [ ! -x "/usr/local/bdwaf/sbin/bdwaf" ] && return 1

    echo "Done."

    return 0
}

# build snort
function build_snort()
{
    if [ ! -d "$SNORT_DIR" ]; then
        echo "Error: Snort souce package not found"
        return 1
    fi

    if [ ! -d "$DAQ_DIR" ]; then
        echo "Error: Missing daq"
        return 1
    fi

    cd $SNORT_DIR
    chmod a+x -R *
    chmod a+x -R $DAQ_DIR

    echo "Building snort..."

    killall -9 snort  > /dev/null 2>&1

    sh build.sh > /dev/null 2>$BUILD_LOG
    cat $BUILD_LOG

    VAR=`cat $BUILD_LOG | grep -iw error`
    [ -n "$VAR" ] && return 1

    # sanity check
    [ ! -x "/etc/snort/bin/snort" ] && return 1

    echo "Done."

    return 0
}

# build user authentication
function build_usr_authen()
{
    if [ ! -d "$USR_AUTHEN_DIR" ]; then
        echo "Error: User authentication souce package not found"
        return 1
    fi

    cd $USR_AUTHEN_DIR

    echo "Building user authentication..."

    killall -9 user_attestation  > /dev/null 2>&1

    sh install.sh > /dev/null 2>$BUILD_LOG
    cat $BUILD_LOG

    VAR=`cat $BUILD_LOG | grep -iw error`
    [ -n "$VAR" ] && return 1

    # sanity check
    [ ! -x "/usr/bin/userauth/user_attestation" ] && return 1

    echo "Done."

    return 0
}

# build av scan
function build_avscan()
{
    if [ ! -d "$AVSCAN_DIR" ]; then
        echo "Error: av scan souce package not found"
        return 1
    fi

    echo "Building av scan..."

    cd $AVSCAN_DIR/src/avsdk/v8/
    make clean  > /dev/null 2>&1
    make > /dev/null 2>$BUILD_LOG
    VAR=`cat $BUILD_LOG | grep -iw error`
    [ -n "$VAR" ] && return 1

    cd $AVSCAN_DIR/sh/
    sh av_update.sh > /dev/null 2>$BUILD_LOG
    VAR=`cat $BUILD_LOG | grep -iw error`
    [ -n "$VAR" ] && return 1

    echo "Done."

    return 0
}

# build anti detect
function build_anti_detect()
{
    if [ ! -d "$ANTI_DETECT_DIR" ]; then
        echo "Error: anti detect souce package not found"
        return 1
    fi

    echo "Building anti detect..."

    cd $ANTI_DETECT_DIR
    make > /dev/null 2>$BUILD_LOG
    VAR=`cat $BUILD_LOG | grep -iw error`
    [ -n "$VAR" ] && return 1

    # sanity check
    [ ! -x "./antidetect" ] && return 1

    [ ! -d "/etc/antidetect/" ] || mkdir -p /etc/antidetect
    \cp -rf ./antidetect /etc/antidetect/antidet

    echo "Done."

    return 0
}

# build ipsec vpn
function build_ipsecvpn()
{
    if [ ! -d "$IPSECVPN_DIR" ]; then
        echo "Error: ipsec vpn souce package not found"
        return 1
    fi

    echo "Building ipsec vpn..."

    cd $IPSECVPN_DIR

    sh install.sh > /dev/null 2>$BUILD_LOG
    VAR=`cat $BUILD_LOG | grep -iw error`
    [ -n "$VAR" ] && return 1

    # sanity check
    [ ! -x "/usr/local/ipsec-vpn/sbin/racoon" ] && return 1

    echo "Done."

    return 0
}

# build ssl vpn
function build_sslvpn()
{
    # please FIXME
    return 0
}

# arguement: user selection
function build_platform()
{
    if [ $1 -eq $USR_SEL_DPDK ]; then
        build_dpdk
        if [ $? -ne 0 ]; then
            echo "build_dpdk_fail" | tee $STATUS
            return 1
        fi
    elif [ $1 -eq $USR_SEL_DPDK_WARPER ]; then
        build_dpdk_warper
        if [ $? -ne 0 ]; then
            echo "build_dpdk_warper_fail" | tee $STATUS
            return 1
        fi
    elif [ $1 -eq $USR_SEL_POLICY ]; then
        build_policy_evolve
        if [ $? -ne 0 ]; then
            echo "build_policy_evolve_fail" | tee $STATUS
            return 1
        fi
    elif [ $1 -eq $USR_SEL_IPS ]; then
        build_ips
       if  [ $? -ne 0 ]; then
           echo "build_ips_fail" | tee $STATUS
           return 1
       fi
    elif [ $1 -eq $USR_SEL_WAF ]; then
        build_waf
        if [ $? -ne 0 ]; then
            echo "build_waf_fail" | tee $STATUS
            return 1
        fi
    elif [ $1 -eq $USR_SEL_SNORT ]; then
        build_snort
        if [ $? -ne 0 ]; then
            echo "build_snort_fail" | tee $STATUS
            return 1
        fi
    elif [ $1 -eq $USR_SEL_USR_AUTH ]; then
        build_usr_authen
        if [ $? -ne 0 ]; then
            echo "build_user_authen_fail" | tee $STATUS
            return 1
        fi
    elif [ $1 -eq $USR_SEL_AVSCAN ]; then
        build_avscan
        if [ $? -ne 0 ]; then
            echo "build_avscan_fail" | tee $STATUS
            return 1
        fi
    elif [ $1 -eq $USR_SEL_ANTI_DETECT ]; then
        build_anti_detect
        if [ $? -ne 0 ]; then
            echo "build_anti_detect_fail" | tee $STATUS
            return 1
        fi
    elif [ $1 -eq $USR_SEL_IPSECVPN ]; then
        build_ipsecvpn
        if [ $? -ne 0 ]; then
            echo "build_ipsecvpn_fail" | tee $STATUS
            return 1
        fi
    elif [ $1 -eq $USR_SEL_SSLVPN ]; then
        build_sslvpn
        if [ $? -ne 0 ]; then
            echo "build_sslvpn_fail" | tee $STATUS
            return 1
        fi
    elif [ $1 -eq $USR_SEL_ALL ]; then
        build_dpdk
        [ $? -ne 0 ] && return 1

        build_dpdk_warper
        [ $? -ne 0 ] && return 1

        build_policy_evolve
        [ $? -ne 0 ] && return 1

        build_ips
        [ $? -ne 0 ] && return 1

        build_waf
        [ $? -ne 0 ] && return 1

        build_snort
        [ $? -ne 0 ] && return 1

        build_usr_authen
        [ $? -ne 0 ] && return 1

        build_avscan
        [ $? -ne 0 ] && return 1

        build_anti_detect
        [ $? -ne 0 ] && return 1

        build_ipsecvpn
        [ $? -ne 0 ] && return 1

        build_sslvpn
        [ $? -ne 0 ] && return 1
    fi

    return 0
}

function show_help
{
    echo "============================== "
    echo "[$USR_SEL_DPDK] Build DPDK"
    echo "[$USR_SEL_DPDK_WARPER] Build DPDK warper"
    echo "[$USR_SEL_POLICY] Build policy evolve"
    echo "[$USR_SEL_AVSCAN] Build av scan"
    echo "[$USR_SEL_IPS] Build IPS"
    echo "[$USR_SEL_WAF] Build WAF"
    echo "[$USR_SEL_SNORT] Build Snort"
    echo "[$USR_SEL_USR_AUTH] Build user authentication"
    echo "[$USR_SEL_ANTI_DETECT] Build anti-detect"
    echo "[$USR_SEL_IPSECVPN] Build ipsec vpn"
    echo "[$USR_SEL_SSLVPN] Build ssl vpn"
    echo "[$USR_SEL_ALL] Build all"
    echo "[$USR_SEL_EXIT] Exit"
    echo -e "Select option:\c "

    read OPT

    # User input must be an integer
    if [[ $OPT =~ ^[0-9]{1,}$ ]]; then
        return $OPT
    fi

    return 0
}

# Main task starts from here
while :
do
    show_help
    USER_SEL=$?

    if [ $USER_SEL -eq 0 ]; then
        continue
    elif [ $USER_SEL -eq $USR_SEL_EXIT ]; then
        break
    fi

    build_platform $USER_SEL
    if [ $? -ne 0 ]; then
        exit 1
    fi
done

echo "Succeed building platform"
exit 0

