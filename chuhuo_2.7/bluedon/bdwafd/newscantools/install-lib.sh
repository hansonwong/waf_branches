#!/bin/sh
#
# Provides:          install-lib.sh
# Description:       common shell script library
#                   
# Author: Claus Wei <zhongwei@yxlink.com>
#
# error code: 41 - 99, current used - 83

################################### definitions of variables ########################

SW_VER=""
RULE_VER=""
MODEL_NO=""
SERVICE_CODE=""
HW_VER=""
RAND_SERIAL=""
BAND_WIDTH=""
WAF_ENHANCE=""
FEATURE_SET=""
WARRANTY_SET=""
DB_ROOT_PASSWD=""
DB_ROOT_NEW_PASSWD=""
DB_WAF_PASSWD=""

HOST_NAME=""

# add license support type field
LIC_SUPPORT_TYPE=2     # 0 - all version, 1 - stand-alone version, 2 - online version
# add two fields for general OEM version
HW_MODEL=""
VENDOR_NAME=""

# used by NVS product
MAX_THREAD=""
MAX_TASK=""
MAX_IP_OF_TASK=""
IP_RANGE_GLOBAL=""
MAX_PORT_THREAD_GLOBAL=""
MAX_HOST_THREAD_GLOBAL=""
MAX_WEB_THREAD_GLOBAL=""
MAX_WEAK_THREAD_GLOBAL=""


# There values should never change. If not, please update this shell script
DB_IP="127.0.0.1"
DB_NAME="waf_hw"
DB_ROOT_USER="root"
DB_WAF_USER="waf"


nic_mapping=""


rand_key=""

############################## variables of config files ##############################


wafrc_const="/etc/waf_constant.rc"
wafrc_setting="/etc/waf_setting.rc"

wafconf="/var/waf/waf.conf"
phpconf="/var/www/yx.config.inc.php"

waf_nic_conf="/etc/waf_nic.conf"
waf_nic_conf_in_php="/var/www/waf_nic.conf"

waf_70net_file="/etc/udev/rules.d/70-persistent-net.rules"

############################ common shell script functions ###########################
#  for waf install and update functions

waf_error_log () {

	# argument 1 - messages

	err_msg_content="$*"

	if [ $err_msg_type = "reset" ]; then
		/var/waf/addsyslog -m "复位失败，错误代码$err_msg_content"
		/bin/echo "reset failed, error : $err_msg_content"		
	elif  [ $err_msg_type = "update" ]; then
		/var/waf/addsyslog -m "固件升级失败，错误代码$err_msg_content"
		/bin/echo "update failed, error : $err_msg_content"		
	elif  [ $err_msg_type = "restore" ]; then
		/var/waf/addsyslog -m "还原失败，错误代码$err_msg_content"
		/bin/echo "restore failed, error : $err_msg_content"		
	else
		/bin/echo "install failed, error : $err_msg_content"
	fi
}



mac2decimal() {
	_tmp=`echo $@ | tr -d ':' | tr "[a-f]" [A-F]`
	printf "%d\n" 0x"$_tmp"
}



################################################################################################################################################



stop_waf_services_for_update() {
	# don't stop to continue even if some errors happen

	FAILURE=0

	# By Claus Wei. Since watchdog monitors wafmgr and ddos, it should be stoped firstly.
	if [ -x "/etc/init.d/wafwd.sh" ]; then 
		echo "stop wafwd daemon..."

		FAILURE=0
		service wafwd.sh stop > /dev/null 2>&1
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to stop wafwd daemon. Aborting..."
			/var/waf/addsyslog -m "固件升级失败，错误代码42"
			FAILURE=42
		fi
	fi

	if [ -x "/etc/init.d/wafmgr.sh" ]; then 
		echo "stop wafmgr daemon..."

		FAILURE=0
		service wafmgr.sh stop > /dev/null 2>&1
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to stop wafmgr daemon. Aborting..."
			/var/waf/addsyslog -m "固件升级失败，错误代码41"
			FAILURE=41
		fi
	fi


	#stop vul scan task
	kill $(ps -ef|grep '/usr/bin/python /var/waf/'|awk '$0 !~/grep/ {print $2}' |tr -s '\\n' ' ')


	if [ -x "/etc/init.d/wafnetwork.sh" ]; then 
		# actually not necessary, because wafnetwork.sh stop don't do anything
		echo "stop waf network shell..."
		service wafnetwork.sh stop   > /dev/null 2>&1
	fi


	if [ -x "/etc/init.d/nvscand" ]; then 
		echo "stop nvscan daemon..."
		/etc/init.d/nvscand stop   > /dev/null 2>&1
	fi

	return $FAILURE
}




