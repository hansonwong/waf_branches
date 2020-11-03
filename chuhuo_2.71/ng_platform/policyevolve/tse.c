#include <stdio.h>
#include <errno.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netdb.h>
#include <string.h>
#include <stdlib.h>

#include "tse.h"
#include "util.h"
#include "connt.h"
#include "rwini.h"
#include "log.h"

#define TSE_MARK_MASK 0x00000fff

#define MAX_COMMON_PROTO_TYPE 256
static uint16_t commonproto[MAX_COMMON_PROTO_TYPE];

#define MAX_COMMON_PORT_TYPE  8192
static uint8_t commonport[MAX_COMMON_PORT_TYPE];

#define TRACE_PACKET(level, fmt, args...) do {              \
	TSE_LOG(TSE_LOG_##level, PACKET, fmt "\n", ## args);     \
} while(0)

#define TRACE_EXCE(level, fmt, args...) do {              \
	TSE_LOG(TSE_LOG_##level, EXCE, fmt "\n", ## args);     \
} while(0)

int TseCommPortProto()
{
	char protostr[100];
	int cnt = 0;
	int value;
	int index;
	for (index = 0; index < MAX_COMMON_PROTO_TYPE; index++){
		sprintf(protostr,"proto-%d",index);
		value = iniGetInt("common",protostr,0);
		commonproto[index] = value;
		if(value >= MAX_COMMON_PORT_TYPE || value == 0) {
			continue;
		}
		commonport[value] = index;
		cnt++;
	}
	return cnt;

}

static void SetExceptionStatus(struct TseHashNode *entry,uint32_t flag)
{
	entry->flag |= 	flag;
}

static void UnSetExceptionStatus(struct TseHashNode *entry,uint32_t flag)
{
	entry->flag &= 	(!flag);
}

static int CheckExceptionStatus(struct TseHashNode *entry, uint32_t flag)
{
    return entry->flag & flag ? 1 : 0;
}


static void 
DumpPacketInfo(Packet * p)
{
	if(p == NULL) return;

	TRACE_PACKET(INFO,"hw_protocol=0x%04x,hook=%s,packetid=%u,packetlen=%u",
			     ntohs(p->hw_proto),
			     hook_type2str(p->hook),
			     p->packet_id,p->pkt_len);
	int hlen = p->hw_addrlen;
	int i;
	/*
	printf("hw_src_addr=");
	for (i = 0; i < hlen-1; i++)
		printf("%02x:",p->hw_addr[i]);
	printf("%02x,",p->hw_addr[hlen-1]);
	*/
	TRACE_PACKET(INFO,"indev=%u,outdev=%u,physindev=%u,physoutdev=%u",
		    p->indev,p->outdev,p->physindev,p->physoutdev);
	
	TRACE_PACKET(INFO,"src_addr:%u.%u.%u.%u,dst_addr:%u.%u.%u.%u",
			IPQUAD(p->pt5.ip_src),IPQUAD(p->pt5.ip_dst));
	TRACE_PACKET(INFO,",src_port:%u,dst_port:%u,%s,mark:%u,hash:%u",
			 p->pt5.port_src,p->pt5.port_dst,
			 getprotobynumber(p->pt5.proto)->p_name,p->mark,p->hash);
}

/**get from jhash of dpdk*/
#define __tse_hash_mix(a, b, c) do { \
	a -= b; a -= c; a ^= (c>>13); \
	b -= c; b -= a; b ^= (a<<8); \
	c -= a; c -= b; c ^= (b>>13); \
	a -= b; a -= c; a ^= (c>>12); \
	b -= c; b -= a; b ^= (a<<16); \
	c -= a; c -= b; c ^= (b>>5); \
	a -= b; a -= c; a ^= (c>>3); \
	b -= c; b -= a; b ^= (a<<10); \
	c -= a; c -= b; c ^= (b>>15); \
} while (0)

/** The golden ratio: an arbitrary value. */
#define TSE_JHASH_GOLDEN_RATIO      0x9e3779b9

