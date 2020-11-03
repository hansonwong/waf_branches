#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <linux/types.h>
#include <net/if.h>
#include <netinet/in.h>

//#include "cm_types.h"
//#include "cm_cpdp.h"
/*
enum {
        CP_DDOS_TYPE_SYN_FLOOD = 0,
        CP_DDOS_TYPE_UDP_FLOOD,
        CP_DDOS_TYPE_ICMP_FLOOD,
        CP_DDOS_TYPE_MAX,
};      
*/        
enum {  
        CP_DDOS_DIR_ORIGINAL = 0,
        CP_DDOS_DIR_REPLY,
        CP_DDOS_DIR_MAX, 
}; 

//FLOOD TYPE
enum {
        DDOS_TYPE_SYN_FLOOD, /* 0 */
        DDOS_TYPE_UDP_FLOOD, /* 1 */
        DDOS_TYPE_ICMP_FLOOD,/* 2 */
        DDOS_TYPE_DNS_FLOOD, /* 3 */
        DDOS_TYPE_ARP_FLOOD, /* 4 */
        DDOS_TYPE_FLOOD_MAX, /* 5 */
		DDOS_TYPE_TEARDROP = DDOS_TYPE_FLOOD_MAX,
		DDOS_TYPE_SMURF,
		DDOS_TYPE_LAND,
		DDOS_TYPE_JUBO_ICMP,
		DDOS_TYPE_WINNUKE,
		DDOS_TYPE_MAX,
};

//TearDrop Smurf LAND JUMOICMP WinNuke
enum{
		DDOS_PKTTYPE_TEARDROP,
		DDOS_PKTTYPE_SMURF,
		DDOS_PKTTYPE_LAND,
		DDOS_PKTTYPE_JUBO_ICMP,
		DDOS_PKTTYPE_WINNUKE,
		DDOS_PKTTYPE_MAX,
};

enum {
		FP_DDOS_DIR_SRC,
        FP_DDOS_DIR_DST,
        FP_DDOS_DIR_MAX,
};

struct cp_ddos_t {
	u_int32_t	limit;
	u_int8_t	state;
	u_int8_t	dir;
	u_int8_t	type;
	u_int8_t	log;
} __attribute__ ((packed));

#define DDOS_PATH "/tmp/dpdk_ddos_sock"

/*ddos_ctl -dir source -type syn_flood -limit 100 -state on*/
int cmd_analyze(struct cp_ddos_t *cpd, int argc, char *argv[])
{
	if (argc != 11)
		return -1;

	if (!strcmp(argv[1], "-dir")) {
		if (!strcmp(argv[2], "source"))
			cpd->dir = CP_DDOS_DIR_ORIGINAL;
		else if (!strcmp(argv[2], "dest"))
			cpd->dir = CP_DDOS_DIR_REPLY;
		else 
			return -1;
	}else {
		return -1;
	}

	if (!strcmp(argv[3], "-type")) {
		if (!strcmp(argv[4], "syn_flood"))
			cpd->type = DDOS_TYPE_SYN_FLOOD;
		else if (!strcmp(argv[4], "udp_flood"))
			cpd->type = DDOS_TYPE_UDP_FLOOD;
		else if (!strcmp(argv[4], "icmp_flood"))
			cpd->type = DDOS_TYPE_ICMP_FLOOD;
		else if (!strcmp(argv[4], "dns_flood"))
			cpd->type = DDOS_TYPE_DNS_FLOOD;
		else if (!strcmp(argv[4], "arp_flood"))
			cpd->type = DDOS_TYPE_ARP_FLOOD;
		else if (!strcmp(argv[4], "teardrop"))
			cpd->type = DDOS_TYPE_TEARDROP;
		else if (!strcmp(argv[4], "smurf"))
			cpd->type = DDOS_TYPE_SMURF;
		else if (!strcmp(argv[4], "land"))
			cpd->type = DDOS_TYPE_LAND;
		else if (!strcmp(argv[4], "jubo_icmp"))
			cpd->type = DDOS_TYPE_JUBO_ICMP;
		else if (!strcmp(argv[4], "winnuke"))
			cpd->type = DDOS_TYPE_WINNUKE;		
		else
			return -1;
	}else {
		return -1;
	}

	if (!strcmp(argv[5], "-limit")) {
		cpd->limit = atoi(argv[6]);
	}else {
		return -1;
	}

	if (!strcmp(argv[7], "-state")) {
		if (!strcmp(argv[8], "on"))
			cpd->state = 1;
		else if (!strcmp(argv[8], "off"))
			cpd->state = 0;
		else
			return -1;
	}else {
		return -1;
	}

	if (!strcmp(argv[9], "-log")) {
		if (!strcmp(argv[10], "on"))
			cpd->log = 1;
		else if (!strcmp(argv[10], "off"))
			cpd->log = 0;
		else
			return -1;
	}else {
		return -1;
	}	
	return 0;
}

int main(int argc, char *argv[])
{
        socklen_t clt_addr_len;
        int cli_fd, ret, i, len;
        struct sockaddr_un cli_addr;
	struct cp_ddos_t cpd;

	ret = cmd_analyze(&cpd, argc, argv);
	if (ret == -1) {
		printf("Example: ddos-ctl -dir source -type syn_flood -limit 100 -state on -log on\n");
		printf("-dir:\tsource/dest\n");
		printf("-type:\tsyn_flood/udp_flood/icmp_flood/dns_flood/arp_flood/teardrop/smurf/land/jubo_icmp/winnuke\n");
		printf("-state:\ton/off\n");
		printf("-log:\ton/off\n");
		return -1;
	}
	
        cli_fd = socket(PF_UNIX, SOCK_STREAM, 0);
        if (cli_fd < 0) {
                perror("socket");
                goto ERR1;   
        }

        cli_addr.sun_family = AF_UNIX;
        strncpy(cli_addr.sun_path, DDOS_PATH, sizeof(cli_addr.sun_path) - 1);

        ret = connect(cli_fd, (struct sockaddr *)&cli_addr, sizeof(cli_addr));
        if (ret == -1) {
                perror("connect");
                goto ERR2;
        }

        ret = send(cli_fd, &cpd, sizeof(struct cp_ddos_t), 0);
ERR2:
        close(cli_fd);
ERR1:
        return 0;
}       
