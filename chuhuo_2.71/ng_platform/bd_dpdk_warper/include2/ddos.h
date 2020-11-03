/*
*ddos module
*move from fastpath network layer to dpdk
*it is better to defense ddos attack earlier
*@mc
*/
#ifndef __DDOS_H_
#define __DDOS_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "link.h"

#define ANTI_DDOS_ON

#ifndef FPN_BIG_ENDIAN
#define FPN_BIG_ENDIAN      4321
#endif
#ifndef FPN_LITTLE_ENDIAN
#define FPN_LITTLE_ENDIAN   1234
#endif

#define FPN_BYTE_ORDER FPN_LITTLE_ENDIAN
#define TRACE_DDOS(level, fmt, args...) \
do {} while(0)
#define FPN_STATS_ADD(a, b) 

#define mtod(m, t) rte_pktmbuf_mtod(m, t)
#define m_len(m) 	(m)->pkt_len //(m)->data_len


//FLOOD TYPE
enum {
        DDOS_TYPE_SYN_FLOOD, /* 0 */
        DDOS_TYPE_UDP_FLOOD, /* 1 */
        DDOS_TYPE_ICMP_FLOOD,/* 2 */
        DDOS_TYPE_DNS_FLOOD, /* 3 */
        DDOS_TYPE_ARP_FLOOD, /* 4 */
        DDOS_TYPE_FLOOD_MAX, /* 5 */
		DDOS_TYPE_TEARDROP = DDOS_TYPE_FLOOD_MAX,
		DDOS_TYPE_SMURF,
		DDOS_TYPE_LAND,
		DDOS_TYPE_JUMBO_ICMP,
		DDOS_TYPE_WINNUKE,
		DDOS_TYPE_MAX,
};

enum {
		DDOS_DIR_SRC,
        DDOS_DIR_DST,
        DDOS_DIR_MAX,
};

static const char* const DDOS_STR[DDOS_TYPE_MAX] = {
	"SYN", 
	"UDP", 
	"ICMP", 
	"DNS", 
	"ARP",
	"TEARDROP",
	"SMURF",
	"LAND",
	"JUMBO_ICMP",
	"WINNUKE"
};

#define	FP_IPPROTO_ICMP		1		/* control message protocol */
#define	FP_IPPROTO_TCP		6		/* tcp */
#define	FP_IPPROTO_UDP		17		/* user datagram protocol */

#define DDOS_PACKET_NONE  0
#define DDOS_PACKET_DROP  1

enum{
	ADDR_LEN_32,
	ADDR_LEN_64
};
#define DNSPORT      53
#define NETBIOS_PORT 139

#define LO8(X)  ((X)&0X00FF)
#define LO16(X) ((X)&0XFFFF)

#define IPV4_PARAM(ipaddr) \
	(((ipaddr))>>24)&0xff, (((ipaddr))>>16)&0xff,(((ipaddr))>>8)&0xff, ((ipaddr))&0xff

//ddos msg 
struct ddos_config_t {
	u_int32_t	limit;
	u_int8_t	state;
	u_int8_t	dir;
	u_int8_t	type;
	u_int8_t	log;
} __attribute__ ((packed));

//
typedef struct {
	u_int32_t       limit;
    u_int8_t        state;
	u_int64_t		packets;
	u_int64_t		bytes;
} __attribute__ ((packed)) ddos_ts_t;


//static struct ddos_config_t ddos_config[DDOS_DIR_MAX][DDOS_TYPE_MAX];
//static ddos_ts_t ddos_ts_tables[DDOS_DIR_MAX][DDOS_TYPE_MAX];//config

#ifndef  DDOS_SOCK_PATH
#define DDOS_SOCK_PATH		"/tmp/dpdk_ddos_sock"
#endif

struct ARP_header {
	unsigned short	hardware;
	unsigned short	protocol;
	unsigned char	hardware_addr_len;
	unsigned char	proto_add_len;
	unsigned short	op;
	unsigned char	src_hw_addr   [6];
	//unsigned char	src_proto_addr[4];
	uint32_t src_proto_addr;
	unsigned char	tgt_hw_addr   [6];
	//unsigned char	tgt_proto_addr[4];
	uint32_t tgt_proto_addr;
} __attribute__ ((packed));

/* copy from fp-in.h */
/*
 * Internet address (a structure for historical reasons)
 */
struct fp_in_addr {
	uint32_t s_addr;
};

/* copy from fp-ip.h */
/*
 * Structure of an internet header, naked of options.
 */
