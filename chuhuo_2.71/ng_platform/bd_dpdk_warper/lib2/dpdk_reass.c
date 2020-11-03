/*
 * Copyright(c) 2007 BDNS
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <sys/stat.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/ioctl.h>
#include <sys/queue.h>

#include "dpdk_frame.h"
#include "dpdk_reass.h"

static struct PktReassInfo * prf;

static void 
reass_drop_pkt(struct ip_reass_frag_tbl * tbl,
	               struct ip_frag * ipfrag)
{
	IP_REASS_STAT_UPDATE(&tbl->stat,dropfrag_num,1);
#if 0
	if(ipfrag->m != NULL)
#endif
	rte_pktmbuf_free(ipfrag->m);
	ipfrag->used = 0;
	//rte_atomic32_clear(&ipfrag->used);
}

static void 
reass_statistics_dump(const struct ip_reass_frag_tbl *tbl)
{
	TRACE_REASS("+---------------------------------------------------------------------------------------------+\n"
		   "| reuse_ipq_num:     %10lu | find_ipq_num:     %10lu | add_ipq_num:      %10lu |\n"
		   "+-------------------------------+------------------------------+------------------------------+\n"
		   "| del_ipq_num:       %10lu | fail_no_ipq:      %10lu | fail_no_ipfrag:   %10lu |\n"
		   "+-------------------------------+------------------------------+------------------------------+\n"
		   "| e_firstfrag_num:   %10lu | e_lastfrag_num:   %10lu | e_length_num:     %10lu |\n"
		   "+-------------------------------+------------------------------+------------------------------+\n"
		   "| e_overlapfrag_num: %10lu | e_smallfrag_num:  %10lu | time_out_num:     %10lu |\n"
		   "+-------------------------------+------------------------------+------------------------------+\n"
		   "| dropfrag_num:      %10lu | transfer_num:     %10lu | do_packet_num:    %10lu |\n"
		   "+-------------------------------+------------------------------+------------------------------+\n"
		   "| reass_ok_num:      %10lu | max_entries:      %10u | use_entries       %10d |\n"
		   "+---------------------------------------------------------------------------------------------+\n",
			tbl->stat.reuse_ipq_num,
			tbl->stat.find_ipq_num,
			tbl->stat.add_ipq_num,
			tbl->stat.del_ipq_num,
			tbl->stat.fail_no_ipq,
			tbl->stat.fail_no_ipfrag,
			tbl->stat.e_firstfrag_num,
			tbl->stat.e_lastfrag_num,
			tbl->stat.e_length_num,
			tbl->stat.e_overlapfrag_num,
			tbl->stat.e_smallfrag_num,
			tbl->stat.time_out_num,
			tbl->stat.dropfrag_num,
			tbl->stat.transfer_num,
			tbl->stat.do_packet_num,
			tbl->stat.reass_ok_num,
			tbl->max_entries,tbl->use_entries);
};

void reass_info_dump(void * __sysinfo)
{
	struct system_info * sysinfo  = (struct system_info*)__sysinfo;
	struct PktReassInfo   * pktreass = sysinfo->pktreass;
	
	unsigned i;
	struct ip_reass_frag_tbl * tbl;
	for (i = 0; i < pktreass->lcorenum; i++){
		tbl = &pktreass->frag_table_buffer[i];
		
		printf("+---------------------------------------------------------------------------------------------+\n"
		   "| reuse_ipq_num:     %10lu | find_ipq_num:     %10lu | add_ipq_num:      %10lu |\n"
		   "+-------------------------------+------------------------------+------------------------------+\n"
		   "| del_ipq_num:       %10lu | fail_no_ipq:      %10lu | fail_no_ipfrag:   %10lu |\n"
		   "+-------------------------------+------------------------------+------------------------------+\n"
		   "| e_firstfrag_num:   %10lu | e_lastfrag_num:   %10lu | e_length_num:     %10lu |\n"
		   "+-------------------------------+------------------------------+------------------------------+\n"
		   "| e_overlapfrag_num: %10lu | e_smallfrag_num:  %10lu | time_out_num:     %10lu |\n"
		   "+-------------------------------+------------------------------+------------------------------+\n"
		   "| dropfrag_num:      %10lu | transfer_num:     %10lu | do_packet_num:    %10lu |\n"
		   "+-------------------------------+------------------------------+------------------------------+\n"
		   "| reass_ok_num:      %10lu | max_entries:      %10u | use_entries       %10u |\n"
		   "+---------------------------------------------------------------------------------------------+\n",
			tbl->stat.reuse_ipq_num,
			tbl->stat.find_ipq_num,
			tbl->stat.add_ipq_num,
			tbl->stat.del_ipq_num,
			tbl->stat.fail_no_ipq,
			tbl->stat.fail_no_ipfrag,
			tbl->stat.e_firstfrag_num,
			tbl->stat.e_lastfrag_num,
			tbl->stat.e_length_num,
			tbl->stat.e_overlapfrag_num,
			tbl->stat.e_smallfrag_num,
			tbl->stat.time_out_num,
			tbl->stat.dropfrag_num,
			tbl->stat.transfer_num,
			tbl->stat.do_packet_num,
			tbl->stat.reass_ok_num,
			tbl->max_entries,tbl->use_entries); 
			printf("tbl my lcore is %d\n",tbl->lcore);
	}
};

#if 0
static void print_tuple5(struct rte_mbuf * m)
{
	if ( m == NULL ) {
		TRACE_REASS("This packet is null,you don't get its tuple5 information!\n");
	}
	TRACE_REASS("tuple5 of this packet:ip_src=%u,ip_dst=%u,port_src=%d,port_dst=%d,proto=%d\n",
			m->tuple.ipv4.ip_src,
			m->tuple.ipv4.ip_dst,
			m->tuple.ipv4.port_src,
			m->tuple.ipv4.port_dst,
			m->tuple.ipv4.proto);
}
#endif

static void 
backfill_mbuf_tuple5(ip_ipq_t * ipq,
                         struct rte_mbuf * m)
{
	if ( m == NULL )
	{
		struct ip_frag * mfrag;
		for ( mfrag = ipq->frag_list; mfrag; mfrag = mfrag->next )
		{
#if DEBUG==1
			if ( mfrag->m == NULL ) {
				printf("This packet is null,you don't get its tuple5 information!\n");
				return;
			}
#endif
			mfrag->m->tuple.ipv4.ip_src   = ipq->tuple.ipv4.ip_src;
			mfrag->m->tuple.ipv4.ip_dst   = ipq->tuple.ipv4.ip_dst;
			mfrag->m->tuple.ipv4.proto    = ipq->tuple.ipv4.proto;
			mfrag->m->tuple.ipv4.port_src = ipq->tuple.ipv4.port_src;
			mfrag->m->tuple.ipv4.port_dst = ipq->tuple.ipv4.port_dst;
			mfrag->m->tag                 = ipq->mbuf_tag;
		}
	}
	else 
	{
		m->tuple.ipv4.ip_src   = ipq->tuple.ipv4.ip_src;
		m->tuple.ipv4.ip_dst   = ipq->tuple.ipv4.ip_dst;
		m->tuple.ipv4.proto    = ipq->tuple.ipv4.proto;
		m->tuple.ipv4.port_src = ipq->tuple.ipv4.port_src;
		m->tuple.ipv4.port_dst = ipq->tuple.ipv4.port_dst;
		m->tag                 = ipq->mbuf_tag;	
	}
}

static void 
fill_ipq_port_rss(ip_ipq_t * ipq,
					struct rte_mbuf *mbuf){

	struct ipv4_hdr * ipv4;
	struct ipv6_hdr * ipv6;
	struct udp_hdr  * udp_hdr;
	struct tcp_hdr  * tcp_hdr;
	struct ipv4_tuple5 *ipv4tuple=&ipq->tuple.ipv4;
	struct ipv6_tuple5 *ipv6tuple=&ipq->tuple.ipv6;
	//uint64_t ol_flags=mbuf->ol_flags;
	uint16_t *port_src;
	uint16_t *port_dst;
	uint8_t   proto,ipv;

	if(mbuf->eth_type == 0x0800)/*if (ol_flags & (PKT_RX_IPV4_HDR | PKT_RX_IPV4_HDR_EXT))*/ {
		ipv4 = rte_pktmbuf_mtod_network(mbuf,struct ipv4_hdr *) ;
		proto= ipv4->next_proto_id;
		port_src=&ipv4tuple->port_src;
		port_dst=&ipv4tuple->port_dst;
		ipv=4;
	} else if(mbuf->eth_type == 0x86dd)/*if(ol_flags & PKT_RX_IPV6_HDR)*/ {
		ipv6 = rte_pktmbuf_mtod_network(mbuf,struct ipv6_hdr *) ;
		proto = ipv6->proto;
		port_src=&ipv6tuple->port_src;
		port_dst=&ipv6tuple->port_dst;
		ipv=6;
	}else {		
		//mbuf->transport_header=??? //reset to what?no need
		memset(&(mbuf->tuple),0,sizeof(mbuf->tuple));
		ipv   = 0;
		proto = 0;
		port_dst = NULL;
		port_src = NULL;
	}

	switch (proto) {
		case IPPROTO_TCP:
			tcp_hdr = rte_pktmbuf_mtod_transport(mbuf,struct tcp_hdr *) ;
			*port_src=rte_be_to_cpu_16(tcp_hdr->src_port);
			*port_dst=rte_be_to_cpu_16(tcp_hdr->dst_port);
			break;
		case IPPROTO_UDP:
			udp_hdr = rte_pktmbuf_mtod_transport(mbuf,struct udp_hdr *) ;
			*port_src=rte_be_to_cpu_16(udp_hdr->src_port);
			*port_dst=rte_be_to_cpu_16(udp_hdr->dst_port);
			break;
		default:
			break;
	}

	if(mbuf->hash.rss != 0) {
		ipq->mbuf_tag = mbuf->hash.rss;
	}else if(ipv==4)  {
#if 1
		static struct ipv4_tuple5 ipv4tmp;
		ipv4tmp.proto=ipv4tuple->proto;
		if(ipv4tuple->ip_src > ipv4tuple->ip_dst){
			ipv4tmp.ip_src=ipv4tuple->ip_src;
			ipv4tmp.ip_dst=ipv4tuple->ip_dst;
		}else {
			ipv4tmp.ip_dst=ipv4tuple->ip_src;
			ipv4tmp.ip_src=ipv4tuple->ip_dst;
		}
		if(ipv4tuple->port_src > ipv4tuple->port_dst){
			ipv4tmp.port_src=ipv4tuple->port_src;
			ipv4tmp.port_dst=ipv4tuple->port_dst;
		}else{
			ipv4tmp.port_src=ipv4tuple->port_dst;
			ipv4tmp.port_dst=ipv4tuple->port_src;
		}
		ipv4tuple=&ipv4tmp;
#endif
			ipq->mbuf_tag=RTE_JHASH((void *)ipv4tuple,sizeof(struct ipv4_tuple5 ),0);
		}else if(ipv==6)
			ipq->mbuf_tag=RTE_JHASH((void *)ipv6tuple,sizeof(struct ipv6_tuple5 ),0);
		else 
			ipq->mbuf_tag = 0;
