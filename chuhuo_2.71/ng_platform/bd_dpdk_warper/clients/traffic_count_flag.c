#include <unistd.h>
#include <dpdk_warp.h>
#include "dpdk_frame.h"

struct system_info  *sysinfo;
#define MAX_BUF_SIZE 1024
void usage(char *argv){
	printf("//-------------------------------------\n");
	printf("Usage: %s enable | disable | status\n",argv);
	printf("//-------------------------------------\n");
}

int main(int argc, char *argv[])
{
	int ret;

	if(argc!=2){
		usage(argv[0]);
		return -1;
	}
	sysinfo=get_dpdkshm((char*)"dpdk-system-info", (char*)"program1");
	if(!sysinfo) {
			printf("get sharemeory fail\n");
			return -1;
	}
	if(!strcmp(argv[1],"enable")){
		if(sysinfo->ftab.ts_flag ==0){
			sysinfo->ftab.ts_flag=1;
		}
		printf("traffic_count_flag enable\n");
	}
	else if(!strcmp(argv[1],"disable")){
		if(sysinfo->ftab.ts_flag==1){
			sysinfo->ftab.ts_flag=0;
		}
		printf("traffic_count_flag disable\n");
	}
	else if(!strcmp(argv[1],"status")){
		Flow_table_status_dump(&sysinfo->ftab);
	}
	else{
		usage(argv[0]);
	}
	return 0;
}

