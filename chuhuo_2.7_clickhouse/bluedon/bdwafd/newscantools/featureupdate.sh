#!/bin/sh
#
# Provides:          featureupdate.sh
# Description:       Use this shell script to control feature set
#                   
# Author: Claus Wei <zhongwei@yxlink.com>



wafrc_setting="/etc/waf_setting.rc"
wafconf="/var/waf/waf.conf"
phpconf="/var/www/yx.config.inc.php"


FEATURE_SET=""
MAX_TASK=""
MAX_THREAD=""
MAX_IP_OF_TASK=""
IP_RANGE_GLOBAL=""
MAX_PORT_THREAD_GLOBAL=""
MAX_HOST_THREAD_GLOBAL=""
MAX_WEB_THREAD_GLOBAL=""
MAX_WEAK_THREAD_GLOBAL=""
WARRANTY_TYPE=""
WARRANTY=""

if [ $# -lt 2 ]; then
	/usr/bin/logger -t "featureupdate"  "param num less than 2"
	exit 0
fi

#/usr/bin/logger -t "featureupdate"  "$*"

params=$#

loop=0
while [ $# -ne 0 ]
do 
	param=${1}
	#echo $param

	if echo $param | grep "feature_set" > /dev/null 2>&1; then
		FEATURE_SET=`echo $param | awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
		echo "feature_set: $FEATURE_SET"
	elif echo $param | grep "max_task" > /dev/null 2>&1; then
		MAX_TASK=`echo $param | awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
		echo "max_task: $MAX_TASK"
	elif echo $param | grep "max_thread" > /dev/null 2>&1; then
		MAX_THREAD=`echo $param | awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
		echo "max_thread: $MAX_THREAD"
	elif echo $param | grep "max_ip_of_task" > /dev/null 2>&1; then
		MAX_IP_OF_TASK=`echo $param | awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
		echo "max_ip_of_task: $MAX_IP_OF_TASK"
	elif echo $param | grep "ip_range_global" > /dev/null 2>&1; then
		IP_RANGE_GLOBAL=`echo $param | awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
		echo "ip_range: $IP_RANGE_GLOBAL"
	elif echo $param | grep "max_port_thread_global" > /dev/null 2>&1; then
		MAX_PORT_THREAD_GLOBAL=`echo $param | awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
		echo "max_port_thread_global: $MAX_PORT_THREAD_GLOBAL"
	elif echo $param | grep "max_host_thread_global" > /dev/null 2>&1; then
		MAX_HOST_THREAD_GLOBAL=`echo $param | awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
		echo "max_host_thread_global: $MAX_HOST_THREAD_GLOBAL"
	elif echo $param | grep "max_web_thread_global" > /dev/null 2>&1; then
		MAX_WEB_THREAD_GLOBAL=`echo $param | awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
		echo "max_web_thread_global: $MAX_WEB_THREAD_GLOBAL"
	elif echo $param | grep "max_weak_thread_global" > /dev/null 2>&1; then
		MAX_WEAK_THREAD_GLOBAL=`echo $param | awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
		echo "max_weak_thread_global: $MAX_WEAK_THREAD_GLOBAL"
	elif echo $param | grep "warranty_type" > /dev/null 2>&1; then
		WARRANTY_TYPE=`echo $param | awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
		echo "warranty_type: $WARRANTY_TYPE"
	elif echo $param | grep "warranty" > /dev/null 2>&1; then
		WARRANTY=`echo $param | awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
		echo "warranty: $WARRANTY"
	else
		echo "new parameter, don't know how to handle"
	fi

	shift
done


if [ ! -z "$FEATURE_SET" ]; then

	if [ `expr length $FEATURE_SET` -eq 35 ]; then

		FAILURE=0
		echo $FEATURE_SET | grep "[0-1]\{8\},[0-1]\{8\},[0-1]\{8\},[0-1]\{8\}"
		FAILURE=$?
		if [ $FAILURE -eq 0 ]; then
			
			echo "new feature set: $FEATURE_SET"
			if [ -e $wafrc_setting ]; then
				/bin/chmod +w $wafrc_setting 
				/bin/sed -i "s/^.*feature_set.*$/feature_set = \"$FEATURE_SET\"/g"  $wafrc_setting
				/bin/chmod -w $wafrc_setting
			fi

			if [ -e $phpconf ]; then
				/bin/sed -i "s/^.*\$feature_set.*;/        \$feature_set = \'$FEATURE_SET\';/g"  $phpconf
			fi
		else
			echo "feature set is invalid, ignore it"
		fi
	else
		echo "feature set is null or other case, ignore it"
	fi


fi


if [ ! -z "$MAX_TASK" ]; then
	if [ $MAX_TASK -ge "1" ]; then
		if [ -e $wafrc_setting ]; then
			/bin/chmod +w $wafrc_setting 
			/bin/sed -i "s/^.*max_task.*$/max_task = $MAX_TASK/g"  $wafrc_setting
			/bin/chmod -w $wafrc_setting
		fi

		if [ -e $phpconf ]; then
			/bin/sed -i "s/^.*\$max_task_global.*;/        \$max_task_global = \'$MAX_TASK\';/g"  $phpconf
		fi
	else
		echo "max task is invalid, ignore it"
	fi
fi


if [ ! -z "$MAX_THREAD" ]; then
	if [ $MAX_THREAD -ge "1" ]; then
		if [ -e $wafrc_setting ]; then
			/bin/chmod +w $wafrc_setting 
			/bin/sed -i "s/^.*max_thread.*$/max_thread = $MAX_THREAD/g"  $wafrc_setting
			/bin/chmod -w $wafrc_setting
		fi

		if [ -e $phpconf ]; then
			/bin/sed -i "s/^.*\$max_thread_global.*;/        \$max_thread_global = \'$MAX_THREAD\';/g"  $phpconf
		fi
	else
		echo "max thread is invalid, ignore it"
	fi
fi


if [ ! -z "$MAX_IP_OF_TASK" ]; then
	if [ $MAX_IP_OF_TASK -ge "1" ]; then
		if [ -e $wafrc_setting ]; then
			/bin/chmod +w $wafrc_setting 
			/bin/sed -i "s/^.*max_ip_of_task.*$/max_ip_of_task = $MAX_IP_OF_TASK/g"  $wafrc_setting
			/bin/chmod -w $wafrc_setting
		fi

		if [ -e $phpconf ]; then
			/bin/sed -i "s/^.*\$max_task_ip_global.*;/        \$max_task_ip_global = \'$MAX_IP_OF_TASK\';/g"  $phpconf
		fi
	else
		echo "max ip of task is invalid, ignore it"
	fi
fi


if [ ! -z "$IP_RANGE_GLOBAL" ]; then
	if [ -e $wafrc_setting ]; then
		/bin/chmod +w $wafrc_setting 
		/bin/sed -i "s/^.*ip_range_global.*$/ip_range_global = \"${IP_RANGE_GLOBAL}\"/g"  $wafrc_setting
		/bin/chmod -w $wafrc_setting
	fi

	if [ -e $phpconf ]; then
		/bin/sed -i "s/^.*\$ip_range_global.*;/        \$ip_range_global = \'${IP_RANGE_GLOBAL}\';/g"  $phpconf
	fi
fi


if [ ! -z "$MAX_PORT_THREAD_GLOBAL" ]; then
	if [ $MAX_PORT_THREAD_GLOBAL -ge "1" ]; then
		if [ -e $wafrc_setting ]; then
			/bin/chmod +w $wafrc_setting 
			/bin/sed -i "s/^.*max_port_thread_global.*$/max_port_thread_global = $MAX_PORT_THREAD_GLOBAL/g"  $wafrc_setting
			/bin/chmod -w $wafrc_setting
		fi

		if [ -e $phpconf ]; then
			/bin/sed -i "s/^.*\$max_port_thread_global.*;/        \$max_port_thread_global = \'$MAX_PORT_THREAD_GLOBAL\';/g"  $phpconf
		fi
	else
		echo "max_port_thread_global is invalid, ignore it"
	fi
fi

if [ ! -z "$MAX_HOST_THREAD_GLOBAL" ]; then
	if [ $MAX_HOST_THREAD_GLOBAL -ge "1" ]; then
		if [ -e $wafrc_setting ]; then
			/bin/chmod +w $wafrc_setting 
			/bin/sed -i "s/^.*max_host_thread_global.*$/max_host_thread_global = $MAX_HOST_THREAD_GLOBAL/g"  $wafrc_setting
			/bin/chmod -w $wafrc_setting
		fi

		if [ -e $phpconf ]; then
			/bin/sed -i "s/^.*\$max_host_thread_global.*;/        \$max_host_thread_global = \'$MAX_HOST_THREAD_GLOBAL\';/g"  $phpconf
		fi
	else
		echo "max_host_thread_global is invalid, ignore it"
	fi
fi

if [ ! -z "$MAX_WEB_THREAD_GLOBAL" ]; then
	if [ $MAX_WEB_THREAD_GLOBAL -ge "1" ]; then
		if [ -e $wafrc_setting ]; then
			/bin/chmod +w $wafrc_setting 
			/bin/sed -i "s/^.*max_web_thread_global.*$/max_web_thread_global = $MAX_WEB_THREAD_GLOBAL/g"  $wafrc_setting
			/bin/chmod -w $wafrc_setting
		fi

		if [ -e $phpconf ]; then
			/bin/sed -i "s/^.*\$max_web_thread_global.*;/        \$max_web_thread_global = \'$MAX_WEB_THREAD_GLOBAL\';/g"  $phpconf
		fi
	else
		echo "max_web_thread_global is invalid, ignore it"
	fi
fi

if [ ! -z "$MAX_WEAK_THREAD_GLOBAL" ]; then
	if [ $MAX_WEAK_THREAD_GLOBAL -ge "1" ]; then
		if [ -e $wafrc_setting ]; then
			/bin/chmod +w $wafrc_setting 
			/bin/sed -i "s/^.*max_weak_thread_global.*$/max_weak_thread_global = $MAX_WEAK_THREAD_GLOBAL/g"  $wafrc_setting
			/bin/chmod -w $wafrc_setting
		fi

		if [ -e $phpconf ]; then
			/bin/sed -i "s/^.*\$max_weak_thread_global.*;/        \$max_weak_thread_global = \'$MAX_WEAK_THREAD_GLOBAL\';/g"  $phpconf
		fi
	else
		echo "max_weak_thread_global is invalid, ignore it"
	fi
fi


if [ ! -z "$WARRANTY" ]; then
	# echo "warranty : $WARRANTY"
	if [ `expr length $WARRANTY` -gt 1 ]; then

		echo "new warranty: $WARRANTY"
		
		if [ $WARRANTY_TYPE == "1" ]; then
			WARRANTY="1"
		else
			WARRANTY=${WARRANTY/\//\\\/}
		fi

		if [ -e $wafrc_setting ]; then
			/bin/chmod +w $wafrc_setting 
			
			if grep "warranty_duration" $wafrc_setting > /dev/null 2>&1
			then
				/bin/sed -i "s/^.*warranty_duration.*$/warranty_duration = \"$WARRANTY\"/g"  $wafrc_setting
			else
				echo "" >> $wafrc_setting
				echo "[warranty]" >> $wafrc_setting
				echo "warranty_duration = \"$WARRANTY\"" >> $wafrc_setting
			fi
			
			/bin/chmod -w $wafrc_setting
		fi

		if [ -e $phpconf ]; then
			if grep "warranty_duration" $phpconf > /dev/null 2>&1
			then
				/bin/sed -i "s/^.*\$warranty_duration.*;/        \$warranty_duration = \'$WARRANTY\';/g"  $phpconf
			else
				/bin/sed -i "/\$lic_expiry_action/ a\        \$warranty_duration = \'$WARRANTY\';" $phpconf
			fi
		fi
		
		if [ -e $wafconf ]; then
			if grep "warranty_duration" $wafconf > /dev/null 2>&1
			then
				/bin/sed -i "s/^.*warranty_duration.*$/warranty_duration = \"$WARRANTY\"/g"  $wafconf
			else
				echo "" >> $wafconf
				echo "[warranty]" >> $wafconf
				echo "warranty_duration = \"$WARRANTY\"" >> $wafconf
			fi
		fi
	else
		echo "warranty set is null or other case, ignore it"
	fi
fi