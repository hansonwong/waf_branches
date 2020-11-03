#include <dpdk_warp.h>
#include "dpdk_frame.h"

struct system_info  *sysinfo;

int main(int argc, char *argv[])
{
	if(argc != 2) {
		printf("usage:./use_kernel on or ./use_kernel off\n");
		return -1;
	}	
	
	sysinfo=get_dpdkshm((char*)"use_kernel", (char*)"program1");
	if(!sysinfo) {
		printf("get sharemeory fail\n");
		exit(-1);
	}

	if(!strcmp(argv[1], "on")) {
		printf("use_kernel on\n");
		sysinfo->kernel_stack_flag = 0;	
	}
	else if(!strcmp(argv[1], "off")) {
		printf("use_kernel off\n");
		sysinfo->kernel_stack_flag = 1;
	}
	else
		printf("usage:./use_kernel on or ./use_kernel off\n");

	

	return 0;
}

