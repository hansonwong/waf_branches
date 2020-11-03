#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netinet/in.h>
#include <stdint.h>
#include <stdarg.h>
#include <inttypes.h>
#include <inttypes.h>
#include <sys/queue.h>
#include <errno.h>
#include <netinet/ip.h>
#include <sys/shm.h>

#include "dpdk_frame.h"

#include "qos_sched.h"
#include <sys/time.h>
#include <time.h>


#include "ddos.h"

#define SERTER_TX_DEBUG  1

#define MAX_ETH_HANDLE  	256
#define MAX_RTE_RING 	 	256
#define MAX_KNI_RING		256
#define MAX_RSS_RING        32

#define MAX_SERVER_CPUS 	16

enum {
 	RECEIVE_FROM_ETH=0, 
	RECEIVE_FROM_RINGBUF,
 	RECEIVE_FROM_KNIFIFO,
 	RECEIVE_FROM_RSSRING,
 	RECEIVE_MAX
};

struct handleinfo{
	int type;
	int priv;
	volatile uint8_t * ifup;
	void *handle;
	eth_rx_burst_t  rx_pkt_burst;
};

struct percpu_process_static{
	int  eth_cnt;
	int  queue_cnt;
	int  kni_cnt;
	int  rss_cnt;
	struct handleinfo  eth[MAX_ETH_HANDLE];
	struct handleinfo  queue[MAX_RTE_RING];
	struct handleinfo  kni[MAX_KNI_RING];
	struct handleinfo  rss[MAX_RSS_RING];
};

struct percpu_process_runtime{
	int cnt;
	int cnt_item[4];
	struct handleinfo  *q[MAX_ETH_HANDLE+MAX_RTE_RING+MAX_KNI_RING];
};

static struct percpu_process_static  	process_st[2];
static struct percpu_process_runtime  process_rt[2][MAX_SERVER_CPUS];
static struct percpu_process_runtime  * volatile p_procss_rt = NULL;
static volatile int process_flag[MAX_SERVER_CPUS];
static volatile uint8_t eth_status[RTE_MAX_ETHPORTS+1];
static volatile int procss_index = 0;

struct dev_queue_ctl {
	uint8_t  queue_start;
	uint8_t  queue_percpu;
	uint8_t  queue_round;
};

static struct dev_queue_ctl dev_queue_ctl_st[2][RTE_MAX_ETHPORTS][SERVER_TX_QUEUES];//description of  perport queue info when percpu
static struct dev_queue_ctl  (* volatile  dev_queue_ctl_rt)[SERVER_TX_QUEUES] = NULL;
static volatile int dev_queue_index = 0;

#define MAX_DEV_QUEUE 256
static struct dev_queue_ctl devqueue[MAX_DEV_QUEUE]; //devqueue[RTE_MAX_ETHPORTS];

static unsigned server_cpus;
static volatile uint32_t server_stop = 1;
static struct clientinfo *server_tx;
static struct system_info *sysinfo;
static struct portinfo *portinfos;

struct client_reginfo tx_info = {
	.issvr = 1,
	.name = "server-tx",
	.priority = MAX_CLINET_PRIORITY - 1,
	.fixedid = 2,
	.rwmode = "r",
	.filter = {
		"all",
	},
	.hook = "out",
	.policy = "BYOUTPORT",
	.qnum = SERVER_TX_QUEUES,
};

static void inthandle(int s __rte_unused) 
{
	int i;

	server_stop = 0;

	for (i = 0; i < MAX_SERVER_CPUS; i++)
		process_flag[i] = 0;

	client_dequeue_stop(server_tx);
	rte_wmb();
	printf("server is going to exit\n");
}

void server_exit(struct clientinfo *server)
{
	struct system_info *system;
	struct clientinfo *tmp;
	int i, j;
	int shmid;

	shmid = shmget((key_t)TC_SHM_KEY_ID, 0, 0);
	if (shmid >= 0) {
		printf("del kernel tc config info shared memory\n");
		shmctl(shmid, IPC_RMID, NULL);
	}

	if (NULL == server) 
		return;

	system = server->sysinfo;
	if (system->svr_ready != server->processid) {
		printf("you are not server,no right to do server_exit!\n");
		return;
	}

	printf("server will be exited,kill all clients!\n");

	for (i = 0; i < MAX_CLINET_PRIORITY; i++) {
		for (j = 0; j < MAX_CLIENT_PARITY; j++) {
			tmp = &system->cinfos[i][j];
			if (!tmp->processid)
				continue;
			if (tmp->processid != server->processid) {
				printf("kill client %s:%d!\n", tmp->name, tmp->processid);
				kill(tmp->processid,SIGINT);
			}
		}
	}
#ifdef ANTI_DDOS_ON
	ddos_exit();
#endif		

}


static void server_init(void) 
{
	server_tx = client_register(&tx_info);
	if (!server_tx){
		printf("client %s register error!\n", tx_info.name);
		exit(0);
	}

	server_cpus = rte_lcore_count() - 1;

	signal(SIGINT, inthandle);
	signal(SIGQUIT, inthandle);
	signal(SIGABRT, inthandle);
	signal(SIGKILL, inthandle);

	sysinfo->mirror_port[0].svrtx_queue = &(server_tx->queue);
	sysinfo->mirror_port[1].svrtx_queue = &(server_tx->queue);

#ifdef ANTI_DDOS_ON
	if (ddos_init() != 0) {
		printf("ddos_init init failed.\n");
		exit(0);
	}
#endif

}