restart_waf_services_for_update() {
	# don't stop to continue even if some errors happen
	
	if [ $# -eq 1 ]; then
		restart_mode=$1
	else
		restart_mode="normal"
	fi

	FAILURE=0

	if [ "$restart_mode" != "recover" ]; then
		##### only call it in normal restart mode ######
		if [ -x "/etc/init.d/wafnetwork.sh" ]; then 
			FAILURE=0
			echo "call wafnetwork.sh to configure all the network related resouces"
			service wafnetwork.sh start > /dev/null 2>&1
			FAILURE=$?
			if [ $FAILURE -ne 0 ]; then
				echo "failed to start wafnetwork.sh. Aborting..."
				/var/waf/addsyslog -m "固件升级失败，错误代码43"
				FAILURE=43
			fi
		fi
	else
		echo "restart_waf_services_for_update, recover mode, don't call wafnetwork.sh"		
	fi

	# start mysqld if stopped
	if [ ! -e "/var/run/mysqld/mysqld.pid" ]; then 
		echo "start mysql service..."
		service mysql start   > /dev/null 2>&1
	fi

	# start apache2 if stopped
	if [ ! -e "/var/run/apache2.pid" ]; then 
		echo "start apache2 service..."
		service apache2 start   > /dev/null 2>&1
	fi

	# start wafmgr
	if [ -x "/etc/init.d/wafmgr.sh" ]; then 
		echo "restart the wafmgr daemon"
		FAILURE=0
		service wafmgr.sh restart > /dev/null 2>&1
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to start wafmgr daemon. Aborting..."
			/var/waf/addsyslog -m "固件升级失败，错误代码44"
			FAILURE=44
		fi
	fi


	# start wafwd
	if [ -x "/etc/init.d/wafwd.sh" ]; then 
		echo "start the wafwd daemon"
		FAILURE=0
		service wafwd.sh restart > /dev/null 2>&1
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to start wafwd daemon. Aborting..."
			/var/waf/addsyslog -m "固件升级失败，错误代码45"
			FAILURE=45
		fi
	fi


	# nvscan daemon
	if [ -x "/etc/init.d/nvscand" ]; then 
		echo "restart nvscan daemon..."
		/etc/init.d/nvscand restart   > /dev/null 2>&1
	fi


	return $FAILURE
}




config_php_module_setting () {

	echo "Update php upload file size to 200M"
	# increase the post max size
	/bin/sed -i "s/^.*post_max_size.*$/post_max_size = 200M /g"  /etc/php5/apache2/php.ini
	# increase the max exec time
	/bin/sed -i "s/^.*max_execution_time = .*;/max_execution_time = 240    ;/g"  /etc/php5/apache2/php.ini

	# Increase the upload file size
	/bin/sed -i "s/^.*upload_max_filesize.*$/upload_max_filesize = 200M /g"  /etc/php5/apache2/php.ini

	# Close display_errors
	/bin/sed -i "s/^display_errors = On.*$/display_errors = Off /g"  /etc/php5/apache2/php.ini

	# Enable Zend Opt in php.ini
	zend_num=`grep "zend_extension=/etc/php5/5_2_x_comp/ZendOptimizer.so" /etc/php5/apache2/php.ini |wc -l`	

	if [ $zend_num -eq 0 ]; then
		echo "Add zend_extension=/etc/php5/5_2_x_comp/ZendOptimizer.so into /etc/php5/apache2/php.ini"

		/bin/sed  -i "/engine = On/ a\ \n; Yxlink, add zend module \nzend_extension=/etc/php5/5_2_x_comp/ZendOptimizer.so"  /etc/php5/apache2/php.ini
	fi


	# Security! Only allow php to access /var/www and /tmp dir, can't access any other dirs
	if grep "^open_basedir = /var/www/:/tmp/" /etc/php5/apache2/php.ini > /dev/null 2>&1
	then
		echo "open_basedir has already been inserted"
	else
		echo "need to config open_basedir"
		/bin/sed -i "s/^.*open_basedir.*=.*$/open_basedir = \/var\/www\/:\/tmp\//g"  /etc/php5/apache2/php.ini

		# confirm if has been inserted
		if grep "^open_basedir = /var/www/:/tmp/" /etc/php5/apache2/php.ini > /dev/null 2>&1
		then
		        echo ""
		else
		        echo "open_basedir = /var/www/:/tmp/" >> /etc/php5/apache2/php.ini
		fi
	fi

	# Security! Disable some risk php functions
	if grep "^disable_functions = phpinfo,passthru,exec,system,chroot,scandir,chgrp,chown,shell_exec,proc_open,proc_get_status,ini_alter,ini_alter,ini_restore,dl,pfsockopen,openlog,syslog,readlink,symlink,popepassthru,stream_socket_serve,popen" /etc/php5/apache2/php.ini > /dev/null 2>&1
	then
		echo "disable_functions has already been inserted"
	else
		echo "need to config disable_functions"
		/bin/sed -i "s/^.*disable_functions.*=.*$/disable_functions = phpinfo,passthru,exec,system,chroot,scandir,chgrp,chown,shell_exec,proc_open,proc_get_status,ini_alter,ini_alter,ini_restore,dl,pfsockopen,openlog,syslog,readlink,symlink,popepassthru,stream_socket_serve,popen/g"  /etc/php5/apache2/php.ini

		# confirm if has been inserted
		if grep "^disable_functions = phpinfo,passthru,exec,system,chroot,scandir,chgrp,chown,shell_exec,proc_open,proc_get_status,ini_alter,ini_alter,ini_restore,dl,pfsockopen,openlog,syslog,readlink,symlink,popepassthru,stream_socket_serve,popen" /etc/php5/apache2/php.ini > /dev/null 2>&1
		then
		        echo ""
		else
		        echo "disable_functions = phpinfo,passthru,exec,system,chroot,scandir,chgrp,chown,shell_exec,proc_open,proc_get_status,ini_alter,ini_alter,ini_restore,dl,pfsockopen,openlog,syslog,readlink,symlink,popepassthru,stream_socket_serve,popen" >> /etc/php5/apache2/php.ini
		fi
	fi

	/bin/sed -i "s/^session.name = PHPSESSID.*$/session.name = nvssession/g"  /etc/php5/apache2/php.ini

	if [ -e /etc/php5/cli/php.ini ]; then
                /bin/sed -i "s/^.*mssql.timeout =.*/mssql.timeout = 600/g"  /etc/php5/cli/php.ini
                /bin/sed -i "s/^.*mssql.connect_timeout =.*/mssql.connect_timeout = 5/g"  /etc/php5/cli/php.ini
	fi


	# add soft link of rewrite.load
	if [ ! -L /etc/apache2/mods-enabled/rewrite.load ]; then
		ln -s /etc/apache2/mods-available/rewrite.load /etc/apache2/mods-enabled/rewrite.load
	fi

	# support zip download
	if [ -e /etc/apache2/mods-available/mime.conf ]; then

	        if grep "^AddType application/octet-stream .zip" /etc/apache2/mods-available/mime.conf > /dev/null 2>&1
	        then
	                echo "AddType application/octet-stream .zip has already been inserted"
	        else
	                echo "need to config AddType application/octet-stream .zip"
	                /bin/sed -i "/AddType application\/x-bzip2 \.bz2/ a\AddType application/octet-stream .zip"  /etc/apache2/mods-available/mime.conf
	                /bin/sed -i "/AddType application\/x-bzip2 \.bz2/ a\AddType application/vnd.openxmlformats .docx .pptx .xlsx"  /etc/apache2/mods-available/mime.conf
	        fi
	fi


	if [ -e /etc/apache2/mods-available/alias.conf ]; then
		if grep "^Alias" /etc/apache2/mods-available/alias.conf  > /dev/null 2>&1
		then
			/bin/sed -i "s/^[^#]/# &/g" /etc/apache2/mods-available/alias.conf
		else
			echo "alias.conf already commented"
		fi
	fi


	# Add to use the chartdirector library
	add_chartdirector_lib
}



update_php_module_setting () {


	add_chartdirector_lib

	if [ -e /etc/php5/cli/php.ini ]; then
		/bin/sed -i "s/^.*mssql.timeout =.*/mssql.timeout = 600/g"  /etc/php5/cli/php.ini
		/bin/sed -i "s/^.*mssql.connect_timeout =.*/mssql.connect_timeout = 5/g"  /etc/php5/cli/php.ini
	fi

	# increase php max exec time
	/bin/sed -i "s/^.*max_execution_time = .*;/max_execution_time = 240    ;/g"  /etc/php5/apache2/php.ini

	if [ -e /etc/apache2/mods-available/mime.conf ]; then

	        if grep "^AddType application/octet-stream .zip" /etc/apache2/mods-available/mime.conf > /dev/null 2>&1
	        then
	                echo "AddType application/octet-stream .zip has already been inserted"
	        else
	                echo "need to config AddType application/octet-stream .zip"

	                /bin/sed -i "/AddType application\/x-bzip2 \.bz2/ a\AddType application/octet-stream .zip"  /etc/apache2/mods-available/mime.conf
	                /bin/sed -i "/AddType application\/x-bzip2 \.bz2/ a\AddType application/vnd.openxmlformats .docx .pptx .xlsx"  /etc/apache2/mods-available/mime.conf
	        fi
	fi
}


# Add chartdirector lib into system
add_chartdirector_lib () {
	# Add to use the chartdirector library
	if grep "^extension=phpchartdir520.dll" /etc/php5/apache2/php.ini > /dev/null 2>&1
	then
		echo "extension=phpchartdir520.dll has already been inserted"
	else
		echo "need to insert extension=phpchartdir520.dll"
		/bin/sed  -i "/; extension_dir directive above\./ a\extension=phpchartdir520.dll"  /etc/php5/apache2/php.ini

		#/bin/sed -i "s/^.*open_basedir.*=.*$/open_basedir = \/var\/www\/:\/tmp\//g"  /etc/php5/apache2/php.ini

		# confirm if has been inserted
		if grep "^extension=phpchartdir520.dll" /etc/php5/apache2/php.ini > /dev/null 2>&1
		then
		        echo ""
		else
		        echo "extension=phpchartdir520.dll" >> /etc/php5/apache2/php.ini
		fi
	fi
}






# error code: 51 - 70
get_waf_config_from_current_device () {

	FAILURE=0
	get_waf_config_in_new_format
	FAILURE=$?
	return $FAILURE
}


# error code: 51 - 60
get_waf_config_in_new_format () {

	echo "get_waf_config_in_new_format, waf_constant.rc"
	# here is /etc/waf_constant.rc
	if [ ! -e  $wafrc_const ]; then
		echo "No $wafrc_const. Aborting..."
		waf_error_log "51"
		return 51
	fi

	# parse the model no
	MODEL_NO=`/bin/grep "modelno" $wafrc_const | awk -F= '{print $2}' | awk -F\" '{print $2}'`
	if [ -z "$MODEL_NO" ]; then
		MODEL_NO=`/bin/grep "modelno" $wafrc_const | awk -F= '{print $2}' | awk -F\; '{print $1}' | tr -d ' ' | tr -d '"'`

		if [ -z "$MODEL_NO" ]; then
			MODEL_NO="NVS-6000"
			echo "model no is invalid, use default value $MODEL_NO"
			waf_error_log "52"
			return 52
		fi
	fi


	# parse the service code
	SERVICE_CODE=`/bin/grep "servicecode" $wafrc_const |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $SERVICE_CODE ]; then
		SERVICE_CODE="WAF0HW0B1201"
		echo "service code is invalid, use default value $SERVICE_CODE"
		waf_error_log "53"
		return 53
	fi

	# parse the hardware version
	HW_VER=`/bin/grep "hwver" $wafrc_const |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $HW_VER ]; then
		HW_VER="2.0"
		echo "hardware version is invalid, use default value $HW_VER"
	fi


	# parse the random serial
	## RAND_SERIAL=`/bin/grep "randserial" $wafrc_const |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	## if [ -z $RAND_SERIAL ]; then
	## 	RAND_SERIAL="12345678"
	## 	echo "random serial is invalid, use default value $RAND_SERIAL"
	## 	waf_error_log "54"
	## 	return 54
	## fi
	# not used in DDOS product
	RAND_SERIAL="12345678"

	# parse the band width
	BAND_WIDTH=`/bin/grep "bandwidth" $wafrc_const |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $BAND_WIDTH ]; then
		BAND_WIDTH="1000M"
		echo "band width is invalid, use default value $BAND_WIDTH"
	fi


	# parse the db ip
	DB_IP=`/bin/grep "db_ip" $wafrc_const |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $DB_IP ]; then
		DB_IP="127.0.0.1"
		echo "db ip addr is invalid, use default value $DB_IP"
	fi

	# parse the db name
	DB_NAME=`/bin/grep "db_name" $wafrc_const |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $DB_NAME ]; then
		DB_NAME="waf_hw"
		echo "db name is invalid, use default value $DB_NAME"
	fi

	# parse the db root user
	DB_ROOT_USER=`/bin/grep "db_root_user" $wafrc_const |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $DB_ROOT_USER ]; then
		DB_ROOT_USER="root"
		echo "db root user is invalid, use default value $DB_ROOT_USER"
	fi


	# parse the db root passwd
	DB_ROOT_PASSWD=`/bin/grep "db_root_passwd" $wafrc_const |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $DB_ROOT_PASSWD ]; then
		echo "db root passwd is invalid"
		waf_error_log "55"
		return 55
	fi

	# parse the db waf user
	DB_WAF_USER=`/bin/grep "db_waf_user" $wafrc_const |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $DB_WAF_USER ]; then
		DB_WAF_USER="waf"
		echo "db waf user is invalid, use default value $DB_WAF_USER"
	fi

	# parse the db waf passwd
	DB_WAF_PASSWD=`/bin/grep "db_waf_passwd" $wafrc_const |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $DB_WAF_PASSWD ]; then
		DB_WAF_PASSWD="yxserver"
		echo "db waf passwd is invalid"
		waf_error_log "56"
		return 56
	fi


	# below is /etc/waf_setting.rc
	echo "get_waf_config_in_new_format, waf_setting.rc"

	# parse the software version
	if [ -e /var/waf/ver ]; then
		SW_VER=`cat /var/waf/ver`
		echo "The sw version is $SW_VER from /var/waf/ver"
	else
		SW_VER=`/bin/grep "swver" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
		echo "No /var/waf/ver exists, this should not happen, use swver $SW_VER in $wafrc_setting"
	fi 

	# parse the rule version
	RULE_VER=`/bin/grep "rulever" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $RULE_VER ]; then
		RULE_VER="1.0.0.1036"
		echo "rule version is invalid, use default value $RULE_VER"
	fi


	MAX_THREAD=`/bin/grep "max_thread" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $MAX_THREAD ]; then
		MAX_THREAD=10
		echo "waf max_thread setting is invalid, use default value $MAX_THREAD"
	fi

	MAX_TASK=`/bin/grep "max_task" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $MAX_TASK ]; then
		MAX_TASK=10
		echo "waf max_task setting is invalid, use default value $MAX_TASK"
	fi

	MAX_IP_OF_TASK=`/bin/grep "max_ip_of_task" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $MAX_IP_OF_TASK ]; then
		MAX_IP_OF_TASK=255
		echo "waf max_ip_of_task setting is invalid, use default value $MAX_IP_OF_TASK"
	fi

	IP_RANGE_GLOBAL=`/bin/grep "ip_range_global" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z "$IP_RANGE_GLOBAL" ]; then
		IP_RANGE_GLOBAL="*.*.*.*"
		echo "waf ip_range_global setting is invalid, use default value $IP_RANGE_GLOBAL"
	fi

	MAX_PORT_THREAD_GLOBAL=`/bin/grep "max_port_thread_global" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $MAX_PORT_THREAD_GLOBAL ]; then
		MAX_PORT_THREAD_GLOBAL=5
		echo "waf max_port_thread_global setting is invalid, use default value $MAX_PORT_THREAD_GLOBAL"
	fi

	MAX_HOST_THREAD_GLOBAL=`/bin/grep "max_host_thread_global" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $MAX_HOST_THREAD_GLOBAL ]; then
		MAX_HOST_THREAD_GLOBAL=5
		echo "waf max_host_thread_global setting is invalid, use default value $MAX_HOST_THREAD_GLOBAL"
	fi

	MAX_WEB_THREAD_GLOBAL=`/bin/grep "max_web_thread_global" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $MAX_WEB_THREAD_GLOBAL ]; then
		MAX_WEB_THREAD_GLOBAL=5
		echo "waf max_web_thread_global setting is invalid, use default value $MAX_WEB_THREAD_GLOBAL"
	fi

	MAX_WEAK_THREAD_GLOBAL=`/bin/grep "max_weak_thread_global" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $MAX_WEAK_THREAD_GLOBAL ]; then
		MAX_WEAK_THREAD_GLOBAL=5
		echo "waf max_weak_thread_global setting is invalid, use default value $MAX_WEAK_THREAD_GLOBAL"
	fi

	HOST_NAME=`/bin/grep "hostname" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $HOST_NAME ]; then
		HOST_NAME="nvs"
		echo "hostname setting is invalid, use default value $HOST_NAME"
	fi

	# parse the waf enhance feature, if not find it, append [feature] section at the end
	WAF_ENHANCE=`/bin/grep "waf_enhance" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $WAF_ENHANCE ]; then
		WAF_ENHANCE=1
		echo "waf enhance feature is invalid, use default value $WAF_ENHANCE"
	fi



	# parse the feature set, if not find it, append feature_set field at the end
	FEATURE_SET=`/bin/grep "feature_set" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	# new format, maybe still no vendorname. get from /var/waf/vendor.conf
	if [ -e /var/waf/vendor.conf ]; then
		VENDOR_NAME=`/bin/grep "VENDOR_SHORT_NAME_STR_ID" /var/waf/vendor.conf |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	else
		VENDOR_NAME="unknown"
	fi

	HW_MODEL=`/bin/grep "hwmodel" $wafrc_const |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $HW_MODEL ]; then
		HW_MODEL="unknown"
	fi

	# parse the license support type feature, if not find it, append [feature] section at the end
	LIC_SUPPORT_TYPE=`/bin/grep "lic_support_type" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $LIC_SUPPORT_TYPE ]; then
		LIC_SUPPORT_TYPE=0
		echo "license support type feature is invalid, use default value $LIC_SUPPORT_TYPE"
	fi
	
	# parse the warranty, if not find it, append [warranty] section at the end
	WARRANTY_SET=`/bin/grep "warranty_duration" $wafrc_setting |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $WARRANTY_SET ]; then
		WARRANTY_SET="2014-05-01/2017-05-01"
		echo "warrantye feature is invalid, use default value $WARRANTY_SET"
	fi
	WARRANTY_SET=${WARRANTY_SET/\//\\\/}
	
	return 0
}


