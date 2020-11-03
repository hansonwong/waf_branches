#include <dpdk_warp.h>
#include "dpdk_frame.h"

struct system_info  *sysinfo;

int main(int argc, char *argv[])
{
	if(argc != 2) {
		printf("usage:./detect_virus on or ./detect_virus off or ./detect_virus status\n");
		return -1;
	}	
	
	sysinfo=get_dpdkshm((char*)"detect_virus", (char*)"program1");
	if(!sysinfo) {
		printf("get sharemeory fail\n");
		exit(-1);
	}

	if(!strcmp(argv[1], "on")) {
		printf("detect_virus on\n");
		sysinfo->detect_virus = 1;	
	}
	else if(!strcmp(argv[1], "off")) {
		printf("detect_virus off\n");
		sysinfo->detect_virus = 0;
	}if(!strcmp(argv[1], "status")){
		printf("detect_virus = %d\n", sysinfo->detect_virus);	
	}
	else
		printf("usage:./detect_virus on or ./detect_virus off or ./detect_virus status\n");

	return 0;
}