static uint32_t
GetHashValue(const void *key, uint32_t length, uint32_t initval)
{
	uint32_t a, b, c, len;
	const uint8_t *k = (const uint8_t *)key;
	const uint32_t *k32 = (const uint32_t *)key;

	len = length;
	a = b = TSE_JHASH_GOLDEN_RATIO;
	c = initval;

	while (len >= 12) {
		a += k32[0];
		b += k32[1];
		c += k32[2];

		__tse_hash_mix(a,b,c);

		k += (3 * sizeof(uint32_t)), k32 += 3;
		len -= (3 * sizeof(uint32_t));
	}

	c += length;
	switch (len) {
		case 11: c += ((uint32_t)k[10] << 24);
		case 10: c += ((uint32_t)k[9] << 16);
		case 9 : c += ((uint32_t)k[8] << 8);
		case 8 : b += ((uint32_t)k[7] << 24);
		case 7 : b += ((uint32_t)k[6] << 16);
		case 6 : b += ((uint32_t)k[5] << 8);
		case 5 : b += k[4];
		case 4 : a += ((uint32_t)k[3] << 24);
		case 3 : a += ((uint32_t)k[2] << 16);
		case 2 : a += ((uint32_t)k[1] << 8);
		case 1 : a += k[0];
		default: break;
	};

	__tse_hash_mix(a,b,c);

	return c;
}

/*
static uint32_t 
GetHashValue(const unsigned char * key,unsigned int klen)
{
	uint32_t hash = 0;
	const unsigned char * __key;
	unsigned int          i;
    for  (__key = key, i = 0; i < klen; i++, __key++) {
		hash = hash * 33 + *__key;  
    }
	return hash;
}
*/
static uint32_t TseHashHash(PacketTuple * p,uint32_t buckets,uint32_t initval)
{
	union HashKey key;
	uint32_t hash;
	key.value.ip_src = p->ip_src;
	key.value.ip_dst = p->ip_dst;
	hash = GetHashValue((const void *)key.buf,sizeof(key.value),initval);
	return hash & (buckets - 1);
}

static struct TseHashNode * 
TseNodeLookup(struct Tacticsevolve * te,PacketTuple *p,uint32_t hash)
{
	struct TseHashNode * entry;
	struct hlist_node  * node;
	hlist_for_each_entry(entry,node,&te->hlist[hash],hchain){
		//if( memcmp(entry->key.buf,key.buf,sizeof(key.value)) == 0 ){
		if(entry->key.value.ip_src == p->ip_src &&
		   entry->key.value.ip_dst == p->ip_dst){
			TRACE_PACKET(DEBUG,"Hash Node src_ip:%u.%u.%u.%u dst_ip:%u.%u.%u.%u",
				                IPQUAD(p->ip_src),
				                IPQUAD(p->ip_dst));
			return entry;
		}
	}
	return NULL;
}


struct TseHashNode * 
GetHashNode(struct Tacticsevolve * te,PacketTuple * p,uint32_t * outhash)
{
	uint32_t hash;
	uint64_t msec;
	struct TseHashNode * entry;
	struct timeval curtime;
	
	hash = TseHashHash(p,te->buckets,0);

	Tse_rwlock_rdlock(&te->hashlock);
	entry = TseNodeLookup(te,p,hash);
	Tse_rwlock_unlock(&te->hashlock);
	
	if(entry != NULL) goto end;

	Tse_rwlock_wrlock(&te->hashlock);
	entry = TseNodeLookup(te,p,hash);
	if(entry != NULL) goto unlock;
	
	entry = (struct TseHashNode *)alloc_mem(te->hashbuff);
	if ( entry == NULL) {
		TRACE_PACKET(WARNING,"alloc entry from shared memory failed");
		goto unlock;
	}

	//memset(entry,0,sizeof(struct TseHashNode));
	//init later
	
	gettimeofday(&curtime,0);
	msec = curtime.tv_sec * 1000 + curtime.tv_usec / 1000;
	entry->ct.time_start      = msec;
	entry->traffic.time_start = msec;
	entry->proto.time_start   = msec;
	entry->ct.isinlist        = 0;
	entry->traffic.isinlist   = 0;
	entry->proto.isinlist     = 0;

	
	entry->key.value.ip_src   = p->ip_src;
	entry->key.value.ip_dst   = p->ip_dst;
	hlist_add_head(&entry->hchain,&te->hlist[hash & (te->buckets - 1)]);
	TRACE_PACKET(DEBUG,"Add entry src_ip:%u.%u.%u.%u dst_ip:%u.%u.%u.%u",
		                IPQUAD(p->ip_src),
				        IPQUAD(p->ip_dst));
	
unlock:
	Tse_rwlock_unlock(&te->hashlock);
end:
	TRACE_PACKET(INFO,"%s(): return entry %p",__func__,entry);
	*outhash = hash;
	return entry;
}

