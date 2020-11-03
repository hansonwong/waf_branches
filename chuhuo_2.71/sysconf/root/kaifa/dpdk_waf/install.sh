#!/bin/bash



#脚本当前路径
cur_path=$(cd `dirname $0`; pwd)
#脚本日志路径
log_path_file=$cur_path/install.log

#各版本代码所在路径
code_path=$cur_path/dest_code/

#mp_server代码编译路径
dpdk_build_path=/home/ng_platform
#mp_server安装路径
mp_server_install_path=${dpdk_build_path}

#bdwaf代码编译路径
waf_build_path=/root/bluedon_waf
#bdwaf安装路径
bdwaf_install_path=/usr/local/bluedon/bdwaf/sbin

. $cur_path/sh/base.fun
. $cur_path/sh/domake.fun
. $cur_path/sh/dealfile.fun


#默认为内存16g,无82574网口,cpu核心数为8
type_mem=mem16g
type_82574=82574y
type_cpu=cpu8

#是否当前脚本加载的大页内存
mount_hugepages=n

#编译代码
Do_Build_code()
{
echoEx "Do_Build_code begin"

  judge_dpdk_is_down
	
  #判断硬件情况
  judge_is_mem8g
  judge_is_82574
  judge_is_cpu4

  . $cur_path/sh/do_build_${type_mem}_${type_82574}_${type_cpu}.fun
  Do_Build_${type_mem}_${type_82574}_${type_cpu}
  
echoEx "Do_Build_code end"
}



#根据当前设备的硬件情况，选择对应的千兆口及万兆口的代码，编译并安装
install()
{
echoEx "install begin"

Do_Build_code

echoEx "install end"
}

echo "">$log_path_file

install
 
