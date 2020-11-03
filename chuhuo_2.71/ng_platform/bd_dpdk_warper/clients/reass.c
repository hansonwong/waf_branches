#include <dpdk_warp.h>
#include "dpdk_frame.h"
#include "dpdk_reass.h"

void reass_help()
{
    printf("usage:reass -E on[off] <start/stop reass>\n");
    printf("     :reass -T 10      <set timeout (0,60](s)>\n");
    printf("     :reass -P 1       <print reass status per 1>\n");
    printf("     :reass -L value   <print reass info>\n");
}

int main(int argc, char *argv[])
{
	int ret = 0;
	
	if(argc != 3) {
        reass_help();
		return -1;
	}
    struct system_info *sysinfo = get_dpdkshm ((char *) "reass", (char *) "program1");
	if(!sysinfo) {
		printf("get sharemeory fail\n");
		return -1;
	}    

    if(strcmp(argv[1], "-E") == 0){
        if(strcmp(argv[2],"on") == 0){
            sysinfo->pktreass->enable = 1;
            printf("enable reass ok!\n");
        }
        else if(strcmp(argv[2],"off") == 0){
            sysinfo->pktreass->enable = 0;
            printf("disable reass ok!\n");
        }
        else {
            reass_help();
            return -1;
        }      
    }

    else if(strcmp(argv[1], "-T") == 0){
        unsigned timeout = 0;
        timeout = atoi(argv[2]);
        if(timeout > 0 && timeout <= 60){
            sysinfo->pktreass->timeout = timeout * sysinfo->pktreass->frag_cycles;
        }
        else{
            printf("you must set (0-60]s\n");
            return -1;
        }    
    }
    
    else if(strcmp(argv[1], "-P") == 0){ 
        unsigned printime = 0;
        printime = atoi(argv[2]);
        if(printime == 0){
            reass_info_dump(sysinfo);          
            return 0;
        }
        while(1){
            reass_info_dump(sysinfo);          
            sleep(printime);
        }
    }
    else if(strcmp(argv[1], "-L") == 0 && strcmp(argv[2], "value") == 0 ){
        printf("Reass Enable :%s\n",sysinfo->pktreass->enable ? "on" : "off");
        printf("Reass Timeout:%lu\n",sysinfo->pktreass->timeout / sysinfo->pktreass->frag_cycles);
    }
    else {
        reass_help();
        return -1;
    }

	return 0;
}



