#include <dpdk_warp.h>
#include "dpdk_frame.h"

struct system_info  *sysinfo;

int main(int argc, char *argv[])
{
	if(argc != 2) {
		printf("usage:./fwaudit on or ./fwaudit off or ./fwaudit status\n");
		return -1;
	}	
	
	sysinfo=get_dpdkshm((char*)"fwaudit", (char*)"program1");
	if(!sysinfo) {
		printf("get sharemeory fail\n");
		exit(-1);
	}

	if(!strcmp(argv[1], "on")) {
		printf("fwaudit on\n");
		sysinfo->fwaudit = 1;	
	}
	else if(!strcmp(argv[1], "off")) {
		printf("fwaudit off\n");
		sysinfo->fwaudit = 0;
	}if(!strcmp(argv[1], "status")){
		printf("fwaudit = %d\n", sysinfo->fwaudit);	
	}
	else
		printf("usage:./fwaudit on or ./fwaudit off or ./fwaudit status\n");

	return 0;
}

