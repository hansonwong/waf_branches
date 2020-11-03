#!/bin/bash

# the following files would be modified for serial login
GRUB_CFG=/boot/grub2/grub.cfg
INITTAB=/etc/inittab
PROFILE=/etc/profile
SECURETTY=/etc/securetty
BASH_PROFILE=/home/admin/.bash_profile
BDCLI=/home/admin/bd_cli/bdcli

# set bdcli to have root priviledge
chmod u+s /home/admin/bd_cli/bdcli

# start ttyS0 when booting the kernel
VARS=`cat $GRUB_CFG | grep ttyS0`
if [ -z "$VARS" ]; then
    VARS="ttyS0 not set in grub.cfg"
fi
echo $VARS

# set serial login environment
VARS=`cat $INITTAB | grep -w ttyS0`
if [ -z "$VARS" ]; then
    VARS="s0:12345:respawn:/sbin/agetty -L 9600 ttyS0 vt100" 
    echo $VARS >> $INITTAB
fi
echo $VARS

# allow user login by ttyS0
VARS=`tail -n 1 $SECURETTY`
if [ "ttyS0" != "$VARS" ]; then
    VARS="ttyS0"
    echo $VARS >> $SECURETTY
fi
echo $VARS

# execute bdcli before user login
VARS=`tail -n 1 $BASH_PROFILE | awk '{print $2}'`
if [ "$BDCLI" != "$VARS" ]; then
    VARS="exec $BDCLI"
    echo $VARS >> $BASH_PROFILE
fi
echo $VARS

# set login timeout
VARS=`cat $PROFILE | grep TMOUT`
if [ -z "$VARS" ]; then
    if [ $# == 2 ] && [ "$1" == "tmout" ]; then
        VARS="export TMOUT=$2"
        echo $VARS >> $PROFILE
    fi
fi
echo $VARS

