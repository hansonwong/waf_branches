#include <dpdk_warp.h>
#include "dpdk_frame.h"

struct system_info  *sysinfo;

int main(int argc, char *argv[])
{
	int ret = 0;
	int port = 0;
	int mode = 0;
	int bridge_id = 0;
	
	if(argc != 3) {
		printf("usage : ./port_config [port_name] [workmode]\n");
		printf("workmode : bypass:5; bridge:8; mirror:9; route:10; nat:11\n");
		printf("example : ./port_config vEth0 10\n");
		return -1;
	}	
	
	sysinfo=get_dpdkshm((char*)"port_config", (char*)"program1");
	if(!sysinfo) {
		printf("get sharemeory fail\n");
		return -1;
	}

        if (strncmp(argv[1], "vEth", 4) != 0) {
                return -1;
        }

	port = atoi(argv[1] + 4);
	mode = atoi(argv[2]);
	/*if((mode == 8) && (argc == 4))
		bridge_id = atoi(argv[3] + 3);
	else if((mode == 8) && (argc != 4))
		return -1;*/
		
	switch(mode) {
	    case 5:
		ret = set_portmode(sysinfo, port, BYPASS, 0);
	        break;
	    case 8 :
	        ret = set_portmode(sysinfo, port, BRIDGE_SIMPLE, bridge_id);
	        break;
	    case 9:
		ret = set_portmode(sysinfo, port, MIRROR_PORT, 0);
	        break;
	    case 10 :
	        ret = set_portmode(sysinfo, port, ADVANCED, 0);
	        break;
	    case 11 :
	        ret = set_portmode(sysinfo, port, NAT_PORT, 0);
	        break;
	    default:
	        break;
	}

	return ret;
}




