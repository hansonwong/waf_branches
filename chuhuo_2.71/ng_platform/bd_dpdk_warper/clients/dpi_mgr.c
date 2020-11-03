#include <dpdk_warp.h>
#include "dpdk_frame.h"
#include "dpi.h"

struct system_info  *sysinfo;

void help()
{
    printf("usage:dpi_mgr <enable|disable>\n");
    printf("     :dpi_mgr guess <enable|disable>\n");
    printf("     :dpi_mgr info\n");
}

int main(int argc, char *argv[])
{
	int ret = 0;
	
	if(!(argc == 3 || argc == 2)) {
       	help();
		return -1;
	}
    sysinfo = get_dpdkshm ((char *) "dpi_mgr", (char *) "program1");
	if(!sysinfo) {
		printf("get sharemeory fail\n");
		return -1;
	}    

	if(!strcmp(argv[1], "enable")) {
		sysinfo->ndpist->ndpi_flag[NDPI_SWITCH] = !!1;	
		printf("dpi_flag enabled\n");
	}
	else if(!strcmp(argv[1], "disable")) {
		sysinfo->ndpist->ndpi_flag[NDPI_SWITCH] = !!0;	
		printf("dpi_flag disabled\n");
	}
	else if(!strcmp(argv[1], "info")) {
		printf("NDPI is %s[%d]\n",sysinfo->ndpist->ndpi_flag[NDPI_SWITCH]?"enable":"disable",sysinfo->ndpist->ndpi_flag[NDPI_SWITCH]);
		printf("NDPI guess app is %s[%d]\n",sysinfo->ndpist->ndpi_flag[NDPI_GUESS_PROTO]?"enable":"disable",sysinfo->ndpist->ndpi_flag[NDPI_GUESS_PROTO]);
		//printf("NDPI total flow:%d  used flow:%d\n",MAX_NDPI_FLOW,sysinfo->ndpist.usedflow.cnt);
#ifdef NDPI_MCORE
		rte_ring_dump(stdout,sysinfo->ndpist->allocq);
#endif
	}
	else if(!strcmp(argv[1], "guess")){
		if(argc == 3){
			if(!strcmp(argv[2], "enable")) {
				sysinfo->ndpist->ndpi_flag[NDPI_GUESS_PROTO] = 1;		
				printf("ndpi guess app enabled\n");
				return 0;
			}
			else if(!strcmp(argv[1], "disable")) {
				sysinfo->ndpist->ndpi_flag[NDPI_GUESS_PROTO] = 0;
				printf("ndpi guess app disabled\n");
				return 0;
			}
		}
		goto err;
	}
    else goto err;
	
	return 0;

err:
	help();
	return -1;
}

