#ng_platform:内存16G+82574无+8cpu核心数
Do_Build_ng_platform_mem16g_82574n_cpu8()
{
  echoEx "Do_Build_ng_platform_mem16g_82574n_cpu8 begin"
  
  #复制标准的万兆口ng_platform的代码
	Do_copy_ng_platform_file
	
	#处理内存16G需要修改的文件
	Do_mem16g_file
	#处理cpu8需要修改的文件
	Do_cpu8_file
	#编译ng_platform
	Do_Build_ng_platform
	
	echoEx "Do_Build_ng_platform_mem16g_82574n_cpu8 end"
}


#bluedon_waf:内存16G+82574无+8cpu核心数
Do_Build_bluedon_waf_mem16g_82574n_cpu8()
{
	echoEx "Do_Build_bluedon_waf_mem16g_82574n_cpu8 begin"
	#复制标准的bluedon_waf的代码
	Do_copy_bluedon_waf_file
	
	Do_Build_bluedon_waf
	
	echoEx "Do_Build_bluedon_waf_mem16g_82574n_cpu8 end"	
}

#内存16G+82574无+8cpu核心数
Do_Build_mem16g_82574n_cpu8()
{
echoEx "DO_Build_mem16g_82574n_cpu8 begin"

Do_clean_build_env;
Do_Build_ng_platform_mem16g_82574n_cpu8;
Do_Build_bluedon_waf_mem16g_82574n_cpu8;

Do_version_file "dpdk_waf_mem16g_82574n_cpu8"

echoEx "DO_Build_mem16g_82574n_cpu8 end"
}