#if 0
	TRACE_REASS("eth_type=0x%x,IP dst = %08x, IP src = %08x, port dst = %d, port src = %d, "
		"proto = %d,inport = %d,tag=0x%x\n",mbuf->eth_type, (unsigned)ipv4tuple->ip_dst, (unsigned)ipv4tuple->ip_src,
				ipv4tuple->port_dst, ipv4tuple->port_src, ipv4tuple->proto,mbuf->inport,mbuf->tag);
#endif

}


/* init fragmentation table */
static int 
ipfrag_table_init(uint32_t max_entries, 
	                int      lcoreid,
	                struct PktReassInfo * pktreass)
{
	ip_ipq_t      *ipq;
	ip_ipq_list_t *hline;
	int index = 0;

	struct ip_reass_frag_tbl * tbl = pktreass->tbl_array[lcoreid];
	memset(tbl,0,sizeof(struct ip_reass_frag_tbl));
	
	tbl->lcore       = lcoreid;
	tbl->pktreass    = pktreass;
	tbl->max_entries = max_entries;
	tbl->use_entries = 0;
	
	for ( index = 0; index < IPV4_REASS_HASH_TABLE_SIZE; index++ ) {
		hline = &tbl->ipq_htable[index];
		TAILQ_INIT(hline);
	}