#define NOT_COM_PROTO_PORT_CANTPASS 0

static int TseProtoAnalyse(struct Tacticsevolve *te,PacketTuple * p,uint32_t pmark)
{
	int flag;
	uint32_t protomark = pmark & TSE_MARK_MASK;
	/*common protocol but not common port*/
	uint32_t proto = protomark < MAX_COMMON_PROTO_TYPE ? protomark : 0;
	if(commonproto[proto] != p->port_src && commonproto[proto] != p->port_dst){
		/*exception*/
		if(commonproto[proto])
			return 1;
		flag = NOT_COM_PROTO_PORT_CANTPASS;
	}
	else flag = 0;
	
	/*common port but not common protocol*/
	if(p->port_src < MAX_COMMON_PORT_TYPE && commonport[p->port_src] != proto){
		if(commonport[p->port_src])
			return 1;
		flag = NOT_COM_PROTO_PORT_CANTPASS;
	}
	else flag = 0;
	
	if(p->port_dst < MAX_COMMON_PORT_TYPE && commonport[p->port_dst] != proto){
		if(commonport[p->port_dst])
			return 1;
		flag = NOT_COM_PROTO_PORT_CANTPASS;
	}
	else flag = 0;
	
	return flag;
}


int TsePortCheck(struct Tacticsevolve * te,struct TseHashNode *entry,Packet  * p)
{
	if(!te->enable[TSE_PORT]) return ACCEPT_CMD;
	if((te->portflag & SRC_PORT) && BITMAP_TEST(te->porttable,p->pt5.port_src)){
		return ACCEPT_CMD;
	}
	else if((te->portflag & DST_PORT) && BITMAP_TEST(te->porttable,p->pt5.port_dst)){
		return ACCEPT_CMD;
	}	
	else if((te->portflag & ALL_PORT) &&
	   BITMAP_TEST(te->porttable,p->pt5.port_src) && 
	   BITMAP_TEST(te->porttable,p->pt5.port_dst)){
	   return ACCEPT_CMD;
	}
	Tse_rwlock_wrlock(&te->listlock[TSE_PORT]);
	entry->porttraffic += p->pkt_len;
	if(entry->porttraffic < te->limitbytes){
		Tse_rwlock_unlock(&te->listlock[TSE_PORT]);
		return ACCEPT_CMD;
	}
	Tse_rwlock_unlock(&te->listlock[TSE_PORT]);
	TRACE_EXCE(NOTICE,"src ip:%u.%u.%u.%u,dst ip:%u.%u.%u.%u port traffic:%u",
		         IPQUAD(p->pt5.ip_src),
		         IPQUAD(p->pt5.ip_dst),
		         entry->porttraffic);
	if(CheckExceptionStatus(entry,TSE_PORT_EXCEPTION)) return DROP_CMD;
	//if port is exception,insert it to tail of list
	entry->type = TSE_PORT;
	Tse_rwlock_wrlock(&te->elock);
	TAILQ_INSERT_TAIL(&te->elist, entry, echain);
	Tse_rwlock_unlock(&te->elock);
	SetExceptionStatus(entry,TSE_PORT_EXCEPTION);
	TRACE_EXCE(NOTICE,"packet port exception src ip:%u.%u.%u.%u,dst ip:%u.%u.%u.%u src port:%d dst port:%d",
		         IPQUAD(p->pt5.ip_src),
		         IPQUAD(p->pt5.ip_dst),
		         p->pt5.port_src,
		         p->pt5.port_dst);
	return DROP_CMD;
}