#if (SERVER_TX_BULK_MODE==1)
static void port_txcpu_update(int port,int op){
	struct dev_queue_ctl  (*p_st)[SERVER_TX_QUEUES] = dev_queue_ctl_st[dev_queue_index];
	uint8_t cpu = port;
	
	if (op == -1) {
		if (p_st[port][cpu].queue_start == (uint8_t)-1) {
			printf("\nport %d have not add txcpu flag !\n", port);
			return ;
		}

		p_st[port][cpu].queue_start = (uint8_t)-1;
		goto DEBUGINFO;
	}

	if (p_st[port][cpu].queue_start != (uint8_t)-1) {
		printf("\nport %d have update txcpu flag !\n", port);
		return ;
	}

	p_st[port][cpu].queue_start = 0;
	p_st[port][cpu].queue_round = 0;
	p_st[port][cpu].queue_percpu = portinfos->txrings[port];

	/*virtual RINGBUF for bridge broadcasting*/
#ifdef BRIDGE_ON
	p_st[VIRTUAL_PORT][VIRTUAL_PORT].queue_start = 0;
	p_st[VIRTUAL_PORT][VIRTUAL_PORT].queue_round = 0;
	p_st[VIRTUAL_PORT][VIRTUAL_PORT].queue_percpu = 1;
#endif

	dev_queue_index = !dev_queue_index;
	dev_queue_ctl_rt = p_st;
	memcpy(&dev_queue_ctl_st[dev_queue_index], p_st, sizeof(dev_queue_ctl_st[0]));

DEBUGINFO:
#if (SERTER_TX_DEBUG==1)
	printf("\nport and qid info(port=%d(%s))===========================\n", port, (op==1) ? "add" : "del");
	
	for (port = 0; port < portinfos->portn;port++) {
		if (!(portinfos->status_uk[port] & USER_STATUS))
			continue;

		printf("prot %d---qid start %d: qid round %d:qid for percpu %d\n",
			port, dev_queue_ctl_rt[port][port].queue_start,
			dev_queue_ctl_rt[port][port].queue_round,
			dev_queue_ctl_rt[port][port].queue_percpu);
	}
#endif
	return ;
}
#else
static int find_txcpu_min(float *txcpus, int n) 
{
	int i, j = 0;
	float min = txcpus[0];

	for (i = 1; i < n; i++) {
		if (txcpus[i] < min) {
			min = txcpus[i];
			j = i;
		}
	}

	return j;
}

static void port_txcpu_update(int port_update __rte_unused, int op __rte_unused)
{
	uint8_t port_id, port;
	uint8_t ports[RTE_MAX_ETHPORTS];
	int p, i, j, active_port;
	float weight;
	struct dev_queue_ctl  (*p_st)[SERVER_TX_QUEUES] = dev_queue_ctl_st[dev_queue_index];
	uint8_t qmin, cpu, cpu2[SERVER_TX_QUEUES];
	float txcpus[SERVER_TX_QUEUES] = {0.0};
	
	//first ixgbe
	active_port = 0;
	weight = 1.0;

	if (SERVER_TX_QUEUES < TX_QUEUES_IXGBE)
		weight = TX_QUEUES_IXGBE / SERVER_TX_QUEUES;
	
	for (port_id = 0; port_id < portinfos->portn;port_id++) {
		if (!(portinfos->status_uk[port_id] & USER_STATUS))
			continue;
		if (portinfos->status_uk[port_id]&IS_IXGBE)
			ports[active_port++]=port_id;
	}

	for (p = 0; p<active_port; p++) {
		port = ports[p];
				
		qmin = (TX_QUEUES_IXGBE < SERVER_TX_QUEUES) ? TX_QUEUES_IXGBE:SERVER_TX_QUEUES;
		memset(cpu2, 0, sizeof(cpu2));

		for (i = 0; i < qmin; i++) {
			cpu = find_txcpu_min(txcpus, SERVER_TX_QUEUES);
			txcpus[cpu] += weight;
			cpu2[cpu]++;
		}

		for (i = 0,j = 0; i < SERVER_TX_QUEUES; i++) {
			while (1) {
				if (cpu2[j % SERVER_TX_QUEUES])
					break;
				j++;
			}
			portinfos->txcpu[port][i] = (j++) % SERVER_TX_QUEUES;
		}

		i = 0;
		j = portinfos->txrings[port] / qmin;

		for (cpu = 0; cpu < SERVER_TX_QUEUES; cpu++) {
			if (!cpu2[cpu])
				continue;
			p_st[port][cpu].queue_percpu = cpu2[cpu] * j;
			p_st[port][cpu].queue_start = i * j;
			p_st[port][cpu].queue_round = 0;
			i += cpu2[cpu];
		}
	}
	
	//then igb
	active_port = 0;
	weight = TX_QUEUES_IGB;

	for (port_id = 0; port_id < portinfos->portn;port_id++) {
		if (!(portinfos->status_uk[port_id] & USER_STATUS))
			continue;

		if (!(portinfos->status_uk[port_id]&IS_IXGBE))
			ports[active_port++] = port_id;
	}

	/*virtual RINGBUF for bridge broadcasting*/
#ifdef BRIDGE_ON
	ports[active_port++] = VIRTUAL_PORT;
	portinfos->txrings[VIRTUAL_PORT] = 1;
#endif

	for (p = 0; p < active_port; p++) {
		port = ports[p];
		cpu = find_txcpu_min(txcpus,SERVER_TX_QUEUES);
		txcpus[cpu] += weight;

		for (i = 0; i < SERVER_TX_QUEUES; i++)
			portinfos->txcpu[port][i] = cpu;

		p_st[port][cpu].queue_start = 0;
		p_st[port][cpu].queue_round = 0;
		p_st[port][cpu].queue_percpu = portinfos->txrings[port];
	}

	dev_queue_index = !dev_queue_index;
	dev_queue_ctl_rt = p_st;
	memcpy(&dev_queue_ctl_st[dev_queue_index], p_st, sizeof(dev_queue_ctl_st[0]));

//DEBUGINFO:
#if (SERTER_TX_DEBUG == 1)
	printf("\nport and  server-tx-queue and qid info(port=%d,%s))============\n", port_update, (op==1) ? "add" : "del");
	printf("server-tx-queue weight info:");
	for (i = 0; i < SERVER_TX_QUEUES; i++)
		printf("%f ,", txcpus[i]);
	printf("\n");
	
	printf("port and serter-tx-queue and qid  info:\n");
	for (port = 0; port < portinfos->portn;port++) {
		if (!(portinfos->status_uk[port] & USER_STATUS))
			continue;
		j = (portinfos->status_uk[port]&IS_IXGBE);

		printf("  port %d (%s):\n", port, j ? "ixgbe" : "igb");
		printf("    server-tx-queue:");
		j = j ? SERVER_TX_QUEUES : 1;
		for (i = 0; i < j; i++)
			printf("%d ", portinfos->txcpu[port][i]);
		printf("\n");

		for (i = 0; i < qmin; i++) {
			cpu = portinfos->txcpu[port][i];
			printf("    queue %d:", cpu);
			printf("start=%d,percpu=%d\n",
				p_st[port][cpu].queue_start, p_st[port][cpu].queue_percpu);
		}
	}
#endif	
	return ;
}
#endif