	TAILQ_INIT(&tbl->ipq_tlist);

	for ( index = 0; index < MAX_IPV4_REASS_PACKETS; index++) {
		ipq = &tbl->ipq_pool[index];
		//rte_atomic32_clear(&ipq->used);
		ipq->used = 0;
	}
	return 0;
}

int reassinit(__attribute__((unused))void * __sysinfo)
{
	//get shared memory
	struct system_info * sysinfo = (struct system_info*)__sysinfo;
	
	unsigned lcores = rte_lcore_count();

	if(lcores > MAX_FRAG_TABLE){
		rte_exit(EXIT_FAILURE,"no enough frag tables for all cores!\n");
	}
	
	uint32_t srt_size = sizeof(struct PktReassInfo);
	uint32_t buf_size = sizeof(struct ip_reass_frag_tbl) * lcores;
	struct PktReassInfo * pktreass = rte_zmalloc_socket("SM_REASS",
		               							     srt_size + buf_size,
		                                             RTE_CACHE_LINE_SIZE,
					                                 sysinfo->socket_id);
	/*note: socket id for every core, you can alloc tbl per times*/
	if(pktreass == NULL){
		rte_exit(EXIT_FAILURE,"alloc reass module shared memory fail!\n");
		
	}
	
	pktreass->frag_cycles = (rte_get_tsc_hz() + MS_PER_S - 1) / MS_PER_S * MS_PER_S;
	pktreass->timeout     = pktreass->frag_cycles * TIME_OUT;
	pktreass->lcorenum    = lcores;
	
	pktreass->frag_table_buffer = (struct ip_reass_frag_tbl *)(pktreass + 1);

	uint16_t coreid = 0;
	uint16_t tbl_id = 0;
	while( coreid < RTE_MAX_LCORE && tbl_id < lcores ){
		if(rte_lcore_is_enabled(coreid)){
			pktreass->tbl_array[coreid] = &pktreass->frag_table_buffer[tbl_id];
			ipfrag_table_init(MAX_IPV4_REASS_PACKETS,coreid,pktreass);
			tbl_id++;
		}
		coreid++;
	}
	prf = pktreass;
	sysinfo->pktreass = pktreass;
	return 0;
}


int reassexit(__attribute__((unused))void * __sysinfo)
{
	//get shared memory
	struct system_info * sysinfo = (struct system_info*)__sysinfo;
#if 0
	TRACE_REASS("statistics of reassembly!\n");
	print_reass();
#endif
	if(sysinfo->pktreass != NULL){
		rte_free(sysinfo->pktreass);
		sysinfo->pktreass = NULL;
		prf = NULL;
	}
	TRACE_REASS("reassembly exit,end!\n");
	return 0;
}

static inline void 
clear_ipq(struct ip_reass_frag_tbl * tbl,ip_ipq_t *ipq)
{
	if (ipq->used != 0){
		IP_REASS_STAT_UPDATE(&tbl->stat,del_ipq_num,1);
		//rte_atomic32_clear(&ipq->used);
		ipq->used = 0;
		ipq->id   = 0;
		ipq->tuple.ipv4.proto = 0;
		tbl->use_entries--;
	}
}

