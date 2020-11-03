#include <dpdk_warp.h>

#include "dpdk_frame.h"


static struct system_info *sysinfo;


static struct clientinfo *client_ext;
struct client_reginfo ext_info={
	.name="client_ext",
	.priority=0,//MAX_CLINET_PRIORITY-1,
	.fixedid=15,
	.rwmode="r",
	.hook="in",
	.qnum=1,
};


static struct ring_queue  *extqueue;
static void 
do_interact_ext_client(int qnum) {
	int i,rx_count,tx_count=0;
	void *data;
	struct rte_mbuf *buf[PACKET_READ_SIZE];
	#define  EXT_CLIENT_SHM_ID  0xa769
	#define  EXT_CLIENT_BUFFSIEZ  1600*1024
	#define  EXT_CLIENT_NODESIZE 1600

	extqueue=ring_queue_shared_create(EXT_CLIENT_SHM_ID,
						EXT_CLIENT_BUFFSIEZ,EXT_CLIENT_NODESIZE);
	if(NULL==extqueue) {
		printf("ring_queue_shared_create failure!\n");
		return ;
	}else 
		printf("extqueue=%p\n",extqueue);
	printf("do_interact_ext_client  ok----------->\n");
	
	while(1) {
		rx_count=dpdk_dequeue1(client_ext,qnum,(void **)buf,PACKET_READ_SIZE);
		//printf("do_interact_ext_client:recv %d\n",rx_count);
		for(i=0;i<rx_count;i++) {
			data=rte_pktmbuf_mtod(buf[i], void *);
			
			if(buf[i]->data_len<EXT_CLIENT_NODESIZE)  {
				if(!ring_queue_add(extqueue,data,buf[i]->data_len))
					tx_count++;
				//if(tx_count%1000000==0)
				//	printf("size=%d...count=%u\n",buf[i]->data_len,tx_count);
			}else 
				printf("mbuf datalen=%d > %d\n",buf[i]->data_len,EXT_CLIENT_NODESIZE);
			dpdk_enqueue(client_ext, buf[i]);
		}
	}
}

static int
extclient_loop(__attribute__((unused)) void *arg){
	unsigned lcore_count,lcore;
	lcore_count=rte_lcore_count();
	lcore = rte_lcore_id();
	printf("here are %d  cores ,my is %d!\n",lcore_count,lcore);
	do_interact_ext_client(0);
	return 0;
}


int main(int argc, char *argv[]) {
	int retval;
	retval = rte_eal_init(argc, argv);
	if (retval < 0)
		return -1;

	sysinfo=dpdk_queue_system_shm_init(0);
	if (!sysinfo)
		return -1;

	client_ext=client_register(&ext_info);
	if(!client_ext){
		printf("client %s register error!\n",ext_info.name);
		exit(0);
	}
	dump_system1();
	dump_system2();
	extclient_loop(NULL);
	return 0;
}
