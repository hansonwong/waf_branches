#! /bin/sh
# Provides:          scanlog.sh
# Description:       create and mount scanlog img
#                   
# Author: HaiboYi <haiboyi@yxlink.com>
#

create_mount_img() {
    dd if=/dev/zero of=/var/webs/scanlog.img bs=1M count=4096
    echo 'y'|mkfs.ext3 -q /var/webs/scanlog.img
    mount -o loop /var/webs/scanlog.img /var/webs/scanlog
}


if [ `mount | grep '/var/webs/scanlog' | grep -v grep | wc -l` -ne 0 ] ;then
    echo "scanlog.img already mount"
    exit 0
else
    /bin/rm -rf /var/webs/scanlog >/dev/null 2>&1
    mkdir /var/webs/scanlog
    if [ -e /var/webs/scanlog.img ];then
        FAILURE=0
        mount -o loop /var/webs/scanlog.img /var/webs/scanlog
        FAILURE=$?
        if [ $FAILURE -ne 0 ]; then
            echo "mount scanlog.img error,recreate it and mount it"
            create_mount_img >/dev/null 2>&1
            exit 2
        else
            echo "scanlog.img mount ok"
            exit 3
        fi
    else
        echo "scanlog.img not found,create it and mount it"
        create_mount_img >/dev/null 2>&1
        exit 4
    fi
fi
