#ng_platform:�ڴ�8G+82574��+8cpu������
Do_Build_ng_platform_mem8g_82574n_cpu8()
{
  echoEx "Do_Build_ng_platform_mem8g_82574n_cpu8 begin"
  
  #���Ʊ�׼�����׿�ng_platform�Ĵ���
	Do_copy_ng_platform_file
	
	#�����ڴ�8G��Ҫ�޸ĵ��ļ�
  Do_mem8g_file
  
  #����cpu8��Ҫ�޸ĵ��ļ�
	Do_cpu8_file
	#����ng_platform
	Do_Build_ng_platform
	
	echoEx "Do_Build_ng_platform_mem8g_82574n_cpu8 end"
}


#bluedon_waf:�ڴ�8G+82574��+8cpu������
Do_Build_bluedon_waf_mem8g_82574n_cpu8()
{
	echoEx "Do_Build_bluedon_waf_mem8g_82574n_cpu8 begin"
	#���Ʊ�׼��bluedon_waf�Ĵ���
	Do_copy_bluedon_waf_file
	
	Do_Build_bluedon_waf
	
	echoEx "Do_Build_bluedon_waf_mem8g_82574n_cpu8 end"	
}

#�ڴ�8G+82574��+8cpu������
Do_Build_mem8g_82574n_cpu8()
{
echoEx "DO_Build_mem8g_82574n_cpu8 begin"

Do_clean_build_env;
Do_Build_ng_platform_mem8g_82574n_cpu8;
Do_Build_bluedon_waf_mem8g_82574n_cpu8;

Do_version_file "dpdk_waf_mem8g_82574n_cpu8"

echoEx "DO_Build_mem8g_82574n_cpu8 end"
}