################################################################################################################################################


reset_dsi_dhcp_config () {

	# reset DSI DHCP config and service
	if [ -e /var/waf/waf_dsi.py ]; then
		python /var/waf/waf_dsi.py
	fi
}


reset_dns_config () {

	if [ -e /var/waf/waf_dns.py ]; then
		python /var/waf/waf_dns.py
	fi
}



reset_hostname_info () {

	/usr/bin/logger -t install-lib "hostname: $HOST_NAME"

	if [ -z $HOST_NAME ]; then
		HOST_NAME="nvs"
	fi

	echo "Updating /etc/hostname with $HOST_NAME"
	# Update permanently
	echo $HOST_NAME > /etc/hostname

	# Update temporarily
	/bin/hostname $HOST_NAME
	echo "Updating /etc/hosts with $HOST_NAME"


	# Firstly delete all "127.0.0.1"
	/bin/sed -i  "/127.0.0.1/d"  /etc/hosts
	# Add two lines of "127.0.0.1"
	sed -i "1i\127.0.0.1       $HOST_NAME.localdomain $HOST_NAME \n127.0.0.1       localhost.localdomain localhost " /etc/hosts

	/bin/sed -i "s/^127.0.1.1.*$/127.0.1.1       $HOST_NAME /g"  /etc/hosts
	# for vulscan product, grant /etc/hosts other access permissions
	chmod 666 /etc/hosts
}



clear_waf_useful_data_when_db_reset () {


	#########   Step 6: clear WTF DB backup data                   ########


	#########   Step 7: clear WAF report data                   ########
	if [ -d /var/www/Report ]; then
		/bin/rm -rf /var/www/tmp/*.csv /var/www/cap/*.cap /var/www/include/libs/tcpdf/cache/*.png /var/www/Report/[0-9]*
	fi


}




update_ld_cache () {
	echo "Update /etc/ld.so.cache for dynamic libs"

	/bin/rm /etc/ld.so.cache

	# update /etc/ld.so.conf to include /var/waf
	sed -i -e '/^\/var\/waf$/d' /etc/ld.so.conf
	echo /var/waf >> /etc/ld.so.conf

	# update /etc/ld.so.conf to include /usr/lib/oracle/11.2/client/lib
	sed -i -e '/^\/usr\/lib\/oracle\/11.2\/client\/lib$/d' /etc/ld.so.conf
	echo /usr/lib/oracle/11.2/client/lib >> /etc/ld.so.conf
	/sbin/ldconfig -f /etc/ld.so.conf -C /etc/ld.so.cache

}



# change all the installed directories and files attributes
change_file_attributes () {

	echo "Update the files attributes accordingly"

	# /var/www, be read and exec
	/bin/chmod -R 554 /var/www 
	# /var/www/tmp, be read, write and exec, actually it is controlled by .htaccess
	/bin/chmod -R 775 /var/www/tmp 
	/bin/chmod -R 775 /var/www/cap
	/bin/chmod -R 775 /var/www/Report
	/bin/chmod -R 775 /var/www/dic
	/bin/chmod -R 775 /var/www/include/libs/tcpdf/cache

	/bin/chown -R www-data /var/www
	/bin/chgrp -R www-data /var/www

	# login
	/bin/chmod +x /bin/login

	# /var/waf
	/bin/chmod -R 554 /var/waf 
	/bin/chmod o+x /var/waf/libsocketlib.so
	/bin/chmod o+x /var/waf 
	/bin/chmod u+w /var/waf/waf.conf 

	if [ -e /var/waf/wafcon ]; then
		/bin/chmod 555 /var/waf/wafcon
	fi

	# /var/vuls_db
	/bin/chmod -R 775      /var/vuls_db
	/bin/chown -R www-data /var/vuls_db
	/bin/chgrp -R www-data /var/vuls_db
	/bin/chmod -R -s       /var/vuls_db


	if [ -e /var/webs ]; then
		# exists but not directory
		if [ ! -d /var/webs ]; then
			rm -f /var/webs
			mkdir /var/webs
		fi
	else
		# no such directory
		mkdir /var/webs
	fi

}

change_tmp_file_attributes () {

	waftmpdir=$1

	echo "Update the temp files attributes accordingly"

	# /var/www, be read and exec
	/bin/chmod -R 554 $waftmpdir/var/www
	# /var/www/tmp, be read, write and exec, actually it is controlled by .htaccess
	/bin/chmod -R 775 $waftmpdir/var/www/tmp
	/bin/chmod -R 775 $waftmpdir/var/www/cap 
	/bin/chmod -R 775 $waftmpdir/var/www/Report
	/bin/chmod -R 775 $waftmpdir/var/www/dic
	/bin/chmod -R 775 $waftmpdir/var/www/include/libs/tcpdf/cache

	/bin/chown -R www-data $waftmpdir/var/www 
	/bin/chgrp -R www-data $waftmpdir/var/www 

	# login
	/bin/chmod +x $waftmpdir/bin/login

	# var/waf
	/bin/chmod -R 554 $waftmpdir/var/waf
	/bin/chmod o+x $waftmpdir/var/waf/libsocketlib.so
	/bin/chmod o+x $waftmpdir/var/waf
	/bin/chmod u+w $waftmpdir/var/waf/waf.conf

	# /var/vuls_db
	if [ -d $waftmpdir/var/vuls_db ]; then
		/bin/chmod -R 775      $waftmpdir/var/vuls_db
		/bin/chown -R www-data $waftmpdir/var/vuls_db
		/bin/chgrp -R www-data $waftmpdir/var/vuls_db
		/bin/chmod -R -s       $waftmpdir/var/vuls_db
	fi

	if [ -e /var/waf/wafcon ]; then
		/bin/chmod 555 $waftmpdir/var/waf/wafcon
	fi

}


restore_important_conf_files () {

	if [ -e /var/waf/waf.conf_update ]; then
		/bin/mv /var/waf/waf.conf_update /var/waf/waf.conf 
	fi

	if [ -e /var/www/yx.config.inc.php_update ]; then
		/bin/mv /var/www/yx.config.inc.php_update /var/www/yx.config.inc.php 
		chown www-data /var/www/yx.config.inc.php
		chgrp www-data /var/www/yx.config.inc.php
	fi

	if [ -e /etc/network/interfaces_update ]; then
		/bin/mv /etc/network/interfaces_update /etc/network/interfaces 
	fi
}



sync_waf_nic_conf_file_to_web () {
	if [ -e $waf_nic_conf ]; then
		/bin/cp $waf_nic_conf $waf_nic_conf_in_php

		/bin/chown www-data $waf_nic_conf_in_php
		/bin/chgrp www-data $waf_nic_conf_in_php
		/bin/chmod 554 $waf_nic_conf_in_php	
	fi
}




config_dmi () {

	dmi=$1

	if echo $dmi | grep '[0-9]\{1,\}\.[0-9]\{1,\}\.[0-9]\{1,\}\.[0-9]\{1,\}' > /dev/null 2>&1; then
		:
	else
		echo "invalid ip address. ignore it. Aborting..."
		exit 1
	fi


	# Suppose the gateway is xxx.xxx.xxx.1. Because this shell is used internally

	gw=`echo $dmi | sed 's/\(.*\)\..*/\1/'`
	gw="$gw.1"

	echo "gateway: $gw"

	# get eth2 external name from /etc/waf_nic.conf
	dmi_name=`/bin/grep "eth2" $waf_nic_conf | awk -F= '{print $1}'`
	echo "DMI: $dmi_name"


	# generate a sql file and update net_config table ETHx item

	tmp_sql_file="/tmp/configdmi.sql"
	echo "USE waf_hw; SET FOREIGN_KEY_CHECKS=0; update net_config SET net_config.Enable='1', net_config.WorkMode='0', net_config.Type='DMI|NVS', net_config.BridgeId='0', net_config.Ip='$dmi', net_config.Netmask='255.255.255.0', net_config.NextHop=null, net_config.Gateway='$gw' where net_config.Name='$dmi_name';update user_route SET user_route.Gateway='$gw' where user_route.Iface='$dmi_name' and user_route.Netmask='0.0.0.0' and user_route.Dest='0.0.0.0' and user_route.Default='1';" > $tmp_sql_file


	# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source $tmp_sql_file\""
	FAILURE=0
	/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source $tmp_sql_file"
	FAILURE=$?
	if [ $FAILURE -ne 0 ]; then
		echo "Error to change DMI ip address, please check. Aborting..."
		/bin/rm $tmp_sql_file
		exit 1
	fi


	if [ -e /var/waf/waf_netconfig.py ]; then

		echo "python /var/waf/waf_netconfig.py $dmi_name"
		python /var/waf/waf_netconfig.py $dmi_name
	fi

	/bin/rm $tmp_sql_file


}




