#ifndef __DPDK_FLOW_H__ 
#define __DPDK_FLOW_H__ 

#include "dpdk_warp.h"
#include "dpdk_config.h"
#include "hlist.h"

#define MAX_NAME_SIZE   32

#define FLOW_TABLE_NAME  "SERVER_FLOW_TABLE"
#define FLOW_ALLOC_QUEUE "FLOW_ALLOC_QUEUE"
#define TRAFFIC_STATISTICS "TRAFFIC_STATISTICS"

enum {
    EXCEPTION_FLOW,
    FIRST_NEW_FLOW,
    FIRST_REPLY_FLOW,
    ESTABLISH_FLOW,
    MAX_STATUS_FLOW,
};

enum {
    FLOW_ORIG,
    FLOW_REPLY,
    FLOW_DIR,
};

enum {
    FLOW_NOT_NAT,
    FLOW_NAT_DIR,
    FLOW_MAX_TYPE,  
};

struct Flow_key {
    uint32_t ip_src;
    uint32_t ip_dst;
    uint16_t port_src;  //tcp udp for port icmp for id
    uint16_t port_dst;  //tcp udp for port icmp for type code
    uint8_t  proto;     //tcp udp icmp
}__rte_cache_aligned;

struct Flow_stats {
    uint64_t totalbytes[FLOW_DIR];
    uint64_t totalpackets;
    uint32_t lastbytes[FLOW_DIR];
    uint32_t TS_bytes[FLOW_DIR];   //for ts using
    uint64_t last_count;
    uint64_t curr_count;
    uint64_t last_seen;
}__rte_cache_aligned;

struct Flow_entry {
    struct Flow_key key[FLOW_MAX_TYPE];      //0 origin key,  1 nat key
    struct Flow_stats stats;
    struct hlist_node hchain[FLOW_MAX_TYPE]; //0 origin hash node, 1 nat hash node
    TAILQ_ENTRY(Flow_entry) tchain;
    void * ext;
    uint32_t hash[FLOW_MAX_TYPE];
    uint32_t ctid;
#define TCP_FIN_ACK_ORIGIN  0x01
#define TCP_ACK_REPLY       0x02
#define TCP_FIN_ACK_REPLY   0x04
#define TCP_ACK_ORIGIN      0x08
    uint8_t tcpfin;
    uint8_t inport;
    uint8_t outport;
    uint8_t isswap[FLOW_MAX_TYPE];
    uint8_t status;
    uint8_t ifmark;
    uint8_t dpicnt;
    uint32_t protoapp;
    uint8_t used;
}__rte_cache_aligned;

typedef TAILQ_HEAD(Flow_entry_list, Flow_entry) Flow_entry_list_t;

struct Flow_root {
    int nums;
    struct hlist_head root;
};

struct Flow_table_core {
    int flownums;
    Flow_entry_list_t lrulist;
    struct Flow_root bucket[FLOW_MAX_TYPE][MAX_FLOW_BUCKET];
}__rte_cache_aligned;

struct Flow_table {
    char name[MAX_NAME_SIZE];
    uint8_t  ftab_flag;
    uint8_t  ts_flag;
    uint32_t totalflow;
    uint64_t tstime;
    uint64_t flowtimeout;
    uint64_t hz;
    struct rte_ring        * ts;
    struct rte_ring        * flowalloc;
    struct Flow_entry      * tabbuf;
    struct Flow_table_core * ftabcorebuf;
}__rte_cache_aligned;

struct Flow_entry * Flow_table_natlookup(struct rte_mbuf *mbuf);
struct Flow_entry * Flow_table_postlookup(struct rte_mbuf *mbuf);
struct Flow_entry * Flow_table_lookup(struct rte_mbuf *mbuf);
void Flow_table_status_dump(struct Flow_table * ftab);
void Flow_TS(struct rte_mbuf * mbuf);
void Flow_TS_bulk(struct rte_mbuf ** mbuf, uint16_t nb_pkts);



#endif

