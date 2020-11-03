#! /bin/sh
#
# Provides:          reset.sh
# Description:       rest the device
#                   
# Author: Claus Wei <zhongwei@yxlink.com>
#
# Usage:  
#   reset.sh 
# error code: 100 - 199, currently 138




# error code: 100 - 110
stop_services_for_reset () {


	if [ -x "/etc/init.d/wafmgr.sh" ]; then 
		echo "stop wafmgr daemon..."

		FAILURE=0
		/etc/init.d/wafmgr.sh stop
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to stop wafmgr daemon. Aborting..."
			/var/waf/addsyslog -m "复位失败，错误代码100。"
			return 100
		fi
	fi


	if [ -x "/etc/init.d/wafwd.sh" ]; then 
		echo "stop wafwd daemon..."

		FAILURE=0
		/etc/init.d/wafwd.sh stop
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to stop wafwd daemon. Aborting..."
			/var/waf/addsyslog -m "复位失败，错误代码101。"
			return 101
		fi
	fi


	if [ -x "/etc/init.d/wafnetwork.sh" ]; then 
		# actually not necessary, because wafnetwork.sh stop don't do anything
		echo "stop waf network shell..."
		/etc/init.d/wafnetwork.sh stop   > /dev/null 2>&1
	fi

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
	
	return 0
}


# error code: 111 - 119
restart_services_for_reset() {

	# start wafnetwork.sh
	FAILURE=0
	/etc/init.d/wafnetwork.sh start
	FAILURE=$?
	if [ $FAILURE -ne 0 ]; then
		echo "failed to start wafnetwork.sh. Aborting..."
		return 111
	fi

	# start wafmgr
	echo "start the wafmgr daemon"
	FAILURE=0
	/etc/init.d/wafmgr.sh restart
	FAILURE=$?
	if [ $FAILURE -ne 0 ]; then
		echo "failed to start wafmgr daemon. Aborting..."
		return 112
	fi

	# start wafwd
	echo "start the wafwd daemon"
	FAILURE=0
	/etc/init.d/wafwd.sh restart
	FAILURE=$?
	if [ $FAILURE -ne 0 ]; then
		echo "failed to start wafwd daemon. Aborting..."
		return 113
	fi

	return 0
}


