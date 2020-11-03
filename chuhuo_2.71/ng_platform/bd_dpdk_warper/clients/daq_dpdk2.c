#include <dpdk_warp.h>
#include "dpdk_frame.h"

static struct system_info *sysinfo;
static struct clientinfo *client_suricata;
struct client_reginfo suricata_info={
	.name="daq_dpdk2",
	.priority=6,
	.policy="RR",
	.filter={
		"proto:6/255,target:1",
		"sip:192.168.1.0/24,dip:172.16.1.1/32,proto:0/0,dport:8080,target:0/1",
		"all,target:0"
		},
	.fixedid=6,
	.rwmode="r",
	.hook="in",
	.qnum=3,
};	

static void 
snort_exit(int s){
	client_unregister(client_suricata);
	exit(0);
}

static int
dap_dpdk_loop(uint32_t index){
	unsigned lcore_count,lcore;
	uint32_t j,rx_count;
	struct rte_mbuf *buf[PACKET_READ_SIZE];
	//uint32_t total_rxcount=0;
	lcore_count=rte_lcore_count();
	lcore = rte_lcore_id();
	printf("here are %d  cores ,my is %d,index=%d!\n",lcore_count,lcore,index);
	while(1) {
		 rx_count=dpdk_dequeue1(client_suricata, index, (void **)buf, PACKET_READ_SIZE);
		 //printf("index=%d,rx_count=%d\n",index,rx_count);
		for(j=0;j<rx_count;j++) {
			//dump_mbuf(buf[j]);
			dpdk_enqueue(client_suricata,buf[j]);
		}
	}
	return 0;
}

static int
daq_main_loop(__attribute__((unused)) void *arg){
	unsigned lcore_count,lcore,tmp;
	lcore_count=rte_lcore_count();
	lcore = rte_lcore_id();
	//printf("here are %d  cores,my is %d.\n",lcore_count,lcore);
	tmp=lcore%lcore_count;
	switch(tmp) {
		case 0:
			dap_dpdk_loop(0);
			break;
		case 1:
			dap_dpdk_loop(1);
			break;
		case 2:
			dap_dpdk_loop(2);
			break;
		default:
			break;
		}
	return 0;
}

int main(int argc, char *argv[]) 
{
	int retval;
	uint32_t lcore;
	retval = rte_eal_init(argc, argv);
	if (retval < 0)
		return -1;
	sysinfo=dpdk_queue_system_shm_init(0);
	if (!sysinfo)
		return -1;
	client_suricata=client_register(&suricata_info);
	if(!client_suricata){
		printf("client %s register error!\n",suricata_info.name);
		return -1;
	}
	dump_system1();
	dump_system2();

	filter_dump_byclinet(client_suricata);
	filter_dump_bysystem(sysinfo);
	
	signal(SIGINT,snort_exit);
	signal(SIGQUIT,snort_exit);
	signal(SIGABRT,snort_exit);
	signal(SIGKILL,snort_exit);

	rte_eal_mp_remote_launch(daq_main_loop, NULL, CALL_MASTER);
	RTE_LCORE_FOREACH_SLAVE(lcore) {
		if (rte_eal_wait_lcore(lcore) < 0) {
			return -1;
		}
	}	
	return 0;
}

