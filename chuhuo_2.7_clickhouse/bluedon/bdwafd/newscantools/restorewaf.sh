#! /bin/sh
#
# Provides:          restorewaf.sh
# Description:       when login with user "restorewaf", this script will be called.
#                    Then we call restore.sh to restore the device.
#                   
# Author: Jian Xiao <jianxiao@yxlink.com>
#
# Usage:  
#   restorewaf.sh 
#

#Firstly, beep several times indicating we are called.

if [ ! -e /var/waf/etc.tar.gz -a ! -e /var/waf/var.tar.gz ]; then
	echo "No backup point was found. Aborting..."
	exit 1
fi

echo -e "\007" >/dev/tty10;
sleep 0.2;
echo -e "\007" >/dev/tty10;
sleep 0.2;
echo -e "\007" >/dev/tty10;
sleep 0.2;
echo -e "\007" >/dev/tty10;


#Then call restore.sh to do other restore job...

if [ -x /var/waf/restore.sh ]; then
	setsid /var/waf/restore.sh
fi


