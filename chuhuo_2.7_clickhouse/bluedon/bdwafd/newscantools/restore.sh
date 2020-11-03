#! /bin/sh
#
# Provides:          restore.sh
# Description:       restore the device with backup tar ball
#                   
# Author: Claus Wei <zhongwei@yxlink.com>
#
# Usage:  
#   restore.sh 
#   
#   
# 


clean_files_when_restore () {

	# clean some dirs

	echo "Remove the apache logs"
	/bin/rm -rf /var/log/apache2/*    

	echo "Remove all the other system and application logs"
	/bin/rm -rf /var/log/*.gz  /var/log/*.log  /var/log/*.log.1  /var/log/*.log.2  /var/log/*.log.3

	/bin/rm -rf /tmp/*

	echo "Remove waf logs"
	/bin/rm -rf /var/waf/*.log /var/waf/*.log.1

	echo "cgi and fcgi logs"
	/bin/rm -rf /var/www/fcgi-bin/*.log /var/www/fcgi-bin/*.log.1 /var/www/cgi-bin/*.log /var/www/cgi-bin/*.log.1

	#Add by xiayuying 2014-01-27
	service nvscand restart
	echo "Remove nvscand logs"
	>/opt/nvscan/var/nvscan/logs/nvscand.dump
	>/opt/nvscan/var/nvscan/logs/nvscand.messages
	>/opt/nvscan/var/nvscan/logs/www_server.log

	echo "Remove nvscand tmp report"
	/bin/rm -rf /opt/nvscan/var/nvscan/users/admin/files/*
	/bin/rm -rf /opt/nvscan/var/nvscan/users/admin/reports/*
	#End

}

add_wafcon_log () {
	#add /var/log/wafcon.log
	if [ ! -e /var/log/wafcon.log ]; then
		echo "touch /var/log/wafcon.log "
		touch /var/log/wafcon.log
		chown conadmin /var/log/wafcon.log
		chgrp conadmin /var/log/wafcon.log
	fi
}



truncate_waf_hw_tables_if_needed () {

	# avoid some wtf web sites are created after backup.
	if [ -e /wtfdata ]; then
		echo "Clear /wtfdata dir"
		/bin/rm -rf /wtfdata  > /dev/null 2>&1
		echo ""
	else
		echo ""
	fi


	if [ -e /wtfdb_sql ]; then
		echo "Clear /wtfdb_sql dir"
		/bin/rm -rf /wtfdb_sql  > /dev/null 2>&1
		echo ""
	else
		echo ""
	fi


	if [ ! -z $DB_ROOT_USER -a ! -z DB_ROOT_PASSWD ]; then

		echo "clear tables: waf_hw.tamper, waf_hw.tamper_db_conn, waf_hw.tamper_db_info, waf_hw.fakelog"
		# clear waf_hw.tamper table 
		FAILURE=0
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h127.0.0.1 -e "truncate table waf_hw.tamper; truncate table waf_hw.tamper_db_conn; truncate table waf_hw.tamper_db_info;  truncate table waf_hw.fakelog"
		if [ $FAILURE -ne 0 ]; then
			/usr/bin/logger -t restore "产品复位失败，错误代码3"
			echo "产品复位失败，错误代码3"
		fi

	fi
}



###############################################################################################



echo "restore the device with device backup point data"

err_msg_type="restore"


######### shall we consider the license file ##########
# /etc/waf.lic
# /etc/license.count


if [ -e /var/waf/etc.tar.gz ]; then

 	/bin/rm -rf /etc/init.d/*

	FAILURE=0
	/bin/tar xfz  /var/waf/etc.tar.gz -C /   > /var/waf/restore_etc.log 2>&1
	FAILURE=$?
	if [ $FAILURE -ne 0 ]; then
		/usr/bin/logger -t restore "产品复位失败，错误代码1"
		echo  "产品复位失败，错误代码1"
	fi
fi


if [ -e /var/waf/var.tar.gz ]; then

	clean_files_when_restore 
	service nvscand restart
	add_wafcon_log

	service wafmgr.sh stop
	if [ -x "/etc/init.d/wafwd.sh" ]; then 
		echo "stop wafwd daemon..."

		/etc/init.d/wafwd.sh stop
	fi
	service apache2 stop
	service mysql stop

	echo "kill all python process"
	kill $(ps -ef|grep 'python'|awk '$0 !~/grep/ {print $2}' |tr -s '\\n' ' ') 

	echo "umount /var/webs/task*.img"
	umount /var/webs/task*.img
	echo "rm -rf /var/webs/task*"
	rm -rf /var/webs/task*
	if [ `mount | grep '/var/webs/scanlog' | grep -v grep | wc -l` -eq 0 ] ;then
		mount -o loop /var/webs/scanlog.img /var/webs/scanlog
	fi
	echo "rm -rf /var/webs/scanlog"
	rm -rf /var/webs/scanlog/*

	# completely clear /var/www and mysql waf_hw dir
	/bin/rm -rf /var/lib/mysql/waf_hw /var/www/*

	FAILURE=0
	/bin/tar xfz  /var/waf/var.tar.gz -C /  > /var/waf/restore_var.log 2>&1
	FAILURE=$?
	if [ $FAILURE -ne 0 ]; then
		/usr/bin/logger -t restore "产品复位失败，错误代码2"
		echo "产品复位失败，错误代码2"
	fi


	echo "use install-lib.sh to collect db config"
	shelldir=`dirname $0`

	if [ ! -x "$shelldir/install-lib.sh" ]; then
		echo "no install-lib.sh"
	else
		# Import functions from common lib
		. $shelldir/install-lib.sh
	fi

	echo "get DB parameters from current device"
	get_waf_config_from_current_device

	# make sure that mysql is ready to use
	service mysql start
	echo "call truncate_waf_hw_tables_if_needed"
	# truncate_waf_hw_tables_if_needed

fi


# echo "Start update default policy"
# ####### update default policy  ##############
# if [ -e "/var/waf/nvscan_policy_manager.py" ]; then
# 	python /var/waf/nvscan_policy_manager.py update 1# > /dev/null 2>&1
# 	python /var/waf/nvscan_policy_manager.py update 2# > /dev/null 2>&1
# fi



echo "restore is finished, reboot now"
/sbin/reboot