static int 
deal_reass_exception(struct ip_reass_frag_tbl * tbl,
						  ip_ipq_t *ipq)
{
	struct ip_frag *mcurr=NULL;
	
	for (mcurr = ipq->frag_list; mcurr; mcurr = mcurr->next) {
		reass_drop_pkt(tbl,mcurr);
	}
	ipq->frag_list = NULL;
	clear_ipq(tbl,ipq);
	return 0;
}

static inline void 
unlink_ipv4_ipq(struct ip_reass_frag_tbl * tbl,
                   ip_ipq_t *ipq)
{
	//remove from hash table
	TAILQ_REMOVE(&tbl->ipq_htable[ipq->hash], ipq, hchain);
	//remove from time chain
	TAILQ_REMOVE(&tbl->ipq_tlist, ipq, tchain);
}

static inline ip_ipq_t * 
link_ipv4_ipq (struct ip_reass_frag_tbl * tbl,
                 ip_ipq_t *ipq)
{

	TAILQ_INSERT_HEAD(&tbl->ipq_htable[ipq->hash], ipq, hchain);
	
	TAILQ_INSERT_TAIL(&tbl->ipq_tlist, ipq, tchain);

	return ipq;
}

static void deal_timelist_ip4frag(struct ip_reass_frag_tbl * tbl)
{
	
	ip_ipq_t * ipq;
	uint64_t   curtime = rte_get_tsc_cycles();
	
	ipq = TAILQ_FIRST(&tbl->ipq_tlist);
	if ((curtime - ipq->start_cycles) > tbl->pktreass->timeout) {
		TRACE_REASS("%s():curtime=%lu,%p timeout\n", __FUNCTION__,curtime,ipq);
		IP_REASS_STAT_UPDATE(&tbl->stat,time_out_num,1);
		unlink_ipv4_ipq(tbl,ipq);
		deal_reass_exception(tbl,ipq);
	}
#if 0
	unsigned   i;
	for ( i = 0; i < MAX_IPV4_REASS_PACKETS; i++) {
		if (TAILQ_EMPTY(&tbl->ipq_tlist)){
			break;
		}
		ipq = TAILQ_FIRST(&tbl->ipq_tlist);
		if ( (curtime - ipq->start_cycles) > tbl->pktreass->timeout) {
			IP_REASS_STAT_UPDATE(&tbl->stat,time_out_num,1);
			unlink_ipv4_ipq(tbl,ipq);
			deal_reass_exception(tbl,ipq);

		} else{
			break;
		}
	}
#endif
}

static inline void 
ipq_init(const struct ipv4_hdr * ip,
         ip_ipq_t *ipq,
         uint32_t hash)
{
	ipq->tuple.ipv4.proto  = ip->next_proto_id;
	ipq->tuple.ipv4.ip_src = rte_be_to_cpu_32(ip->src_addr);
	ipq->tuple.ipv4.ip_dst = rte_be_to_cpu_32(ip->dst_addr);
	
	ipq->id                = ip->packet_id;
	ipq->head_complete     = 0;
	ipq->head_first_come   = 0;
	ipq->recvd_len         = 0;
	ipq->frag_count        = 0;
	ipq->hash              = hash;
	ipq->start_cycles      = rte_get_tsc_cycles();
	ipq->last_cycles       = ipq->start_cycles;
	ipq->exception         = FALSE;
	
	ipq->index             = 0;
	ipq->frag_list         = NULL;
	
	rte_atomic32_init(&ipq->first_recvd);
	rte_atomic32_init(&ipq->last_recvd);
	memset(ipq->frag_pool,0,sizeof(ipq->frag_pool));

}

static inline ip_ipq_t * 
alloc_ipq_entry(struct ip_reass_frag_tbl * tbl)
{
	static unsigned index = 0;
	unsigned i;
	ip_ipq_t * ipq = NULL;

	for  ( i = 0; i < MAX_IPV4_REASS_PACKETS; i++) {
		ipq = &tbl->ipq_pool[index];
		index = (index + 1) % MAX_IPV4_REASS_PACKETS;
		if (ipq->used == 0) {
			//rte_atomic32_test_and_set(&ipq->used)
			ipq->used = 1;
			tbl->use_entries++;
			return ipq;
		}
	}
	return NULL;
}

static inline int 
compare_ipq(ip_ipq_t * ipq,
                const struct ipv4_hdr * ip)
{
#if DEBUG==1
	if ( ipq == NULL || ip == NULL ) {
		printf("%s:param is NULL!\n")
		return -1;
	}
#endif
	if ((ipq->tuple.ipv4.ip_src == rte_be_to_cpu_32(ip->src_addr)) &&
		(ipq->tuple.ipv4.ip_dst == rte_be_to_cpu_32(ip->dst_addr)) &&
		(ipq->tuple.ipv4.proto  == ip->next_proto_id) &&
		(ipq->id                == ip->packet_id))
	{
		return 0;
	}
	return -1;
}
	
static inline ip_ipq_t *
find_ipq(struct ip_reass_frag_tbl * tbl, 
	       const struct ipv4_hdr *ip,
	       uint32_t hash)
{
	ip_ipq_t * ipq;
	TAILQ_FOREACH(ipq, &tbl->ipq_htable[hash], hchain) {
		if ( compare_ipq(ipq,ip) == 0 ){
			return ipq;
		}
	}
	return NULL;
}

