/*
 * Copyright(c) 2007 BDNS
 */
 
#ifndef __DPDK_IP_REASS_H__
#define __DPDK_IP_REASS_H__

#include <sys/queue.h>


#define IP_REASS_OVERLAP_DEAL 1

//#define IP_REASS_IN_SERVER	   1
//#define IP_REASS_EXCEPTION_WAY   1 


//#define IP_REASS_PRINT_INFO 1

#define DEBUG 0

#ifdef IP_REASS_PRINT_INFO 
#define TRACE_REASS(fmt,args...) do {\
		printf(fmt,##args);          \
} while(0)
#else
#define TRACE_REASS(fmt,args...) do {} while(0)
#endif

#define IP_REASS_TBL_STAT 
#ifdef IP_REASS_TBL_STAT
#define IP_REASS_STAT_UPDATE(s, f, v)   ((s)->f += (v))
#else
#define IP_REASS_STAT_UPDATE(s, f, v)   do {} while (0)
#endif /* IP_REASS_TBL_STAT */


#define MAX_IPV4_REASS_PACKETS 32

/* queue hash table size */
#define IPV4_REASS_HASH_TABLE_SIZE 16

/* maximum number of fragment */
#define MAX_IP_FRAGMENT_NUM 100

/*maximum ip packet size*/
#define IP_MAXPACKET_SIZE 65535

#define IP_FRAG_MIN_SIZE 32

#define TIME_OUT 10

#define PKT_DROP        -1
#define PKT_KEEP        0

#ifndef TRUE
#define TRUE  1
#define FALSE 0
#endif

struct ip_frag_hash_key {
	uint32_t src_addr;
	uint32_t dst_addr;
	uint16_t packet_id;
	uint8_t  next_proto_id;
}__rte_cache_aligned;


/** fragmentation table statistics */
struct ip_reass_tbl_stat {
	uint64_t reuse_ipq_num;
	uint64_t find_ipq_num;
	uint64_t add_ipq_num;      
	uint64_t del_ipq_num;
	uint64_t fail_no_ipq;    
	uint64_t fail_no_ipfrag;
	uint64_t e_firstfrag_num;
	uint64_t e_lastfrag_num;
	uint64_t e_length_num;
	uint64_t e_overlapfrag_num;
	uint64_t e_smallfrag_num;
	uint64_t time_out_num;
	uint64_t dropfrag_num;
	uint64_t transfer_num;
	uint64_t do_packet_num;
	uint64_t reass_ok_num;
};

/*keep start_offset and end end_offset of current rte_mbuf*/
struct ip_frag {
	uint32_t start_offset;     //start offset of this fragment
	uint32_t end_offset;       //end offset of this fragment
	uint16_t used;             //frag pool flag: is used? //rte_atomic32_t   used; */    
	uint16_t is_last_frag;
//	uint32_t head_overlap;
//	uint32_t tail_overlap;
	struct rte_mbuf * m;       //current fragment
	struct ip_frag  * next;    //next ip_frag
};

/* IPv4/IPv6 fragment queue */
struct ip_ipq {
union{
	struct ipv4_tuple5 	ipv4;
	struct ipv6_tuple5 	ipv6;
}tuple;
	uint32_t      		mbuf_tag;
	uint32_t      		id;
	
	rte_atomic32_t      first_recvd;
	rte_atomic32_t      last_recvd;
	uint32_t            head_complete;
	uint32_t            head_first_come;

	uint32_t       		total_len;
	uint32_t       		recvd_len;
	
	uint32_t       		frag_count;
	uint32_t       		hash;
	
	uint64_t 			start_cycles;                  /* date when reassembly was started */
	uint64_t 			last_cycles;                   /* date when last fragment was received */

	uint16_t            used;                          /* if ipq is used. //rte_atomic32_t used;*/
	uint8_t             exception;
	uint8_t 			index;
	struct ip_frag  	frag_pool[MAX_IP_FRAGMENT_NUM]; 
	struct ip_frag     *frag_list;

	TAILQ_ENTRY(ip_ipq) hchain;                       
	TAILQ_ENTRY(ip_ipq) tchain;                      
} __rte_cache_aligned;

typedef struct ip_ipq ip_ipq_t;
typedef TAILQ_HEAD(ip_ipq_list, ip_ipq) ip_ipq_list_t;


/** fragmentation table */
struct ip_reass_frag_tbl {
	uint32_t             max_entries;     /* max ipq entries */
	uint32_t       		 use_entries;     /* ipq entries in use. */
	struct ip_reass_tbl_stat stat;	      /* statistics counters. */
	struct PktReassInfo *pktreass;
	ip_ipq_t * last;                      /* last used ipq entry. */
	ip_ipq_list_t ipq_tlist;                              //list of time-ordered ipq entries
	ip_ipq_list_t ipq_htable[IPV4_REASS_HASH_TABLE_SIZE]; //hash table for ipq enteies
	ip_ipq_t      ipq_pool[MAX_IPV4_REASS_PACKETS];
	int lcore;
}__rte_cache_aligned;


#define MAX_FRAG_TABLE 32

struct PktReassInfo {
	int enable;
	unsigned lcorenum;
	uint64_t timeout;
	uint64_t frag_cycles;
	struct ip_reass_frag_tbl * tbl_array[RTE_MAX_LCORE];
	struct ip_reass_frag_tbl * frag_table_buffer;
};



int reassinit(void*);
int reassexit(void*);

void print_reass(void);
void reass_info_dump(void * __sysinfo);

int pkt_reass_enable(void);

int ipv4_pkt_is_fragmented(const struct ipv4_hdr * hdr);

int ipv4_reassemble(struct rte_mbuf * mbuf,
	                     struct rte_mbuf **out_pkts,
	                     uint16_t  nb_pkts);


#ifdef MCORE_IPV6_REASS
int ipv6_reassemble(struct rte_mbuf * mbuf,
	                   struct rte_mbuf **out_pkts,
	                   uint16_t nb_pkts);
#endif


#endif /* __DPDK_IP_REASS_H__ */