static int percpu_process_static_update(int type)
{
	int i, j;
	unsigned cpus;
	struct percpu_process_static  *p_st;
	struct percpu_process_runtime  *p_rt;
	uint8_t port_id;
	uint16_t queue_id;
	int n = 0;
	
	p_st = &process_st[procss_index];

	switch (type) {
		case RECEIVE_FROM_ETH: 
		{
			printf("percpu process port info:");
			for (port_id = 0; port_id < portinfos->portn;port_id++) {
				/*if (!(portinfos->status_uk[port_id] & USER_STATUS))
					continue;*/
				for (queue_id = 0; queue_id < portinfos->rxrings[port_id]; queue_id++) {
					p_st->eth[n].type = RECEIVE_FROM_ETH;
					p_st->eth[n].ifup = &eth_status[port_id];
					p_st->eth[n].priv = ((int)port_id << 8) | (queue_id &0xff);//port_id no need
					p_st->eth[n].handle = rte_eth_devices[port_id].data->rx_queues[queue_id];
					p_st->eth[n].rx_pkt_burst = rte_eth_devices[port_id].rx_pkt_burst;
					n++;					
				}
				printf("(%d,%d) ", port_id, portinfos->rxrings[port_id]);
			}
			printf("\n");
			p_st->eth_cnt = n;

#if (SERVER_TX_BULK_MODE==1)
			n = 0;
			for (port_id = 0; port_id < portinfos->portn; port_id++) {
				/*if (!(portinfos->status_uk[port_id] & USER_STATUS))
					continue;
				if ((portinfos->mode[port_id].mode == LOOP_SIMPLE) || 
				   (portinfos->mode[port_id].mode == DIRECT_CONNECT_SIMPLE))
					continue;*/

				p_st->queue[n].type = RECEIVE_FROM_RINGBUF;
				p_st->queue[n].ifup = &eth_status[port_id];
				p_st->queue[n].priv = port_id;
				p_st->queue[n].handle = server_tx->queue.rings[port_id];
				p_st->queue[n].rx_pkt_burst = 0;
				n++;
			}
			/*virtual RINGBUF for bridge broadcasting*/
#ifdef BRIDGE_ON
			port_id = VIRTUAL_PORT;
			p_st->queue[n].type = RECEIVE_FROM_RINGBUF;
			p_st->queue[n].ifup = &eth_status[port_id];
			p_st->queue[n].priv = port_id;
			p_st->queue[n].handle = server_tx->queue.rings[port_id];
			p_st->queue[n].rx_pkt_burst = 0;
			n++;
#endif			
			p_st->queue_cnt = n;
			printf("percpu process queue info: %d\n", p_st->queue_cnt);	
#endif
		}
		/*break;*/ //here no break
		case RECEIVE_FROM_RINGBUF:
		{
#if (SERVER_TX_BULK_MODE==1)
			//return 0;
#else
			/*uint32_t q = 0, need_server_tx = 0;
			uint8_t port_id;
			for (port_id = 0; port_id < portinfos->portn; port_id++) {
				if (!(portinfos->status_uk[port_id] & USER_STATUS))
					continue;
				if ((portinfos->mode[port_id].mode == LOOP_SIMPLE) || 
				   (portinfos->mode[port_id].mode == DIRECT_CONNECT_SIMPLE))
					continue;
				need_server_tx = 1;
				break;
			}

			if (need_server_tx)
			 	for (q = 0; q < server_tx->queue.qnum; q++) {
					p_st->queue[q].type = RECEIVE_FROM_RINGBUF;
					p_st->queue[q].priv = q;
					p_st->queue[q].handle = server_tx->queue.rings[q];
					p_st->queue[q].rx_pkt_burst = 0;
			}

			p_st->queue_cnt = q;*/
			
			for (queue_id = 0; queue_id < server_tx->queue.qnum; queue_id++) {
				p_st->queue[queue_id].type = RECEIVE_FROM_RINGBUF;
				p_st->queue[queue_id].ifup = &eth_status[RTE_MAX_ETHPORTS];
				p_st->queue[queue_id].priv = queue_id;
				p_st->queue[queue_id].handle = server_tx->queue.rings[queue_id];
				p_st->queue[queue_id].rx_pkt_burst = 0;
			}

			p_st->queue_cnt = queue_id;
			printf("percpu process queue info: %d\n", p_st->queue_cnt);
#endif
		}
		//break;
		case RECEIVE_FROM_KNIFIFO:
		{
			for (n = 0, port_id = 0; port_id < portinfos->portn;port_id++) {
				/*if (!(portinfos->status_uk[port_id] & USER_STATUS))
					continue;*/
				p_st->kni[n].type = RECEIVE_FROM_KNIFIFO;
				p_st->kni[n].ifup = &eth_status[port_id];
#if (SERVER_TX_BULK_MODE==1)
				p_st->kni[n].priv = port_id;
#else
				p_st->kni[n].priv = portinfos->txcpu[port_id][0];//select one of server-tx's queues which is be allocated to this port
#endif
				p_st->kni[n].handle = portinfos->kni[port_id];
				p_st->kni[n].rx_pkt_burst = 0;
				n++;
			}
			p_st->kni_cnt = n;
			printf("percpu process kni info: %d\n",p_st->kni_cnt);	
		}
		//break;
		case RECEIVE_FROM_RSSRING:
		{
			for(n = 0; n < (int)server_cpus; n++) {
				p_st->rss[n].type = RECEIVE_FROM_RSSRING;
				p_st->rss[n].ifup = &eth_status[RTE_MAX_ETHPORTS];
				p_st->rss[n].priv = n;
				p_st->rss[n].handle = sysinfo->rss_rings[n];
				p_st->rss[n].rx_pkt_burst = 0;
			}
			p_st->rss_cnt = n;
			printf("percpu process rss_rings info: %d\n",p_st->kni_cnt);
		}
		break;
		default :
			return -1;
	}
	
	p_rt = process_rt[procss_index];
	for (cpus = 0; cpus < server_cpus; cpus++){
		p_rt[cpus].cnt = 0;
		p_rt[cpus].cnt_item[0] = 0;
		p_rt[cpus].cnt_item[1] = 0;
		p_rt[cpus].cnt_item[2] = 0;
		p_rt[cpus].cnt_item[3] = 0;
	}

	cpus = 0;
	#define CPUS_ROUND() \
		cpus++;	\
		if(cpus>=server_cpus)	\
			cpus=0
	for (i = 0; i < p_st->eth_cnt; i++) {
		if((i != 0) && (((p_st->eth[i].priv & 0xff00) >> 8) != ((p_st->eth[i - 1].priv & 0xff00) >> 8))) {
			CPUS_ROUND();
		}
		j = p_rt[cpus].cnt;
		p_rt[cpus].q[j] = &(p_st->eth[i]);
		p_rt[cpus].cnt++;
		p_rt[cpus].cnt_item[0]++;		
		//CPUS_ROUND();
	}

	cpus = 0;
	for(i = 0; i < p_st->rss_cnt; i++) {
		j = p_rt[cpus].cnt;
		p_rt[cpus].q[j] = &(p_st->rss[i]);
		p_rt[cpus].cnt++;
		p_rt[cpus].cnt_item[1]++;
		CPUS_ROUND();
	}

	for (i = 0; i < p_st->queue_cnt; i++) {
		j = p_rt[cpus].cnt;
		p_rt[cpus].q[j] = &(p_st->queue[i]);
		p_rt[cpus].cnt++;
		p_rt[cpus].cnt_item[2]++;
		CPUS_ROUND();
	}

	for (i = 0; i < p_st->kni_cnt; i++) {
		j = p_rt[cpus].cnt;
		p_rt[cpus].q[j] = &(p_st->kni[i]);
		p_rt[cpus].cnt++;
		p_rt[cpus].cnt_item[3]++;
		CPUS_ROUND();
	}

	for (cpus=0;cpus<server_cpus;cpus++) {
		p_rt[cpus].cnt_item[1] += p_rt[cpus].cnt_item[0];
		p_rt[cpus].cnt_item[2] += p_rt[cpus].cnt_item[1];
		p_rt[cpus].cnt_item[3] += p_rt[cpus].cnt_item[2];
	}

	procss_index = !procss_index;
	//memcpy((void *)&process_st[procss_index], (void *)p_st, sizeof(struct percpu_process_static));
	p_procss_rt = p_rt;
	for (cpus = 0; cpus < server_cpus; cpus++) {
		p_rt[cpus].q[p_rt[cpus].cnt] = 0;
		process_flag[cpus] = 0;
	}
#if (SERTER_TX_DEBUG == 1)
	printf("\ncpu task info=================================\n");
	for (cpus = 0; cpus < server_cpus; cpus++) {
		printf("cpu %d statistic info:total cnt %d: %d--%d--%d--%d\n", cpus, p_rt[cpus].cnt,
			p_rt[cpus].cnt_item[0],p_rt[cpus].cnt_item[1],p_rt[cpus].cnt_item[2],p_rt[cpus].cnt_item[3]);

		printf("task ifno (type,priv,handle,func):");
		for (i = 0; i < p_rt[cpus].cnt; i++)
			printf("(%d,0x%x,%p,%p),", p_rt[cpus].q[i]->type, p_rt[cpus].q[i]->priv,
				p_rt[cpus].q[i]->handle,p_rt[cpus].q[i]->rx_pkt_burst);
		printf("\n\n");
	}
#endif
	return 0;
}