static inline uint32_t 
get_ipq_hash(const struct ipv4_hdr *ip)
{
	struct ip_frag_hash_key key;
	key.src_addr      = ip->src_addr;
	key.dst_addr      = ip->dst_addr;
	key.packet_id     = ip->packet_id;
	key.next_proto_id = ip->next_proto_id;

	uint32_t hash;
	hash = RTE_JHASH((void *)&key,sizeof(struct ip_frag_hash_key),0);
	return ( hash % IPV4_REASS_HASH_TABLE_SIZE );
}

static ip_ipq_t * 
get_ipq(struct ip_reass_frag_tbl * tbl,
          const struct ipv4_hdr *ip)
{
	uint32_t hash;
	ip_ipq_t *ipq;

	hash = get_ipq_hash(ip);

	ipq = find_ipq(tbl,ip,hash);

	if ( ipq != NULL ){
		IP_REASS_STAT_UPDATE(&tbl->stat,find_ipq_num,1); 
		goto end;
	}

	if (tbl->use_entries == tbl->max_entries){
		deal_timelist_ip4frag(tbl);
	}
	
	ipq = alloc_ipq_entry(tbl);
	if ( ipq == NULL) {
		TRACE_REASS("don't have enough space for allocating queue entry\n");
		IP_REASS_STAT_UPDATE(&tbl->stat,fail_no_ipq,1);
		goto end;
	}
	IP_REASS_STAT_UPDATE(&tbl->stat,add_ipq_num,1);
	/*init ipq*/
	ipq_init(ip,ipq,hash);
	link_ipv4_ipq(tbl,ipq);
 end: 
	return ipq;
}

static struct ip_frag * 
alloc_ip_frag_entry(ip_ipq_t * ipq)
{
	unsigned i;
	struct ip_frag * ipfrag;

	for  ( i = 0; i < MAX_IP_FRAGMENT_NUM; i++) {
		ipfrag = &ipq->frag_pool[ipq->index];
		ipq->index = (ipq->index + 1) % MAX_IP_FRAGMENT_NUM;
		if (ipfrag->used == 0) {
			ipfrag->used = 1;
			//rte_atomic32_test_and_set(&ipfrag->used)
			return ipfrag;
		}
	}
	return NULL;
}

static void 
do_small_frag(ip_ipq_t * ipq,
	              struct ip_frag ** ipfrag)
{
	uint16_t data_len,copy_len;
	struct ip_frag * next;
	struct ip_frag * head = ipq->frag_list;
	struct ipv4_hdr * ip;
	
	if ( !ipq->head_complete &&     //head not complete
		  ipq->frag_count >=2 &&    //two fragments at least
		  head->start_offset == 0){ //first fragment have come
		  
		next = head->next;
		data_len = head->end_offset - head->start_offset;
			
		if (data_len <= IP_FRAG_MIN_SIZE && head->end_offset == next->start_offset){

			copy_len = next->end_offset - next->start_offset;
#if 0
			rte_pktmbuf_prepend(next->m,data_len);
			rte_memcpy((void *)((char *)(next->m->buf_addr) + next->m->data_off),
						rte_pktmbuf_mtod_transport(head->m->data_off,void *),
						data_len+head->m->transport_header-head->m->data_off);
#endif

			rte_pktmbuf_append(head->m,copy_len);
			rte_memcpy((void *)((char *)(head->m->buf_addr) + head->m->transport_header + data_len),
					    rte_pktmbuf_mtod_transport(next->m,void *),
						copy_len);
			
			ip = rte_pktmbuf_mtod_network(head->m,struct ipv4_hdr *);
			
			ip->total_length = rte_cpu_to_be_16(data_len+copy_len+sizeof(struct ipv4_hdr));
			head->end_offset += copy_len;
			ipq->head_first_come = TRUE;
			ipq->head_complete   = TRUE;
			head->next = next->next;
			ipq->frag_count--;
			if ((*ipfrag)->start_offset != 0){
				*ipfrag = head;
			}
			rte_pktmbuf_free(next->m);
			//rte_atomic32_clear(&next->used);
			next->used = 0;
		}
	}
}

/*insert current frag to ipq*/
static int do_insert_ipq(struct ip_reass_frag_tbl * tbl,
	                        ip_ipq_t                 * ipq,
	                        struct ip_frag           * mcurr,
	                        struct ipv4_hdr          * ip)
{
	struct ip_frag * mprev;
	struct ip_frag * mfrag;
	int      ret = 0;

#ifdef IP_FRAGMENT_OVERLAP_DEAL
	uint16_t ofset	  = 0;
	uint16_t data_len = 0;
#endif

	/*find pos from frag_list
		            s|-----|e
	  s|-----|e	
	*/
	mprev = NULL;
	for (mfrag = ipq->frag_list; mfrag; mfrag = mfrag->next) {
		if ( mcurr->start_offset <= mfrag->start_offset ){
			break;
		}
		mprev = mfrag;
	}
	
