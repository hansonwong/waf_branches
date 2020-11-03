#! /bin/sh
#
# Provides:          backup.sh
# Description:       backup the device for future restoring in case critical error happens
#                   
# Author: Claus Wei <zhongwei@yxlink.com>
#
# Usage:  
#   backup.sh 
#   
#   
#


#add by xiayuying 20140725 
#Before backup, check nvs system and clear unuse files
/usr/bin/python /var/waf/CheckInstance.py

# must stop mysql before backup... otherwise mysql transaction will be corrupted and mysql may occupy 100% CPU usage by chance.
service mysql stop

FAILURE=0
/bin/tar -cz --same-owner --same-permissions --numeric-owner -f /var/waf/var.tar.gz --exclude=/var/waf/var.tar.gz --exclude=/var/waf/etc.tar.gz --exclude=/var/run --exclude=/var/cache --exclude=/var/log --exclude=/var/lock --exclude=/var/spool --exclude=/var/lib/mysql/waf_hw/alert_* --exclude=/var/lib/mysql/waf_hw/flow_* --exclude=/var/lib/mysql/waf_hw/pagestat_* --exclude=/var/lib/mysql/waf_hw/querywhere*   /var  > /var/waf/backup_var.log 2>&1
FAILURE=$?
echo "Backup result: $FAILURE"
if [ $FAILURE -ne 0 ]; then
	/usr/bin/logger -t backup "产品备份失败，错误代码1, $FAILURE"
	echo "failed to setup device backup point, please check..."
fi


FAILURE=0
/bin/tar -cz --same-owner --same-permissions --numeric-owner -f /var/waf/etc.tar.gz --exclude=/var/waf/var.tar.gz --exclude=/var/waf/etc.tar.gz  /etc   > /var/waf/backup_etc.log 2>&1
FAILURE=$?
echo "Backup result: $FAILURE"
if [ $FAILURE -ne 0 ]; then
	/usr/bin/logger -t backup "产品备份失败，错误代码2, $FAILURE"
	echo "failed to setup device backup point, please check..."
fi

service mysql start