int TseTrafficStat(struct Tacticsevolve *te,struct TseHashNode *entry,Packet *p)
{
	uint64_t msec;
	struct timeval curtime;
	struct TeRuntime * rt;
	struct TeParam   * tp;

	if(!te->enable[TSE_TRAFFIC]) return ACCEPT_CMD;

	rt = &entry->traffic;
	tp = &te->traffic;
	gettimeofday(&curtime,0);
	msec = curtime.tv_sec * 1000 + curtime.tv_usec / 1000;
	
	Tse_rwlock_wrlock(&te->listlock[TSE_TRAFFIC]);
	
	rt->total_per_times += p->pkt_len;
	rt->total_all_times += p->pkt_len;
	
	if(rt->total_per_times < tp->threshold) {
		if(rt->isinlist == 0){
			TAILQ_INSERT_TAIL(&te->lrulist[TSE_TRAFFIC], entry, lruchain[TSE_TRAFFIC]);
			rt->isinlist = 1;
		}
		Tse_rwlock_unlock(&te->listlock[TSE_TRAFFIC]);
		return ACCEPT_CMD;
	}
	
	rt->total_per_times = 0;
	
	if(rt->isinlist){
		TAILQ_REMOVE(&te->lrulist[TSE_TRAFFIC], entry, lruchain[TSE_TRAFFIC]);
	}
	
	rt->time_start = msec;
	rt->over_times++;

	TRACE_EXCE(NOTICE,"src ip:%u.%u.%u.%u,dst ip:%u.%u.%u.%u total:%u per:%u times:%d",
		         IPQUAD(p->pt5.ip_src),
		         IPQUAD(p->pt5.ip_dst),
		         rt->total_all_times,
		         rt->total_per_times,
		         rt->over_times);
	
	if(rt->over_times < tp->max_times){
		TAILQ_INSERT_TAIL(&te->lrulist[TSE_TRAFFIC], entry, lruchain[TSE_TRAFFIC]);
		rt->isinlist = 1;
		Tse_rwlock_unlock(&te->listlock[TSE_TRAFFIC]);
		return ACCEPT_CMD;
	}
	
	Tse_rwlock_unlock(&te->listlock[TSE_TRAFFIC]);
	
	if(CheckExceptionStatus(entry,TSE_TRAFFIC_EXCEPTION)) return DROP_CMD;
	entry->type = TSE_TRAFFIC;
	Tse_rwlock_wrlock(&te->elock);
	TAILQ_INSERT_TAIL(&te->elist, entry, echain);
	Tse_rwlock_unlock(&te->elock);
	SetExceptionStatus(entry,TSE_TRAFFIC_EXCEPTION);
	TRACE_EXCE(NOTICE,"packet traffic exception src ip:%u.%u.%u.%u,dst ip:%u.%u.%u.%u src port:%d dst port:%d",
		         IPQUAD(p->pt5.ip_src),
		         IPQUAD(p->pt5.ip_dst),
		         p->pt5.port_src,
		         p->pt5.port_dst);
	return DROP_CMD;
}