sync_waf_config_2_waf_conf_file () {
	# sync /var/waf/waf.conf according to waf_constant.rc and waf_setting.rc

	if [ -e $wafconf ]; then

		echo "Config $wafconf accordingly..."

		/bin/sed -i "s/^.*db_ip.*$/db_ip = \"$DB_IP\"  /g"  $wafconf
		/bin/sed -i "s/^.*db_name.*$/db_name = \"$DB_NAME\"  /g"  $wafconf

		/bin/sed -i "s/^.*db_user.*$/db_user = \"$DB_ROOT_USER\"  /g"  $wafconf
		/bin/sed -i "s/^.*db_passwd.*$/db_passwd = \"$DB_ROOT_PASSWD\"  /g"  $wafconf

		if grep "lic_support_type" $wafconf > /dev/null 2>&1
		then
			/bin/sed -i "s/^.*lic_support_type.*$/lic_support_type = $LIC_SUPPORT_TYPE/g"  $wafconf
		else
			# insert [lic_support_type] field after [wait_to_restart_wafmgr] field if doesn't exist
			/bin/sed -i "/wait_to_restart_wafmgr/ a\\\\n# license\nlic_support_type = $LIC_SUPPORT_TYPE" $wafconf
		fi
		
		# Add for warranty_duration 20140421 xiayuying
		if grep "warranty_duration" $wafconf > /dev/null 2>&1
		then
			/bin/sed -i "s/^.*warranty_duration.*$/warranty_duration = \"$WARRANTY_SET\" /g"  $wafconf
		else
			# insert [warranty_duration] field after [lic_support_type] field if doesn't exist
			# /bin/sed -i "/lic_support_type/ a\[warranty]" $wafconf
			echo "[warranty]" >> $wafconf
			/bin/sed -i "/\[warranty\]/ a\warranty_duration = \"$WARRANTY_SET\"" $wafconf
		fi
		#End 

		echo ""
	fi

}


sync_waf_config_2_web_dir () {
	# sync /var/www/yx.config.inc.php according to waf_constant.rc and waf_setting.rc

	if [ -e $phpconf ]; then
		echo "Config $phpconf accordingly..."

		/bin/sed -i "s/^.*\$model.*;/        \$model = \'$MODEL_NO\';/g"  $phpconf
		/bin/sed -i "s/^.*\$servicecode.*;/        \$servicecode = \'$SERVICE_CODE\';/g"  $phpconf

		/bin/sed -i "s/^.*\$hwver.*;/        \$hwver = \'$HW_VER\';/g"  $phpconf
		/bin/sed -i "s/^.*\$rulever.*;/        \$rulever = \'$RULE_VER\';/g"  $phpconf

		#swver from /etc/waf.ver will be like this: 2.6.01.2122. But "swver" field in yx.config.inc.php will be 2.6, and "build" field in yx.config.inc.php will be 2.6.01.2122
		BUILD_VER=$SW_VER
		/bin/sed -i "s/^.*\$build.*;/        \$build = \'$BUILD_VER\';/g"  $phpconf

		major=`echo $SW_VER | awk -F\. '{print $1}'`
		minor=`echo $SW_VER | awk -F\. '{print $2}'`
		FIRMWARE_VER="$major.$minor"
		/bin/sed -i "s/^.*\$swver.*;/        \$swver = \'$FIRMWARE_VER\';/g"  $phpconf

		# synchronize dbuser, dbpw, dbhost, dbname with /etc/waf.rc
		/bin/sed -i "s/^.*\$dbuser.*;/        \$dbuser = \'$DB_WAF_USER\';/g"  $phpconf
		/bin/sed -i "s/^.*\$dbpw.*;/        \$dbpw = \'$DB_WAF_PASSWD\';/g"  $phpconf
		/bin/sed -i "s/^.*\$dbhost.*;/        \$dbhost = \'$DB_IP\';/g"  $phpconf
		/bin/sed -i "s/^.*\$dbname.*;/        \$dbname = \'$DB_NAME\';/g"  $phpconf

		# synchronize the enhance feature...
		/bin/sed -i "s/^.*\$enhance.*;/        \$enhance = \'$WAF_ENHANCE\';/g"  $phpconf
		/bin/sed -i "s/^.*\$feature_set.*;/        \$feature_set = \'$FEATURE_SET\';/g"  $phpconf


		# max thread setting...
		/bin/sed -i "s/^.*\$max_thread_global.*;/        \$max_thread_global = \'$MAX_THREAD\';/g"  $phpconf

		# max task setting...
		/bin/sed -i "s/^.*\$max_task_global.*;/        \$max_task_global = \'$MAX_TASK\';/g"  $phpconf

		# max ip of every task setting...
		/bin/sed -i "s/^.*\$max_task_ip_global.*;/        \$max_task_ip_global = \'$MAX_IP_OF_TASK\';/g"  $phpconf

		# ip range setting...
		/bin/sed -i "s/^.*\$ip_range_global.*;/        \$ip_range_global = \'$IP_RANGE_GLOBAL\';/g"  $phpconf

		# max port thread of every task setting...
		/bin/sed -i "s/^.*\$max_port_thread_global.*;/        \$max_port_thread_global = \'$MAX_PORT_THREAD_GLOBAL\';/g"  $phpconf

		# max host thread of every task setting...
		/bin/sed -i "s/^.*\$max_host_thread_global.*;/        \$max_host_thread_global = \'$MAX_HOST_THREAD_GLOBAL\';/g"  $phpconf

		# max web thread of every task setting...
		/bin/sed -i "s/^.*\$max_web_thread_global.*;/        \$max_web_thread_global = \'$MAX_WEB_THREAD_GLOBAL\';/g"  $phpconf

		# max weak thread of every task setting...
		/bin/sed -i "s/^.*\$max_weak_thread_global.*;/        \$max_weak_thread_global = \'$MAX_WEAK_THREAD_GLOBAL\';/g"  $phpconf

		#Begin 20140421 xiayuying add for warranty_duration
		# synchronize the warranty feature... 
		if grep "warranty_duration" $phpconf > /dev/null 2>&1
		then
			/bin/sed -i "s/^.*\$warranty_duration.*;/        \$warranty_duration = \'$WARRANTY_SET\';/g"  $phpconf
		else
			# insert [warranty_duration] field after [lic_expiry_action] field if doesn't exist
			/bin/sed -i "/max_weak_thread_global/ a\        \$warranty_duration = \'$WARRANTY_SET\';" $phpconf
		fi
		#End

		echo ""
	fi
}


