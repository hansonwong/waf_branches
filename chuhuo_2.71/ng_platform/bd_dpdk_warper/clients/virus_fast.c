#include <dpdk_warp.h>
#include "dpdk_frame.h"

struct system_info  *sysinfo;

int main(int argc, char *argv[])
{
	if(argc != 2) {
		printf("usage:./detect_virus_fast on or ./detect_virus_fast off or ./detect_virus_fsat status\n");
		return -1;
	}	
	
	sysinfo=get_dpdkshm((char*)"detect_virus_fast", (char*)"program1");
	if(!sysinfo) {
		printf("get sharemeory fail\n");
		exit(-1);
	}

	if(!strcmp(argv[1], "on")) {
		printf("detect_virus_fast on\n");
		sysinfo->detect_virus_fast = 1;	
	}
	else if(!strcmp(argv[1], "off")) {
		printf("detect_virus_fast off\n");
		sysinfo->detect_virus_fast = 0;
	}
	else if(!strcmp(argv[1], "status")){
	    printf("detect_virus_fast = %d\n", sysinfo->detect_virus_fast);	
	}
	else
		printf("usage:./detect_virus_fast on or ./detect_virus_fsat off or ./detect_virus_fsat status\n");

	return 0;
}