	if (mfrag) {
		
		TRACE_REASS("found a next fragment %u-%u\n",(unsigned)mfrag->start_offset,(unsigned)mfrag->end_offset);
		/*
			first	 s|-----|e
		curr	  s|-----|e
		
		*/
		if (mcurr->end_offset > mfrag->start_offset) {

			TRACE_REASS("tail overlap exception\n");
			IP_REASS_STAT_UPDATE(&tbl->stat,e_overlapfrag_num,1);
				
#ifdef IP_REASS_IN_SERVER
				
	#ifdef IP_FRAGMENT_OVERLAP_DEAL
	
			ofset = mcurr->end_offset - mfrag->start_offset;
			mcurr->end_offset -= ofset;
			if ( mcurr->start_offset <= mcurr->end_offset ){
				reass_drop_pkt(tbl,mcurr);
				return 0;
			}
			if(rte_pktmbuf_trim(mcurr->m,ofset) == -1){
				reass_drop_pkt(tbl,mcurr);
				return -1;
			}
			data_len = mcurr->end_offset - mcurr->start_offset;
			ip->total_length = rte_cpu_to_be_16( data_len + sizeof(struct ipv4_hdr));	
	#else
			reass_drop_pkt(tbl,mcurr);
			return PKT_DROP;
	#endif
	
#else
	#ifdef IP_FRAGMENT_OVERLAP_DEAL
			ofset = mcurr->end_offset - mfrag->start_offset;
			mcurr->end_offset -= ofset;
			data_len = mcurr->end_offset - mcurr->start_offset;
	#else 
			reass_drop_pkt(tbl,mcurr);
			return PKT_DROP;
	#endif
#endif
	
		}
	}

	if (mprev) {
		/*
			                         mfrag  s|-----|e
			    mprev s|-----|e
			     curr    s|-----|e
		*/	
		TRACE_REASS("found a prev fragment %u-%u\n",(unsigned)mprev->start_offset,(unsigned)mprev->end_offset);
	
		if (mcurr->start_offset < mprev->end_offset) {
				
			TRACE_REASS("head overlap exception\n");
			IP_REASS_STAT_UPDATE(&tbl->stat,e_overlapfrag_num,1);
	
#ifdef IP_REASS_IN_SERVER
	
	#ifdef IP_FRAGMENT_OVERLAP_DEAL

			ofset = mprev->end_offset - mcurr->start_offset;
			mcurr->start_offset += ofset;

			if ( mcurr->start_offset <= mcurr->end_offset ){
				reass_drop_pkt(tbl,mcurr);
				return 0;
			}
			memmove(rte_pktmbuf_mtod(mcurr->m,char *)+ofset,
					rte_pktmbuf_mtod(mcurr->m,char *),
					sizeof(struct ether_hdr)+ sizeof(struct ipv4_hdr ));
			rte_pktmbuf_adj(mcurr->m,ofset);
			data_len = mcurr->end_offset - mcurr->start_offset;
			ip->total_length = rte_cpu_to_be_16(data_len+sizeof(struct ipv4_hdr));			
	#else
			reass_drop_pkt(tbl,mcurr);
			return PKT_DROP;
	#endif
	
#else
	#ifdef IP_FRAGMENT_OVERLAP_DEAL
			ofset = mprev->end_offset - mcurr->start_offset;
			mcurr->start_offset += ofset;
			data_len = mcurr->end_offset - mcurr->start_offset;
	#else
			reass_drop_pkt(tbl,mcurr);
			return PKT_DROP;
	#endif

#endif
		}
		mcurr->next = mfrag;
		mprev->next = mcurr;
	} 
	else {
		TRACE_REASS("inserting fragment at head of queue %p\n", ipq);
		mcurr->next = mfrag;
		ipq->frag_list = mcurr;
	}
	ipq->frag_count++;
	ipq->recvd_len += mcurr->end_offset - mcurr->start_offset;

	return ret;

}

#ifdef IP_REASS_IN_SERVER
static int reass_ipv4_fragment(struct rte_mbuf **pm,
	                                 ip_ipq_t *ipq,
	                                 struct ip_reass_frag_tbl * tbl)
{
	struct ip_frag *mreass, *mcurr, *mnext;
	struct rte_mbuf * p;
	struct ipv4_hdr * ip;
	int error = 0;
	
	mreass = ipq->frag_list;
	ipq->frag_list = NULL;
	
	for (mcurr = mreass->next; mcurr; mcurr= mnext) {
		mnext = mcurr->next;
		if (rte_pktmbuf_adj(mcurr->m, mcurr->m->transport_header - mcurr->m->mac_header) == NULL) {
			error = 1;
			break;
		}
		p = rte_pktmbuf_lastseg(mreass->m);
		p->next = mcurr->m;
		mreass->m->nb_segs = (uint8_t)(mreass->m->nb_segs + mcurr->m->nb_segs);
		mreass->m->pkt_len += mcurr->m->pkt_len;
		mcurr->m->pkt_len = mcurr->m->data_len;
		mcurr->m->nb_segs = 1;
	}
	if (unlikely(error != 0)) {
		TRACE_REASS("Error during reass\n");
		
		for (; mcurr; mcurr = mnext) {
			mnext = mcurr->next;
			reass_drop_pkt(tbl,mcurr);
		}
		reass_drop_pkt(tbl,mreass);
		return PKT_DROP;
	}

	ip = rte_pktmbuf_mtod_network(mreass->m, struct ipv4_hdr*);
	ip->total_length = rte_cpu_to_be_16(ipq->total_len + sizeof(struct ipv4_hdr));
	ip->fragment_offset = (uint16_t)(ip->fragment_offset & rte_cpu_to_be_16(IPV4_HDR_DF_FLAG));
	ip->hdr_checksum = rte_ipv4_cksum(ip);

