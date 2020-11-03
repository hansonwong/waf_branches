#! /bin/sh
#
# Provides:          resetwaf.sh
# Description:       when login with user "resetwaf", this script will be called.
#                    Then we call reset.sh to rest the device.
#                   
# Author: Jian Xiao <jianxiao@yxlink.com>
#
# Usage:  
#   resetwaf.sh 
#

#Firstly, beep several times indicating we are called.

echo -e "\007" >/dev/tty10;
sleep 0.2;
echo -e "\007" >/dev/tty10;
sleep 0.2;
echo -e "\007" >/dev/tty10;
sleep 0.2;
echo -e "\007" >/dev/tty10;


#Then call reset.sh to do other reset job...

if [ -x /var/waf/reset.sh ]; then
	setsid /var/waf/reset.sh
fi