static void  percpu_process_init(void) 
{
	int i, j;
	memset(&process_st, 0, sizeof(process_st));
	memset(&process_rt, 0, sizeof(process_rt));

	for (i = 0; i < MAX_SERVER_CPUS; i++)
		process_flag[i] = 1;

	for (i = 0; i < RTE_MAX_ETHPORTS; i++)
		eth_status[i]=0;
	eth_status[i-1]=1;
	eth_status[i]=1;
	percpu_process_static_update(RECEIVE_FROM_ETH);
	//percpu_process_static_update(RECEIVE_FROM_RINGBUF);
	//percpu_process_static_update(RECEIVE_FROM_RSSRING);

	for (i = 0; i < RTE_MAX_ETHPORTS; i++) {
		for(j = 0; j < SERVER_TX_QUEUES; j++) {
			dev_queue_ctl_st[0][i][j].queue_start = (uint8_t)-1;
			dev_queue_ctl_st[1][i][j].queue_start = (uint8_t)-1;
		}
	}
	
	for (i = 0; i < portinfos->portn; i++) {
		if (!(portinfos->status_uk[i] & USER_STATUS))
			continue;
		port_txcpu_update(i, 1);
	}
}

/* add for calculate queue id in bulk workmode */
static void pereth_process_init(void)
{	
	int i = 0;
	
	memset(devqueue,0,sizeof(devqueue));
	for(i = 0; i < MAX_DEV_QUEUE; i++){
		devqueue[i].queue_percpu = 1;
	}
	
	for(i = 0; i < portinfos->portn; i++){
		if(portinfos->txrings[i] != 0)
			devqueue[i].queue_percpu = portinfos->txrings[i];
		else printf("eth output queue nums is zero(divisor is zero)\n");
	}
#ifdef BRIDGE_ON
		devqueue[VIRTUAL_PORT].queue_percpu = 1;
#endif
}


