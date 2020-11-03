#!/bin/sh
# author: zhongwei@yxlink.com

maxmount=`/sbin/tune2fs -l /dev/sda1 | /bin/grep "Maximum mount count:" | /usr/bin/awk '{print $4}'`


if [ $maxmount -gt 1 ]; then
        echo "Next REBOOT will force disk integrity check"
	/sbin/tune2fs -l /dev/sda1 -C $maxmount  > /dev/null      
fi

