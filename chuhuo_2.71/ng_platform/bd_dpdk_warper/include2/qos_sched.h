/*
 * Copyright(c) 2007 BDNS
 */
 
#ifndef __QOS_SCHED_H__
#define __QOS_SCHED_H__

#include <rte_mbuf.h>
#include <rte_jhash.h>

#define SCHED_COLLECT_STATS		1

#ifdef SCHED_COLLECT_STATS
#define SCHED_STATS_ADD(stat,val) (stat) += (val)
#else
#define SCHED_STATS_ADD(stat,val) do {(void) (val);} while (0)
#endif

#define RTE_MAX_PORT 16

#define TB_DEFAULT_BUCKETSIZE 8196
#define TB_DEFAULT_CIR 204800  // default 1 MB/S
#define TB_DEFAULT_PIR 204800  // default 1 MB/S

#define DEFAULT_VIRLINE_ID    0
#define TB_DEFAULT_VIR_RATE   12500000  //100Mbps



#define QOS_DOWN 0
#define QOS_UP   1

#define DOWN_LINK 0
#define UP_LINK   1

#define QOS_SUBPORT_FUN_FORBID 1

#define MAX_QUEUE_SIZE 128

#define MAX_MEMORY_NAME_SIZE      32

#define MAX_HASH_ENTRIES         262144  /*IP*/
#define HASH_ENTRIES_PER_BUCKET  4
#define MAX_USERS_PER_SUBPORT    2048

#define APP_TYPE_NUMS_PER_IP     8     /**< can have 8 traffic class per ip key*/
#define MAX_SUBPORT_NUMS         1024   /**/
#define MAX_HIERARCHY_MAP_ENTRY  (MAX_HASH_ENTRIES * APP_TYPE_NUMS_PER_IP)

#define MAX_PIPE_PER_SUBPORT     256
#define MAX_SUBPORT_PER_VIRLINE  16 //16
#define MAX_VIRTUAL_LINE         64 //256

#define MAX_MESSAGE_NUMS 8            /**< command message queue size*/

//PROTOCOL HASH MAP
#define PROTOCOL_SHIFT 0x0000000000000001
#define PROTOCOL_MAX   0xFFFFFFFFFFFFFFFF
#define PROTOCOL_TOTAL 256  // PROTOCOL_NUMS * PROTOCOL_BITS
#define PROTOCOL_NUMS  4
#define PROTOCOL_BITS  64  

#define TOKEN_BUCKET_MIN_PERIOD 100

//default pipe index in subport
#define DEFAULT_PIPE_INDEX 0

#define MAX_SHARED_PIPE_NUMS 1


//pipe type
#define SHARED_PIPE  0x1
#define SINGLE_PIPE  0x2
#define DEFAULT_PIPE 0x4  //not delete


//subport bandwidth update flag
#define  RATE_UPLINK	0
#define  RATE_DOWNLINK	1
#define  CEIL_UPLINK	2
#define  CEIL_DOWNLINK	3

//back code
#define CODE_CALL_OK     1000
#define CODE_PORT_NOFD   1001
#define CODE_PORT_DOWN   1002
#define CODE_RE_ENABLE   1003
#define CODE_RE_DISABLE  1004
#define CODE_ENABLE_FAIL 1005
#define CODE_ADD_SP_FAIL 1006
#define CODE_DEL_SP_FAIL 1007
#define CODE_ADD_VL_FAIL 1008
#define CODE_DEL_VL_FAIL 1009
#define CODE_UNKNOWN_CMD 1010


//message queue option code
#define QOS_OPCODE_NONE         0x00
#define QOS_OPCODE_ENABLE       0x01
#define QOS_OPCODE_DISABLE      0x02
#define QOS_OPCODE_ADD_SUBPORT  0x04
#define QOS_OPCODE_DEL_SUBPORT  0x08
#define QOS_OPCODE_ADD_VIRLINE  0x10
#define QOS_OPCODE_DEL_VIRLINE  0x20



#define DEFAULT_MTU     1500
#define FRAME_OVERHEAD  0


#define MSG_KEY_T    9876543210
#define MSG_MAX_SIZE 256


struct msgbuf
{
	long mtype;
	char mtext[MSG_MAX_SIZE];
};


struct hierarchy_map_path {
  //uint32_t traffic_class:2;        /**< Traffic class ID (0 .. 3)*/
	uint32_t pipe:20;                /**< Pipe ID */
	uint32_t subport:10;             /**< Subport ID */
	uint32_t color:2;                /**< Color */
};

