#include <dpdk_warp.h>
#include "dpdk_frame.h"

struct system_info  *sysinfo;

static void help()
{
	printf("usage:./ddos_flag enable,\tenable ddos defense\n");
	printf("     :./ddos_flag disable,\tdisable ddos defense\n");
	printf("     :./ddos_flag status,\t get the status of ddos defense\n");
}

int main(int argc, char *argv[])
{
	if(argc != 2) {
		help();
		return -1;
	}	
	
	sysinfo=get_dpdkshm((char*)"ddos_flag", (char*)"program1");
	if(!sysinfo) {
		printf("get sharemeory fail\n");
		exit(-1);
	}

	if(!strcmp(argv[1], "enable")) {
		//printf("ddos_flag enable\n");
		sysinfo->ddos_flag = 1;
                if(1 == sysinfo->ddos_flag)
                    printf("ddos_flag enable success\n");
                else
                    printf("ddos_flag enable failed\n");
	}
	else if(!strcmp(argv[1], "disable")) {
		//printf("ddos_flag disable\n");
		sysinfo->ddos_flag = 0;
                if(0 == sysinfo->ddos_flag)
                    printf("ddos_flag disable success\n");
                else
                    printf("ddos_flag disable failed\n");
	}
        else if(!strcmp(argv[1], "status")){
                printf("ddos_flag = %d(%s)\n", sysinfo->ddos_flag, sysinfo->ddos_flag == 0 ? "disable":"enable");
        }
	else
		help();

	return 0;
}

