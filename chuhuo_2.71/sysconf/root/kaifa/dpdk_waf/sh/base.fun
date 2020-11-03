echoEx()
{
	echo "[$(date +%Y%m%d%H%M%S)]$1"
	echo "[$(date +%Y%m%d%H%M%S)]$1" >>$log_path_file
}

#判断执行结果,失败即中断
judgeResult()
{
	if [ $? -ne 0 ];then
		echoEx "$1 fail:"$?
		exit 0
	fi
}

#关掉mpserver
judge_dpdk_is_down()
{
echoEx "judge_dpdk_is_down begin"
  mpcount=`ps -ef|grep mp_server|grep -v grep |wc -l`
	if [ $mpcount -ne 0 ];then
	  echoEx "mp_server 运行中,请切换到代理模式后再操作"
	  exit 0
	fi
echoEx "judge_dpdk_is_down end"
}


#清理编译环境
Do_clean_build_env()
{
  echoEx "Do_clean_env begin"
    
	if [ -d "$dpdk_build_path" ]; then  
	    echoEx "do rm -rf $dpdk_build_path"
      rm -rf $dpdk_build_path
	fi 
	
	if [ -d "$waf_build_path" ]; then  
	    echoEx "do rm -rf $waf_build_path"
      rm -rf $waf_build_path
	fi  
	echoEx "Do_clean_env end"
}



#判断内存是否小于16g
judge_is_mem8g()
{
echoEx "judge_is_mem8g begin"
	memtotal=`cat /proc/meminfo | grep -i MemTotal |awk '{ print $2}' `
	if [ $memtotal -lt 16000000 ]; then  
    type_mem=mem8g
    echo 2048 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
    echo 2048 > /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages
  else
    type_mem=mem16g
    echo 5120 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
    echo 5120 > /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages
  fi
  echoEx "mem size:$memtotal ,type_mem:$type_mem"
echoEx "judge_is_mem8g end"
}


#判断是否有82574L网口
judge_is_82574()
{
echoEx "judge_is_82574 begin"
  chmod 755 $cur_path/sh/dpdk_nic_bind.py
	n82574=`$cur_path/sh/dpdk_nic_bind.py --s | grep 82574|wc -l`
	if [ $n82574 -ne 0 ];then
	type_82574=82574y
	else
	type_82574=82574n
	fi
	echoEx "n82574:$n82574,type_82574:$type_82574"
echoEx "judge_is_82574 end"
}


#判断查看CPU核心数是否小于8
judge_is_cpu4()
{
echoEx "judge_is_cpu4 begin"
	cputotal=`cat /proc/cpuinfo | grep -i processor|wc -l `
	if [ $cputotal -lt 8 ]; then  
    type_cpu=cpu4
    else
    type_cpu=cpu8
    fi
  echoEx "cputotal:$cputotal ,type_cpu:$type_cpu"
echoEx "judge_is_cpu4 end"
}


#生成版本信息文件
Do_version_file()
{	
echoEx "Do_version_file begin"
  echo "[$(date +%Y%m%d%H%M%S)]$1" >$dpdk_build_path/warper_version.ini
  echo "[$(date +%Y%m%d%H%M%S)]$1" >$waf_build_path/bluedon_waf_version.ini
echoEx "Do_version_file end"
}