union hierarchy_map_entry{
	struct hierarchy_map_path hierarchy;
	uint32_t sched;
};

//hash table key, used for configuring diffcult traffic 
struct ip_addr_key{
	uint32_t ip_addr;
};

struct traffic_value{
	struct ip_addr_key key;
	uint32_t nums;
	union hierarchy_map_entry entry[APP_TYPE_NUMS_PER_IP];
}__rte_cache_aligned;


struct sched_queue {
	uint64_t qw;
	uint64_t qr;
};


enum sched_state {
	e_PREFETCH_PIPE = 0,
	e_PREFETCH_QUEUE_ARRAYS,
	e_PREFETCH_MBUF,
	e_READ_MBUF,
};

struct sched_stats {
	/* Packets */
	uint64_t n_pkts;
	uint64_t n_pkts_dropped;
	/* Bytes */
	uint64_t n_bytes; 
	uint64_t n_bytes_dropped;
};

struct token_bucket_data {
	uint64_t tb_time;              /* Time of latest update of token bucket */
	uint64_t tb_credits;	       /* Number of bytes currently available in bucket */
	uint64_t tb_size;	           /* Upper limit for token bucket */
	uint64_t tb_period;            /* Number of CPU cycles for one update of token bucket */
	uint64_t tb_bytes_per_period;  /* Number of bytes to add to token bucket on each update*/
};

struct sched_virtual_line_bwinfo{
	uint64_t total_bandwidth;
	uint64_t total_ceil;
	uint64_t period;
	uint64_t bytes_per_period;
	uint64_t totaltokens;
	struct   sched_stats stats;
};

union subport_id{
	struct{
		uint32_t id:31;
		uint32_t flag:1;		
	} value;
	uint32_t subportid;
};

struct sched_virtual_line{
	uint32_t lineroadid;
	uint32_t lineroadindex;
	struct sched_virtual_line_bwinfo bwinfo[2];
	union subport_id subportid[MAX_SUBPORT_PER_VIRLINE];
	uint32_t used;
	struct sched_virtual_line * next;
}__rte_cache_aligned;


struct sched_pipe_inner {
	uint32_t activate;
	uint32_t qindex;
	struct token_bucket_data pipe_tb;
	struct sched_queue queue;
	struct sched_stats stats;
} __rte_cache_aligned;


struct sched_pipe{
	uint32_t pipeid;
	uint32_t ipaddr;
	int32_t  traffic_index;
	struct sched_pipe_inner pipeinner[2];
}__rte_cache_aligned;

struct msg_ds {
	long mtype;
	uint32_t cmdtype;
	uint32_t type;
	uint32_t portid;
	uint32_t subportkey;
	uint32_t virlinekey;
	uint32_t priority;
	uint32_t users;
	uint32_t qsize;
	uint64_t tb_size;
	uint64_t tb_cir_sport[2];
	uint64_t tb_pir_sport[2];
	uint64_t tb_pir_pipe[2];
	uint64_t tb_vir_rate[2];
	uint64_t protomask[PROTOCOL_NUMS];
}__rte_cache_aligned;


struct sched_subport_inner{
	/*runtime data*/
	struct token_bucket_data subport_tb_cir;   //runtime data of token bucket 
	struct token_bucket_data subport_tb_pir;
	uint32_t next_pipeid;
	uint32_t exaust;
	uint32_t activate_queues;
	enum   sched_state  state;
	struct sched_stats  stats;
	struct sched_pipe * current_pipe;
	struct rte_mbuf   * pkt;
	struct rte_mbuf  ** q_base;
	struct sched_virtual_line_bwinfo * virline_bw;
};

struct sched_subport {
	
	/* User parameters */
	uint32_t priority;
	uint32_t sportkey;
	uint16_t qsize;
	uint16_t type;   //pipe type SHARED_PIPE--SINGLE_PIPE--DEFAULT_PIPE
	uint16_t forbid;
	uint32_t users;
	uint64_t protomask[PROTOCOL_NUMS];  //PROTOCOL_NUMS * 64 protocols

	//token bucket param
	uint64_t tb_cir_sport[2];  /**< Committed Information Rate (CIR). Measured in bytes per second. */
	uint64_t tb_pir_sport[2];  /**< Peak Information Rate (PIR). Measured in bytes per second. */
	uint64_t tb_pir_pipe[2];   /**< Peak Information Rate (PIR). Measured in bytes per second. */       
	uint64_t tb_size;          /**< bucket size*/
	
	/*inner data*/
	uint8_t  used;
	uint32_t groupid;

