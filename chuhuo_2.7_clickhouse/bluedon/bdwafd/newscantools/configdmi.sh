#!/bin/sh


get_db_user_and_passwd (){


	# parse the db root user
	DB_ROOT_USER=`/bin/grep "db_root_user" $wafrc_const |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $DB_ROOT_USER ]; then
		echo "db root user is invalid"
		exit 1
	fi


	# parse the db root passwd
	DB_ROOT_PASSWD=`/bin/grep "db_root_passwd" $wafrc_const |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $DB_ROOT_PASSWD ]; then
		echo "db root passwd is invalid"
		exit 1
	fi

	DB_IP=`/bin/grep "db_ip" $wafrc_const |awk -F= '{print $2}' |awk -F\; '{print $1}' |tr -d ' ' |tr -d '"'`
	if [ -z $DB_IP ]; then
		DB_IP="127.0.0.1"
		echo "db ip addr is invalid, use default value $DB_IP"
	fi

}

usage () {
	echo "Usage: `basename $0`  ipaddr" >&2
	echo "       config ip address of DMI interface"
	exit 1
}


###########################################################################################################


if [ $# -lt 1 ]; then
	usage
	exit
fi

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

waf_nic_conf="/etc/waf_nic.conf"
wafrc_const="/etc/waf_constant.rc"

DB_ROOT_PASSWD=
DB_ROOT_USER=
get_db_user_and_passwd


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




