#include <dpdk_warp.h>
#include <sys/types.h>
#include <sys/wait.h>
#include "dpdk_frame.h"

static struct system_info *sysinfo;
static struct clientinfo *client_suricata;
struct client_reginfo suricata_info={
	.name="client_suricata",
	.priority=4,
	.policy="BYMULTIPLIER_SS",
	.filter={
		"all"
		},
	.fixedid=4,
	.rwmode="r",
	.hook="in",
	.qnum=8,
	.sub_client_qnum = { 4, 4 } ,
};	

pid_t child_pid[MAX_SUB_CLIENTS];

static void 
snort_exit(int s){
	int i = 0;
	
	client_unregister(client_suricata);

	for(i = 0; i < MAX_SUB_CLIENTS; i++) {
		kill(child_pid[i], SIGINT);
	}
	exit(0);
}

int main(int argc, char *argv[]) 
{
	pid_t child_process_one, child_process_two;
	uint32_t i, rx_count, index = 0;
	struct rte_mbuf *buf[PACKET_READ_SIZE];
	struct subqueueinfo *sub_queue;
	
	sysinfo=get_dpdk_shm_cpu("daq","program1","0x06",0);
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

	/* get cores */
	int cores[2], j = -1;
	for(i=0;i<2;i++) {
		j=rte_get_next_lcore(j, 0, 0);
		cores[i]=j;	
	}

	/* process 1 */
	child_process_one = fork();
	if(child_process_one == 0) {
		printf("my pid is : %d, my cors is : %d\n", getpid(), cores[0]);
		child_pid[0] = getpid();
		eal_thread_init_master(cores[0]);	
		sub_queue = &(client_suricata->queue.sub_queue[0]);
		while(1) {	
			rx_count = dpdk_dequeue3(client_suricata, sub_queue, &index, (void **)buf, PACKET_READ_SIZE);
			if(!rx_count)
				continue;
			for(i=0; i<rx_count; i++) {			
				dpdk_enqueue(client_suricata,buf[i]);
			}
		}
		return 0;
	}else if(child_process_one < 0) {
		printf("fork child one error\n");
		return -1;
	}

	/* process 2 */
	child_process_two = fork();
	if(child_process_two == 0) {
		printf("my pid is : %d, my cors is : %d\n", getpid(), cores[1]);
		child_pid[1] = getpid();
		eal_thread_init_master(cores[1]);
		sub_queue = &(client_suricata->queue.sub_queue[1]);
		while(1) {					
			rx_count = dpdk_dequeue3(client_suricata, sub_queue, &index, (void **)buf, PACKET_READ_SIZE);
			if(!rx_count)
				continue;
			for(i=0; i<rx_count; i++) {				
				rte_pktmbuf_free(buf[i]);
			}
		}
		return 0;
	}else if(child_process_two < 0) {
		printf("fork child two error\n");
		return -1;
	}
	
	int st1, st2; 
	
	waitpid( child_process_one, &st1, 0); 
	waitpid( child_process_two, &st2, 0); 
	printf("in parent, child 1 pid = %d\n", child_process_one); 
	printf("in parent, child 2 pid = %d\n", child_process_two); 
	printf("in parent, pid = %d\n", getpid()); 
	printf("in parent, child 1 exited with %d\n", st1); 
	printf("in parent, child 2 exited with %d\n", st2); 

	return 0;
}