//static rte_spinlock_t intr_lock = RTE_SPINLOCK_INITIALIZER;
static void update_port_status(uint8_t port_id)
{
	struct rte_eth_link link;
	int flag = 0;
	
	if (!server_stop)
		return ;

	//rte_spinlock_lock(&intr_lock);
	link.link_status = 0;	
	rte_eth_link_get_nowait(port_id, &link);

	if ((portinfos->status_uk[port_id] & USER_STATUS) == 0 && link.link_status == 1) {	
		flag = 1;
	}
	else if ((portinfos->status_uk[port_id]&USER_STATUS)==1 && link.link_status==0) {
		flag=-1;
	}

	if (link.link_status) {
		portinfos->status_uk[port_id] |= USER_STATUS;
		if (link.link_speed == 10000)
			portinfos->status_uk[port_id] |= IS_IXGBE;
	}
	else
		portinfos->status_uk[port_id] &= ~USER_STATUS;

	if ((portinfos->status_uk[port_id] & USER_STATUS) && !(portinfos->status_uk[port_id] & KERN_STATUS)) {
		if (portinfos->status_uk[port_id] & KNI_STATUS)
			setetherstatus((const char *)(portinfos->kni[port_id]->name), 1);
        system("python /usr/local/bluedon/networking/route.py boot_recover > /dev/null 2>&1 &");
	}

	if (!(portinfos->status_uk[port_id] & USER_STATUS) && (portinfos->status_uk[port_id] & KERN_STATUS)) {
		if (portinfos->status_uk[port_id] & KNI_STATUS)
			setetherstatus((const char *)(portinfos->kni[port_id]->name), 0);
	}
	
	portinfos->schport[port_id].linkspeed = link.link_speed;
	
	if (flag) {
		port_txcpu_update(port_id,flag);
		printf("vEth%u is being %s\n",port_id,flag<0?"DOWN":"UP");
		eth_status[port_id] = flag < 0 ? 0 : 1;
		//percpu_process_static_update(RECEIVE_FROM_KNIFIFO);
		/*percpu_process_static_update(RECEIVE_FROM_ETH);*/
	}
	//rte_spinlock_unlock(&intr_lock);
}

