#ng_platform:�ڴ�16G+82574��+4cpu������
Do_Build_ng_platform_mem16g_82574n_cpu4()
{
  echoEx "Do_Build_ng_platform_mem16g_82574n_cpu4 begin"
  
  #���Ʊ�׼�����׿�ng_platform�Ĵ���
	Do_copy_ng_platform_file
	
	#�����ڴ�16G��Ҫ�޸ĵ��ļ�
	Do_mem16g_file
	
	#�������׿ڵ�cpu4��Ҫ�޸ĵ��ļ�
  Do_cpu4_file

	#����ng_platform
	Do_Build_ng_platform
	
	echoEx "Do_Build_ng_platform_mem16g_82574n_cpu4 end"
}


#bluedon_waf:�ڴ�16G+82574��+4cpu������
Do_Build_bluedon_waf_mem16g_82574n_cpu4()
{
	echoEx "Do_Build_bluedon_waf_mem16g_82574n_cpu4 begin"
	#���Ʊ�׼��bluedon_waf�Ĵ���
	Do_copy_bluedon_waf_file
	
	Do_Build_bluedon_waf
	
	echoEx "Do_Build_bluedon_waf_mem16g_82574n_cpu4 end"	
}

#�ڴ�16G+82574��+4cpu������
Do_Build_mem16g_82574n_cpu4()
{
echoEx "DO_Build_mem16g_82574n_cpu4 begin"

Do_clean_build_env;
Do_Build_ng_platform_mem16g_82574n_cpu4;
Do_Build_bluedon_waf_mem16g_82574n_cpu4;

Do_version_file "dpdk_waf_mem16g_82574n_cpu4"

echoEx "DO_Build_mem16g_82574n_cpu4 end"
}
