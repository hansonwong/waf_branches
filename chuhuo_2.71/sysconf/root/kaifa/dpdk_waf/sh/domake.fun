#查看大页内存挂载，如无即挂载
judge_hugepages_is_mount()
{
echoEx "judge_hugepages_is_mount begin"
    nhugepages=`cat /proc/mounts|grep hugetlbfs|wc -l`
	if [ $nhugepages -eq 0 ];then
	  echoEx "do mount hugepages "
	  mount_hugepages=y
	  mkdir -p /mnt/huge
	  mount -t hugetlbfs nodev /mnt/huge
	  echo 5120 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
	  echo 5120 > /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages
	fi
echoEx "judge_hugepages_is_mount end"
}

#当前脚本加载的大页内存，编译完毕后，卸载
umount_hugepages()
{
	echoEx "umount_hugepages begin"
	
	if [[ $mount_hugepages =~ "y" ]] ;then
	  echoEx "do umount_hugepages"
	  umount /mnt/huge
	  if [ $? -eq 0 ];then
	  rm -rf /mnt/huge
	  fi
	fi
	
	echoEx "umount_hugepages end"
}

#编译dpdk-1.8.0
Do_Build_dpdk()
{	
echoEx "Do_Build_dpdk begin"
	cd $dpdk_build_path/dpdk-1.8.0/
	./tools/setup.sh << EOF >> $log_path_file 2>&1
23

9

29

EOF


  judgeResult "build dpdk-1.8.0"	
  
echoEx "Do_Build_dpdk end"
}

#编译bd_dpdk_warper
Do_Build_bd_dpdk_warper()
{	
echoEx "Do_Build_bd_dpdk_warper begin"
	cd $dpdk_build_path/bd_dpdk_warper/
	export RTE_SDK=/home/ng_platform/dpdk-1.8.0
	echoEx "Do_Build_bd_dpdk_warper dpdk_warper.sh "
	./dpdk_warper.sh  >> $log_path_file 2>&1
  judgeResult "build bd_dpdk_warper"		
echoEx "Do_Build_bd_dpdk_warper end"
}

#编译ng_platform
Do_Build_ng_platform()
{	
echoEx "Do_Build_ng_platform begin"
  #修改文件属性
	cd $dpdk_build_path/
	chmod -R 755 *
	
	judge_hugepages_is_mount
	
	Do_Build_dpdk
	Do_Build_bd_dpdk_warper
	
	umount_hugepages
echoEx "Do_Build_ng_platform end"
}

#编译ModSecurity
Do_Build_ModSecurity()
{	
echoEx "Do_Build_ModSecurity begin"
	cd $waf_build_path/ModSecurity
	echoEx "Do_Build_ModSecurity:make clean"
	make clean  >> $log_path_file 2>&1
	
	echoEx "Do_Build_ModSecurity:autogen.sh"
	./autogen.sh  >> $log_path_file 2>&1
  judgeResult "ModSecurity autogen.sh"	
  
  echoEx "Do_Build_ModSecurity:configure"
  ./configure --enable-standalone-module --disable-mlogc  >> $log_path_file 2>&1
  judgeResult "ModSecurity configure "	
  
  echoEx "Do_Build_ModSecurity:make"
  make  >> $log_path_file 2>&1
  judgeResult "ModSecurity make"
echoEx "Do_Build_ModSecurity end"
}

#编译nginx-1.4.4
Do_Build_nginx()
{	
echoEx "Do_Build_nginx begin"
	cd $waf_build_path/nginx-1.4.4
	
	echoEx "Do_Build_nginx:make clean"
	make clean  >> $log_path_file 2>&1
	
	echoEx "Do_Build_nginx:premake.sh"
	./premake.sh  >> $log_path_file 2>&1
  judgeResult "nginx premake.sh"	
  
  echoEx "Do_Build_nginx:make"
  make  >> $log_path_file 2>&1
  judgeResult "nginx make "	
  
  echoEx "Do_Build_nginx:make install"
  make install >> $log_path_file 2>&1
  judgeResult "nginx make install"	
  
  cd $bdwaf_install_path
  chmod 754 ./nginx*
	
  cp -f ./nginx ./bdwaf.new
  judgeResult "cp -f cp -f ./nginx ./bdwaf.new"
  
echoEx "Do_Build_nginx end"
}

#编译ModSecurity跟nginx-1.4.4
Do_Build_bluedon_waf()
{	
echoEx "Do_Build_bluedon_waf begin"
	#修改文件属性
	cd $waf_build_path/
	chmod -R 755 *
  
  #编译ModSecurity
  Do_Build_ModSecurity
  
  #编译nginx-1.4.4
  Do_Build_nginx  
echoEx "Do_Build_bluedon_waf end"
}
