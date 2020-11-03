#include <dpdk_warp.h>
#include "dpdk_frame.h"

void  *handle;
struct client_reginfo mirror_in_info={
	.name="mirror_client",
	.priority=5,
	.fixedid=4,
	.rwmode="r",
	.hook="mirror_in",
	.filter={
		"all",
		},
	.qnum=1,
	.policy="SS",
};	

FILE *fp = NULL;
uint64_t sum_rx_count = 0;

static unsigned char pacp_file_header[24] = {
	0xd4,0xc3,0xb2,0xa1,0x02,0x00,0x04,0x00,
	0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
	0xff,0xff,0x00,0x00,0x01,0x00,0x00,0x00
};

struct local_timeval
{
	int tv_sec;
	int tv_usec;
};

struct local_pcap_pkthdr
{
	struct local_timeval ts;
	int32_t caplen;
	int32_t len;
};

#if (ENABLE_MIRROR_FUNCTION == 1)

void 
save_pcap_file(FILE *fp, const struct _pcap_pkthdr *pkthdr, u_char *data)
{
	struct local_pcap_pkthdr hdr;

	hdr.ts.tv_sec=pkthdr->ts.tv_sec;
	hdr.ts.tv_usec=pkthdr->ts.tv_usec;
	hdr.caplen=pkthdr->caplen;
	hdr.len=pkthdr->len;

	/* write header */
	if(fwrite(&hdr, 1, sizeof(struct local_pcap_pkthdr), fp) != sizeof(struct local_pcap_pkthdr)) {
		printf("fwrite hdr error\n");
		return;
	}

	/* write data */
	if(fwrite((char *)data, 1, hdr.len, fp) != (unsigned int)hdr.len)
		printf("fwrite data error\n");
}

void 
callbk(u_char *user, const struct _pcap_pkthdr *pkthdr,u_char *data)
{
	sum_rx_count++;

	save_pcap_file(fp, pkthdr, data);
}

static void 
mirror_exit(int s){
	printf("mirror sum_rx_count = %lu\n", sum_rx_count);
	if(fp)
		fclose(fp);
	mirror_close(handle);
	exit(0);
}
#endif

int main(int argc, char *argv[]) 
{
#if(ENABLE_MIRROR_FUNCTION == 1)
	int port_id = 0;
	uint32_t i = 0;
	char str[64] = {0};
	char tmp_char = 0;

	if(argc != 4) {
		printf("usage:./tcpdump vEth0 -w /home/tcpdump.pcap\n");
		return -1;
	}

	/* check device name */
	if(strncmp(argv[1], "vEth", 4) != 0) {
		printf("Error: the device name \"%s\" is wrong, must be like \"vEth0\"\n", argv[1]);
		return -1;
	}
	for(i = 0; i < strlen(argv[1] + 4); i++) {
		tmp_char = *(argv[1] + 4 + i);
		if(!isdigit(tmp_char)) {
			printf("Error: \"%c\" is no a digit character\n", tmp_char);
			return -1;
		}
	}

	/* check mode */
	if(strcmp(argv[2], "-w") == 0) {
		if((argc != 4) || (!argv[3])) {
			printf("Error: please input like this \"./tcpdump vEth0 -w /home/tcpdump.pcap\"\n");
			return -1;
		}
	}else {
		printf("Error: please input like this \"./tcpdump vEth0 -w /home/tcpdump.pcap\"\n");
		return -1;
	}

	/* set filter */
	port_id = atoi(argv[1] + 4);
	sprintf(str, "inport:%d", port_id);	
	mirror_in_info.filter[0] = str;	

	/* open pcap file */
	fp = fopen(argv[3], "w+");
	if(!fp) {
		printf("Error: open %s error\n", argv[2]);
		return -1;
	}

	if(fwrite(pacp_file_header, 1, sizeof(pacp_file_header), fp) != sizeof(pacp_file_header)) {
		printf("Error: write pcap file header error\n");
		fclose(fp);
		return -1;
	}
	
	handle = mirror_open(&mirror_in_info, "0x02");

	if(handle == NULL) {
		if(fp)
			fclose(fp);
		printf("Error: mirror open error\n");
		return -1;
	}

	signal(SIGINT,mirror_exit);
	signal(SIGQUIT,mirror_exit);
	signal(SIGABRT,mirror_exit);
	signal(SIGKILL,mirror_exit);

	dump_system1();
	dump_system2();

	mirror_loop(handle,-1,callbk,NULL);

	mirror_close(handle);

#else
	printf("the mirror function is disable...\n");
#endif
	return 0;
}



