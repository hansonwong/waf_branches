#include <dpdk_warp.h>
#include "dpdk_frame.h"

struct system_info  *sysinfo;

int main(int argc, char *argv[])
{
	if(argc != 2) {
		printf("usage:./portscan on or ./portscan off or ./portscan status\n");
		return -1;
	}	
	
	sysinfo=get_dpdkshm((char*)"portscan", (char*)"program1");
	if(!sysinfo) {
		printf("get sharemeory fail\n");
		exit(-1);
	}

	if(!strcmp(argv[1], "on")) {
		printf("portscan on\n");
		sysinfo->s_portscan = 1;	
	}
	else if(!strcmp(argv[1], "off")) {
		printf("portscan off\n");
		sysinfo->s_portscan = 0;
	}if(!strcmp(argv[1], "status")){
		printf("portscan = %d\n", sysinfo->s_portscan);	
	}
	else
		printf("usage:./portscan on or ./portscan off or ./portscan status\n");

	return 0;
}

