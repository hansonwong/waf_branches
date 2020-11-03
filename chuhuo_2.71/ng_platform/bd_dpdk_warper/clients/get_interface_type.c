#include <unistd.h>
#include <dpdk_warp.h>
#include "dpdk_frame.h"

#define STATUS_KNI 0x10
struct system_info  *sysinfo;

void usage(char *argv){
	printf("Usage:\n");
	printf("		%s interface_name ...\n",argv);
}
int main(int argc,char *argv[]){
	int ret,i,j;
	int network_num;
	char buffer[1024] = {0};
	if(argc < 2){
		usage(argv[0]);
		exit(-1);
	}
	
	sysinfo=get_dpdkshm((char*)"dpdk-system-info", (char*)"program1");
	if(!sysinfo) {
			printf("get sharemeory fail\n");
			return -1;
	}
	for(i=1;i<argc;i++){
		for(j=0;j<RTE_MAX_ETHPORTS;j++){
			if(sysinfo->portinfos.kni[j]->name){
				if(strncmp(sysinfo->portinfos.kni[j]->name,argv[i],strlen(argv[i]))==0){
					if(sysinfo->portinfos.status_uk[j]&STATUS_KNI){
						sprintf(buffer+strlen(buffer),"%s,1\n",argv[i]);
					}
					else{
						sprintf(buffer+strlen(buffer),"%s,0\n",argv[i]);
					}	
					break;
				}
			}
		}
		if(j==RTE_MAX_ETHPORTS){
			sprintf(buffer+strlen(buffer),"%s,-1\n",argv[i]);
		}
	}
	printf("%s",buffer);
	return 0;
}