# error code: 120 - 129
reset_waf_hw_db_tables () {

	FAILURE=0

	if [ ! -e "/var/run/mysqld/mysqld.pid" ]; then 
		echo "start mysql service before reconstruct..."
		FAILURE=0
		/usr/bin/service mysql start > /dev/null 2>&1
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to reconstruct. Aborting..."
			/var/waf/addsyslog -m "复位失败，错误代码120"
			return 120
		fi
	fi

	if [ -e "/var/waf/init_waf_hw.sql" ]; then 

		# replace the hostname with the hostname in setting
		replace_localhostname_in_config_with_waf_setting_value  "/var/waf/init_waf_hw.sql"

		FAILURE=0
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/init_waf_hw.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/init_waf_hw.sql"
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to reconstruct. Aborting..."
			/var/waf/addsyslog -m "复位失败，错误代码121"
			return 121
		fi	
	else
		echo "No database reconstruct scripts. Aborting..."

		/var/waf/addsyslog -m "复位失败，错误代码122"
		return 122
	fi

	if [ -e "/var/waf/init_waf_hw_extended.sql" ]; then 
		FAILURE=0
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/init_waf_hw_extended.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/init_waf_hw_extended.sql"
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to reconstruct. Aborting..."
			/var/waf/addsyslog -m "复位失败，错误代码131"
			return 131
		fi	
	else
		echo "No database reconstruct scripts. Aborting..."

		/var/waf/addsyslog -m "复位失败，错误代码131"
		return 131
	fi

	# generate flowbak table
	if [ -e "/var/waf/init_flowbak.sql" ]; then
		FAILURE=0
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/init_flowbak.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/init_flowbak.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create init_flowbak db. Aborting..."
			/var/waf/addsyslog -m "复位失败，错误代码133"
			return 133
		fi

	else
		echo "NO /var/waf/init_flowbak.sql. Aborting..."
		/var/waf/addsyslog -m "复位失败，错误代码134"
		return 134
	fi


	if [ -e "/var/waf/host_vul_info.sql" ]; then 

		FAILURE=0
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/host_vul_info.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/host_vul_info.sql"
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to reconstruct. Aborting..."
			/var/waf/addsyslog -m "复位失败，错误代码131"
			return 131
		fi	
	else
		echo "No database reconstruct scripts. Aborting..."

		/var/waf/addsyslog -m "复位失败，错误代码132"
		return 132
	fi

	if [ -e "/var/waf/cgidb.sql" ]; then 

		FAILURE=0
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/cgidb.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/cgidb.sql"
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to reconstruct. Aborting..."
			/var/waf/addsyslog -m "复位失败，错误代码131"
			return 131
		fi	
	else
		echo "No database reconstruct scripts. Aborting..."

		/var/waf/addsyslog -m "复位失败，错误代码132"
		return 132
	fi

	# init cve_info tables
	if [ -e "/var/waf/cve_info.sql" ]; then 

		FAILURE=0
		#echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/cve_info.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/cve_info.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create table cve_info.sql. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/cve_info.sql. Aborting..."
		exit 1
	fi


	if [ -e "/var/waf/web_vul_list.sql" ]; then 

		FAILURE=0
		echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/web_vul_list.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/web_vul_list.sql"
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to reconstruct. Aborting..."
			/var/waf/addsyslog -m "复位失败，错误代码131"
			return 131
		fi	
	else
		echo "No database reconstruct scripts. Aborting..."

		/var/waf/addsyslog -m "复位失败，错误代码132"
		return 132
	fi


	# init host_family_list tables
	if [ -e "/var/waf/host_family_list.sql" ]; then 

		FAILURE=0
		#echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/host_family_list.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/host_family_list.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create table host_family_list.sql. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/host_family_list.sql. Aborting..."
		exit 1
	fi

	# init host_family_ref tables
	if [ -e "/var/waf/host_family_ref.sql" ]; then 

		FAILURE=0
		#echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/host_family_ref.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/host_family_ref.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create table host_family_ref.sql. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/host_family_ref.sql. Aborting..."
		exit 1
	fi


	# init nvscan_server_preference tables
	if [ -e "/var/waf/nvscan_server_preference.sql" ]; then 

		FAILURE=0
		# echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/nvscan_server_preference.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/nvscan_server_preference.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create table nvscan_server_preference.sql. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/nvscan_server_preference.sql. Aborting..."
		exit 1
	fi


	# init nvscan_plugin_preference tables
	if [ -e "/var/waf/nvscan_plugin_preference.sql" ]; then 

		FAILURE=0
		# echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/nvscan_plugin_preference.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/nvscan_plugin_preference.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create table nvscan_plugin_preference.sql. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/nvscan_plugin_preference.sql. Aborting..."
		exit 1
	fi


	# init web_family_list tables
	if [ -e "/var/waf/web_family_list.sql" ]; then 

		FAILURE=0
		#echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		#echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/web_family_list.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/web_family_list.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create table web_family_list.sql. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/web_family_list.sql. Aborting..."
		exit 1
	fi


	# init web_family_ref tables
	if [ -e "/var/waf/web_family_ref.sql" ]; then 

		FAILURE=0
		#echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		#echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/web_family_ref.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/web_family_ref.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create table web_family_ref.sql. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/web_family_ref.sql. Aborting..."
		exit 1
	fi
	
	if [ -e "/var/waf/translation_info.sql" ]; then 

		FAILURE=0
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/translation_info.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create table translation_info.sql. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/translation_info.sql. Aborting..."
		exit 1
	fi

	# init network related table
	if [ -e "/var/waf/init_netconfig.sql" ]; then

		gen_netconfig_sql="/tmp/gen_init_netconfig.sql"

		FAILURE=0
		# call this function to generate the new one according to this device model
		generate_network_sql "init" "/var/waf/init_netconfig.sql" $gen_netconfig_sql
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to reconstruct. Aborting..."
			/var/waf/addsyslog -m "复位失败，错误代码125"
			return 125
		fi

		FAILURE=0
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source $gen_netconfig_sql"
		FAILURE=$?

		/bin/rm $gen_netconfig_sql > /dev/null 2>&1

		if [ $FAILURE -ne 0 ]; then
			echo "failed to reconstruct. Aborting..."
			/var/waf/addsyslog -m "复位失败，错误代码126"
			return 126
		fi

	else
		echo "No database reconstruct scripts. Aborting..."
		/var/waf/addsyslog -m "复位失败，错误代码127"
		return 127
	fi


	return 0
}