generate_or_update_waf_constant_rc () {
	# update or generate /etc/waf_constant.rc
	if [ -e $wafrc_const ]; then
		echo "$wafrc_const already exists, just updating it"
		# /etc/waf_constant.rc is already there, just update
		/bin/chmod +w $wafrc_const
		
		/bin/sed -i "s/^.*modelno.*$/modelno = \"$MODEL_NO\"/g"  $wafrc_const
		/bin/sed -i "s/^.*servicecode.*$/servicecode = $SERVICE_CODE /g"  $wafrc_const		
		/bin/sed -i "s/^.*hwver.*$/hwver = $HW_VER /g"  $wafrc_const

		/bin/sed -i "s/^.*bandwidth.*$/bandwidth = $BAND_WIDTH /g"  $wafrc_const		


		/bin/sed -i "s/^.*db_ip.*$/db_ip = $DB_IP /g"  $wafrc_const		
		/bin/sed -i "s/^.*db_name.*$/db_name = $DB_NAME /g"  $wafrc_const		
		
		/bin/sed -i "s/^.*db_root_user.*$/db_root_user = $DB_ROOT_USER /g"  $wafrc_const		
		/bin/sed -i "s/^.*db_root_passwd.*$/db_root_passwd = $DB_ROOT_PASSWD /g"  $wafrc_const		

		/bin/sed -i "s/^.*db_waf_user.*$/db_waf_user = $DB_WAF_USER /g"  $wafrc_const		
		/bin/sed -i "s/^.*db_waf_passwd.*$/db_waf_passwd = $DB_WAF_PASSWD /g"  $wafrc_const		

		# two new fields: hwmodel, vendorname
		if grep "hwmodel" $wafrc_const > /dev/null 2>&1
		then
			/bin/sed -i "s/^.*vendorname.*$/vendorname = $VENDOR_NAME /g"  $wafrc_const		
			/bin/sed -i "s/^.*hwmodel.*$/hwmodel = $HW_MODEL /g"  $wafrc_const		
		else
			# insert one if doesn't exist
			/bin/sed -i "/bandwidth/ a\vendorname = $VENDOR_NAME" $wafrc_const
			/bin/sed -i "/bandwidth/ a\hwmodel = $HW_MODEL" $wafrc_const
		fi

		/bin/chmod -w $wafrc_const
		echo ""
	else
		# There is no /etc/waf_constant.rc, create one
		echo "Generating $wafrc_const"
		
		echo "">$wafrc_const 
		echo "[resource]">>$wafrc_const
		echo "modelno = \"$MODEL_NO\"">>$wafrc_const
		echo "servicecode = $SERVICE_CODE">>$wafrc_const
		echo "hwver = $HW_VER">>$wafrc_const
		echo "randserial = $RAND_SERIAL">>$wafrc_const
		echo "bandwidth = $BAND_WIDTH">>$wafrc_const
		echo "hwmodel = $HW_MODEL">>$wafrc_const
		echo "vendorname = $VENDOR_NAME">>$wafrc_const

		echo "">>$wafrc_const
		echo "[mysql]">>$wafrc_const
		echo "db_ip = $DB_IP">>$wafrc_const	
		echo "db_name = $DB_NAME">>$wafrc_const
		echo "db_root_user = $DB_ROOT_USER">>$wafrc_const
		echo "db_root_passwd = $DB_ROOT_PASSWD">>$wafrc_const
		echo "db_waf_user = $DB_WAF_USER">>$wafrc_const
		echo "db_waf_passwd = $DB_WAF_PASSWD">>$wafrc_const
		echo "">>$wafrc_const
		

		/bin/chmod -w $wafrc_const

		echo ""
	fi
}


generate_or_update_waf_setting_rc () {

	# update or generate /etc/waf_setting.rc

	if [ -e $wafrc_setting ]; then

		echo "$wafrc_setting already exists, just updating it"

		/bin/chmod +w $wafrc_setting

		/bin/sed -i "s/^.*swver.*$/swver = $SW_VER /g"  $wafrc_setting		
		/bin/sed -i "s/^.*rulever.*$/rulever = $RULE_VER /g"  $wafrc_setting		


		/bin/sed -i "s/^.*hostname.*$/hostname = \"$HOST_NAME\"/g"  $wafrc_setting

		/bin/sed -i "s/^.*waf_enhance.*$/waf_enhance = \"$WAF_ENHANCE\"/g"  $wafrc_setting
		/bin/sed -i "s/^.*feature_set.*$/feature_set = \"${FEATURE_SET}\"/g"  $wafrc_setting
		
		# added in NVS product
		/bin/sed -i "s/^.*max_thread.*$/max_thread = \"$MAX_THREAD\"/g"  $wafrc_setting
		/bin/sed -i "s/^.*max_task.*$/max_task = \"$MAX_TASK\"/g"  $wafrc_setting

		# in case max_ip_of_task doesn't exist
		if grep "max_ip_of_task" $wafrc_setting > /dev/null 2>&1
		then
			/bin/sed -i "s/^.*max_ip_of_task.*$/max_ip_of_task = \"$MAX_IP_OF_TASK\"/g"  $wafrc_setting
		else
			# insert it if doesn't exist, put after max_task
			/bin/sed -i "/max_task/ a\max_ip_of_task = $MAX_IP_OF_TASK" $wafrc_setting
		fi

		# in case ip_range_global doesn't exist
		if grep "ip_range_global" $wafrc_setting > /dev/null 2>&1
		then
			/bin/sed -i "s/^.*ip_range_global.*$/ip_range_global = \"${IP_RANGE_GLOBAL}\"/g"  $wafrc_setting
		else
			# insert it if doesn't exist, put after max_ip_of_task
			/bin/sed -i "/max_ip_of_task/ a\ip_range_global = \"${IP_RANGE_GLOBAL}\"" $wafrc_setting
		fi

		# in case max_port_thread_global doesn't exist
		if grep "max_port_thread_global" $wafrc_setting > /dev/null 2>&1
		then
			/bin/sed -i "s/^.*max_port_thread_global.*$/max_port_thread_global = \"$MAX_PORT_THREAD_GLOBAL\"/g"  $wafrc_setting
		else
			# insert it if doesn't exist, put after ip_range_global
			/bin/sed -i "/ip_range_global/ a\max_port_thread_global = $MAX_PORT_THREAD_GLOBAL" $wafrc_setting
		fi

		# in case max_host_thread_global doesn't exist
		if grep "max_host_thread_global" $wafrc_setting > /dev/null 2>&1
		then
			/bin/sed -i "s/^.*max_host_thread_global.*$/max_host_thread_global = \"$MAX_HOST_THREAD_GLOBAL\"/g"  $wafrc_setting
		else
			# insert it if doesn't exist, put after max_port_thread_global
			/bin/sed -i "/max_port_thread_global/ a\max_host_thread_global = $MAX_HOST_THREAD_GLOBAL" $wafrc_setting
		fi

		# in case max_web_thread_global doesn't exist
		if grep "max_web_thread_global" $wafrc_setting > /dev/null 2>&1
		then
			/bin/sed -i "s/^.*max_web_thread_global.*$/max_web_thread_global = \"$MAX_WEB_THREAD_GLOBAL\"/g"  $wafrc_setting
		else
			# insert it if doesn't exist, put after max_host_thread_global
			/bin/sed -i "/max_host_thread_global/ a\max_web_thread_global = $MAX_WEB_THREAD_GLOBAL" $wafrc_setting
		fi

		# in case max_weak_thread_global doesn't exist
		if grep "max_weak_thread_global" $wafrc_setting > /dev/null 2>&1
		then
			/bin/sed -i "s/^.*max_weak_thread_global.*$/max_weak_thread_global = \"$MAX_WEAK_THREAD_GLOBAL\"/g"  $wafrc_setting
		else
			# insert it if doesn't exist, put after max_web_thread_global
			/bin/sed -i "/max_web_thread_global/ a\max_weak_thread_global = $MAX_WEAK_THREAD_GLOBAL" $wafrc_setting
		fi

		if grep "lic_support_type" $wafrc_setting > /dev/null 2>&1
		then
			/bin/sed -i "s/^.*lic_support_type.*$/lic_support_type = $LIC_SUPPORT_TYPE/g"  $wafrc_setting
		else
			# insert [lic_support_type] field after [feature_set] field if doesn't exist
			/bin/sed -i "/feature_set/ a\lic_support_type = $LIC_SUPPORT_TYPE" $wafrc_setting
		fi
		
		#Add for warranty_duration xiayuying 20140421
		if grep "warranty_duration" $wafrc_setting > /dev/null 2>&1
		then
			/bin/sed -i "s/^.*warranty_duration.*$/warranty_duration = \"$WARRANTY_SET\"/g"  $wafrc_setting
		else
			# insert [warranty_duration] field after [lic_support_type] field if doesn't exist
			# /bin/sed -i "/lic_support_type/ a\[warranty]" $wafconf
			echo "[warranty]" >> $wafrc_setting
			/bin/sed -i "/\[warranty\]/ a\warranty_duration = \"$WARRANTY_SET\"" $wafrc_setting
		fi
		#End

		/bin/chmod -w $wafrc_setting

		echo ""
	else
		# There is no /etc/waf_setting.rc, create one
		echo "Generating $wafrc_setting"

		echo "">$wafrc_setting 
		echo "[version]">>$wafrc_setting
		echo "swver = $SW_VER">>$wafrc_setting
		echo "rulever = $RULE_VER">>$wafrc_setting
		echo "">>$wafrc_setting

		echo "[other]">>$wafrc_setting
		echo "hostname = \"$HOST_NAME\"">>$wafrc_setting
		echo "">>$wafrc_setting

		echo "[vul_limitation]">>$wafrc_setting
		echo "max_thread = \"$MAX_THREAD\"">>$wafrc_setting
		echo "max_task = \"$MAX_TASK\"">>$wafrc_setting
		echo "max_ip_of_task = \"$MAX_IP_OF_TASK\"">>$wafrc_setting
		echo "ip_range_global = \"${IP_RANGE_GLOBAL}\"">>$wafrc_setting
		echo "max_port_thread_global = \"$MAX_PORT_THREAD_GLOBAL\"">>$wafrc_setting
		echo "max_web_thread_global = \"$MAX_WEB_THREAD_GLOBAL\"">>$wafrc_setting
		echo "max_host_thread_global = \"$MAX_HOST_THREAD_GLOBAL\"">>$wafrc_setting
		echo "max_weak_thread_global = \"$MAX_WEAK_THREAD_GLOBAL\"">>$wafrc_setting

		echo "">>$wafrc_setting

		echo "[feature]">>$wafrc_setting
		echo "waf_enhance = \"$WAF_ENHANCE\"">>$wafrc_setting
		echo "feature_set = \"${FEATURE_SET}\"">>$wafrc_setting
		echo "lic_support_type = $LIC_SUPPORT_TYPE">>$wafrc_setting
		
		#Add for warranty_duration xiayuying 20140421
		echo "" >> $wafrc_setting
		echo "[warranty]" >> $wafrc_setting
		echo "warranty_duration = \"${WARRANTY_SET/\\/}\"" >> $wafrc_setting
		#End

		echo "">>$wafrc_setting

		/bin/chmod -w $wafrc_setting

		echo ""
	fi

}