int TseCtStat(struct Tacticsevolve *te,struct TseHashNode *entry,PacketTuple * p)
{
	uint64_t msec;
	struct timeval curtime;
	struct TeRuntime * rt;
	struct TeParam   * tp;
	
	if(!te->enable[TSE_CONNECT]) return ACCEPT_CMD;

	rt = &entry->ct;
	tp = &te->ct;
	gettimeofday(&curtime,0);
	//msec = curtime.tv_sec << 10 - curtime.tv_sec << 4 - curtime.tv_sec << 2
	msec = curtime.tv_sec * 1000 + curtime.tv_usec / 1000;

	Tse_rwlock_wrlock(&te->listlock[TSE_CONNECT]);
	
	rt->total_per_times++;
	rt->total_all_times++;
	
	if(rt->total_per_times < tp->threshold) {
		if(rt->isinlist == 0){
			TAILQ_INSERT_TAIL(&te->lrulist[TSE_CONNECT], entry, lruchain[TSE_CONNECT]);
			rt->isinlist = 1;
		}
		Tse_rwlock_unlock(&te->listlock[TSE_CONNECT]);
		return ACCEPT_CMD;
	}
	
	rt->total_per_times = 0;
	
	if(rt->isinlist){
		TAILQ_REMOVE(&te->lrulist[TSE_CONNECT], entry, lruchain[TSE_CONNECT]);
	}
	
	rt->time_start = msec;
	rt->over_times++;

	TRACE_EXCE(NOTICE,"src ip:%u.%u.%u.%u,dst ip:%u.%u.%u.%u total:%u per:%u times:%d",
		         IPQUAD(p->ip_src),
		         IPQUAD(p->ip_dst),
		         rt->total_all_times,
		         rt->total_per_times,
		         rt->over_times);

	if(rt->over_times < tp->max_times){
		TAILQ_INSERT_TAIL(&te->lrulist[TSE_CONNECT], entry, lruchain[TSE_CONNECT]);
		rt->isinlist = 1;
		Tse_rwlock_unlock(&te->listlock[TSE_CONNECT]);
		return ACCEPT_CMD;
	}
	
	Tse_rwlock_unlock(&te->listlock[TSE_CONNECT]);

	if(CheckExceptionStatus(entry,TSE_CONNECT_EXCEPTION)) return DROP_CMD;
	entry->type = TSE_CONNECT;
	Tse_rwlock_wrlock(&te->elock);
	TAILQ_INSERT_TAIL(&te->elist, entry, echain);
	Tse_rwlock_unlock(&te->elock);
	SetExceptionStatus(entry,TSE_CONNECT_EXCEPTION);
	TRACE_EXCE(NOTICE,"packet connect exception src ip:%u.%u.%u.%u,dst ip:%u.%u.%u.%u src port:%d dst port:%d",
		         IPQUAD(p->ip_src),
		         IPQUAD(p->ip_dst),
		         p->port_src,
		         p->port_dst);
	return DROP_CMD;
}

int TseProtoStat(struct Tacticsevolve *te,struct TseHashNode *entry,Packet *p)
{
	uint64_t msec;
	struct timeval curtime;
	struct TeRuntime * rt;
	struct TeParam   * tp;

	if(!te->enable[TSE_PROTO]) return ACCEPT_CMD;

	rt = &entry->proto;
	tp = &te->proto;
	gettimeofday(&curtime,0);
	msec = curtime.tv_sec * 1000 + curtime.tv_usec / 1000;

	if(TseProtoAnalyse(te,&p->pt5,p->mark) == 0) return ACCEPT_CMD;
	
	Tse_rwlock_wrlock(&te->listlock[TSE_PROTO]);
	
	rt->total_per_times++;
	rt->total_all_times++;
	
	if(rt->total_per_times < tp->threshold) {
		if(rt->isinlist == 0){
			TAILQ_INSERT_TAIL(&te->lrulist[TSE_PROTO], entry, lruchain[TSE_PROTO]);
			rt->isinlist = 1;
		}
		Tse_rwlock_unlock(&te->listlock[TSE_PROTO]);
		return ACCEPT_CMD;
	}
	
	rt->total_per_times = 0;
	
	if(rt->isinlist){
		TAILQ_REMOVE(&te->lrulist[TSE_PROTO], entry, lruchain[TSE_PROTO]);
	}
	
	rt->time_start = msec;
	rt->over_times++;

	TRACE_EXCE(NOTICE,"src ip:%u.%u.%u.%u,dst ip:%u.%u.%u.%u total:%u per:%u times:%d",
		         IPQUAD(p->pt5.ip_src),
		         IPQUAD(p->pt5.ip_dst),
		         rt->total_all_times,
		         rt->total_per_times,
		         rt->over_times);

	if(rt->over_times < tp->max_times){
		TAILQ_INSERT_TAIL(&te->lrulist[TSE_PROTO], entry, lruchain[TSE_PROTO]);
		rt->isinlist = 1;
		Tse_rwlock_unlock(&te->listlock[TSE_PROTO]);
		return ACCEPT_CMD;
	}
	
	Tse_rwlock_unlock(&te->listlock[TSE_PROTO]);

	if(CheckExceptionStatus(entry,TSE_PROTOCO_EXCEPTION)) return DROP_CMD;
	entry->type = TSE_PROTO;
	Tse_rwlock_wrlock(&te->elock);
	TAILQ_INSERT_TAIL(&te->elist, entry, echain);
	Tse_rwlock_unlock(&te->elock);
	SetExceptionStatus(entry,TSE_PROTOCO_EXCEPTION);
	TRACE_EXCE(NOTICE,"packet protocol exception src ip:%u.%u.%u.%u,dst ip:%u.%u.%u.%u src port:%d dst port:%d",
		         IPQUAD(p->pt5.ip_src),
		         IPQUAD(p->pt5.ip_dst),
		         p->pt5.port_src,
		         p->pt5.port_dst);
	return DROP_CMD;

}

