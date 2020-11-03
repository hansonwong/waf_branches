
#ifndef _TSE_H_
#define _TSE_H_

#include <sys/time.h>
#include <stdint.h>
#include <sys/queue.h>

#include "hlist.h"
#include "mem_manage.h"
#include "thread.h"

#define MAX_PORT_NUMS         65536

#define MAX_KEY_SIZE          16
#define MAX_HASH_BUCKET       1024//65536
#define MAX_HASH_BUCKET_SIZE  8
#define MAX_HASH_ENTRIES      8192//524288 //MAX_HASH_BUCKET * MAX_HASH_BUCKET_SIZE

#define ETHER_HEAD_SIZE 14

#define ACCEPT_CMD 1
#define DROP_CMD   0

struct TseNFctTable_;

typedef int ( *RuleCallBack )(const uint32_t src,const uint32_t dst,const uint32_t rejectime,int type);

struct PacketTuple_ {
	uint32_t ip_src;
	uint32_t ip_dst;
	uint16_t port_src;
	uint16_t port_dst;
	uint8_t  proto;
}__attribute__((__packed__));
typedef struct PacketTuple_ PacketTuple;

typedef struct Packet_ {
	uint16_t nfq_index;
	uint16_t verdicted;
	uint16_t hook;
	uint16_t hw_proto;
	uint32_t packet_id;
	uint32_t hw_addrlen;
	uint8_t  hw_addr[16];
	uint32_t hash;
	uint32_t mark;
	uint32_t pkt_len;
	uint32_t indev;
	uint32_t outdev;
	uint32_t physindev;
	uint32_t physoutdev;
	struct timeval ts;
	PacketTuple pt5;
}Packet;

struct ipv4_hdr {
	uint8_t  version_ihl;		/**< version and header length */
	uint8_t  type_of_service;	/**< type of service */
	uint16_t total_length;		/**< length of packet */
	uint16_t packet_id;		/**< packet ID */
	uint16_t fragment_offset;	/**< fragmentation offset */
	uint8_t  time_to_live;		/**< time to live */
	uint8_t  next_proto_id;		/**< protocol ID */
	uint16_t hdr_checksum;		/**< header checksum */
	uint32_t src_addr;		/**< source address */
	uint32_t dst_addr;		/**< destination address */
} __attribute__((__packed__));

struct udp_hdr {
	uint16_t src_port;    /**< UDP source port. */
	uint16_t dst_port;    /**< UDP destination port. */
	uint16_t dgram_len;   /**< UDP datagram length */
	uint16_t dgram_cksum; /**< UDP datagram checksum */
} __attribute__((__packed__));

struct tcp_hdr {
	uint16_t src_port;  /**< TCP source port. */
	uint16_t dst_port;  /**< TCP destination port. */
	uint32_t sent_seq;  /**< TX data sequence number. */
	uint32_t recv_ack;  /**< RX data acknowledgement sequence number. */
	uint8_t  data_off;  /**< Data offset. */
	uint8_t  tcp_flags; /**< TCP flags */
	uint16_t rx_win;    /**< RX flow control window. */
	uint16_t cksum;     /**< TCP checksum. */
	uint16_t tcp_urp;   /**< TCP urgent pointer, if any. */
} __attribute__((__packed__));

#define TSE_NONE_EXCEPTION      0x00000000U
#define TSE_PORT_EXCEPTION      0x00000001U
#define TSE_TRAFFIC_EXCEPTION   0x00000002U
#define TSE_CONNECT_EXCEPTION   0x00000004U
#define TSE_PROTOCO_EXCEPTION   0x00000008U

#define TSE_ENABLE 0

#define TSE_DEFAULT_QUEUE  "26-30"
#define TSE_DEFAULT_REJECT 60
#define TSE_DEFAULT_EPORT  "1025-65535"

#define TSE_REJECTIME_UNIT 60 // second
#define TSE_TRAFFIC_UNIT   1048576 //1024 * 1024 MB
#define TSE_TRAFFIC_MAX_VALUE (UINT32_MAX/TSE_TRAFFIC_UNIT)
#define TSE_TIME_UNIT      1000

#define PORT_LIMIT_BYTES     10240
#define TSE_DEFAULT_PORTTYPE "all"

#define TRAFFIC_THRESHOLD  10
#define TRAFFIC_MAX_TIMES  10 
#define TRAFFIC_INTERVALS  60

#define PROTOCO_THRESHOLD  10
#define PROTOCO_MAX_TIMES  10 
#define PROTOCO_INTERVALS  60

#define CONNECT_THRESHOLD  10
#define CONNECT_MAX_TIMES  10
#define CONNECT_INTERVALS  60


enum strategies_t
{
	TSE_PORT = 0,
	TSE_TRAFFIC,
	TSE_PROTO,
	TSE_CONNECT,
	TSE_MAX
};

struct TeParam{
	uint32_t interval;    //meter in seconds
	uint32_t threshold;
	uint32_t max_times;
};

struct TeRuntime{
	uint64_t time_start;
	uint32_t total_all_times; 
	uint32_t total_per_times;
	uint16_t over_times;
	uint16_t isinlist;
};

union HashKey{
	struct {
		uint32_t ip_src;
		uint32_t ip_dst;
	} value;
	uint8_t buf[MAX_KEY_SIZE];
};

struct TseHashNode{
	union  HashKey key;
	uint32_t porttraffic;
	struct TeRuntime traffic;
	struct TeRuntime proto;
	struct TeRuntime ct;
	struct hlist_node hchain;
	uint32_t flag;
	int type;
	TAILQ_ENTRY(TseHashNode) lruchain[TSE_MAX];
	TAILQ_ENTRY(TseHashNode) echain;
}__attribute__((__packed__));

typedef TAILQ_HEAD(hash_node_list, TseHashNode) head_list_t;

struct Tacticsevolve{
	uint8_t enable[TSE_MAX];
	uint32_t rejectime;
	uint32_t limitbytes;
#define SRC_PORT 0x0001 
#define DST_PORT 0x0002
#define ALL_PORT 0x0004
	uint32_t portflag;
	struct TeParam traffic;
	struct TeParam proto;
	struct TeParam ct;
	uint32_t sum_bytes;
	uint32_t entries;
	uint32_t entries_used;
	uint32_t buckets;
	RuleCallBack cb;
	head_list_t lrulist[TSE_MAX];
	head_list_t elist;
	Tse_rwlock_t listlock[TSE_MAX];
	Tse_rwlock_t elock;
	Tse_rwlock_t hashlock;
	bitmap_set * porttable;
	struct TseNFctTable_ * nfctab;
	struct hlist_head hlist[MAX_HASH_BUCKET];
	MemManage * hashbuff;
}__attribute__((__packed__));


void TseFree(struct Tacticsevolve * te);
struct Tacticsevolve * TseCreate();
int TsePacketRelease(struct Tacticsevolve *te,Packet *p);
int TseAdminVerdict(struct Tacticsevolve *te);
struct TseHashNode * GetHashNode(struct Tacticsevolve * te,PacketTuple * p,uint32_t * outhash);
int TsePortCheck(struct Tacticsevolve * te,struct TseHashNode *entry,Packet  * p);
int TseTrafficStat(struct Tacticsevolve *te,struct TseHashNode *entry,Packet *p);
int TseCtStat(struct Tacticsevolve *te,struct TseHashNode *entry,PacketTuple * p);
int TseProtoStat(struct Tacticsevolve *te,struct TseHashNode *entry,Packet *p);
int TseCommPortProto();

#endif /*_TSE_H_*/