generate_network_sql () {

	# init or update two types
	gen_type=$1
	netconfig_sql=$2
	gen_netconfig_sql_file=$3

	#echo "input netconfig.sql: $netconfig_sql"
	#echo "output generated netconfig.sql: $gen_netconfig_sql_file"


	if [ -e $netconfig_sql ]; then
		/bin/rm $gen_netconfig_sql_file > /dev/null 2>&1
		#echo "/bin/cp $netconfig_sql  $gen_netconfig_sql_file"
		/bin/cp $netconfig_sql  $gen_netconfig_sql_file
	else
		echo "No $netconfig_sql exists. Aborting..."
		return 46
	fi


	# parse the /etc/waf_nic.conf
	if [ ! -e $waf_nic_conf ]; then
		echo "No $waf_nic_conf, please do preinstall.sh again and generate $waf_nic_conf. Aborting..."
		return 47
	fi

	. $waf_nic_conf > /dev/null 2>&1

	echo "There are $NIC_NUM NICs on this device model"

	if [ -z $ETH0 ]; then
		echo "No ETH0 on this device model"
		nic_begin=1
	else
		echo "ETH0 exists on this device model"
		nic_begin=0
	fi


	############## firstly, replace eth0...eth4. If two bridges, replace eth5, eth6 ############
	nic_index=$nic_begin
	while [ $nic_index -lt  `expr $NIC_NUM + $nic_begin` ] 
	do
		ETH_ext_name="ETH$nic_index"

		ETH_int_name=`/bin/grep "$ETH_ext_name\>" $waf_nic_conf |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`

		#echo "Extern: ${ETH_ext_name}, Internal: ${ETH_int_name}"

		# remember DMI
		if [ $ETH_int_name = "eth2" ]; then
			DMI_ext_name=$ETH_ext_name
		fi


		# update all the variables eth0, eth1, eth2, eth3, eth4 with ETHx in processed_init_netconfig.sql
		case $ETH_int_name in 

			'eth2'|'eth3')
				echo "update $ETH_int_name with $ETH_ext_name"

				normal_eth_sql=`grep ".*net_config.*$ETH_int_name\>" $gen_netconfig_sql_file`
				normal_eth_sql=`echo $normal_eth_sql | /bin/sed s/$ETH_int_name/$ETH_ext_name/g`
				#echo "new normal sql: $normal_eth_sql"
				/bin/sed -i "s/^.*net_config.*$ETH_int_name.*$/$normal_eth_sql/g" $gen_netconfig_sql_file
			;;
			
			*)
			:
			;;

		esac
		nic_index=`expr $nic_index + 1`
	done




	########################## 3rd, add default gateway in user_route in install case ########################
	if [ "$gen_type" = "init" ]; then
		echo "default gateway in install case"
		default_gateway_sql=`grep "user_route.*eth2" $gen_netconfig_sql_file | /bin/sed  "s/^.*INSERT/INSERT/g" `
		default_gateway_sql=`echo $default_gateway_sql |  /bin/sed s/eth2/$DMI_ext_name/g`
		/bin/sed -i "/^.*user_route.*eth2.*$/ a\\$default_gateway_sql" $gen_netconfig_sql_file
	fi


	################################ 4th, append all the other left ETHx #######################################
	#generate the sample sql sentence
	other_eth_sql=`grep "ETH-SAMPLE-NAME" $gen_netconfig_sql_file | /bin/sed  "s/^.*INSERT/INSERT/g" `
	#echo "other_eth_sql: $other_eth_sql"


	nic_index=$nic_begin
	while [ $nic_index -lt  `expr $NIC_NUM + $nic_begin` ] 
	do
		ETH_ext_name="ETH$nic_index"


		if  /bin/grep "net_config.*$ETH_ext_name\>" $gen_netconfig_sql_file >/dev/null 2>&1 
		then
			#echo "already exists in the sql file, don't append again"
			:
		else
			#echo "append $ETH_ext_name into sql file at the end"				
			new_sql=`echo "$other_eth_sql" | sed "s/ETH-SAMPLE-NAME/$ETH_ext_name/g" `
			sed -i "/ETH-SAMPLE-NAME/ a\\$new_sql" $gen_netconfig_sql_file
		fi

		nic_index=`expr $nic_index + 1`
	done

	#echo ""
	#cat $gen_netconfig_sql_file

        lefteth4=`grep -e "net_config.*eth4" $gen_netconfig_sql_file | wc -l`
        # echo "$lefteth4"
        if [ $lefteth4 -eq 1 ]; then
                echo "remove eth4 from sql because device has no eth4"
                sed -i "s/^.*net_config.*eth4.*$//g" $gen_netconfig_sql_file
        fi


        lefteth3=`grep -e "net_config.*eth3" $gen_netconfig_sql_file | wc -l`
        # echo "$lefteth3"
        if [ $lefteth3 -eq 1 ]; then
                echo "remove eth3 from sql because device has no eth3"
                sed -i "s/^.*net_config.*eth3.*$//g" $gen_netconfig_sql_file
        fi

        # cat $gen_netconfig_sql_file

        ####### verify integrity at last #########
        lefteth=`grep -e "net_config.*eth" $gen_netconfig_sql_file | wc -l`
        echo "left eth: $lefteth"
        if [ $lefteth -ne 0 ]; then
                echo "gen net_config sql error, still have ethx in sql file."
                /bin/rm "$gen_netconfig_sql_file" > /dev/null 2>&1
                return 48
        fi

}





add_db_user_and_grant_privileges () {

	# because need to use mysql (add user), make sure that mysql is ready to use for a while and then stop it to update
	if [ ! -e "/var/run/mysqld/mysqld.pid" ]; then 
		echo "start mysql service..."
		service mysql start   > /dev/null 2>&1
	fi


	# Add db waf user
	# create a temp sql file and write sql code into it, then execute it.
	tmp_sql_file="/tmp/adduser.sql"
	echo "GRANT select,delete,insert,update,drop,create,alter,create view,show view,index,create temporary tables,create routine, alter routine, execute ON *.* TO '$DB_WAF_USER'@'localhost' IDENTIFIED BY '$DB_WAF_PASSWD';" > $tmp_sql_file

	# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source $tmp_sql_file\""
	FAILURE=0
	/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source $tmp_sql_file"
	FAILURE=$?
	if [ $FAILURE -ne 0 ]; then
		echo "Error to change database waf user password, please check."
		FAILURE=49
	fi

	/bin/rm $tmp_sql_file

	return $FAILURE
}



install_waf_hw_db_tables () {

	# init all the other tables except rules and netconfig related
	if [ -e "/var/waf/init_waf_hw.sql" ]; then 

		# replace the hostname with the hostname in setting
		replace_localhostname_in_config_with_waf_setting_value  "/var/waf/init_waf_hw.sql"

		FAILURE=0
		#echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/init_waf_hw.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/init_waf_hw.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create waf_hw db. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/init_waf_hw.sql. Aborting..."
		exit 1
	fi

	


	if [ -e "/var/waf/init_waf_hw_extended.sql" ]; then
		FAILURE=0
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/init_waf_hw_extended.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/init_waf_hw_extended.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create waf_hw extended db. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/init_waf_hw_extended.sql. Aborting..."
		exit 1
	fi


	# generate flowbak table
	if [ -e "/var/waf/init_flowbak.sql" ]; then
		FAILURE=0
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/init_flowbak.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/init_flowbak.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create init_flowbak db. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/init_flowbak.sql. Aborting..."
		exit 1
	fi

	# init network related table
	if [ -e /var/waf/init_netconfig.sql ]; then

		gen_netconfig_sql_file="/tmp/gen_init_netconfig.sql"
		# call this function to generate the new one according to this device model
		FAILURE=0
		generate_network_sql "init" "/var/waf/init_netconfig.sql" $gen_netconfig_sql_file
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to generate netconfig sql. Aborting..."
			exit 1
		fi


		FAILURE=0
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source $gen_netconfig_sql_file"
		/bin/rm $gen_netconfig_sql_file

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create netconfig tables db. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/init_netconfig.sql. Aborting..."
		exit 1
	fi


	# init nvscan vul_info tables
	if [ -e "/var/waf/host_vul_info.sql" ]; then 

		FAILURE=0
		# echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		#  echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/host_vul_info.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/host_vul_info.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create table host_vul_info.sql. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/host_vul_info.sql. Aborting..."
		exit 1
	fi

	# init nvscan vul_info_dep tables
	if [ -e "/var/waf/vul_info_dep.sql" ]; then 

		FAILURE=0
		# echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		#  echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/host_vul_info.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/vul_info_dep.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create table vul_info_dep.sql. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/vul_info_dep.sql. Aborting..."
		exit 1
	fi

	# init cve_info tables
	if [ -e "/var/waf/cve_info.sql" ]; then 

		FAILURE=0
		# echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
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

	# init translation_info tables
	if [ -e "/var/waf/translation_info.sql" ]; then 

		FAILURE=0
		# echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/translation_info.sql\""
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

	# init nvscan web_vul_list tables
	if [ -e "/var/waf/web_vul_list.sql" ]; then 

		FAILURE=0
		#echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		#echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/web_vul_list.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/web_vul_list.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create table web_vul_list.sql. Aborting..."
			exit 1
		fi
	else
		echo "NO /var/waf/web_vul_list.sql. Aborting..."
		exit 1
	fi

	# init nvscan cgidb tables
	if [ -e "/var/waf/cgidb.sql" ]; then 

		FAILURE=0
		#echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		#echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/cgidb.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/cgidb.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create table cgidb.sql. Aborting..."
			exit 1
		fi
	else
		echo "NO /var/waf/cgidb.sql. Aborting..."
		exit 1
	fi

	
	# init host_family_list tables
	if [ -e "/var/waf/host_family_list.sql" ]; then 

		FAILURE=0
		# echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
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
		# echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
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


	return 0
}



