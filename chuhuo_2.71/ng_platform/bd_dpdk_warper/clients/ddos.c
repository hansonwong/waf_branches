#include <dpdk_warp.h>
#include "dpdk_frame.h"

struct system_info  *sysinfo;

int main(int argc, char *argv[])
{
	uint32_t flag = 0;
	
	if(argc != 2) {
		printf("usage:./ddos on or ./ddos off\n");
		return -1;
	}	
	
	sysinfo=get_dpdkshm((char*)"ddos", (char*)"program1");
	if(!sysinfo) {
		printf("get sharemeory fail\n");
		exit(-1);
	}

	if(!strcmp(argv[1], "on")) {
		printf("ddos on\n");
		flag = 0;
	}
	else if(!strcmp(argv[1], "off")) {
		printf("ddos off\n");
		flag = 1;
	}
	else
		printf("usage:./ddos on or ./ddos off\n");

	sysinfo->kernel_stack_flag = flag;	

	return 0;
}