	TRACE_REASS("ip->total_length=%x,ip->fragment_offset=%x,ip->hdr_checksum=%x\n",ip->total_length,ip->fragment_offset,ip->hdr_checksum);
	mreass->m->ol_flags |= PKT_RX_IP_REASS;
	pm[0] = mreass->m;
	
	return 1;
}

#endif

static int 
check_timeout(struct ip_reass_frag_tbl * tbl,
                  ip_ipq_t *ipq,
                  struct ip_frag * ipfrag)
{
	/*check timeout*/
	uint64_t curtime = rte_get_tsc_cycles();
	
	if ((curtime - ipq->start_cycles) > tbl->pktreass->timeout) {
		TRACE_REASS("time out!!!!!!\n");
		IP_REASS_STAT_UPDATE(&tbl->stat,time_out_num,1);
		reass_drop_pkt(tbl,ipfrag);
		unlink_ipv4_ipq(tbl,ipq);
		deal_reass_exception(tbl,ipq);
		return TRUE;
	}
	else return FALSE;
}

int pkt_reass_enable(void)
{
	return prf->enable;
}

int ipv4_pkt_is_fragmented(const struct ipv4_hdr * hdr) 
{
	uint16_t flag_offset, ip_flag, ip_ofs;

	flag_offset = rte_be_to_cpu_16(hdr->fragment_offset);
	ip_ofs = (uint16_t)(flag_offset & IPV4_HDR_OFFSET_MASK);
	ip_flag = (uint16_t)(flag_offset & IPV4_HDR_MF_FLAG);

	return ip_flag != 0 || ip_ofs  != 0;
}


/*
 * @return
 *  >0:return n packets;  0:packet is kept; -1: packet is dropped
 */