static int 
TseCmdVerdict(struct Tacticsevolve *te,struct TseHashNode *entry,Packet *p)
{

	int ret;
	//port 
	ret = TsePortCheck(te,entry,p);
	if(ret == DROP_CMD) goto reject;
	
	//traffic
	ret = TseTrafficStat(te,entry,p);
	if(ret == DROP_CMD) goto reject;

	ret = TseProtoStat(te,entry,p);
	if(ret == DROP_CMD) goto reject;

	return ACCEPT_CMD;
	
reject:
	TRACE_EXCE(WARNING,"%s():exception,you should add iptables rule",__func__);
	return DROP_CMD;
	
}

int 
TsePacketRelease(struct Tacticsevolve *te,Packet *p)
{
	int ret;
	struct TseHashNode * entry;
	entry = GetHashNode(te,&p->pt5,&p->hash);

	DumpPacketInfo(p);

	if(entry == NULL){
		TRACE_EXCE(WARNING,"%s():Hash Table is run out!",__func__);
		return -1;
	}

	ret = TseCmdVerdict(te,entry,p);
	return ret;
}

int TseHashClear(struct Tacticsevolve *te,struct TseHashNode *entry)
{
	/*port have not use lock, from traffic start*/
	int index = TSE_TRAFFIC;
	int inlist = 0;
	for (; index < TSE_MAX; index++){
		switch(index){
			case TSE_PORT:
				break;
			case TSE_TRAFFIC:
				inlist = entry->traffic.isinlist;
				break;
			case TSE_PROTO:
				inlist = entry->proto.isinlist;
				break;
			case TSE_CONNECT:
				inlist = entry->ct.isinlist;
				break;
		}
		Tse_rwlock_wrlock(&te->listlock[index]);
		if(inlist != 0)
			TAILQ_REMOVE(&te->lrulist[index], entry, lruchain[index]);
		Tse_rwlock_unlock(&te->listlock[index]);
	}
	Tse_rwlock_wrlock(&te->hashlock);
	__hlist_del(&entry->hchain);
	Tse_rwlock_unlock(&te->hashlock);
	return free_mem(te->hashbuff,entry);
}

int TseAdminVerdict(struct Tacticsevolve *te)
{
	struct TseHashNode *entry=NULL;
	//port exception
	Tse_rwlock_wrlock(&te->elock);
	entry = TAILQ_FIRST(&te->elist);
	if(entry != NULL){
		te->cb(entry->key.value.ip_src,entry->key.value.ip_dst,te->rejectime,entry->type);
		TAILQ_REMOVE(&te->elist,entry,echain);
		if(TseHashClear(te,entry) < 0){
			TRACE_EXCE(WARNING,"Tse Hash Clear failed!");
		}
	}
	Tse_rwlock_unlock(&te->elock);
	
	struct timeval ctime;
	gettimeofday(&ctime,0);
	uint64_t curtime = ctime.tv_sec * 1000 + ctime.tv_usec / 1000;

	int index;
	
	for (index = 0; index < TSE_MAX; index++ ){
		Tse_rwlock_wrlock(&te->listlock[index]);
		entry = TAILQ_FIRST(&te->lrulist[index]);
		if(entry != NULL){
			switch(index){
				case TSE_PORT:
					break;
				case TSE_TRAFFIC:
					if(curtime - entry->traffic.time_start > te->traffic.interval){
						TAILQ_REMOVE(&te->lrulist[index], entry, lruchain[index]);
						entry->traffic.total_per_times = 0;
						entry->traffic.time_start = curtime;
						TAILQ_INSERT_TAIL(&te->lrulist[index], entry, lruchain[index]);
					}
					break;
				case TSE_PROTO:
					if(curtime - entry->proto.time_start > te->proto.interval){
						TAILQ_REMOVE(&te->lrulist[index], entry, lruchain[index]);
						entry->proto.total_per_times = 0;
						entry->proto.time_start = curtime;
						TAILQ_INSERT_TAIL(&te->lrulist[index], entry, lruchain[index]);
					}
					break;
				case TSE_CONNECT:
					if(curtime - entry->ct.time_start > te->ct.interval){
						TAILQ_REMOVE(&te->lrulist[index], entry, lruchain[index]);
						entry->ct.total_per_times = 0;
						entry->ct.time_start = curtime;
						TAILQ_INSERT_TAIL(&te->lrulist[index], entry, lruchain[index]);
					}
					break;
			}
		}
		Tse_rwlock_unlock(&te->listlock[index]);
	}
	return 0;
}