# update waf_hw db tables, only used in update case. Don't use it in install or reset case
update_waf_hw_db_tables () {

	FAILURE=0

	# check db service is there ?
	if [ ! -e "/var/run/mysqld/mysqld.pid" ]; then 
		echo "start mysql service before reconstruct..."
		FAILURE=0
		/usr/bin/service mysql start > /dev/null 2>&1
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to reconstruct. Aborting..."
			/var/waf/addsyslog -m "固件升级失败，错误代码71"
			return 71
		fi
	fi

	
	if [ -e "/var/waf/update_waf_hw.sql" ]; then 

		# replace the hostname with the hostname in setting
		replace_localhostname_in_config_with_waf_setting_value  "/var/waf/update_waf_hw.sql"

		FAILURE=0
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/update_waf_hw.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/update_waf_hw.sql"
		FAILURE=$?

		/bin/rm /var/waf/update_waf_hw.sql  > /dev/null 2>&1

		if [ $FAILURE -ne 0 ]; then
			echo "failed to reconstruct. Aborting..."
			/var/waf/addsyslog -m "固件升级失败，错误代码72"
			return 72
		fi	
	else
		echo "No database reconstruct scripts."
	fi


	if [ -e "/var/waf/update_waf_hw_extended.sql" ]; then 
		FAILURE=0
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/update_waf_hw_extended.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/update_waf_hw_extended.sql"
		FAILURE=$?

		/bin/rm /var/waf/update_waf_hw_extended.sql  > /dev/null 2>&1

		if [ $FAILURE -ne 0 ]; then
			echo "failed to reconstruct update_waf_hw_extended.sql. Aborting..."
			/var/waf/addsyslog -m "固件升级失败，错误代码83"
			return 83
		fi	
	else
		echo "No update_waf_hw_extended.sql reconstruct scripts."

	fi


	# init network related table
	if [ -e "/var/waf/update_netconfig.sql" ]; then

		gen_netconfig_sql_file="/tmp/gen_update_netconfig.sql"
		# call this function to generate the new one according to this device model

		FAILURE=0
		generate_network_sql "update" "/var/waf/update_netconfig.sql" $gen_netconfig_sql_file
		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to generate netconfig.sql. Aborting..."
			/var/waf/addsyslog -m "固件升级失败，错误代码74"
			return 74
		fi

		FAILURE=0
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source $gen_netconfig_sql_file"
		FAILURE=$?

		/bin/rm $gen_netconfig_sql_file > /dev/null 2>&1
		/bin/rm /var/waf/update_netconfig.sql  > /dev/null 2>&1

		if [ $FAILURE -ne 0 ]; then
			echo "failed to reconstruct. Aborting..."
			/var/waf/addsyslog -m "固件升级失败，错误代码75"
			return 75
		fi
	else
		echo "No update netconfig related database reconstruct scripts. "
	fi

	# init nvscan vul_info_dep tables
	if [ -e "/var/waf/vul_info_dep.sql" ]; then 

		FAILURE=0
		# echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		#  echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/host_vul_info.sql\""
		/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/vul_info_dep.sql"

		FAILURE=$?
		if [ $FAILURE -ne 0 ]; then
			echo "failed to create table vul_info_dep.sql. Aborting..."
			exit 1
		fi

	else
		echo "NO /var/waf/vul_info_dep.sql. Aborting..."
		exit 1
	fi
	# init translation_info tables
	if [ -e "/var/waf/translation_info.sql" ]; then 

		FAILURE=0
		# echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
		# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/translation_info.sql\""
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
    # online update support,not necessary to run follow sql

	# # init nvscan vul_info tables
	# if [ -e "/var/waf/host_vul_info.sql" ]; then 

	# 	FAILURE=0
	# 	# echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
	# 	# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/host_vul_info.sql\""
	# 	/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/host_vul_info.sql"

	# 	FAILURE=$?
	# 	if [ $FAILURE -ne 0 ]; then
	# 		echo "failed to create table host_vul_info.sql. Aborting..."
	# 		exit 1
	# 	fi

	# else
	# 	echo "NO /var/waf/host_vul_info.sql. Aborting..."
	# 	exit 1
	# fi


	# # init cve_info tables
	# if [ -e "/var/waf/cve_info.sql" ]; then 

	# 	FAILURE=0
	# 	# echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
	# 	# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/cve_info.sql\""
	# 	/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/cve_info.sql"

	# 	FAILURE=$?
	# 	if [ $FAILURE -ne 0 ]; then
	# 		echo "failed to create table cve_info.sql. Aborting..."
	# 		exit 1
	# 	fi

	# else
	# 	echo "NO /var/waf/cve_info.sql. Aborting..."
	# 	exit 1
	# fi


	# # init nvscan web_vul_list tables
	# if [ -e "/var/waf/web_vul_list.sql" ]; then 

	# 	FAILURE=0
	# 	echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
	# 	echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/web_vul_list.sql\""
	# 	/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/web_vul_list.sql"

	# 	FAILURE=$?
	# 	if [ $FAILURE -ne 0 ]; then
	# 		echo "failed to create table web_vul_list.sql. Aborting..."
	# 		exit 1
	# 	fi

	# else
	# 	echo "NO /var/waf/web_vul_list.sql. Aborting..."
	# 	exit 1
	# fi

	# # init nvscan cgidb tables
	# if [ -e "/var/waf/cgidb.sql" ]; then 

	# 	FAILURE=0
	# 	echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
	# 	echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/cgidb.sql\""
	# 	/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/cgidb.sql"

	# 	FAILURE=$?
	# 	if [ $FAILURE -ne 0 ]; then
	# 		echo "failed to create table cgidb.sql. Aborting..."
	# 		exit 1
	# 	fi

	# else
	# 	echo "NO /var/waf/cgidb.sql. Aborting..."
	# 	exit 1
	# fi


	# # init host_family_list tables
	# if [ -e "/var/waf/host_family_list.sql" ]; then 

	# 	FAILURE=0
	# 	# echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
	# 	# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/host_family_list.sql\""
	# 	/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/host_family_list.sql"

	# 	FAILURE=$?
	# 	if [ $FAILURE -ne 0 ]; then
	# 		echo "failed to create table host_family_list.sql. Aborting..."
	# 		exit 1
	# 	fi

	# else
	# 	echo "NO /var/waf/host_family_list.sql. Aborting..."
	# 	exit 1
	# fi

	
	# # init host_family_ref tables
	# if [ -e "/var/waf/host_family_ref.sql" ]; then 

	# 	FAILURE=0
	# 	# echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
	# 	# echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/host_family_ref.sql\""
	# 	/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/host_family_ref.sql"

	# 	FAILURE=$?
	# 	if [ $FAILURE -ne 0 ]; then
	# 		echo "failed to create table host_family_ref.sql. Aborting..."
	# 		exit 1
	# 	fi

	# else
	# 	echo "NO /var/waf/host_family_ref.sql. Aborting..."
	# 	exit 1
	# fi


	# # init web_family_list tables
	# if [ -e "/var/waf/web_family_list.sql" ]; then 

	# 	FAILURE=0
	# 	echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
	# 	echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/web_family_list.sql\""
	# 	/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/web_family_list.sql"

	# 	FAILURE=$?
	# 	if [ $FAILURE -ne 0 ]; then
	# 		echo "failed to create table web_family_list.sql. Aborting..."
	# 		exit 1
	# 	fi

	# else
	# 	echo "NO /var/waf/web_family_list.sql. Aborting..."
	# 	exit 1
	# fi

	
	# # init web_family_ref tables
	# if [ -e "/var/waf/web_family_ref.sql" ]; then 

	# 	FAILURE=0
	# 	echo "connecting to local db, db ip: $DB_IP, db username: $DB_ROOT_USER, db password: $DB_ROOT_PASSWD"
	# 	echo "/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e \"source /var/waf/web_family_ref.sql\""
	# 	/usr/bin/mysql -u$DB_ROOT_USER -p$DB_ROOT_PASSWD -h$DB_IP -e "source /var/waf/web_family_ref.sql"

	# 	FAILURE=$?
	# 	if [ $FAILURE -ne 0 ]; then
	# 		echo "failed to create table web_family_ref.sql. Aborting..."
	# 		exit 1
	# 	fi

	# else
	# 	echo "NO /var/waf/web_family_ref.sql. Aborting..."
	# 	exit 1
	# fi


	return 0
}


check_eth_num_with_given_nic_mapping_type ()  {
	# not used in NVS product
	:
}


replace_localhostname_in_config_with_waf_setting_value () {

	sql_file=$1

	if [ $HOST_NAME != "yxlinknvs" ]; then

		if [ -e $sql_file ]; then

			sql_1=`/bin/grep ".*config\>.*ha_local_hostname" $sql_file | /bin/sed ""`
			sql_1=`echo $sql_1 | /bin/sed "s/'yxlinknvs/'$HOST_NAME/g"`
			# echo "sql_1: $sql_1"
			if [ ! -z "$sql_1" ]; then
				/bin/sed -i "s/^.*config\>.*ha_local_hostname.*$/$sql_1/g" $sql_file
			fi

			sql_2=`/bin/grep ".*config\>.*ha_other_hostname" $sql_file | /bin/sed ""`
			sql_2=`echo $sql_2 | /bin/sed "s/'yxlinknvs/'$HOST_NAME/g"`
			# echo "sql_2: $sql_2"
			if [ ! -z "$sql_2" ]; then
				/bin/sed -i "s/^.*config\>.*ha_other_hostname.*$/$sql_2/g" $sql_file
			fi

			sql_3=`/bin/grep ".*config_bak\>.*ha_local_hostname" $sql_file | /bin/sed ""`
			sql_3=`echo $sql_3 | /bin/sed "s/'yxlinknvs/'$HOST_NAME/g"`
			# echo "sql_3: $sql_3"
			if [ ! -z "$sql_3" ]; then
				/bin/sed -i "s/^.*config_bak\>.*ha_local_hostname.*$/$sql_3/g" $sql_file
			fi

			sql_4=`/bin/grep ".*config_bak\>.*ha_other_hostname" $sql_file | /bin/sed ""`
			sql_4=`echo $sql_4 | /bin/sed "s/'yxlinknvs/'$HOST_NAME/g"`
			# echo "sql_4: $sql_4"
			if [ ! -z "$sql_4" ]; then
				/bin/sed -i "s/^.*config_bak\>.*ha_other_hostname.*$/$sql_4/g" $sql_file
			fi
		fi
	fi
}


