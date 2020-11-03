#include <dpdk_warp.h>
#include "dpdk_frame.h"

static struct system_info *sysinfo;
static struct portinfo  *ports;
static struct clientinfo *client_kni;
struct client_reginfo kni_info={
	.name="client_kni",
	.priority=MAX_CLINET_PRIORITY-3,
	.fixedid=4,
	.rwmode="r",
	.hook="out",
	.qnum=1,//ports->portn,
};
static volatile uint32_t kni_stop = 1;

static void
inthandle(int s) {
		s=s;
		kni_stop=0;
		rte_wmb();
}



static int kni_ingress(void) {
	unsigned i,j;
	unsigned qnum= client_kni->queue.qnum;
	uint16_t nb_rx/*,num*/ ;
	int port;
	struct rte_ring *queue;
	struct rte_mbuf *buf[PACKET_READ_SIZE];

	for(i=0;i<qnum;i++) {
		queue=client_kni->queue.rings[i];
		nb_rx = rte_ring_dequeue_burst(queue,(void *)buf, PACKET_READ_SIZE);
		if(!nb_rx) 
			continue;
#if 0
		num = rte_kni_tx_burst(ports->kni[i], buf, nb_rx);	
		if (unlikely(num < nb_rx)) 
			burst_free_mbufs(&buf[num], nb_rx - num);
			
#else
		for(j=0;j<nb_rx;j++){
			port=buf[j]->port;
			//printf("kni ingress:port=%d\n",port);
			if(!rte_kni_tx_burst(ports->kni[port], &buf[j], 1))
				burst_free_mbufs(&buf[j], 1);
		}

#endif	
	}
	return 0;
}


static void
kni_egress(void)
{
	unsigned /*nb_tx,*/ num;
	uint32_t i,j,nb_kni;
	struct rte_mbuf *buf[PACKET_READ_SIZE];
	nb_kni = ports->portn;


	for (i = 0; i < nb_kni; i++) {
		num = rte_kni_rx_burst(ports->kni[i], buf, PACKET_READ_SIZE);
		if(!num)
			continue;
		if (unlikely(num > PACKET_READ_SIZE)) {
			printf("Error receiving from KNI\n");
			return;
		}
#if 0
		nb_tx = rte_eth_tx_burst(i, 0, buf, (uint16_t)num);
		if (unlikely(nb_tx < num)) {
			burst_free_mbufs(&buf[nb_tx], num - nb_tx);
		}
#else
		for(j=0;j<num;j++){
			//printf("kni engress:port=%d\n",buf[j]->port);
			dpdk_enqueue(client_kni, buf[j]);
		}
#endif
	}
}

static int
client_kni_loop(__attribute__((unused)) void *arg){
	unsigned lcore_count,lcore;
	static volatile uint32_t *fstop=&kni_stop;
	lcore_count=rte_lcore_count();
	lcore = rte_lcore_id();
	printf("here are %d  cores ,my is %d!\n",lcore_count,lcore);
	
	while(*fstop) {
		kni_ingress();
		kni_egress();
		usleep(1);
	}
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
	ports=&(sysinfo->portinfos);
	client_kni=client_register(&kni_info);
	if(!client_kni){
		printf("client %s register error!\n",client_kni->name);
		return -1;
	}
	signal(SIGINT,inthandle);
	signal(SIGQUIT,inthandle);
	signal(SIGABRT,inthandle);
	signal(SIGKILL,inthandle);
	
	client_kni_loop(NULL);
	return 0;
}