/* init Tacticsevolve */
struct Tacticsevolve * TseCreate()
{
	struct Tacticsevolve * te;
	uint32_t size_te    = sizeof(struct Tacticsevolve);
	uint32_t size_port  = (MAX_PORT_NUMS / BITMAP_PER_SIZE) * sizeof(bitmap_set);
	uint32_t size_hmem  = mem_manage_memory_bytes(MAX_HASH_ENTRIES,sizeof(struct TseHashNode));
	
	uint32_t base_te    = 0; 
	uint32_t base_port  = 0;
	uint32_t base_hmem  = 0;
	uint32_t base       = 0;
	
	base_port += base_te   + ALGIN_DATA(size_te,   ALIGN_SIZE);	
    base_hmem += base_port + ALGIN_DATA(size_port, ALIGN_SIZE);
	base      += base_hmem + ALGIN_DATA(size_hmem, ALIGN_SIZE);
	
	te = (struct Tacticsevolve *)malloc(base);
	if (te == NULL) {
		TRACE_EXCE(ERR,"%s():Tacticsevolve memory allocation failed",__func__);
		goto err;
	}
	memset(te,0,base);

	te->entries   = MAX_HASH_ENTRIES;
	te->buckets   = MAX_HASH_BUCKET;
	te->sum_bytes = base;
	
	te->porttable = (bitmap_set*)((uint8_t *)te + base_port);

	TAILQ_INIT(&te->elist);
	int idx;
	for(idx = 0; idx < TSE_MAX; idx++){
		TAILQ_INIT(&te->lrulist[idx]);
		if(0 != Tse_rwlock_init(&te->listlock[idx],NULL)){
			TRACE_EXCE(ERR,"%d list rwlock initialization failed",idx);
			goto err;
		}
	}
	if(0 != Tse_rwlock_init(&te->hashlock,NULL)){
		TRACE_EXCE(ERR,"hash rwlock initialization failed");
		goto err;
	}
	if(0 != Tse_rwlock_init(&te->elock,NULL)){
		TRACE_EXCE(ERR,"exception list rwlock initialization failed");
		goto err;
	}

	/*
	uint32_t index;
	for(index = 0; index < te->buckets; index++){
		INIT_HLIST_HEAD(&te->hlist[index]);
	}
	*/
	uint8_t *data = (uint8_t *)te + base_hmem;
	te->hashbuff  = mem_manage_init(te->entries,sizeof(struct TseHashNode),data,size_hmem);
	if(te->hashbuff == NULL){
		TRACE_EXCE(ERR,"%s():Tacticsevolve init memory manage failed",__func__);
		free(te);
		goto err;
	}

	te->nfctab = CreateCtTable();
	if(te->nfctab == NULL){
		free(te);
		goto err;
	}
	
	return te;
err:
	exit(-1);
}

void TseFree(struct Tacticsevolve * te)
{
	int idx;
	for(idx = 0; idx < TSE_MAX; idx++){
		Tse_rwlock_destroy(&te->listlock[idx]);
	}
	Tse_rwlock_destroy(&te->hashlock);
	Tse_rwlock_destroy(&te->elock);
	if(te != NULL){
		free(te);
	}
}


