#include <dpdk_warp.h>
#include "dpdk_frame.h"

struct system_info  *sysinfo;

int main(int argc, char *argv[])
{
	int ret = 0;
	int port1 = 0, port2 = 0;
	struct portinfo *portinfos;
	
	if(argc != 4) {
		printf("usage:./vir_line add vEth0 vEth1\n");
		return -1;
	}	
	
	sysinfo=get_dpdkshm((char*)"vir_line", (char*)"program1");
	if(!sysinfo) {
		printf("get sharemeory fail\n");
		return -1;
	}

	port1 = atoi(argv[2] + 4);
	port2 = atoi(argv[3] + 4);

	portinfos = &(sysinfo->portinfos);

	if(strcmp(argv[1], "add") == 0) {
		if((portinfos->mode[port1].mode == DIRECT_CONNECT) || (portinfos->mode[port2].mode == DIRECT_CONNECT)) {
			printf("There is a port had been set vir_line, can not change!\n");
			return -1;
		}
		ret = set_portmode(sysinfo, port1, DIRECT_CONNECT, port2);
	}else if(strcmp(argv[1], "del") == 0) {
		ret = set_portmode(sysinfo, port1, ADVANCED, 0);
		ret = set_portmode(sysinfo, port2, ADVANCED, 0);
	}else if(strcmp(argv[1], "edit") == 0) {
		int value1 = portinfos->mode[port1].value;
		int value2 = portinfos->mode[port2].value;
		
		if(portinfos->mode[value1].mode == DIRECT_CONNECT) {
			set_portmode(sysinfo, value1, ADVANCED, 0);
		}

		if(portinfos->mode[value2].mode == DIRECT_CONNECT) {
			set_portmode(sysinfo, value2, ADVANCED, 0);
		}

		ret = set_portmode(sysinfo, port1, DIRECT_CONNECT, port2);
	}	

	return ret;
}



