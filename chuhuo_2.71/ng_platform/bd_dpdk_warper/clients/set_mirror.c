#include <dpdk_warp.h>
#include "dpdk_frame.h"

#define MIRROR_IN_PATH   "/etc/mp_server/mirror/mirror_in.conf"
#define MIRROR_OUT_PATH  "/etc/mp_server/mirror/mirror_out.conf"

struct system_info  *sysinfo;

int main(int argc, char *argv[])
{
#if (ENABLE_MIRROR_FUNCTION == 1)
	int ret = 0;
	int i = 0;
	FILE *fp;
	char buf[128] = {0};
	
	if(argc != 2) {
		printf("usage:./set_mirror in or out or all\n");
		return -1;
	}	
	
	sysinfo=get_dpdkshm((char*)"port_config", (char*)"program1");
	if(!sysinfo) {
		printf("get sharemeory fail\n");
		return -1;
	}

	if(!strcmp(argv[1], "in")) {
		//in
		for(i = 0; i < CLIENT_MAX_FILTER; i++) {
			memset(sysinfo->mirror_port[0].user_rule[i], 0x00, sizeof(sysinfo->mirror_port[0].user_rule[i]));
		}
		i = 0;
		memset(buf, 0x00, sizeof(buf));
		fp = fopen(MIRROR_IN_PATH, "r");
		if(!fp)
			return -1;
		while(fgets(buf, sizeof(buf), fp)) {
			rte_memcpy(sysinfo->mirror_port[0].user_rule[i], buf, strlen(buf));
			memset(buf, 0x00, sizeof(buf));
			i++;
			if(i >= CLIENT_MAX_FILTER)
				break;
		}
		fclose(fp);
		ret = set_mirror_port_rules(sysinfo, 0);
	}else if(!strcmp(argv[1], "out")) {
		//out
		for(i = 0; i < CLIENT_MAX_FILTER; i++) {
			memset(sysinfo->mirror_port[1].user_rule[i], 0x00, sizeof(sysinfo->mirror_port[1].user_rule[i]));
		}
		i = 0;
		memset(buf, 0x00, sizeof(buf));
		fp = fopen(MIRROR_OUT_PATH, "r");
		if(!fp)
			return -1;
		while(fgets(buf, sizeof(buf), fp)) {
			rte_memcpy(sysinfo->mirror_port[1].user_rule[i], buf, strlen(buf));
			memset(buf, 0x00, sizeof(buf));
			i++;
			if(i >= CLIENT_MAX_FILTER)
				break;
		}
		fclose(fp);
		ret = set_mirror_port_rules(sysinfo, 1);
	}else if(!strcmp(argv[1], "all")) {
		//in
		for(i = 0; i < CLIENT_MAX_FILTER; i++) {
			memset(sysinfo->mirror_port[0].user_rule[i], 0x00, sizeof(sysinfo->mirror_port[0].user_rule[i]));
		}
		i = 0;
		memset(buf, 0x00, sizeof(buf));
		fp = fopen(MIRROR_IN_PATH, "r");
		if(!fp)
			return -1;
		while(fgets(buf, sizeof(buf), fp)) {
			rte_memcpy(sysinfo->mirror_port[0].user_rule[i], buf, strlen(buf));
			memset(buf, 0x00, sizeof(buf));
			i++;
			if(i >= CLIENT_MAX_FILTER)
				break;
		}
		fclose(fp);
		ret = set_mirror_port_rules(sysinfo, 0);

		//out
		for(i = 0; i < CLIENT_MAX_FILTER; i++) {
			memset(sysinfo->mirror_port[1].user_rule[i], 0x00, sizeof(sysinfo->mirror_port[1].user_rule[i]));
		}
		i = 0;
		memset(buf, 0x00, sizeof(buf));
		fp = fopen(MIRROR_OUT_PATH, "r");
		if(!fp)
			return -1;
		while(fgets(buf, sizeof(buf), fp)) {
			rte_memcpy(sysinfo->mirror_port[1].user_rule[i], buf, strlen(buf));
			memset(buf, 0x00, sizeof(buf));
			i++;
			if(i >= CLIENT_MAX_FILTER)
				break;
		}
		fclose(fp);
		ret = set_mirror_port_rules(sysinfo, 1);
	}

	return ret;
#else
	printf("the mirror function is disable\n");
	return -1;
#endif
}





