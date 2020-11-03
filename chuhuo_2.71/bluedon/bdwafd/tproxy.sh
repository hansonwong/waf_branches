#!/bin/sh

# add or delete on configure, 0 for add, and 1 for delete. default is add.
DEL_FLAG=0

# bridge or route, 0 for route, and 1 for bridge.default is route.
TYPE=0

# bridge's name.
BRIDGE=""
INTERFACES=""

# destination port. default is 80
DPORT=80

# proxy port. default is 3129.
TPORT=3129

# the number of iptables' rule
IPTABLES=0
EBTABLES=0

# show the help information
usage() {
    return 0
	echo "Usage: tproxy.sh {bridge | route} name {add | del} dport dport_num tport tport_num"
	echo "parameter:"
	echo "       bridge:          bridge transparent proxy mode"
	echo "       route:           route transparent proxy mode"
	echo "       name:            bridge's name. meanless for route transparent proxy mode, but must appear"
	echo "       dport dport_num: specifies the destination port number"
	echo "       tport tport_num: specifies the transparent port number"
	echo "       help:            show this help information"
}

# parse the parameter 
parse_parameter() {
	if test $# = 7; then
		if test $1 = "bridge"; then
			BRIDGE=$2
			TYPE=1
		elif test $1 = "route"; then
			TYPE=0
		else
			usage
			exit 2
		fi
	else
		usage
		exit 1
	fi

	# default is add
	if test $3 = "del"; then
		DEL_FLAG=1
	elif test $3 = "add"; then
		DEL_FLAG=0
	else
		usage
		exit 2
	fi

	DPORT=$5
	TPORT=$7
}

# get the interface from the bridge's name
get_interface() {
	num=`brctl show | wc -l`
	if test $num -lt 3; then
		exit 3
	fi

	INTERFACES=$(brctl show| awk -v num="$num" '{if($0~/^'"$BRIDGE"'/){print $4;while(FNR < num){getline; if($0~/^\w/){exit}else{print $1}}}}')
	unset num
}

# get the number of rule
check_rule() {
	IPTABLES=`iptables -t mangle -L PREROUTING | awk '{if($0~/TPROXY redirect/)print}'| wc -l`
	EBTABLES=`ebtables -t broute -L BROUTING | awk '{if($0~/--ip-proto tcp --ip-dport.*-j redirect  --redirect-target DROP/)print}' | wc -l`
}

add_route() {
	# 增加策略路由
	ip rule add fwmark 1 lookup 100 2>/dev/null
	ip -f inet route add local 0.0.0.0/0 dev lo table 100 2>/dev/null

	# 开启路由功能	
	echo 1 > /proc/sys/net/ipv4/ip_forward

	# 禁用反向路由过滤
	cd /proc/sys/net/ipv4/conf
	for i in ./*/rp_filter; do
   		echo 0 > $i
 	done
 	unset i

 	#设置iptables规则
 	iptables -t mangle -N DIVERT
	iptables -t mangle -A DIVERT -j MARK --set-mark 1
	iptables -t mangle -A DIVERT -j ACCEPT

	iptables -t mangle -A PREROUTING -i eth1 -p tcp --dport $DPORT -m socket -j DIVERT
	iptables -t mangle -A PREROUTING -i eth1 -p tcp --dport $DPORT -j TPROXY --tproxy-mark 0x1/0x1 --on-port $TPORT
	iptables -t mangle -A PREROUTING -i eth2 -p tcp --sport $DPORT -m socket -j DIVERT
	iptables -t mangle -A PREROUTING -i eth2 -p tcp --sport $DPORT -j TPROXY --tproxy-mark 0x1/0x1 --on-port $TPORT
}

add_ebtables() {
	#for i in $INTERFACES; do
	  ebtables -t broute -F
    ebtables -t broute -A BROUTING -p IPv4 -j redirect --redirect-target DROP
		#ebtables -t broute -A BROUTING -i eth1 -p ipv4 --ip-proto tcp --ip-dport $DPORT -j redirect --redirect-target DROP
		#ebtables -t broute -A BROUTING -i eth2 -p ipv4 --ip-proto tcp --ip-sport $DPORT -j redirect --redirect-target DROP
	#done
}

del_ebtables() {
	ebtables -t broute -F
	ebtables -t broute -X
	#for i in $INTERFACES; do
	#	ebtables -t broute -D BROUTING -i $i -p ipv4 --ip-proto tcp --ip-dport $DPORT -j redirect --redirect-target DROP
	#	ebtables -t broute -D BROUTING -i $i -p ipv4 --ip-proto tcp --ip-sport $DPORT -j redirect --redirect-target DROP
	#done
}

add_bridge() {
	get_interface

	num=0
	for i in $INTERFACES; do
		num=`expr $num + 1`
	done

	if test $num -lt 2; then
		exit 4
	fi

	add_ebtables
	cd /proc/sys/net/bridge/
 	for i in *
 	do
   	echo 0 > $i
 	done
 	unset i

 	add_route
}

# clean all the configure
clean_config() {
	# 删除策略路由
	ip rule del fwmark 1 lookup 100 2>/dev/null
	ip -f inet route del local 0.0.0.0/0 dev lo table 100 2>/dev/null

	# 删除桥代理相关配置
	cd /proc/sys/net/bridge/
	for i in *
 	do
   	echo 1 > $i
 	done
 	unset i

	# 删除路由代理相关配置
	# 防止用户是出于路由模式，导致路由无法通过，所以这个不设置回来
	# echo 0 > /proc/sys/net/ipv4/ip_forward
	cd /proc/sys/net/ipv4/conf
	for i in ./*/rp_filter;	do
  		echo 1 > $i
 	done
 	unset i
}

parse_parameter $@
check_rule

if test $DEL_FLAG -eq 0; then
	# add
	if test $TYPE -eq 0; then
		# add route
		if test $IPTABLES -gt 0; then
			iptables -t mangle -A PREROUTING -p tcp --dport $DPORT -j TPROXY --tproxy-mark 0x1/0x1 --on-port $TPORT 
		else
			# no iptables rule exist, add all rule
			add_route
		fi
	else
		#add bridge
		if test $EBTABLES -gt 0; then
			#echo "add ebtables"
			get_interface
			add_ebtables
			iptables -t mangle -A PREROUTING -i eth1 -p tcp --dport $DPORT -j TPROXY --tproxy-mark 0x1/0x1 --on-port $TPORT
			iptables -t mangle -A PREROUTING -i eth2 -p tcp --sport $DPORT -j TPROXY --tproxy-mark 0x1/0x1 --on-port $TPORT
		else
			# no ebtables rule exist, add all rule
			#echo "add bridge"
			add_bridge
		fi
	fi
else
	# delete
	if test $TYPE -eq 0; then
		# delete route
		iptables -t mangle -D PREROUTING -p tcp --dport $DPORT -j TPROXY --tproxy-mark 0x1/0x1 --on-port $TPORT 
		check_rule
		if test $IPTABLES -eq 0; then
			# clean all the configure
			clean_config
		fi
	else
		# delete bridge
		get_interface
		del_ebtables
		check_rule
		#iptables -t mangle -D PREROUTING -p tcp --dport $DPORT -j TPROXY --tproxy-mark 0x1/0x1 --on-port $TPORT	
		iptables -t mangle -F
		iptables -t mangle -X
		if test $EBTABLES -eq 0; then
			# clean all the configure
			clean_config
		fi
	fi
fi

exit 0