backup_important_device_confs () {

	########### OS related confs ###########

	# network interfaces
	if [ -e /etc/network/interfaces_bak ]; then
		/bin/cp /etc/network/interfaces_bak /var/backups/interfaces.bak >/dev/null 2>&1
	fi

	# route tables
	/bin/cp /etc/iproute2/rt_tables    /var/backups/rt_tables.bak >/dev/null 2>&1

	# host
	/bin/cp /etc/hosts                 /var/backups/hosts.bak >/dev/null 2>&1

	# dhcp3 server
	/bin/cp /etc/dhcp3/dhcpd.conf      /var/backups/dhcpd.conf.bak >/dev/null 2>&1
	/bin/cp /etc/default/dhcp3-server  /var/backups/dhcp3-server.bak >/dev/null 2>&1

	# sshd
	backup_sshd_conf
	/bin/cp /etc/ssh/ssh_config        /var/backups/ssh_config.bak  >/dev/null 2>&1

	# mysql 
	/bin/cp /etc/mysql/my.cnf          /var/backups/my.cnf.bak >/dev/null 2>&1

	# apache2
	backup_apache2_ports_conf

	# php5
	/bin/cp /etc/php5/apache2/php.ini  /var/backups/php.ini.bak >/dev/null 2>&1


	########### WAF related confs ###########
	/bin/cp /etc/waf_constant.rc  /var/backups/waf_constant.rc.bak >/dev/null 2>&1
	/bin/cp /etc/waf_setting.rc   /var/backups/waf_setting.rc.bak  >/dev/null 2>&1
	/bin/cp /etc/waf_nic.conf     /var/backups/waf_nic.conf.bak    >/dev/null 2>&1


}



restore_important_device_confs () {
	
	# network interfaces
	if [ -e /var/backups/interfaces.bak ]; then
		/bin/cp /var/backups/interfaces.bak /etc/network/interfaces 
	fi

	# route tables
	if [ -e /var/backups/rt_tables.bak ]; then
		/bin/cp /var/backups/rt_tables.bak /etc/iproute2/rt_tables
	fi

	# host
	if [ -e /var/backups/hosts.bak ]; then
		/bin/cp /var/backups/hosts.bak  /etc/hosts
	fi


	# dhcp3 server
	if [ -e  /var/backups/dhcpd.conf.bak ]; then
		/bin/cp /var/backups/dhcpd.conf.bak /etc/dhcp3/dhcpd.conf 
	fi

	if [ -e /var/backups/dhcp3-server.bak ]; then
		/bin/cp /var/backups/dhcp3-server.bak /etc/default/dhcp3-server  
	fi

	# sshd
	if [ -e /var/backups/sshd_config.bak ]; then
		/bin/cp /var/backups/sshd_config.bak /etc/ssh/sshd_config       
	fi

	if [ -e /var/backups/ssh_config.bak ]; then
		/bin/cp  /var/backups/ssh_config.bak /etc/ssh/ssh_config  
	fi


	# mysql 
	if [ -e /var/backups/my.cnf.bak ]; then
		/bin/cp /var/backups/my.cnf.bak /etc/mysql/my.cnf         
	fi


	# apache2
	if [ -e /var/backups/ports.conf.bak ]; then
		/bin/cp /var/backups/ports.conf.bak /etc/apache2/ports.conf     
	fi


	# php5
	if [ -e  /var/backups/php.ini.bak ]; then
		/bin/cp  /var/backups/php.ini.bak /etc/php5/apache2/php.ini  
	fi



	########### WAF related confs ###########
	if [ -e /var/backups/waf_constant.rc.bak ]; then
		/bin/cp /var/backups/waf_constant.rc.bak /etc/waf_constant.rc  
	fi

	if [ -e  /var/backups/waf_setting.rc.bak ]; then
		/bin/cp /var/backups/waf_setting.rc.bak  /etc/waf_setting.rc   
	fi

	if [ -e  /var/backups/waf_nic.conf.bak ]; then
		/bin/cp  /var/backups/waf_nic.conf.bak /etc/waf_nic.conf       
	fi
}


backup_apache2_ports_conf () {

	
	/bin/cp /etc/apache2/ports.conf    /var/backups/ports.conf.bak >/dev/null 2>&1

	if [ -e /var/backups/ports.conf.bak ]; then

	 	/bin/sed -i "/^.*Listen.*443.*$/d" /var/backups/ports.conf.bak

		# add all the listen addresses except RPI
		if grep "# NameVirtualHost statement here" /var/backups/ports.conf.bak >/dev/null 2>&1
		then
			/bin/sed -i "/# NameVirtualHost statement here/ a\    Listen 192.168.1.10:443\n    Listen 192.168.100.1:443\n    Listen 127.0.0.1:443"  /var/backups/ports.conf.bak
		elif grep "IfModule mod_ssl.c" /var/backups/ports.conf.bak >/dev/null 2>&1
		then
			/bin/sed -i "/IfModule mod_ssl.c/ a\    Listen 192.168.1.10:443\n    Listen 192.168.100.1:443\n    Listen 127.0.0.1:443"  /var/backups/ports.conf.bak
		else
			/usr/bin/logger -t backup "ports.conf.bak is invalid, can't backup it"
		fi
	fi
}


backup_sshd_conf () {

	/bin/cp /etc/ssh/sshd_config       /var/backups/sshd_config.bak >/dev/null 2>&1

	if [ -e /var/backups/sshd_config.bak ]; then
		# remove all the listen address
	 	/bin/sed -i "/^ListenAddress.*$/d" /var/backups/sshd_config.bak
		# add new listen address
		/bin/sed -i "/interfaces\/protocols sshd will bind to/ a\ListenAddress 192.168.1.10\nListenAddress 192.168.100.1\nListenAddress 127.0.0.1"  /var/backups/sshd_config.bak
	fi
}


reset_apache2_listen_address () {

	if [ -e /etc/apache2/ports.conf ]; then

	 	/bin/sed -i "/^.*Listen.*443.*$/d" /etc/apache2/ports.conf

		# add all the listen addresses except RPI
		if grep "# NameVirtualHost statement here" /etc/apache2/ports.conf >/dev/null 2>&1
		then
			/bin/sed -i "/# NameVirtualHost statement here/ a\    Listen 192.168.1.10:443\n    Listen 192.168.100.1:443\n    Listen 127.0.0.1:443"  /etc/apache2/ports.conf
		elif grep "IfModule mod_ssl.c" /etc/apache2/ports.conf >/dev/null 2>&1
		then
			/bin/sed -i "/IfModule mod_ssl.c/ a\    Listen 192.168.1.10:443\n    Listen 192.168.100.1:443\n    Listen 127.0.0.1:443"  /etc/apache2/ports.conf
		else
			/usr/bin/logger -t reset "ports.conf is invalid, can't reset it"
		fi
	fi
}


reset_ssh_listen_address () {

	if [ -e /etc/ssh/sshd_config ]; then
		# remove all the listen address
	 	/bin/sed -i "/^ListenAddress.*$/d" /etc/ssh/sshd_config
		# add new listen address
		/bin/sed -i "/interfaces\/protocols sshd will bind to/ a\ListenAddress 192.168.1.10\nListenAddress 192.168.100.1\nListenAddress 127.0.0.1"  /etc/ssh/sshd_config
	fi
}


reset_ntp_conf () {

	if [ -e /etc/ntp.conf ]; then
		# remove all the server lines
	 	/bin/sed -i "/^server.*$/d" /etc/ntp.conf
		echo "server 210.72.145.44" >> /etc/ntp.conf
	fi
}


extract_nvscan_nasl_files () {

	PLUGTARORIG="/opt/nvscan/lib/nvscan/plugins-original.tar.bz"
	PLUGTAR="/opt/nvscan/lib/nvscan/plugins.tar.bz"

	if [ -e "$PLUGTAR" ]; then
		tar xfvj $PLUGTARORIG -C /opt/nvscan/lib/nvscan/plugins > /dev/null
		# strip 2 will remove dir name like FTP测试/xxx
		tar xfvj  $PLUGTAR -C /opt/nvscan/lib/nvscan/plugins --strip 2   > /dev/null

		rm $PLUGTARORIG $PLUGTAR
	fi

}

extract_nvscan_nasl_files_when_update () {
	
	PLUGTARORIG="/opt/nvscan/lib/nvscan/plugins-original.tar.bz"
	PLUGTAR="/opt/nvscan/lib/nvscan/plugins.tar.bz"

	if [ -e "$PLUGTARORIG" ]; then
		tar xfvj $PLUGTARORIG -C /opt/nvscan/lib/nvscan/plugins > /dev/null
	
		rm $PLUGTARORIG
	fi

	if [ -e "$PLUGTAR" ]; then
		# strip 2 will remove dir name like FTP测试/xxx
		tar xfvj  $PLUGTAR -C /opt/nvscan/lib/nvscan/plugins --strip 2   > /dev/null
	
		rm $PLUGTAR
	fi
}


