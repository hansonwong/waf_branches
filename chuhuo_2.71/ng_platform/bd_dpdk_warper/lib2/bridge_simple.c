#include <dpdk_warp.h>

#include "dpdk_frame.h"
#include "link.h"
#include "hash.h"
#include "memfixed.h"
#include "bridge_simple.h"

#ifndef ETHER_ADDR_LEN
#define ETHER_ADDR_LEN (6)
#endif

static struct system_info *sysinfo;
static struct portinfo  *ports;

#define MAX_PORT_MAC_INFO  8192
#define MAX_PTMAC_HASH     1024
#define MAX_AGE            300

struct  port_mac {
	union{
		uint64_t key;
		struct {
			uint8_t mac[ETHER_ADDR_LEN];			
			uint16_t br_id;/* bridge id */
		};
	};
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
	uint16_t *key=(uint16_t *)&(pmac->key);
	for (i=0;i<4;i++) {
		hash = hash * 33 + key[i];
	}
	return hash;  
	//return default_hash((uint8_t *)&(pmac->mac),sizeof(pmac->mac));
}

static int port_mac_same(struct list_head  *link,struct  port_mac *pmac) {
	struct  port_mac *tmp=GET_ITEM_BYLINK(link);
	return (tmp->key==pmac->key);
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
static struct memfixed *m;

static void 
bridge_groupinfo_show(struct portinfo  *portinfos)
{
	uint8_t port, port_cnt,i;

	for(port = 0; port < portinfos->portn; ++port){
		if(portinfos->mode[port].mode!=BRIDGE_SIMPLE)
			continue;
		printf("port %d,brid %d,",port,portinfos->mode[port].value);
		port_cnt=portinfos->bridge_group[port][0];
		printf("number of the same brid is %d:",port_cnt);
		for(i=1;i<=port_cnt;i++)
			printf("%d,",portinfos->bridge_group[port][i]);
		printf("\n");
	}
}

int 
port_brid_update(struct portinfo *portinfos,uint8_t  portid,int mode,int value)
{
	int old_mode = portinfos->mode[portid].mode;
	int old_value = portinfos->mode[portid].value;
	int op=(((mode==BRIDGE_SIMPLE)<<1)|(old_mode==BRIDGE_SIMPLE));
	uint8_t port_same_brid[RTE_MAX_ETHPORTS];
	uint8_t port,i,cnt,n;

	switch(op){
		case 0://
			return 0;
		case 1: //del
			printf("port %d mode is bridge, can not change to other mode\n", portid);
			return -1;
		case 2:{//add
				for(port = 0,cnt=0; port < portinfos->portn; ++port){		
					if(portinfos->mode[port].mode == mode && value == portinfos->mode[port].value)
						port_same_brid[cnt++]=port;
				}
				
				for(i=0;i<cnt;i++) //add peer to me
					portinfos->bridge_group[portid][1+i]=port_same_brid[i];
				portinfos->bridge_group[portid][0]=cnt;
				
				for(i=0;i<cnt;i++) { //add me to peer
					port=port_same_brid[i];
					n=portinfos->bridge_group[port][0]++;
					portinfos->bridge_group[port][n+1]=portid;
				}
			}	
			bridge_groupinfo_show(portinfos);
			return 0;
		case 3:
			if(old_value != value){
				printf("port %d is bridge, bridge id is %d, can not change to other bridge id\n", portid,old_value);
				return -1;
			}
			break;
		default:
			return -1;		
	}
	return 0;
}

static uint16_t
get_samebrid_up_port(uint8_t buf[RTE_MAX_ETHPORTS],int myport) {
	uint16_t i,k,port;
	uint16_t n=ports->bridge_group[myport][0];

	for(i=1,k=0;i<=n;i++){
		port = ports->bridge_group[myport][i];
		if(ports->status_uk[port]&USER_STATUS)
			buf[k++]=port;
	}
	return k;		
}

static int 
mac_learning(uint8_t portid,uint8_t *smac, uint16_t brid) {
	struct  port_mac pm;
	struct  port_mac *pmh;

	pm.key = (*(uint64_t*)smac) & 0xffffffffffff;//memcpy(pm.mac, smac, MAC_ADDR_LEN);
	pm.br_id = brid;
	pm.port=portid;
	
	if(hhash_find(h,&pm)) //existed
		return 0;

	printf("learning sucess...\n");
	pmh=mempool_malloc(m);
	if(!pmh) {
		printf("%s:malloc fail\n",__FUNCTION__);
		return -1;
	}
	pmh->key = pm.key;
	pmh->port=portid;
	pmh->age=MAX_AGE;
	hhash_add(h,pmh,&(pmh->hl));
	
	return 0;
}

static int 
bridge_forwarding(uint8_t *dmac, uint16_t brid){
	struct list_head *link;
	struct  port_mac  *item;
	struct  port_mac pm;
	
	pm.key = (*(uint64_t*)dmac) & 0xffffffffffff;//memcpy(pm.mac, dmac, MAC_ADDR_LEN);
	pm.br_id = brid;

	link=hhash_find(h,&pm); 
	if(link) {
		item=GET_ITEM_BYLINK(link);
			return item->port;
	}

	return VIRTUAL_PORT;
}

void
do_bridge(struct rte_mbuf *m){
	struct ether_hdr *eth;
	int port=m->port;
	int outport;
	int brid = ports->mode[port].value;
		
	eth = rte_pktmbuf_mtod(m, struct ether_hdr *);
	mac_learning(port,eth->s_addr.addr_bytes, brid);
	outport=bridge_forwarding(eth->d_addr.addr_bytes, brid);
	m->port = (uint8_t)outport;

	return;
}

uint16_t
do_bridge_broadcast(struct rte_mbuf **m_clone,struct rte_mbuf *src_mbuf){
	uint16_t j,n,k;
	uint8_t port_brd[RTE_MAX_ETHPORTS];//broadcast to these ports
	
	n = get_samebrid_up_port(port_brd, src_mbuf->inport);
	if(unlikely(!n))
			return 0;
	else {
		for(j=0,k=0;j<n-1;j++,k++) {
			m_clone[k] = rte_pktmbuf_clone(src_mbuf, sysinfo->pktmbuf_hdr_pool);
			if(unlikely(m_clone[k]==NULL)){
				printf("impossible:%s,%d,rte_pktmbuf_clone fail!\n",__FUNCTION__,__LINE__);
				break;
			}
			m_clone[k]->port=port_brd[j];
		}
		m_clone[k]=src_mbuf;
		m_clone[k]->port=port_brd[j];
		k++;
	}
	
	return k;
}

static int
bridge_init(void* _sysinfo) {
	sysinfo = (struct system_info*)_sysinfo;
	ports=&(sysinfo->portinfos);
	m=mempool_init(&minfo);
	if(!m)
		goto error0;
	h=hashcreate(&hinfo);
	if(!h)
		goto error1;

	return 0;
error1:
	mempool_exit(m,&minfo);
error0:
	return -1;	
}

static int
bridge_exit(void *arg  __attribute__((__unused__))) {
	hashdestroy(h,&hinfo);
	mempool_exit(m,&minfo);
	return 0;
}

MODULE_INIT(bridge_init)
MODULE_EXIT(bridge_exit)


