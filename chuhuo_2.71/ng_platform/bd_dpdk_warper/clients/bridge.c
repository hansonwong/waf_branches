#include <dpdk_warp.h>

#include "dpdk_frame.h"
#include "link.h"
#include "hash.h"
#include "memfixed.h"
#if 1
static struct system_info *sysinfo;
static struct rte_mempool *clone_pool;
static struct portinfo  *ports;
static struct clientinfo *client_bridge;
struct client_reginfo bridge_info={
	.name="client_bridge",
	.priority=MAX_CLINET_PRIORITY-2,
	.fixedid=3,
	.rwmode="r",
	.hook="out",
	.filter={
		"all",
	},
	.qnum=1,
};

#define MAX_PORT_MAC_INFO  8192
#define MAX_PTMAC_HASH  	 1024
#define MAX_AGE			300
struct  port_mac {
	uint64_t mac;//port+mac[6]
	uint16_t port;
	uint16_t age;
	struct list_head hl;
};
#define BRIDGE_INFO   "bridge_info"
#define BRIDGE_HASH  "bridge_hash"
#define GET_ITEM_BYLINK(link) \
(struct  port_mac *)list_entry(link,struct  port_mac,hl)

static uint32_t port_mac_hash(struct  port_mac  *pmac) {
	int  i; 
	uint32_t hash = 0;  
	uint16_t *key=(uint16_t *)&(pmac->mac);
	key+=1;
	for (i=0;i<3;i++) 
		hash = hash * 33 + key[i];
    	return hash;  
	//return default_hash((uint8_t *)&(pmac->mac),sizeof(pmac->mac));
}

static  int    port_mac_same(struct list_head  *link,struct  port_mac *pmac) {
	struct  port_mac *tmp=GET_ITEM_BYLINK(link);
	return  (tmp->mac==pmac->mac);
 }

static  int port_mac_update(struct list_head  *link){
	struct  port_mac *tmp=GET_ITEM_BYLINK(link);
	tmp->age=MAX_AGE;
	return 0;
}


static void *pmac_info_malloc(int size) {
	return dpdk_shm_alloc(sysinfo,BRIDGE_INFO,size);
}

static void *pmac_hash_malloc(int size) {
	return dpdk_shm_alloc(sysinfo,BRIDGE_HASH,size);
}
 
static struct hashinfo  hinfo={
	.bucket=MAX_PTMAC_HASH,
	.hash=(phash)port_mac_hash,
	.compare=(pcompare)port_mac_same,
	.update=(pupdate)port_mac_update,
	.malloc=(pmalloc)pmac_hash_malloc,
	.free=dpdk_shm_free,
};
static struct meminfo  minfo={
	.totalunit=MAX_PORT_MAC_INFO,
    	.unitsize=sizeof(struct  port_mac),
    	.malloc=(mmalloc)pmac_info_malloc,
    	.free=dpdk_shm_free,
};

static struct hhash *h;
static  struct memfixed *m;


static void
brige_exit(int s) {
	client_unregister(client_bridge);
	hashdestroy(h,&hinfo);
	mempool_exit(m,&minfo);
	exit(0);s=s;
	//signal(s, SIG_DFL);
}


static int
brige_init(void) {
	m=mempool_init(&minfo);
	if(!m)
		goto error0;
	h=hashcreate(&hinfo);
	if(!h)
		goto error1;
	client_bridge=client_register(&bridge_info);
	if(!client_bridge){
		printf("client %s register error!\n",bridge_info.name);
		goto error2;
	}
	dump_system1();
	dump_system2();
	signal(SIGINT,brige_exit);
	signal(SIGQUIT,brige_exit);
	signal(SIGABRT,brige_exit);
	signal(SIGKILL,brige_exit);
	return 0;
error2:
	hashdestroy(h,&hinfo);
error1:
	mempool_exit(m,&minfo);
error0:
	return -1;	
}


static int 
mac_learning(uint8_t portid,uint8_t *smac) {
	struct  port_mac pm;
	struct  port_mac *pmh;

	pm.mac=((*(uint64_t *)smac)&0xffffffffffff);
	pm.port=portid;
	if(hhash_find(h,&pm)) //existed
		return 0;

	printf("learning sucess...\n");
	pmh=mempool_malloc(m);
	if(!pmh) {
		printf("%s:malloc fail\n",__FUNCTION__);
		return -1;
	}
	pmh->mac=pm.mac;
	pmh->port=portid;
	pmh->age=MAX_AGE;
	hhash_add(h,pmh,&(pmh->hl));
	return 0;
}



static int 
brige_forwarding(uint8_t portid,uint8_t *dmac){
	struct list_head *link;
	struct  port_mac  *item;
	struct  port_mac pm;
	
	pm.mac=((*(uint64_t *)dmac)&0xffffffffffff);
	pm.port=portid;
	link=hhash_find(h,&pm);
	if(link) {
		item=GET_ITEM_BYLINK(link);
		//printf("found,port=%d\n",item->port);
		return item->port;
	}else 
		return -1;
}

static int 
get_all_uplink(char buf[RTE_MAX_ETHPORTS],int myport) {
	uint32_t i,k=0;
	for(i=0,k=0;i<ports->portn;i++) {
		if((ports->status_uk[i]&USER_STATUS)&&i!=myport)
			buf[k++]=i;
	}
	return k;		
}

static void
do_bridge(struct rte_mbuf *m) {
	struct ether_hdr *eth;
	struct rte_mbuf *mclone;
	int outport,n,i;
	eth = rte_pktmbuf_mtod(m, struct ether_hdr *);
	mac_learning(m->inport,eth->s_addr.addr_bytes);
	outport=brige_forwarding(m->inport,eth->d_addr.addr_bytes); 
	if(-1!=outport){
		m->port=outport;
		dpdk_enqueue(client_bridge,m);
	}else {
		char buf[RTE_MAX_ETHPORTS];
		if(1==ports->portn) { //only one port ,
			rte_pktmbuf_free(m);
			return ;
		}
		n=get_all_uplink(buf,m->inport);
		for(i=0;i<n-1;i++) {
			mclone = rte_pktmbuf_clone(m, clone_pool);
			mclone->port=buf[i];
			dpdk_enqueue(client_bridge,mclone);
		}
		//last
		m->port=buf[i];
		dpdk_enqueue(client_bridge,m);
	}
}

static int
client_bridge_loop(__attribute__((unused)) void *arg){
	unsigned lcore_count,lcore;
	uint32_t  index=0,j,rx_count;
	struct rte_mbuf *buf[PACKET_READ_SIZE];
	//uint32_t total_rxcount=0;
	lcore_count=rte_lcore_count();
	lcore = rte_lcore_id();
	printf("here are %d  cores ,my is %d!\n",lcore_count,lcore);
	while(1) {
		rx_count=dpdk_dequeue2(client_bridge,&index,(void **)buf,PACKET_READ_SIZE);
		//printf("bridge--->rx_count=%d\n",rx_count);
		//total_rxcount+=rx_count;
		//if(total_rxcount%1400000==0)
		//	printf("total_rxcount=%d\n",total_rxcount);
		for(j=0;j<rx_count;j++) {
			rte_prefetch0(rte_pktmbuf_mtod(buf[j], void *));
			do_bridge(buf[j]);
		}
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
	clone_pool=sysinfo->pktmbuf_pool;
	ports=&(sysinfo->portinfos);
	if(brige_init())
		return -1;
	
	client_bridge_loop(NULL);
	return 0;
}
#endif