int ipv4_reassemble(struct rte_mbuf *  mbuf,
	                     struct rte_mbuf ** out_pkts,
	                     uint16_t           nb_pkts)
{
	struct ip_frag  * mcurr;
	struct ipv4_hdr * ip;
	ip_ipq_t        * ipq;
	uint64_t          data_len;
	uint16_t          fragment_offset, ip_offset, ip_mf;
	int               ret = 0;
	
	struct ip_reass_frag_tbl * tbl = prf->tbl_array[rte_lcore_id()];
	
	//do packets num
	IP_REASS_STAT_UPDATE(&tbl->stat,do_packet_num,1);
	
	//look up ipq queue
	ip = rte_pktmbuf_mtod_network(mbuf,struct ipv4_hdr *);
	if ( tbl->last != NULL && compare_ipq(tbl->last,ip) == 0 ){
		ipq = tbl->last;
		IP_REASS_STAT_UPDATE(&tbl->stat,reuse_ipq_num,1);
	}
	else {
		ipq = get_ipq(tbl,ip);
		if ( ipq == NULL ) {
			IP_REASS_STAT_UPDATE(&tbl->stat,dropfrag_num,1);
			rte_pktmbuf_free(mbuf);
			return PKT_DROP;
		}
		tbl->last = ipq;
	}

#ifndef IP_REASS_EXCEPTION_WAY
	if (unlikely(ipq->exception == TRUE))
	{
		uint64_t curtime = rte_get_tsc_cycles();
		if ((curtime - ipq->start_cycles) > tbl->pktreass->timeout) {
			unlink_ipv4_ipq(tbl,ipq);
			clear_ipq(tbl,ipq);
		}
		rte_pktmbuf_free(mbuf);
		IP_REASS_STAT_UPDATE(&tbl->stat,dropfrag_num,1);
		return PKT_DROP;
	}
#endif

	//alloc ip_frag entry
	if ((mcurr = alloc_ip_frag_entry(ipq)) == NULL){
		IP_REASS_STAT_UPDATE(&tbl->stat,fail_no_ipfrag,1);
		IP_REASS_STAT_UPDATE(&tbl->stat,dropfrag_num,1);
		rte_pktmbuf_free(mbuf);
		return PKT_DROP;
	}

	data_len        = rte_be_to_cpu_16(ip->total_length) - sizeof(struct ipv4_hdr); 
	fragment_offset = rte_be_to_cpu_16(ip->fragment_offset);
	ip_offset       = (uint16_t)(fragment_offset & IPV4_HDR_OFFSET_MASK);
	ip_mf           = (uint16_t)(fragment_offset & IPV4_HDR_MF_FLAG);

	//assignment for current ip_frag
	mcurr->m            = mbuf;
	mcurr->start_offset = ip_offset * IPV4_HDR_OFFSET_UNITS;
	mcurr->end_offset   = mcurr->start_offset + data_len;

//print basic information of fragment packet
#if DEBUG==1 	
	TRACE_REASS("data_len=%d,pkt_len=%d,nb_segs=%d,buf_len=%d,data_off=%d\n",
		    mcurr->m->data_len,mcurr->m->pkt_len,mcurr->m->nb_segs,mcurr->m->buf_len,mcurr->m->data_off);

	TRACE_REASS("data_len=%lu,start_offset=%u,end_offset=%u,fragment_offset=%u,ip_offset=%u,ip_mf=%u\n",
		    data_len,
		   (unsigned)mcurr->start_offset, 
		   (unsigned)mcurr->end_offset,
		   (unsigned)fragment_offset,
		   (unsigned)ip_offset,
		   (unsigned)ip_mf);
#endif

	if (check_timeout(tbl,ipq,mcurr)) {
		goto timeout;
	}
	
	/* if it is the first fragment */
	if ( ip_offset == 0 ){
		if (rte_atomic32_test_and_set(&ipq->first_recvd)){
			TRACE_REASS("we received first fragment!\n");
			if ( data_len > IP_FRAG_MIN_SIZE ) {
				ipq->head_complete   = TRUE;
				ipq->head_first_come = TRUE;
			}
		}
		else {
			TRACE_REASS("we have already received the first fragment,Exception!\n");
			IP_REASS_STAT_UPDATE(&tbl->stat,e_firstfrag_num,1);
			reass_drop_pkt(tbl,mcurr);
			goto end;
		}
	}
	
	/* if it is the last fragment*/
	if ( ip_mf == 0 ) {
		TRACE_REASS("--------------last fragment---------------\n");
		if (rte_atomic32_test_and_set(&ipq->last_recvd)){
			ipq->total_len      = mcurr->end_offset;
			mcurr->is_last_frag = TRUE;
		} else {
			TRACE_REASS("we have already received the last fragment,Exception!\n");
			IP_REASS_STAT_UPDATE(&tbl->stat,e_lastfrag_num,1);
			reass_drop_pkt(tbl,mcurr);
			goto end;
		}
	} else if (rte_atomic32_read(&ipq->last_recvd)) {
		if ( mcurr->end_offset >= ipq->total_len ) {
			TRACE_REASS("new fragment end_offset is longer than size of the packet,Exception\n");	
			IP_REASS_STAT_UPDATE(&tbl->stat,e_length_num,1);
			reass_drop_pkt(tbl,mcurr);
			goto end;
		}
	}

	/*check size exception*/
	if (unlikely(mcurr->end_offset > (IP_MAXPACKET_SIZE - sizeof(struct ipv4_hdr)))) {
		TRACE_REASS("size exceeds 64K\n");
		IP_REASS_STAT_UPDATE(&tbl->stat,e_length_num,1);
		reass_drop_pkt(tbl,mcurr);
		goto end;
	}
	
	if(PKT_DROP == do_insert_ipq(tbl,ipq,mcurr,ip)){
		goto end;
	}
	
	do_small_frag(ipq,&mcurr);

	TRACE_REASS("-----------total_len=%d,recvd_len=%d---------\n",ipq->total_len,ipq->recvd_len);

	if (ipq->head_first_come && ipq->head_complete){
		fill_ipq_port_rss(ipq,mcurr->m);
		backfill_mbuf_tuple5(ipq,NULL);
	}
	else if ( ipq->head_complete ){
		backfill_mbuf_tuple5(ipq,mcurr->m);
	}

#ifdef IP_REASS_IN_SERVER  //reassemble all fragments to complete packet in server

	if (rte_atomic32_read(&ipq->last_recvd) && (ipq->total_len == ipq->recvd_len)){
		TRACE_REASS("all fragments received in reass mode\n");
		unlink_ipv4_ipq(tbl,ipq);
		ret=reass_ipv4_fragment(out_pkts,ipq,tbl);
		IP_REASS_STAT_UPDATE(&tbl->stat,reass_ok_num,1);
		IP_REASS_STAT_UPDATE(&tbl->stattransfer_num,,1);
		clear_ipq(tbl,ipq);
	}
	
#else
	struct ip_frag * mfrag;
	uint16_t index = 0;
	if (ipq->head_first_come && ipq->head_complete){
		for (mfrag = ipq->frag_list; mfrag; mfrag = mfrag->next) {
#if 1
			if (nb_pkts <= index){
				TRACE_REASS("packets of output buffer is too small\n");
				break;
			}
#endif
			mfrag->m->ol_flags |= PKT_RX_IP_REASS;
			out_pkts[index++] = mfrag->m;
			mfrag->m = NULL;
		}
		ret = index;
		ipq->head_first_come = FALSE;
		IP_REASS_STAT_UPDATE(&tbl->stat,transfer_num,index);
	}
	else if ( ipq->head_complete ){
		mcurr->m->ol_flags |= PKT_RX_IP_REASS;
		out_pkts[0]= mcurr->m;
		mcurr->m = NULL;
		ret = 1;
		IP_REASS_STAT_UPDATE(&tbl->stat,transfer_num,1);
	}

	if (rte_atomic32_read(&ipq->last_recvd) && (ipq->total_len == ipq->recvd_len)){
		TRACE_REASS("all fragments received in not reass mode\n");
		IP_REASS_STAT_UPDATE(&tbl->stat,reass_ok_num,1);
		unlink_ipv4_ipq(tbl,ipq);
		clear_ipq(tbl,ipq);
	}
	
#endif 
	reass_statistics_dump(tbl);
	return ret;
 
end:
	
#ifdef IP_REASS_EXCEPTION_WAY

	unlink_ipv4_ipq(tbl,ipq);
	deal_reass_exception(tbl,ipq);
	
#else 
	ipq->exception = TRUE;
#endif

timeout:
#if DEBUG==1
	reass_statistics_dump(tbl);
#endif
	return ret;
}

MODULE_INIT(reassinit);
MODULE_EXIT(reassexit);