	/*virtual line*/
	uint32_t lineroadid;
	uint32_t lineroadindex;
	uint32_t linesportid;

	/*pipe*/
	uint32_t n_pipes;
	uint32_t n_shared_pipes;
	uint32_t n_single_pipes;
	uint32_t n_valid_pipes;
	
	struct sched_subport * next;
	
	//runtime data
	struct sched_subport_inner * runtime[2];
	
	/* Large data structures */
	struct sched_subport_inner * run_entry;
	struct sched_pipe * pipe;
	struct sched_pipe * single_pipe;
	struct rte_mbuf  ** queue_array;	
	uint8_t * memory;
} __rte_cache_aligned;


struct sched_port{
	uint32_t port_id;                        /**physical port id*/
	int 	 socket_id;
	int      enable;                         /**if qos is enable or disable*/
	uint32_t linkspeed;                      /**port link speed*/
	uint32_t mtu;
	uint32_t frame_overhead; 

	/* Timing */
	uint64_t hz;
	uint64_t time;

	uint64_t rate_total[2];
	uint64_t rate_used[2];

	/*virtual list*/
	struct sched_virtual_line *  list_line;
	struct sched_virtual_line ** list_line_tail;

	/*for dequeue*/
	struct   rte_mbuf **pkts_out[2];
	uint32_t n_pkts_out[2];

	uint64_t pktstat;
	struct   sched_subport *  sport_list;          /**sched list*/
	struct   sched_subport ** sport_default;       /*pointer default flow*/
	uint32_t subport_nodefault_nums;
	//subport alloc index
	uint32_t subport_index;
	//hierarchy_map_entry alloc index
	//uint32_t hentry_index;
	
	/* Large data structures */	
	struct   rte_hash            * hkey;           /**hash table: key compute*/
	struct 	 traffic_value       * hvalue;    	   /**hash table: store value table*/
  //struct   hierarchy_map_entry * hentry;
	struct 	 sched_subport       * subport;        /**qos sched port buffer*/
	struct   sched_virtual_line  * virline;
	uint32_t                     * ipbuf;
	uint8_t                      * memory;
}__rte_cache_aligned;


int sched_port_enqueue(struct sched_port *port, struct rte_mbuf  *pkt, uint8_t flag);
int sched_port_bulk_enqueue(struct sched_port *port, struct rte_mbuf **pkts,uint32_t n_pkts,uint8_t flag);
int sched_port_dequeue(struct sched_port *port, struct rte_mbuf **pkts,uint32_t n_pkts,uint8_t flag);

int init_sched_port(struct sched_port * port,uint16_t portid,int socketid);

void port_subport_enable(struct sched_subport * sport);
void port_subport_disable(struct sched_subport * sport);

void port_singlepipe_enable(struct sched_subport * sport);
void port_singlepipe_disable(struct sched_subport * sport);

struct sched_subport ** sched_subport_lookup(struct sched_port * port,uint32_t in_priority);
void uninstall_sched_subport(struct sched_port * port,struct sched_subport * sport);

struct sched_virtual_line ** virtual_line_lookup(struct sched_port * port,uint32_t lineroadid);

int port_qos_update_sport_pir(struct sched_port * port,
							         struct sched_subport *subport,
							         uint64_t rate,
							         uint8_t flag);
int port_qos_update_sport_cir(struct sched_port * port,
							         struct sched_subport *subport,
							         uint64_t rate,
							         uint8_t flag);

int port_qos_update_pipe_rate(struct sched_port * port,
								     struct sched_subport *subport,
									 uint64_t rate,
									 uint8_t flag);


int port_qos_update_groupid(struct sched_port * port,uint32_t sportkey,uint32_t priority);


void port_pipe_update_bucketsize(struct sched_subport *subport,uint32_t bucketsize);

void port_subport_update_bucketsize(struct sched_subport *subport,uint32_t bucketsize);

int port_subport_default_reset(struct sched_port * port);

void print_virline_real_rate(struct sched_virtual_line * line,
								struct sched_stats *upstats,
								struct sched_stats *downstats);

void print_subport_real_rate(struct sched_subport * sport,
	                              struct sched_stats *upstats,
	                              struct sched_stats *downstats);

void print_pipe_real_rate(struct sched_pipe * pipe,
								struct sched_stats *upstats,
								struct sched_stats *downstats);


void print_qos_sched_stat(void * arg);

int qos_init(__attribute__((unused))void * __sysinfo);
int qos_exit(__attribute__((unused))void * __sysinfo);

int qos_manage(void * arg);


#endif /* __QOS_SCHED_H__ */

























