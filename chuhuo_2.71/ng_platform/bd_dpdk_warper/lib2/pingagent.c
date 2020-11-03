#include <stdlib.h>
#include <stdio.h>

#include <rte_icmp.h>
#include "dpdk_config.h"
#include "dpdk_frame.h"

#define RTE_LOGTYPE_PING RTE_LOGTYPE_USER1

#if PING_LOG_DEBUG
#define PING_LOG RTE_LOG
#else 
#define PING_LOG(l,t,...) do{}while(0)
#endif

struct ip_st{
	unsigned int ip;
	unsigned int flag;
	uint64_t lasttime;
	uint16_t ttl;
	uint16_t used;
	struct icmp_hdr icmp;
};

#define MAX_DST_IP 16

struct ip_table{
	unsigned int ipsrc;
	int idx;
	struct ip_st ipdst[MAX_DST_IP];
};

struct ip_addr_group {
	unsigned int ip;
	unsigned int mask;
};

#define IP_GROUP 2
struct ip_table_cpu {
	rte_rwlock_t lock;
	struct ip_table ipt[IP_GROUP][256];
};

static struct ip_table_cpu iptabentry;
static struct ip_table_cpu * iptab = &iptabentry;


struct ip_addr_group group[] = {{0xC0A80A00,0xFFFFFF00},
	 							{0xC0A80B00,0xFFFFFF00},
	               			   };

#define REPLY_OK    5
#define ORIG_FIRST  1

#define MS_PER_S        1000
#define MAX_TIMEOUT_SEC 4

static uint64_t MAX_TIMEOUT;

#ifdef __BIG_ENDIAN
#define IPQUAD(addr) \
((unsigned char *)&addr)[3], \
((unsigned char *)&addr)[2], \
((unsigned char *)&addr)[1], \
((unsigned char *)&addr)[0]
#else
#define IPQUAD(addr) \
((unsigned char *)&addr)[0], \
((unsigned char *)&addr)[1], \
((unsigned char *)&addr)[2], \
((unsigned char *)&addr)[3]
#endif


static void timeout_set(void)
{
	MAX_TIMEOUT = MAX_TIMEOUT_SEC * rte_get_tsc_hz();
}

static int pinginit(__attribute__((unused))void * __sysinfo)
{
	memset(iptab,0,sizeof(struct ip_table_cpu));
	rte_rwlock_init(&iptab->lock);
	timeout_set();
	return 0;
}

static uint16_t icmp_cksum(uint16_t *addr, int len)
{
	int nleft = len;
	uint32_t sum = 0;
	uint16_t *w = addr;
	uint16_t answer = 0;

	while (nleft > 1) {
		sum += *w++;
		nleft -= 2;
	}

	if (nleft == 1) {
		*(unsigned char *)(&answer) = *(unsigned char *)w ;
		sum += answer;
	}

	sum = (sum >> 16) + (sum & 0xffff);
	sum += (sum >> 16);
	answer = ~sum;
	return(answer);
}


static void check_timeout(struct ip_table * ipt)
{
	int i;
	uint64_t cur = rte_rdtsc();
	for(i = 0; i < MAX_DST_IP; i++){
		if(ipt->ipdst[i].lasttime != 0 && (cur - ipt->ipdst[i].lasttime) > MAX_TIMEOUT){
			PING_LOG(DEBUG,PING,"timeout!!! srcip=%u.%u.%u.%u  dstip=%u.%u.%u.%u\n",IPQUAD(ipt->ipsrc),IPQUAD(ipt->ipdst[i].ip));
			ipt->ipdst[i].ip       = 0;
			ipt->ipdst[i].lasttime = 0;
			ipt->ipdst[i].flag     = 0;
			ipt->ipdst[i].used     = 0;
		}
	}
}