reset_dic_file () {
	#form.dic
	/bin/rm -rf /var/www/dic/form_*.dic
	/bin/cp /var/www/dic/form.dic /var/www/dic/form_2.dic

	#ftp.dic
	/bin/rm -rf /var/www/dic/ftp_*.dic
	/bin/cp /var/www/dic/ftp.dic /var/www/dic/ftp_2.dic

	#keyword.dic
	/bin/rm -rf /var/www/dic/keyword_*.dic
	/bin/cp /var/www/dic/keyword.dic /var/www/dic/keyword_2.dic

	#mssql.dic
	/bin/rm -rf /var/www/dic/mssql_*.dic
	/bin/cp /var/www/dic/mssql.dic /var/www/dic/mssql_2.dic

	#mysql.dic
	/bin/rm -rf /var/www/dic/mysql_*.dic
	/bin/cp /var/www/dic/mysql.dic /var/www/dic/mysql_2.dic

	#oracle.dic
	/bin/rm -rf /var/www/dic/oracle_*.dic
	/bin/cp /var/www/dic/oracle.dic /var/www/dic/oracle_2.dic

	#rdp.dic
	/bin/rm -rf /var/www/dic/rdp_*.dic
	/bin/cp /var/www/dic/rdp.dic /var/www/dic/rdp_2.dic

	#remote.dic
	/bin/rm -rf /var/www/dic/remote_*.dic
	/bin/cp /var/www/dic/remote.dic /var/www/dic/remote_2.dic

	#smb.dic
	/bin/rm -rf /var/www/dic/smb_*.dic
	/bin/cp /var/www/dic/smb.dic /var/www/dic/smb_2.dic

	#ssh.dic
	/bin/rm -rf /var/www/dic/ssh_*.dic
	/bin/cp /var/www/dic/ssh.dic /var/www/dic/ssh_2.dic

	#telnet.dic
	/bin/rm -rf /var/www/dic/telnet_*.dic
	/bin/cp /var/www/dic/telnet.dic /var/www/dic/telnet_2.dic

	#tomcatweakpwd.dic
	/bin/rm -rf /var/www/dic/tomcatweakpwd_[0-999].dic
	/bin/cp /var/www/dic/tomcatweakpwd.dic /var/www/dic/tomcatweakpwd_2.dic

	#tomcatweakpwd_port.dic
	/bin/rm -rf /var/www/dic/tomcatweakpwd_port_[0-999].dic
	/bin/cp /var/www/dic/tomcatweakpwd_port.dic /var/www/dic/tomcatweakpwd_port_2.dic

	#vnc.dic
	/bin/rm -rf /var/www/dic/vnc_*.dic
	/bin/cp /var/www/dic/vnc.dic /var/www/dic/vnc_2.dic

	#webshell.dic
	/bin/rm -rf /var/www/dic/webshell_*.dic
	/bin/cp /var/www/dic/webshell.dic /var/www/dic/webshell_2.dic

	chown www-data /var/www/dic/*
	chgrp www-data /var/www/dic/*
}


clear_system_and_applications_logs () {

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

	#add /var/log/wafcon.log
	if [ ! -e /var/log/wafcon.log ]; then
		echo "touch /var/log/wafcon.log "
		touch /var/log/wafcon.log
		chown conadmin /var/log/wafcon.log
		chgrp conadmin /var/log/wafcon.log
	fi
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



#####################################################################################################
# main part of shell script

shelldir=`dirname $0`

err_msg_type="reset"   # control how to show the error messages


if [ ! -x "$shelldir/install-lib.sh" ]; then
	echo "no install-lib.sh"
	/var/waf/addsyslog -m "复位失败，错误代码130"
else
	# Import functions from common lib
	. $shelldir/install-lib.sh
fi




netconfigbak="/etc/network/interfaces_bak"
netconfig="/etc/network/interfaces"


#########   Step 1: Get current config from device                     ########
FAILURE=0
echo "get_waf_config_from_current_device"
# error code: 
get_waf_config_from_current_device
FAILURE=$?
if [ $FAILURE -ne 0 ]; then
	echo "failed to start stop waf services. Aborting..."
	/var/waf/addsyslog -m "复位失败，请立即重启设备。"
	# restore current system status
	restore_important_device_confs
	restart_services_for_reset
	/sbin/reboot
fi



#########   Step 2: Stop the services if needed                      ########
echo "Stop the waf services..."
FAILURE=0
#error code: 
stop_services_for_reset
FAILURE=$?
if [ $FAILURE -ne 0 ]; then
	echo "failed to start stop waf services. Aborting..."
	/var/waf/addsyslog -m "复位失败，请立即重启设备。"
	# restore current system status
	restore_important_device_confs
	restart_services_for_reset
	/sbin/reboot
fi


#############################################################################

change_file_attributes


######### Step 3: update or generate config files under several locations  ########
sync_waf_config_2_waf_conf_file

sync_waf_config_2_web_dir



#########   Step 4: Reconstruct the database waf_hw                  ########
echo "Reconstruct the database..."
#error code: 
FAILURE=0
reset_waf_hw_db_tables
reset_dic_file
FAILURE=$?
if [ $FAILURE -ne 0 ]; then
	echo "failed to start stop waf services. Aborting..."
	/var/waf/addsyslog -m "复位失败，请立即重启设备。"
	# restore current system status
	restore_important_device_confs
	restart_services_for_reset
	/sbin/reboot
fi


#########   Step 5: reset some services config and start them if necessary   ########


#########   Step 6: clear some useful data when db reset                    ########
clear_waf_useful_data_when_db_reset


#########   Step 7: Clear system and application logs                       ########
clear_system_and_applications_logs
add_wafcon_log

#########   Step 8: Restore network config                                  ########
# not needed now
reset_apache2_listen_address

reset_ssh_listen_address

if [ -e /etc/network/interfaces_bak ]; then
	/bin/cp /etc/network/interfaces_bak /etc/network/interfaces
fi


#########   Step 9: Update host name and other system settings              ########
reset_dsi_dhcp_config

reset_dns_config

reset_hostname_info

reset_ntp_conf

#########   Step 10: make device backup point                               ########
if [ -x /var/waf/backup.sh ]; then

	if [ ! -e /var/waf/etc.tar.gz -a ! -e /var/waf/var.tar.gz ]; then
		echo "###No device restore point was found, backup now###"
		/var/waf/backup.sh
	fi
fi


# echo "Start update default policy"
# ####### update default policy  ##############
# if [ -e "/var/waf/nvscan_policy_manager.py" ]; then
# 	python /var/waf/nvscan_policy_manager.py update 1# > /dev/null 2>&1
# 	python /var/waf/nvscan_policy_manager.py update 2# > /dev/null 2>&1
# fi


#######    clear history list    #########
history -w
/bin/rm ~/.bash_history

#########   Step 11: Reboot the device                                      ########
echo "Reboot the device now..."
/sbin/reboot



