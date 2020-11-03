#!/bin/bash



#�ű���ǰ·��
cur_path=$(cd `dirname $0`; pwd)
#�ű���־·��
log_path_file=$cur_path/install.log

#���汾��������·��
code_path=$cur_path/dest_code/

#mp_server�������·��
dpdk_build_path=/home/ng_platform
#mp_server��װ·��
mp_server_install_path=${dpdk_build_path}

#bdwaf�������·��
waf_build_path=/root/bluedon_waf
#bdwaf��װ·��
bdwaf_install_path=/usr/local/bluedon/bdwaf/sbin

. $cur_path/sh/base.fun
. $cur_path/sh/domake.fun
. $cur_path/sh/dealfile.fun


#Ĭ��Ϊ�ڴ�16g,��82574����,cpu������Ϊ8
type_mem=mem16g
type_82574=82574y
type_cpu=cpu8

#�Ƿ�ǰ�ű����صĴ�ҳ�ڴ�
mount_hugepages=n

#�������
Do_Build_code()
{
echoEx "Do_Build_code begin"

  judge_dpdk_is_down
	
  #�ж�Ӳ�����
  judge_is_mem8g
  judge_is_82574
  judge_is_cpu4

  . $cur_path/sh/do_build_${type_mem}_${type_82574}_${type_cpu}.fun
  Do_Build_${type_mem}_${type_82574}_${type_cpu}
  
echoEx "Do_Build_code end"
}



#���ݵ�ǰ�豸��Ӳ�������ѡ���Ӧ��ǧ�׿ڼ����׿ڵĴ��룬���벢��װ
install()
{
echoEx "install begin"

Do_Build_code

echoEx "install end"
}

echo "">$log_path_file

install
 