static int __pingagent(struct rte_mbuf * mbuf)
{
	int ret = 0;
	int pload_len,difflen,i;

	uint64_t curtime;
	unsigned int srcip,dstip;
	
	struct ipv4_hdr * iphdrp;
	struct icmp_hdr * icmph;
	struct ip_table * ipt;
	struct ether_addr ethaddr;
	struct ether_hdr *eth_hdr;
	eth_hdr = rte_pktmbuf_mtod(mbuf, struct ether_hdr*);
	iphdrp  = rte_pktmbuf_mtod_network(mbuf,struct ipv4_hdr *);
	icmph   = (struct icmp_hdr *)(iphdrp + 1);
	
	if(iphdrp->next_proto_id != 1) return 0;
	if(eth_hdr->ether_type != 0x0800){
		DPDK_LOG(DEBUG,PLATFORM,"buf is not ip packets,but process as ip icmp\n");
		return 0;
	}
#define IP_MF 0x2000 
#define IP_OFFSET 0x1FFF
	if((iphdrp->fragment_offset & rte_cpu_to_be_16(IP_MF | IP_OFFSET)) != 0) return 0;

	srcip  = rte_be_to_cpu_32(iphdrp->src_addr);
	dstip  = rte_be_to_cpu_32(iphdrp->dst_addr);
	
	rte_rwlock_write_lock(&iptab->lock);
	for(i = 0; i < IP_GROUP; i++){
		if((srcip & group[i].mask) == group[i].ip){
			ipt = &iptab->ipt[i][srcip & (~group[i].mask)];
			break;
		}
	}
	if(i == IP_GROUP) goto dst_process;


	check_timeout(ipt);
	curtime = rte_rdtsc();
	for(i = 0; i < MAX_DST_IP; i++){
		if(ipt->ipdst[i].ip == dstip){
			if(ipt->ipdst[i].flag == REPLY_OK){
				
				icmph->icmp_type = IP_ICMP_ECHO_REPLY;
				icmph->icmp_code = ipt->ipdst[i].icmp.icmp_code;
				pload_len = rte_be_to_cpu_16(iphdrp->total_length) - sizeof(struct ipv4_hdr);
				icmph->icmp_cksum = 0;
				icmph->icmp_cksum = icmp_cksum((uint16_t *)icmph,pload_len);

				iphdrp->src_addr = rte_cpu_to_be_32(dstip);
				iphdrp->dst_addr = rte_cpu_to_be_32(srcip);
				iphdrp->time_to_live = ipt->ipdst[i].ttl;
				iphdrp->hdr_checksum = 0;
				iphdrp->hdr_checksum = rte_ipv4_cksum(iphdrp);

				ether_addr_copy(&eth_hdr->s_addr, &ethaddr);
				ether_addr_copy(&eth_hdr->d_addr, &eth_hdr->s_addr);
				ether_addr_copy(&ethaddr, &eth_hdr->d_addr);

				ipt->ipdst[i].lasttime = curtime;
				PING_LOG(DEBUG,PING,"src %u.%u.%u.%u dst %u.%u.%u.%u icmp agent reply  %d\n",IPQUAD(dstip),IPQUAD(srcip),i);
				ret = 1;
				goto srcret;
			}
			else {
				PING_LOG(DEBUG,PING,"src %u.%u.%u.%u dst %u.%u.%u.%u icmp not agent reply\n",IPQUAD(srcip),IPQUAD(dstip));
				goto srcret;
			}
		}
	}
	if(i == MAX_DST_IP){
		for(i = 0; i < MAX_DST_IP; i++){
			if(ipt->ipdst[ipt->idx].used==0){
				PING_LOG(DEBUG,PING,"src %u.%u.%u.%u dst %u.%u.%u.%u icmp first come or timeout come %d\n",IPQUAD(srcip),IPQUAD(dstip),ipt->idx);
				ipt->ipdst[ipt->idx].ip       = dstip;
				ipt->ipdst[ipt->idx].flag     = ORIG_FIRST;
				ipt->ipdst[ipt->idx].lasttime = curtime;
				ipt->ipdst[ipt->idx].used     = 1;
				ipt->idx = (ipt->idx + 1) % MAX_DST_IP;
				break;
			}
			ipt->idx = (ipt->idx + 1) % MAX_DST_IP;
		}
	}
srcret:
	rte_rwlock_write_unlock(&iptab->lock);
	return ret;

dst_process:
	for(i = 0; i < IP_GROUP; i++){
		if((dstip & group[i].mask) == group[i].ip){
			ipt = &iptab->ipt[i][dstip & (~group[i].mask)];
			break;
		}
	}
	if(i == IP_GROUP) goto dstret;
	
	if(icmph->icmp_type == IP_ICMP_ECHO_REPLY){
		for(i = 0; i < MAX_DST_IP; i++){
			if(ipt->ipdst[i].ip == srcip){
				if(ipt->ipdst[i].flag == ORIG_FIRST){
					PING_LOG(DEBUG,PING,"src %u.%u.%u.%u dst %u.%u.%u.%u icmp echo reply  %d\n",IPQUAD(srcip),IPQUAD(dstip),i);
					ipt->ipdst[i].flag = REPLY_OK;
					ipt->ipdst[i].icmp.icmp_code   = icmph->icmp_code;
					ipt->ipdst[i].icmp.icmp_type   = icmph->icmp_type;
					ipt->ipdst[i].icmp.icmp_cksum  = icmph->icmp_cksum;
					ipt->ipdst[i].icmp.icmp_ident  = icmph->icmp_ident;
					ipt->ipdst[i].icmp.icmp_seq_nb = icmph->icmp_seq_nb;
					ipt->ipdst[i].ttl              = iphdrp->time_to_live;
				}
				break;
			}
		}
	}
dstret:
	rte_rwlock_write_unlock(&iptab->lock);
	return ret;
}

int pingagent(struct rte_mbuf * mbuf)
{
#ifdef PING_MCORE
	return __pingagent(mbuf);
#else
	return 0;
#endif
}

#ifdef PING_MCORE

MODULE_INIT(pinginit);

#endif