struct fp_ip {
#if FPN_BYTE_ORDER == FPN_LITTLE_ENDIAN
	u_int	ip_hl:4,		/* header length */
	ip_v:4;				/* version */
#elif FPN_BYTE_ORDER == FPN_BIG_ENDIAN
	u_int	ip_v:4,			/* version */
	ip_hl:4;			/* header length */
#else
#error  "Adjust your byte order"
#endif
	u_char	ip_tos;			/* type of service */
	u_short	ip_len;			/* total length */
	u_short	ip_id;			/* identification */
	u_short	ip_off;			/* fragment offset field */
#define	FP_IP_RF 0x8000			/* reserved fragment flag */
#define	FP_IP_DF 0x4000			/* dont fragment flag */
#define	FP_IP_MF 0x2000			/* more fragments flag */
#define	FP_IP_OFFMASK 0x1fff		/* mask for fragmenting bits */
	u_char	ip_ttl;			/* time to live */
	u_char	ip_p;			/* protocol */
	u_short	ip_sum;			/* checksum */
	struct	fp_in_addr ip_src, ip_dst;	/* source and dest address */
} __attribute__ ((packed));

struct icmphdr {
#define ICMP_ECHO_REQUEST (8)
	uint8_t  icmp_type;   /* ICMP packet type. */
	uint8_t  icmp_code;   /* ICMP packet code. */
	uint16_t icmp_cksum;  /* ICMP packet checksum. */
	uint16_t icmp_ident;  /* ICMP packet identifier. */
	uint16_t icmp_seq_nb; /* ICMP packet sequence number. */
} __attribute__((__packed__));

/* copy from fp-udp.h */
struct fp_udphdr {
	uint16_t   source;
	uint16_t   dest;
	uint16_t   len;
	uint16_t   check;
} __attribute__ ((packed));

/* copy from fp-tcp.h */
struct fp_tcphdr {
	uint16_t   source;
	uint16_t   dest;
	uint32_t   seq;
	uint32_t   ack_seq;
#if FPN_BYTE_ORDER == FPN_LITTLE_ENDIAN
	uint16_t   res1:4,
		   doff:4,
		   fin:1,
		   syn:1,
		   rst:1,
		   psh:1,
		   ack:1,
		   urg:1,
		   ece:1,
		   cwr:1;
#elif FPN_BYTE_ORDER == FPN_BIG_ENDIAN
	uint16_t   doff:4,
		   res1:4,
		   cwr:1,
		   ece:1,
		   urg:1,
		   ack:1,
		   psh:1,
		   rst:1,
		   syn:1,
		   fin:1;
#else
#error  "Adjust your byte order"
#endif
	uint16_t   window;
	uint16_t   check;
	uint16_t   urg_ptr;
} __attribute__ ((packed));



//static unsigned int ip_list_tot = 100;
#define ip_pkt_list_tot (1024 - 2)
#define IP_LIST_HASH_SIZE 1024
#define IP_LIST_TOT	  1024 

#define ONE_SECOND              rte_get_tsc_hz()
#define DDOS_LOG_RATE             (ONE_SECOND) /*rate limit, every DDOS_LOG_RT seconds printf a log*/
#define DDOS_SECOND             ONE_SECOND
#define JHASH_GOLDEN_RATIO      0x9e3779b9
#define DDOS_TCP_HITCOUNT       5
#define DDOS_UDP_HITCOUNT       5
#define DDOS_ICMP_HITCOUNT      5
#define DDOS_ENTRY_POOL_LEN  (IP_LIST_TOT * DDOS_DIR_MAX * DDOS_TYPE_FLOOD_MAX)


struct ddos_table {
	unsigned int            entries;
	struct list_head        lru_list;
	struct list_head        iphash[IP_LIST_HASH_SIZE];
};

//static struct ddos_table ddos_tables[DDOS_DIR_MAX][DDOS_TYPE_MAX];

struct ddos_entry {
	struct list_head        list;//for hash
	struct list_head        lru_list;//long list
	union {
		uint32_t            addr;//ip addr
		uint32_t			mac_addr;//mac addr	
	};
	//u_int8_t                index;
	//u_int16_t               nstamps;
	uint32_t                index;
	uint32_t                nstamps;
	unsigned long           stamps[0];
};

#define typecheck(type,x) \
	({	type __dummy; \
	 typeof(x) __dummy2; \
	 (void)(&__dummy == &__dummy2); \
	 1; \
	 })

#define time_after(a,b)		\
	(typecheck(unsigned long, a) && \
	 typecheck(unsigned long, b) && \
	 ((long)(b) - (long)(a) < 0))

#ifndef print_ip
#define print_ip(ptr) \
		printf("%s,%u-%u-%u-%u\n", #ptr, ((ptr)>>24)&0xff, ((ptr)>>16)&0xff,((ptr)>>8)&0xff, (ptr)&0xff)
#endif

#define DEBUG 0
#if DEBUG
#define DDOS_DEBUG(format, args...)\
	fprintf(stdout, "%s, line=%d, "format, __FUNCTION__, __LINE__, ##args)
#else
#define DDOS_DEBUG(format, args...)
#endif


//---------------------------------------------------->
//function
extern int8_t  ddos_init(void);
extern void    ddos_exit(void);
extern int     fp_ddos_defense(const struct rte_mbuf * const m);
extern void    *ddos_get_config(__attribute__((unused)) void *arg);

#ifdef __cplusplus
}
#endif

#endif /* __DDOS_H_ */
