#include <dpdk_warp.h>
#include "dpdk_frame.h"

void  *handle;
struct client_reginfo mirror_in_info={
	.name="mirror_client",
	.priority=5,
	.fixedid=4,
	.rwmode="r",
	.hook="mirror_out",
	.filter={
		"all",
		},
	.qnum=1,
	.policy="SS",
};	


uint64_t sum_rx_count = 0;
void callbk(u_char *user, const struct _pcap_pkthdr *pkthdr,u_char *data){
	sum_rx_count++;
	
#if 0 /* for debug */
	static int count=0;
	printf("%d---->datalen=%d\n",count++,pkthdr->len);

	int i;
	//print header
	printf("pcap time:%lu-%lu\n",pkthdr->ts.tv_sec,pkthdr->ts.tv_usec);
	printf("caplen=%d,len=%d\n",pkthdr->caplen,pkthdr->len);

	//print data
	for(i=0;i<pkthdr->len;i++){
		if(i&&i%8==0)
			printf("\n");
		printf("%02x ",data[i]);
	}
	printf("\n");
#endif
}

static void 
mirror_exit(int s){
	printf("mirror sum_rx_count = %lu\n", sum_rx_count);
	mirror_close(handle);
	exit(0);
}

int main(int argc, char *argv[]) 
{
#if(ENABLE_MIRROR_FUNCTION == 1)
	printf("coreamsk = %s,num=%s\n",argv[1],argv[2]);
	
	mirror_in_info.priority+=atoi(argv[2]);
	
	handle = mirror_open(&mirror_in_info, argv[1]);

	if(handle == NULL) {
		printf("==>mirror open error\n");
		return 0;
	}

	signal(SIGINT,mirror_exit);
	signal(SIGQUIT,mirror_exit);
	signal(SIGABRT,mirror_exit);
	signal(SIGKILL,mirror_exit);

	dump_system1();
	dump_system2();

	mirror_loop(handle,-1,callbk,NULL);

	printf("mirror sum_rx_count = %lu\n", sum_rx_count);
	mirror_close(handle);

#else
	printf("the mirror function is disable...\n");
#endif
	return 0;
}