static struct rte_kni *get_kni_byport(uint8_t port)
{
	return (port >= RTE_MAX_ETHPORTS) ? NULL : portinfos->kni[port];
}

static void server_log_init(struct dpdk_log * log)
{
	memset(log,0,sizeof(struct dpdk_log));
	log->level = RTE_LOG_ERR;//RTE_LOG_LEVEL;
	log->type  = RTE_LOGTYPE_PLATFORM;
	log->flag  = 0;
	rte_set_log_type(0xffffffff,0);
	//rte_set_log_type(log->type,1);
	log->atype |= log->type;
	rte_set_log_level(log->level);
	rte_openlog_stream(log->file);
}

static void do_log_config(void)
{
	struct dpdk_log * log = &sysinfo->log;
	FILE * file = NULL;
	
	if(log->oldfile != NULL && log->oldfile != stderr && 
		log->oldfile != stdin && log->oldfile != stdout){
		if(!fclose(log->oldfile)){
			printf("close file ok!\n");
			log->oldfile = NULL;
		}
	}
	if(!log->flag) return;

	switch(log->flag){
		case 1:
			rte_set_log_type(log->type,1);
            log->atype |= log->type;
			break;
		case 2:
			rte_set_log_type(log->type,0);
            log->atype &= (~log->type);
			break;
		case 3:
			rte_set_log_level(log->level);
			break;
		case 4:
			if(!strcmp(log->filepath,"default")){
				file = NULL;
			}
			else { 
				file = fopen(log->filepath,"a+");
				printf("open file %s\n",log->filepath);
				if(!file){
					printf("open file %s failed\n",log->filepath);
					break;
				}
			}
			rte_openlog_stream(file);
			log->oldfile = log->file;
			log->file = file;
			break;
        case 5:
            rte_set_log_type(log->atype,1);
            log->dpdk_debug = 1;
            break;
        case 6:
            rte_set_log_type(0xffffffff,0); /*clear all*/
            log->dpdk_debug = 0;
            break;
		default:
			break;
		}
	log->flag = 0;
	return;
}
#if 0
static void port_check(void)
{
	uint8_t portid,flag=0;
	uint8_t port_num=portinfos->portn;
	struct rte_eth_link  link;

	for (portid = 0; portid < port_num; portid++) {
		update_port_status(portid);
	}
}
#endif
static void *do_manager_task(__attribute__((unused)) void *arg)
{
	int i;
	struct timeval cur_time;     
	volatile uint32_t *fstop = &server_stop;

    gettimeofday(&cur_time, NULL);  
	*msec = cur_time.tv_sec*1000 + cur_time.tv_usec/1000;
	
	while (*fstop) {
		for (i = 0; i < 1000; i++) {
			usleep(1000);
			(*msec)++;
			//qos_manage(sysinfo);
		}
		do_log_config();
		detect_client(server_tx);
		//port_check();

		//if (((*msec / 1000) % 5) == 0) {
			for (i = 0; i < portinfos->portn; i++) {
				if (!(portinfos->status_uk[i] & USER_STATUS))
					continue;
	
				rte_eth_stats_get(i, &(portinfos->stats_uk[i]));
				portinfos->stats_uk[i].omissed = rte_atomic64_read(&(portinfos->port_tx_dp[i]));
			}
		//}
	}

	printf("manager exit!\n");
	return NULL;
}

static int port_queue_config_check(void)
{
	int i, ret = 0;

	if (server_tx->queue.policy == BY_OUTPORT)
		return 0;

	for (i = 0; i < portinfos->portn; i++) {
		if (!(portinfos->status_uk[i] & USER_STATUS))
			continue;
		if (portinfos->txrings[i] < SERVER_TX_QUEUES ) {
			printf("NOTICE: servet-tx policy is not \"BY-OUTPORT\"!\n"
			"but port %d have %d queue,smaller than server-tx queue %d !may be error!\n",
			i, portinfos->txrings[i] , SERVER_TX_QUEUES);
			ret = -1;
		}
	}

	return ret;
}

static inline int percpu_process_runtime_check(int cpu, struct percpu_process_runtime  *pprt)
{
	int i;

	if (!pprt || !pprt->cnt)  
		return -1;

	for (i = 0; i < pprt->cnt; i++) {
		if (unlikely(!(pprt->q[i]) ||
		             !(pprt->q[i]->handle) ||
		             (pprt->q[i]->type >= RECEIVE_MAX)||
		             (pprt->q[i]->type == 0 && !(pprt->q[i]->rx_pkt_burst)))) {
			printf("NOTICE:cpu=%d,pprt may be error\n",cpu);
			return -1;				
		}
	}

	usleep(cpu);

#if 0
	printf("cpu=%d,task %d:", cpu, pprt->cnt);
	printf("task ifno (type,priv,handle,func):");
	for (i = 0; i < pprt->cnt; i++)
		printf("(%d,0x%x,%p,%p),", pprt->q[i]->type, pprt->q[i]->priv,
			pprt->q[i]->handle, pprt->q[i]->rx_pkt_burst);
	printf("\n");
#endif
		
	return 0;
}

