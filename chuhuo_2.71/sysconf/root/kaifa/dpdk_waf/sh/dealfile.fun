#���Ʊ�׼��ng_platform�Ĵ���
Do_copy_ng_platform_file()
{
  echoEx "Do_copy_ng_platform_file begin"
	cp -rf $cur_path/sour_code/ng_platform $dpdk_build_path
	judgeResult "copy ng_platform"
	echoEx "Do_copy_ng_platform_file end"
}


#���Ʊ�׼��bluedon_waf�Ĵ���
Do_copy_bluedon_waf_file()
{
  echoEx "Do_copy_bluedon_waf_file begin"
	#׼��bluedon_waf�Ĵ���
	cp -rf $cur_path/sour_code/bluedon_waf  $waf_build_path
	judgeResult "copy bluedon_waf"
	
	echoEx "Do_copy_bluedon_waf_file end"
}

#�����ڴ�8G��Ҫ�޸ĵ��ļ�
Do_mem8g_file()
{	
echoEx "Do_mem8g_file begin"
	sed -i '/^#define DPDK_NB_MBUFS/ c#define DPDK_NB_MBUFS  70000' $dpdk_build_path/bd_dpdk_warper/include2/dpdk_frame.h
	echo 2048 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
  echo 2048 > /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages
echoEx "Do_mem8g_file end"
}

#�����ڴ�16G��Ҫ�޸ĵ��ļ�
Do_mem16g_file()
{	
echoEx "Do_mem16g_file begin"
	echo 5120 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
  echo 5120 > /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages
echoEx "Do_mem16g_file end"
}

#����82574������Ҫ�޸ĵ��ļ�
Do_82574y_file()
{
echoEx "Do_82574y_file begin"	
  #ע�͵������жϵ�������ע��
	sed -i  '/.intr_conf = {/,+2 s#^#//#g' $dpdk_build_path/bd_dpdk_warper/lib2/dpdk_frame.c
	sed -i  's#rte_eth_dev_callback_register(#//rte_eth_dev_callback_register(#g' $dpdk_build_path/bd_dpdk_warper/lib2/dpdk_frame.c
	
	#�������ڼ�⺯��
	sed -i '/do_manager_task(__attribute_/ i\static void port_check(void) \n{\n        uint8_t portid,flag=0;\n        uint8_t port_num=portinfos->portn;\n        struct rte_eth_link  link;\n\n        for (portid = 0; portid < port_num; portid++) {\n                update_port_status(portid);\n        }\n}\n' $dpdk_build_path/bd_dpdk_warper/server/server.c 
	
	#�����ڼ�⺯���ŵ�������������
	sed -i '/detect_client(/ a\port_check();' $dpdk_build_path/bd_dpdk_warper/server/server.c 		
echoEx "Do_82574y_file end"
}
#����cpu4��Ҫ�޸ĵ��ļ�
Do_cpu4_file()
{	
echoEx "Do_cpu4_file begin"
  #����kni���߳�ģʽ���0��
  sed -i '/kni_alloc(struct portinfo/,+20 s#//conf.core_id = 0#conf.core_id = 0#g' $dpdk_build_path/bd_dpdk_warper/lib2/dpdk_frame.c
  sed -i '/conf.force_bind = 1;/,/conf.core_id = 1;/ s#^#//#g' $dpdk_build_path/bd_dpdk_warper/lib2/dpdk_frame.c
  
  #�޸�kni�̰߳󶨵�CPU
	#sed -i 's#kthread_bind(kni_kthread, 1)#kthread_bind(kni_kthread, 0)#g' $dpdk_build_path/dpdk-1.8.0/lib/librte_eal/linuxapp/kni/kni_misc.c
	
	#�޸�DPDK�����շ����Ķ�����
	sed -i '/#define ONE_G_PORT_RX_QUEUES/ c#define ONE_G_PORT_RX_QUEUES   1' $dpdk_build_path/bd_dpdk_warper/include2/dpdk_frame.h
  sed -i '/#define ONE_G_PORT_TX_QUEUES/ c#define ONE_G_PORT_TX_QUEUES   1' $dpdk_build_path/bd_dpdk_warper/include2/dpdk_frame.h
  sed -i '/#define TEN_G_PORT_RX_QUEUES/ c#define TEN_G_PORT_RX_QUEUES   1' $dpdk_build_path/bd_dpdk_warper/include2/dpdk_frame.h
  sed -i '/#define TEN_G_PORT_TX_QUEUES/ c#define TEN_G_PORT_TX_QUEUES   1' $dpdk_build_path/bd_dpdk_warper/include2/dpdk_frame.h
  
  #�޸�/usr/local/bluedon/bdwaf/conf/nginx.conf
  sed -i '/^worker_processes/ cworker_processes 2;' $bdwaf_install_path/../conf/nginx.conf*
  sed -i '/^worker_cpu_affinity/ cworker_cpu_affinity 0100 1000;' $bdwaf_install_path/../conf/nginx.conf*
  sed -i '/^\s*worker_connections/ cworker_connections 102400;' $bdwaf_install_path/../conf/nginx.conf*
  sed -i '/^worker_cpu_affinity/ cworker_cpu_affinity 0001 0010;' /etc/nginx/nginx.conf
echoEx "Do_cpu4_file end"
}

#����cpu8��Ҫ�޸ĵ��ļ�
Do_cpu8_file()
{	
echoEx "Do_cpu8_file begin"
  
  #�޸�/usr/local/bluedon/bdwaf/conf/nginx.conf
  sed -i '/^worker_processes/ cworker_processes 4;' $bdwaf_install_path/../conf/nginx.conf*
  sed -i '/^worker_cpu_affinity/ cworker_cpu_affinity 01000000 00100000 00010000 00000100;' $bdwaf_install_path/../conf/nginx.conf*
  sed -i '/^\s*worker_connections/ cworker_connections 204800;' $bdwaf_install_path/../conf/nginx.conf*
  sed -i '/^worker_cpu_affinity/ cworker_cpu_affinity 00000001 10000000 ;' /etc/nginx/nginx.conf
  
echoEx "Do_cpu8_file end"
}

