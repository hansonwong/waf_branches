/*
*ddos module
*move from fastpath network layer to dpdk
*it is better to defense ddos attack earlier
*@mc
*/


#include <dpdk_warp.h>

#include "dpdk_frame.h"
#include "link.h"
#include "hash.h"
#include "memfixed.h"
#include <sys/socket.h>
#include <sys/un.h>
#include <stddef.h>
#include <time.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>
#include "ddos.h"
#include <arpa/inet.h>

#undef htonl
#undef htons
#undef ntohl
#undef ntohs

static struct system_info *sysinfo;
static struct rte_mempool *clone_pool;
static struct portinfo  *ports;
static u_int8_t g_ddos_log_on = 0;

#define DDOS_LOG_FILE "/var/log/ddos/bd_ddos.log"
static FILE *fp = NULL;

#ifndef DDOS_LOG
#define DDOS_LOG(format, args...) \
do{\
	time_t t;\
	char* t_sz = NULL;\
	char buf[128] = {0};\
	static uint64_t last = 0;\
	uint64_t now;\
	\
	time(&t);\
	t_sz = ctime(&t);\
	snprintf(buf, sizeof(buf), "%s", t_sz);\
	buf[strlen(t_sz) - 1] = 0;\
	if(unlikely(!fp)){\
		fp = fopen(DDOS_LOG_FILE, "w+");\
	}\
	now = rte_get_tsc_cycles();\
	if(fp && g_ddos_log_on && (now - last) > DDOS_LOG_RATE){\
		last = now;\
		fprintf(fp, "%s, "format, buf, ##args);\
		fflush(fp);\
	}\
}while(0);
#else
#define DDOS_LOG(format, args...)
#endif

static rte_rwlock_t  lock;
static struct ddos_config_t ddos_config[DDOS_DIR_MAX][DDOS_TYPE_MAX];
static ddos_ts_t ddos_ts_tables[DDOS_DIR_MAX][DDOS_TYPE_MAX];//config
static struct ddos_table ddos_tables[DDOS_DIR_MAX][DDOS_TYPE_MAX];
static struct rte_mempool *ddos_entry_pool = NULL;

static u_int32_t hash_rnd;
static int hash_rnd_initted;

static void get_random_bytes(void *buf, unsigned int nbytes)
{
#ifndef min
#define min(a, b) (((a) < (b)) ? (a) : (b))
#endif

	unsigned int i;
	for (i = 0; i < nbytes; ++i) {
		((char *)buf)[i] = i;
	}
}

#define __jhash_mix(a, b, c) \
{ \
	a -= b; a -= c; a ^= (c>>13); \
	b -= c; b -= a; b ^= (a<<8); \
	c -= a; c -= b; c ^= (b>>13); \
	a -= b; a -= c; a ^= (c>>12);  \
	b -= c; b -= a; b ^= (a<<16); \
	c -= a; c -= b; c ^= (b>>5); \
	a -= b; a -= c; a ^= (c>>3);  \
	b -= c; b -= a; b ^= (a<<10); \
	c -= a; c -= b; c ^= (b>>15); \
}

static inline unsigned int jhash_3words(unsigned int a, unsigned int b, unsigned int c, unsigned int initval)
{
	a += JHASH_GOLDEN_RATIO;
	b += JHASH_GOLDEN_RATIO;
	c += initval;

	__jhash_mix(a, b, c);

	return c;
}

static inline unsigned int jhash_1word(unsigned int a, unsigned int initval)
{
	return jhash_3words(a, 0, 0, initval);
}

static unsigned int recent_entry_hash4(uint32_t addr)
{
	if (!hash_rnd_initted) {
		get_random_bytes(&hash_rnd, sizeof(hash_rnd));
		hash_rnd_initted = 1;
	}

	return jhash_1word(addr, hash_rnd) &
		(IP_LIST_HASH_SIZE - 1);
}


static struct rte_mempool *fp_pmem_pool_create (const char *name,
		unsigned int len,unsigned int cell_size)
{
	struct rte_mempool *pool;
	
	pool = rte_mempool_create(name, len, cell_size, 32, 0, NULL, NULL, NULL, NULL,
		rte_socket_id(), 0);

	return pool;
}


static int fp_pmem_pool_free(struct rte_mempool *pool, void *objp)
{
	if (pool == NULL) {
		return -1;
	}
	rte_mempool_put(pool, objp);
	return 0;
}

static void *fp_pmem_pool_alloc(struct rte_mempool *pool)
{
	void *objp = NULL;
	return (rte_mempool_get(pool, &objp)<0?NULL:objp);
}


static int8_t fp_pmem_pool_destory(void)
{
	unsigned char dir, type;
	int ret;
	struct ddos_table *t = NULL;
	struct ddos_entry *entry = NULL;

	for(dir = 0; dir < DDOS_DIR_MAX; ++dir)
	for(type = 0; type < DDOS_TYPE_MAX; ++type){
		t = &ddos_tables[dir][type];
		DDOS_DEBUG("\n\nt[%u][%u]->entries = %u\n", dir, type, t->entries);
		list_for_each_entry(entry, &t->lru_list, lru_list){
			print_ip(entry->addr);
			DDOS_DEBUG("lru_list  addr = %u, index = %u, nstamps = %u\n", 
				entry->addr, entry->index,entry->nstamps);			
			ret = fp_pmem_pool_free(ddos_entry_pool, entry);
			if (ret == -1) {
				//TRACE_DDOS(FP_LOG_WARNING, "free entry pool failed\n");
				DDOS_DEBUG("free entry pool failed\n");
				return ret;
			}
		}
	}

	return 0;
}

#if DEBUG
static void dump_fp_ip(struct fp_ip *ip)
{

	printf("\n------------------dump_fp_ip------------------\n");
	printf("ip_v = %u\n", ip->ip_v);
	printf("ip_hl = %u\n", ip->ip_hl);
	printf("ip_tos = %u\n", ip->ip_tos);
	printf("ip_len = %u\n", ntohs(ip->ip_len));
	printf("ip_id = %u\n", ntohs(ip->ip_id));
	printf("ip_off = %u\n", ntohs(ip->ip_off));
	printf("ip_ttl = %u\n", ip->ip_ttl);
	printf("ip_p = %u\n", ip->ip_p);
	printf("ip_sum = %u\n", ntohs(ip->ip_sum));
	printf("ntohl(ip->ip_src.s_addr)=0x%x\n", ntohl(ip->ip_src.s_addr));
	print_ip(ntohl(ip->ip_src.s_addr));
	print_ip(ntohl(ip->ip_dst.s_addr));
	printf("\n");
}

static void dump_ipv4_hdr(struct ipv4_hdr *ip)
{
	printf("\n------------------dump_iphdr------------------\n");
	printf("version_ihl = 0x%x, %d,%d\n", ip->version_ihl, (ip->version_ihl >> 4), ip->version_ihl & 0x0f);
	printf("ip_tos = %u\n", ip->type_of_service);
	printf("ip_len = %u\n", ntohs(ip->total_length));
	printf("ip_id = %u\n", ntohs(ip->packet_id));
	printf("ip_off = %u\n", ip->fragment_offset);
	printf("ip_ttl = %u\n", ip->time_to_live);
	printf("ip_p = %u\n", ip->next_proto_id);
	printf("ip_sum = %u\n", ntohs(ip->hdr_checksum));
	print_ip(ntohl(ip->src_addr));
	print_ip(ntohl(ip->dst_addr));
	printf("\n");
}

static void dump_ethhdr(struct ether_hdr *eth_hdr)
{
#define print_mac(mac_ptr) \
	printf("%s:%02x-%02x-%02x-%02x-%02x-%02x\n", #mac_ptr, (mac_ptr)[0], (mac_ptr)[1], (mac_ptr)[2], (mac_ptr)[3], (mac_ptr)[4], (mac_ptr)[5])

	printf("\n------------------dump_ethhdr------------------\n");
	print_mac(eth_hdr->d_addr.addr_bytes);
	print_mac(eth_hdr->s_addr.addr_bytes);
	printf("ether_type = 0x%04x\n", ntohs(eth_hdr->ether_type));
}

static void ddos_entry_print(const struct ddos_table *t)
{
	struct ddos_entry *pos2;
	list_for_each_entry(pos2, &t->lru_list, lru_list)
		printf("lru_list  addr = %u index = %u", pos2->addr, pos2->index);
	printf("\n");

	return ;
}
#endif

static void dump_mempool_info(struct rte_mempool *ddos_entry_pool)
{
	printf("total size = %u,used = %u , can be used = %u \n", 
		ddos_entry_pool->size, 
		ddos_entry_pool->size - rte_mempool_count(ddos_entry_pool),
		rte_mempool_count(ddos_entry_pool));
}

static struct ddos_entry *
ddos_entry_lookup(const struct ddos_table *table, uint32_t addrp)
{
	struct ddos_entry *e;
	unsigned int h;

	h = recent_entry_hash4(addrp);

	list_for_each_entry(e, &table->iphash[h], list){
		if (e->addr == addrp)
			return e;
	}

	return NULL;
}

static void ddos_entry_remove(struct ddos_table *t, struct ddos_entry *e)
{
	int ret;
	list_del(&e->list);
	list_del(&e->lru_list);
	ret = fp_pmem_pool_free(ddos_entry_pool, e);
	if (ret == -1) {
		DDOS_DEBUG("free entry pool failed\n");
	}
	t->entries--;
}

static struct ddos_entry *
ddos_entry_init(struct ddos_table *t, uint32_t addr)
{
	struct ddos_entry *e;

	DDOS_DEBUG("%s,%d, t->entries = %u, addr = %u\n", __FUNCTION__, __LINE__, t->entries, addr);
	if (t->entries >= IP_LIST_TOT) {
		e = list_entry(t->lru_list.next, struct ddos_entry, lru_list);
		ddos_entry_remove(t, e);
	}

	e = fp_pmem_pool_alloc(ddos_entry_pool);
	if (e == NULL) {
		printf("\n\n%s,%d, fp_pmem_pool_alloc failed \n", __FUNCTION__, __LINE__);
		return NULL;
	}
	e->addr 	    = addr;
	e->stamps[0] 	= rte_get_tsc_cycles();
	e->nstamps   	= 1;
	e->index     	= 1;
	list_add_tail(&e->list, &t->iphash[recent_entry_hash4(addr)]);
	list_add_tail(&e->lru_list, &t->lru_list);
	t->entries++;

	DDOS_DEBUG("t->entries = %u\n", t->entries);
	return e;
}

static void ddos_entry_update(struct ddos_table *t, struct ddos_entry *e)
{
	DDOS_DEBUG("e->index= %u\n", e->index);
	e->index %= ip_pkt_list_tot;
	DDOS_DEBUG("e->index= %u\n", e->index);
	e->stamps[e->index++] = rte_get_tsc_cycles();
	if (e->index > e->nstamps)
		e->nstamps = e->index;
	DDOS_DEBUG("e->index = %u, e->nstamps = %u\n", e->index, e->nstamps);
	list_move_tail(&e->lru_list, &t->lru_list);
}


void *ddos_get_config(__attribute__((unused)) void *arg){
	
	struct sockaddr_un server_addr;
	int serv_sock;
	int on;
	struct linger linger;
	socklen_t server_len;

	/* Create socket */
	serv_sock = socket(AF_UNIX, SOCK_STREAM, 0);
	if (serv_sock < 0) {
		perror("cannot open socket");
		return NULL;
	}
	
	/* set reuse addr option, to avoid bind error when re-starting */
	on = 1;

	if (setsockopt(serv_sock, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on)) < 0) {
		perror("setsockopt SO_REUSEADDR");
		goto error;
	}	

	/* immediately send a TCP RST when closing socket */
	linger.l_onoff  = 1;
	linger.l_linger = 0;

	if (setsockopt(serv_sock, SOL_SOCKET, SO_LINGER, &linger, sizeof(linger)) < 0) {
		perror("setsockopt SO_LINGER");
		goto error;
	}

	server_addr.sun_family = AF_UNIX;
	strcpy(server_addr.sun_path, DDOS_SOCK_PATH);
	server_len = strlen(DDOS_SOCK_PATH) + offsetof(struct sockaddr_un, sun_path);

	unlink(DDOS_SOCK_PATH);
	//if (bind(serv_sock, (struct sockaddr *)&su, sizeof(struct sockaddr)) < 0) {
	if (bind(serv_sock, (struct sockaddr *)&server_addr, server_len) < 0) {
		perror("ddos: cannot bind socket");
		goto error;
	}

	if (listen (serv_sock, 1)) {
		perror("listen");
		goto error;
	}

	struct sockaddr_un   remote;
	socklen_t            remote_len = sizeof(remote);
	int                  cli_sock;
	printf("ddos_get_config!\n");
	while(1){
		printf("server waiting...\n");
		
		remote_len = sizeof(remote);
		if ((cli_sock = accept (serv_sock, (struct sockaddr *)&remote, &remote_len)) < 0) {
			printf("accept: %s\n", strerror(errno));
			continue;
		}

		struct ddos_config_t cdd;
		int ret;
		ret = recv (cli_sock, &cdd, sizeof(struct ddos_config_t), 0);
		if (ret != sizeof(struct ddos_config_t))
			continue;

		printf("\ncdd->limit = %u\n", (cdd.limit));
		printf("cdd->state = %u\n", (cdd.state));
		printf("cdd->dir = %u\n", (cdd.dir));
		printf("cdd->type = %u\n", (cdd.type));	

		if(cdd.dir >= DDOS_DIR_MAX || cdd.type >= DDOS_TYPE_MAX)
			continue;

		ddos_config[cdd.dir][cdd.type] = cdd;
		ddos_ts_tables[cdd.dir][cdd.type].limit = cdd.limit;
		ddos_ts_tables[cdd.dir][cdd.type].state = cdd.state;
		g_ddos_log_on = cdd.log;
		
		close(cli_sock);
	}
	
error:
	close(serv_sock);
	//unlink(DDOS_SOCK_PATH);
	return NULL;
}


static inline int ipproto_to_ddostype(struct fp_ip *ip)
{
	uint32_t proto, type;
	struct fp_tcphdr *th = NULL;
	struct fp_udphdr *uh = NULL;

	proto = ip->ip_p;

	switch(proto = ip->ip_p){
	case FP_IPPROTO_TCP:{
		th = (struct fp_tcphdr *)((char *)ip + ip->ip_hl * 4);
		type = (th->syn == 1) ? DDOS_TYPE_SYN_FLOOD : -1;
		break;
	}

	case FP_IPPROTO_UDP:{
		type = DDOS_TYPE_UDP_FLOOD;
		uh = (struct fp_udphdr *)((char *)ip + ip->ip_hl * 4);
		type = (ntohs(uh->dest) == DNSPORT) ? DDOS_TYPE_DNS_FLOOD : DDOS_TYPE_UDP_FLOOD;
		break;
	}

	case FP_IPPROTO_ICMP:{
		type = DDOS_TYPE_ICMP_FLOOD;
		break;
	}

	default:
		type = -1;
	}

	return type;
}

static int __fp_ddos_defense(uint8_t dir, uint8_t type, uint32_t ipaddr, uint32_t len)
{
	uint64_t tm = rte_get_tsc_cycles() - DDOS_SECOND;
	struct ddos_entry *e;
	struct ddos_table *t;
	uint32_t i, hits = 0, hitcount;
	ddos_ts_t *fdd = &ddos_ts_tables[dir][type];

	if (!fdd->state)
		goto L1;

	if (ipaddr == 0) {
		TRACE_DDOS(FP_LOG_WARNING, "spoofed source address (0.0.0.0)\n");
		goto L1;
	}

	rte_rwlock_read_lock(&lock);
	t = &ddos_tables[dir][type];
	rte_rwlock_read_unlock(&lock);
	hitcount = fdd->limit;

	rte_rwlock_read_lock(&lock);
	e = ddos_entry_lookup(t, ipaddr);
	rte_rwlock_read_unlock(&lock);
	if (e == NULL) {//not found
		DDOS_DEBUG("not FOUND!\n");
		rte_rwlock_write_lock(&lock);
		e = ddos_entry_init(t, ipaddr);
		rte_rwlock_write_unlock(&lock);
		if (e == NULL) {
			TRACE_DDOS(FP_LOG_WARNING, "ddos entry init failed\n");
			goto L1;
		}
	}
	
	DDOS_DEBUG("e->nstamps = %u\n", e->nstamps);
	for (i = 0; i < e->nstamps; i++) {
		if (time_after(tm, e->stamps[i]))//if e->stamps[i] < time 
			continue;
		if (++hits >= hitcount) {
			DDOS_DEBUG("++hits >= hitcount\n");
			FPN_STATS_ADD(&fdd->bytes, len);
			return DDOS_PACKET_DROP;
		}
	}
	rte_rwlock_write_lock(&lock);
	ddos_entry_update(t, e);
	rte_rwlock_write_unlock(&lock);
L1:
	return DDOS_PACKET_NONE;
}

static int packet_attack_defense(const struct fp_ip *ip)
{
	uint8_t  proto, ret = DDOS_PACKET_NONE;
	uint8_t  type;
	uint8_t  flag;
	uint32_t icmp_pkt_len = 0;
	uint32_t sip = ntohl(ip->ip_src.s_addr);
	uint32_t dip = ntohl(ip->ip_dst.s_addr);	
	const struct icmphdr   *icmphdr = NULL;
	const struct fp_tcphdr *th      = NULL;
	//struct fp_udphdr *uh	  = NULL;

	proto = ip->ip_p;
	switch(proto){
	case FP_IPPROTO_TCP:{
		th = (const struct fp_tcphdr *)((const char *)ip + (ip->ip_hl << 2));

		//WinNuke ATTACK
		flag = ddos_ts_tables[DDOS_DIR_SRC][DDOS_TYPE_WINNUKE].state;
		if(!flag)
			goto end;
		if(th->urg == 1 && (ntohs(th->dest) == NETBIOS_PORT)){
			ret  = DDOS_PACKET_DROP;
			type = DDOS_TYPE_WINNUKE;
			DDOS_LOG("EVENT=%s SIP=%u.%u.%u.%u DIP=%u.%u.%u.%u THRES=%u\n",
				DDOS_STR[type], IPV4_PARAM(sip), IPV4_PARAM(dip), 0);			
			goto end;
		}

		//LAND ATTACK
		flag = ddos_ts_tables[DDOS_DIR_SRC][DDOS_TYPE_LAND].state;
		if(!flag)
			goto end;		
		if(th->syn == 1 && sip == dip){
			ret  = DDOS_PACKET_DROP;
			type = DDOS_TYPE_LAND;
			DDOS_LOG("EVENT=%s SIP=%u.%u.%u.%u DIP=%u.%u.%u.%u THRES=%u\n",
				DDOS_STR[type], IPV4_PARAM(sip), IPV4_PARAM(dip), 0);			
			goto end;
		}
		break;
	}/* FP_IPPROTO_TCP */

	case FP_IPPROTO_ICMP:{
		icmphdr = (const struct icmphdr *)((const char *)ip + (ip->ip_hl << 2));
		
		//SMURF ATTACK
		flag = ddos_ts_tables[DDOS_DIR_SRC][DDOS_TYPE_SMURF].state;
		if(!flag)
			goto end;		
		if(icmphdr->icmp_type == ICMP_ECHO_REQUEST && 
		   (LO8(dip) == 0XFF || LO16(dip) == 0XFFFF)
		   ){
			ret  = DDOS_PACKET_DROP;
			type = DDOS_TYPE_SMURF;
			DDOS_LOG("EVENT=%s SIP=%u.%u.%u.%u DIP=%u.%u.%u.%u THRES=%u\n",
				DDOS_STR[type], IPV4_PARAM(sip), IPV4_PARAM(dip), 0);			
			goto end;
		}

		//JUMBO ICMP
		flag = ddos_ts_tables[DDOS_DIR_SRC][DDOS_TYPE_JUMBO_ICMP].state;
		if(!flag)
			goto end;
		
		icmp_pkt_len = ntohs(ip->ip_len) - (ip->ip_hl << 2);
		if(icmp_pkt_len > 1480){
			ret  = DDOS_PACKET_DROP;
			type = DDOS_TYPE_JUMBO_ICMP;
			DDOS_LOG("EVENT=%s SIP=%u.%u.%u.%u DIP=%u.%u.%u.%u THRES=%u\n",
				DDOS_STR[type], IPV4_PARAM(sip), IPV4_PARAM(dip), 0);				
			goto end;
		}

		break;
	}/* FP_IPPROTO_ICMP */

	default:
		ret = DDOS_PACKET_NONE;
	}/* switch */	

end:
	return ret;
}

int fp_ddos_defense(const struct rte_mbuf * const m)
{ 
	int type, ret;
	uint32_t len = m_len(m);
	uint32_t sip, dip;
	struct ARP_header *arph    = NULL;
	struct fp_ip      *ip      = rte_pktmbuf_mtod_network(m, struct fp_ip *);
	struct ether_hdr  *eth_hdr = rte_pktmbuf_mtod(m, struct ether_hdr*);

	//ARP FLOOD
	if (ntohs(eth_hdr->ether_type) ==  ETHER_TYPE_ARP ) {
		type = DDOS_TYPE_ARP_FLOOD;
		arph = (struct ARP_header *)((char*)eth_hdr + sizeof(struct ether_hdr));
		sip = ntohl(arph->src_proto_addr);
		dip = ntohl(arph->tgt_proto_addr);	
		goto DO_DDOS;
	}

	if (ntohs(eth_hdr->ether_type) !=  ETHER_TYPE_IPv4 ) {
		DDOS_DEBUG("not ip packet !!!\n");
		goto L1;
	}

	if (ntohs(ip->ip_off) & FP_IP_OFFMASK) {
		DDOS_DEBUG("%s,%d\n", __FUNCTION__, __LINE__);
		TRACE_DDOS(FP_LOG_WARNING, "sanity check failed\n");
		goto L1;
	}   

	//packet attack
	ret = packet_attack_defense(ip);
	if (ret == DDOS_PACKET_DROP)
		return DDOS_PACKET_DROP;	

	type = ipproto_to_ddostype(ip);
	if (type == -1)
		goto L1;

	//syn/udp/dns/icmp flood
	sip = ntohl(ip->ip_src.s_addr);
	dip = ntohl(ip->ip_dst.s_addr);

DO_DDOS:
	ret = __fp_ddos_defense(DDOS_DIR_SRC, type, sip, len);
	if (ret == DDOS_PACKET_DROP){
		DDOS_LOG("EVENT=%s SIP=%u.%u.%u.%u DIP=%u.%u.%u.%u THRES=%u\n",
			DDOS_STR[type], IPV4_PARAM(sip), IPV4_PARAM(dip), ddos_config[DDOS_DIR_SRC][type].limit);
		return DDOS_PACKET_DROP;
	}

	ret = __fp_ddos_defense(DDOS_DIR_DST, type, dip, len);
	if (ret == DDOS_PACKET_DROP){
		DDOS_LOG("EVENT=%s SIP=%u.%u.%u.%u DIP=%u.%u.%u.%u THRES=%u\n",
			DDOS_STR[type], IPV4_PARAM(sip), IPV4_PARAM(dip), ddos_config[DDOS_DIR_DST][type].limit);
		return DDOS_PACKET_DROP;
	}
	
L1:
	return DDOS_PACKET_NONE;
}

static int fp_ddos_defense_init(void)
{
	unsigned int i, j, k;
	struct rte_mempool* mz = NULL;
	const char* pool_name = "ddos_entry_poolxx";

	rte_rwlock_init(&lock);

	//init  ddos_tables
	for (i = 0; i < DDOS_DIR_MAX; i++) {
		for (j = 0; j < DDOS_TYPE_MAX; j++) {
			INIT_LIST_HEAD(&ddos_tables[i][j].lru_list);
			for (k = 0; k < IP_LIST_HASH_SIZE; k++)
				INIT_LIST_HEAD(&ddos_tables[i][j].iphash[k]);
		}
	}

	/*create pool*/
	mz = rte_mempool_lookup(pool_name);
	if(mz == NULL) {
		ddos_entry_pool = fp_pmem_pool_create(pool_name, DDOS_ENTRY_POOL_LEN,
				sizeof(struct ddos_entry) + sizeof(unsigned long) * ip_pkt_list_tot);
		if (ddos_entry_pool == NULL) {
			printf("%s:%d:create %s failed\n", __FUNCTION__, __LINE__, pool_name);
			return -1;
		}
	}
	else {
		printf("%s has been created...\n", pool_name);
		ddos_entry_pool = mz;
	}
	
	return 0;
}

//---------------------------------------------------->

void
ddos_exit(void) {
	int8_t ret;
	ret = unlink(DDOS_SOCK_PATH);
	printf("%s, line=%d\n", __FUNCTION__, __LINE__);fflush(NULL);
	if(ret == -1){
		printf("unlink(DDOS_SOCK_PATH) error: %d,%s!\n", errno, strerror(errno));
	}
	ret = fp_pmem_pool_destory();
	if(ret == -1){
		printf("fp_pmem_pool_destory error!\n");
	}	
}

int8_t
ddos_init(void) {
	int8_t ret = fp_ddos_defense_init();
	if (ret == -1) {
		printf("ddos_defense_init failed\n");
		return -1;
	}

	pthread_t tid;
	ret = pthread_create(&tid, NULL, ddos_get_config, NULL);
	if (ret != 0) {
		printf("pthread_create failed\n");
		return -1;
	}	

	return 0;
}

//MODULE_INIT(ddos_init)
//MODULE_EXIT(ddos_exit)