#if (SERVER_TX_BULK_MODE==1)
static inline uint16_t get_qid(uint8_t port, __attribute__((unused)) uint8_t cpuindex)
{
	return (devqueue[port].queue_round++ % devqueue[port].queue_percpu);
}

#else
static inline uint16_t get_qid(uint8_t port, uint8_t cpuindex)
{
	volatile struct dev_queue_ctl *qid_ctl;
	uint16_t qid;

	qid_ctl = &dev_queue_ctl_rt[port][cpuindex];
	qid = qid_ctl->queue_start+qid_ctl->queue_round%qid_ctl->queue_percpu;
	qid_ctl->queue_round++;
	//printf("port=%d,cpuindindex=%d,qid=%d\n", port, cpuindex, qid);
	
	return qid;
}
#endif

static void per_cpu_process(int cpu) 
{
	int i, j;
	int  count, count1;
	volatile uint32_t *fstop = &server_stop;
	volatile int  *cpuflag;
	struct percpu_process_runtime  * volatile pprt;
	struct handleinfo  ** volatile  q;
	int cnt, cnt1, cnt2, cnt3, cnt4;
	struct rte_mbuf *buf[PACKET_READ_SIZE];
	uint16_t rx_count = 0, ret = 0;
	uint64_t cpu_sum_count = 0;
	int pkts_num = 0, index = 0;
	struct rte_mbuf * out_pkts[ANALYZE_MAX_MBUF];
	unsigned rss_ring_index = 0;
	
	cpuflag = &process_flag[cpu];
	pprt = &p_procss_rt[cpu];
	
	printf("my core =%d,cpu=%d\n", rte_lcore_id(), cpu);
	set_process_priority(server_tx);

	//check port
	port_queue_config_check();
	while (*fstop) {
		if (!dev_queue_ctl_rt) {
			printf("NOTICE:dev port have not ready!\n");
			sleep(1);
			continue;
		}

		pprt = &p_procss_rt[cpu];
		if(-1 == percpu_process_runtime_check(cpu, pprt)) {
			sleep(1);
			continue;
		}

		q = pprt->q;
		cnt = pprt->cnt;
		cnt1 = pprt->cnt_item[0];
		cnt2 = pprt->cnt_item[1];
		cnt3 = pprt->cnt_item[2];
		cnt4 = pprt->cnt_item[3];
		count = count1 = 0;

		while (*cpuflag) {
			for (i = 0; i < cnt1; i++) {
				rx_count = (q[i]->rx_pkt_burst)(q[i]->handle, buf, PACKET_READ_SIZE);
				if (!rx_count) {
					count++;
					DPDK_LOG(DEBUG,PLATFORM,"Line:%d Rx from eth,portid:%u queue:%u queue id %d queue handle %p\n",
						     __LINE__,q[i]->priv>>8,q[i]->priv&0xff,i,q[i]->handle);
					continue;
				}
				DPDK_LOG(DEBUG,PLATFORM,"Line:%d Rx from eth,portid:%u queue:%u,packets:%u\n",
										__LINE__,q[i]->priv>>8,q[i]->priv&0xff,rx_count);
				cpu_sum_count += rx_count;
				port_input_bulk(sysinfo, buf, rx_count, 0xff & q[i]->priv, cpu);
				//for(j = 0; j < rx_count; j++)
				//	port_input(sysinfo, buf[j], cpu);
			}

			for ( ; i < cnt2; i++) {
				rx_count = rte_ring_dequeue_burst((struct rte_ring *)(q[i]->handle), (void *)buf, PACKET_READ_SIZE);
				if (!rx_count) {
					count++;
					continue;
				}

				for(j  = 0; j < rx_count; j++) {
					packet_preprocessing(&(sysinfo->filterinfo[FILTER_DPDK_FRAME]), buf[j]);									
					dpdk_enqueue_byeth(sysinfo, buf[j]);
				}
			}

			for ( ; i < cnt3; i++) {
				rx_count = rte_ring_dequeue_burst((struct rte_ring *)(q[i]->handle), (void *)buf, PACKET_READ_SIZE);
				if (!rx_count) {
					count++;
					continue;
				}
				//cpu_sum_count+=rx_count;

				if (sysinfo->kernel_stack_flag == 0) {
					for (j = 0; j < rx_count; j++){
                        if (unlikely(buf[j]->port >= rte_eth_dev_count())) { 
                            DPDK_LOG(ERR,PLATFORM,"%s %d : port = %d, total ports = %d\n", __FUNCTION__, __LINE__, buf[j]->port, rte_eth_dev_count());
                            rte_pktmbuf_free(buf[j]);                            
                            continue;
                        }
						
						if(unlikely(buf[j]->userdef == 0 || buf[j]->userdef >= WORK_MODE_MAX)){
							DPDK_LOG(ERR,PLATFORM,"Line:%d after from app,port mode is %u\n",__LINE__,buf[j]->userdef);
						}
						if ((buf[j]->userdef != NAT_PORT) && (buf[j]->userdef != DIRECT_CONNECT) && (buf[j]->userdef != MIRROR_PORT)){
							if (!rte_kni_tx_burst(portinfos->kni[buf[j]->port], &buf[j], 1)) {
								DPDK_LOG(WARNING,PLATFORM,"Line:%d ADVACED BRIDGE Tx kernel queue full mbuf->port=%u\n",__LINE__,buf[j]->port);
								rte_pktmbuf_free(buf[j]);
							}
						} 
						else {
							port_output(server_tx, buf[j], get_qid(buf[j]->port, q[i]->priv), cpu);
						}
					}
				}
				else {
#if (SERVER_TX_BULK_MODE==1)
					port_output_bulk(server_tx, buf, rx_count, get_qid(q[i]->priv, q[i]->priv), cpu);
#else
					for (j = 0; j < rx_count; j++)
						port_output(server_tx, buf[j], get_qid(buf[j]->port, q[i]->priv), cpu);
#endif
				}
			}

			for ( ; i < cnt4; i++) {	
				rx_count=rte_kni_rx_burst((struct rte_kni *)(q[i]->handle), buf, PACKET_READ_SIZE);
				if (!rx_count) {
					DPDK_LOG(DEBUG,PLATFORM,"Line:%d rx from kernel,type:%d priv:%d queue id %d queue handle %p\n",
						     __LINE__,q[i]->type,q[i]->priv,i,q[i]->handle);
					count++;
					continue;
				}
				//cpu_sum_count+=rx_count;
				for (j = 0; j < rx_count; j++) {
					buf[j]->rings_cnt = NULL;
					if(unlikely(buf[j]->userdef == 0 || buf[j]->userdef >= WORK_MODE_MAX)){
						DPDK_LOG(ERR,PLATFORM,"Line:%d after rx from kernel,port mode is %u\n",__LINE__,buf[j]->userdef);
					}
					if (buf[j]->userdef == NAT_PORT) {
						pkts_num = packet_tuple_analyzer(buf[j], out_pkts, ANALYZE_MAX_MBUF);
						for (index = 0; index < pkts_num; index++) {
							pingagent(out_pkts[index]);
							rss_ring_index = out_pkts[index]->tag % server_cpus; //if there is two cpus, use "& 0x01", else use "% server_cpus"
							ret = rte_ring_enqueue_burst(sysinfo->rss_rings[rss_ring_index],(void **)&out_pkts[index],1);
							if(!ret) {
								DPDK_LOG(WARNING,PLATFORM,"Line:%d NAT_PORT software rss rings enqueue failed\n", __LINE__);
								rte_pktmbuf_free(out_pkts[index]);
							}
						}
					}
					else {
						port_output(server_tx, buf[j], get_qid(buf[j]->port, q[i]->priv),cpu);
					}
				}
			}			
			
			if (count == cnt) {
				if ((++count1) & 0x10)
					usleep(1);
			}
			count = 0;
		}
		*cpuflag = 1;
	}

	printf("cpu %d exit,sum_count=%lu!\n", cpu,cpu_sum_count);
}


static int server_main_loop(__attribute__((unused)) void *arg)
{
	unsigned lcore_count, lcore, cpus;
	
	lcore_count = rte_lcore_count() - 1;
	lcore = rte_lcore_id();

	printf("server are %d  cores,my is %d.\n",lcore_count,lcore);
	
	cpus = lcore % lcore_count;
	if (lcore == 0)
		do_manager_task(NULL);
	else
		per_cpu_process(cpus); 
	return 0;
}


int main(int argc, char *argv[]) 
{
	int i, retval;
	uint32_t lcore;
	//pthread_t tid;
	struct kni_ctl knictl = {&server_stop, get_kni_byport};
		
	if (rte_eal_init(argc, argv) < 0) {
		rte_exit(EXIT_FAILURE, "Invalid EAL arguments\n");
		return -1;
	}

	if( !(sysinfo = dpdk_queue_system_shm_init(1)))
		return -1;

	server_log_init(&sysinfo->log);
	dpdk_sysport_init(sysinfo, (~0x0), update_port_status);
	portinfos = &sysinfo->portinfos;

	server_init();
	/*percpu_process_init();*/
	init_kni_um(portinfos, &knictl);
	
	for (i = 0; i < portinfos->portn; i++) {
		retval = dpdk_port_init(sysinfo, i, NULL, NULL);
		if (retval != 0)
			rte_exit(EXIT_FAILURE, "Cannot initialise port %u\n", (unsigned)i);
		//init_sched_port(&portinfos->schport[i], i, sysinfo->socket_id);
	}
	percpu_process_init();
	pereth_process_init();
	//init_kni_um(portinfos, &knictl);
	do_module_inits(sysinfo);
	//dump_portinfo();
	
	//dump_system2();
	//filter_dump_byclinet(server_tx);
	//filter_dump_bysystem(sysinfo);
	//pthread_create(&tid, NULL, do_manager_task, NULL);	
	
	rte_eal_mp_remote_launch(server_main_loop, NULL, CALL_MASTER);
	RTE_LCORE_FOREACH_SLAVE(lcore) {
		if (rte_eal_wait_lcore(lcore) < 0) {
			return -1;
		}
	}	
	
	//pthread_join(tid, &status);
	server_exit(server_tx);
	exit_kni_um(portinfos);
	do_module_exits(sysinfo);

	return 0;
}

