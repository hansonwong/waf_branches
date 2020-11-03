#ifndef __DPDK_FRAME_H
#define __DPDK_FRAME_H
//---------------------------------------------------------------
#ifdef __cplusplus
extern "C" {
#define UINT8_MAX 255
#define UINT16_MAX 65535
#endif

//---------------------------------------------------------------
#include <sys/types.h>				        					
#include <sys/ipc.h>	
#include <sched.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <signal.h>
//#include <pthread.h>
#include <fcntl.h> 
#include <sys/time.h>

#include "dpdk_warp.h"
#include <rte_kni.h>
#include <rte_kni_fifo.h>

#include "dpdk_config.h"
#include "fp-log.h"
#include "filter/rfc.h"
#include "module.h"
#include "qos_sched.h"
#include "flow.h"

#define CLINET_STRING_MAX 32
#define CLIENT_QUEUE_SIZE 2048 * 128//2048

#if DPDK_LOG_DEBUG
#define DPDK_LOG RTE_LOG
#else
#define DPDK_LOG(l,t,...) do{}while(0)
#endif

/*default 32,you can modify it and consistent with actual. This will improve performance*/
//#define RTE_MAX_ETHPORTS  3  

//kernet tc shared memory key
#define TC_SHM_KEY_ID  89421208

#define CLIENT_TRANS_BYFILTER 1

#define ENABLE_MIRROR_FUNCTION 1

#define ENABLE_APP_STATISTICS 0

#define ENABLE_CLIENT_APP 0

//#define ENABLE_PACKET_REASS

// Feature switches 

#define SERVER_TX_BULK_MODE 1
#if (SERVER_TX_BULK_MODE==1)
#define SERVER_TX_QUEUES  RTE_MAX_ETHPORTS
#define CLINET_RXQUEUE_MAX  RTE_MAX_ETHPORTS
#else
#define SERVER_TX_QUEUES 	2 //server-tx will use xxx queues for send
#define CLINET_RXQUEUE_MAX 	8

#define TX_QUEUES_IXGBE     1//server-tx will be ready for xxx queues for ixgbe,should be >=1
#define TX_QUEUES_IGB	   0.25//server-tx will be ready for xxx queues for igb,should be <=1
#endif
#define VIRTUAL_PORT	 RTE_MAX_ETHPORTS-1

#define MAX_CLINET_PRIORITY	    16
#define MAX_CLIENT_PARITY		16
#define CLIENT_MAX_FILTER 		16

#define MAX_CLIENTS  256
#define MAX_CLIENTS_HASHSIZE  	(MAX_CLIENTS*16)
#define MAX_CLIENTS_HASHMASK	(MAX_CLIENTS_HASHSIZE-1)


enum {
	DISABLE = 0,
	ENABLE = 1,
};

struct client_filter {
	uint32_t mark_cnt;
	uint32_t rule_cnt;
	char **userconf;  //limited to access to this field by yourself process
	uint64_t mark[CLIENT_MAX_FILTER];//app marks,invalid when 0
	struct FILTER rule[CLIENT_MAX_FILTER];//filter rule for in/out
};

#define MAX_SUB_CLIENTS 2

struct subqueueinfo {
	uint32_t queue_start;
	uint32_t queue_end;
	uint32_t queue_num;
};

struct client_rxqueue {
	uint32_t qnum;	//receive queue numbers
#define ROUND_ROBIN 0
#define SAMESRC_SAMEDEST  1
#define BY_FILTER		2
#define BY_OUTPORT		3
#define BY_MULTIPLIER_RR  0x400
#define BY_MULTIPLIER_SS  0x401
	uint32_t policy;	//loadbalance policy
	rte_atomic64_t total_rx;
	rte_atomic64_t total_tx;
	rte_atomic64_t total_dp;
	rte_atomic64_t total_dp_byref;
	rte_atomic64_t rings_mbuf_cnt[CLINET_RXQUEUE_MAX];
#define MAX_USLEEP_TIMES 1000
	volatile int usleep_times[CLINET_RXQUEUE_MAX];//semaphore for every ring
	struct rte_ring *rings[CLINET_RXQUEUE_MAX];//when recv,one queue may be splited into N parts,for loadbalance
	int q_handle_flag[CLINET_RXQUEUE_MAX];//0 : no core use this queue; 1 : one core use this queue
#if (SERVER_TX_BULK_MODE==0)
	uint8_t **txcpu;
#endif
	uint32_t group;
	struct subqueueinfo sub_queue[MAX_SUB_CLIENTS];
};


struct clientinfo{
	char name[CLINET_STRING_MAX];
	uint32_t processid; //process id.invalid when 0
	uint32_t fixedid;	   // fixed ID,only one
	uint32_t priority;     //The packet will be  passed backward according to the priority increasing
#define MODE_READONLY  0
#define MODE_WRITEABLE 1
	uint32_t rwmode; 	  //read or write
#define DPDK_IN				0
#define DPDK_OUT			1
#define DPDK_APP			2
#define DPDK_MIRRORIN		3
#define DPDK_MIRROROUT	    4
	uint32_t	hook;
	struct client_filter  filter;//filter fules
	struct client_rxqueue queue;//rx_queue
	//rte_rwlock_t  lock;
	struct clientinfo *next;
	void *sysinfo;
	void *bufpool; //for mirror ENABLE_MIRROR_FUNCTION
	volatile uint32_t fstop;
};

struct client_reginfo {
	const char *name;
	uint32_t issvr; //is server?
	uint32_t priority;
	uint32_t fixedid;
	const char *rwmode;//"r","w","c"
	const char *hook;//"in","out","app"
	const char *filter[CLIENT_MAX_FILTER];
	uint32_t qnum;
	const char *policy;//"RR" or "SS","BYFILTER","BYOUTPORT","BYMULTIPLIER_RR","BYMULTIPLIER_SS"
	uint32_t sub_client_qnum[MAX_SUB_CLIENTS];
};

struct  clientext_warper{
	uint32_t priority; 
	uint16_t maskhash;
	uint16_t clients;
	struct clientinfo *client[MAX_CLIENT_PARITY];
	struct clientext_warper *next; 
};

struct clientext  {
	rte_rwlock_t  lock;
	struct  clientext_warper *entry;	
};

struct clientint {
	uint32_t clients;
	rte_rwlock_t  lock;
	struct clientinfo *first;
	struct clientinfo *client[MAX_CLIENT_PARITY];
};

#define USER_RULE_LEN 128
struct mirror_info {
	uint8_t portid;
	struct client_rxqueue *svrtx_queue;
	struct client_filter m_filter;	
	char user_rule[CLIENT_MAX_FILTER][USER_RULE_LEN];
};
//---------------------------------------------------------------
enum {
	INVALID_MODE=0,

	LOOP_SIMPLE=3,
	LOOP,
	BYPASS,
	DIRECT_CONNECT_SIMPLE,
	DIRECT_CONNECT,
	BRIDGE_SIMPLE,
	MIRROR_PORT,
	ADVANCED,
	NAT_PORT,
	WORK_MODE_MAX
};


#define DEAULT_MODE ADVANCED

struct port_workmode{
	int mode;
	int value;	
};

struct port_stats{
	uint64_t rx;
	uint64_t tx;
	uint64_t tx_drop;
} __rte_cache_aligned;


struct portinfo {
	phys_addr_t status_uk_phys;
	phys_addr_t stats_uk_phys;
	uint8_t portn;
	uint8_t rxrings[RTE_MAX_ETHPORTS];
	uint8_t txrings[RTE_MAX_ETHPORTS];
#if (SERVER_TX_BULK_MODE==0)
	uint8_t txcpu[RTE_MAX_ETHPORTS][SERVER_TX_QUEUES];
#endif
#define USER_STATUS	0x01
#define KERN_STATUS	0x02
#define KNI_STATUS	0x04
#define IS_IXGBE	0x10
	uint8_t status_uk[RTE_MAX_ETHPORTS];
	uint8_t bridge_group[RTE_MAX_ETHPORTS][RTE_MAX_ETHPORTS];
	struct rte_kni *kni[RTE_MAX_ETHPORTS];
	struct rte_eth_conf portconf[RTE_MAX_ETHPORTS];
	struct port_workmode	mode[RTE_MAX_ETHPORTS];
	struct rte_eth_stats stats_uk[RTE_MAX_ETHPORTS];
	rte_atomic64_t port_tx_dp[RTE_MAX_ETHPORTS];
	uint32_t tc_ctl_switch;
	struct sched_port schport[RTE_MAX_ETHPORTS];
}__rte_cache_aligned;

extern const  char *portmode[];
//---------------------------------------------------------------
#define SYSTEM_INFO  			"dpdk-system-info"
#define SYSTEM_CLIENT_RING 	"ring-%d-%d-%d"
#define SYSTEM_RSS_RING     "rss-ring-%d"

#define SYS_FILTER_INVALID  -1
#define SYS_FILTER_NAME 	"'system-filter"
#define SYS_FILTER_MEMSIZE (10<<20)

enum __FILTER_OWNER{
	FILTER_DPDK_FRAME,
#if(ENABLE_MIRROR_FUNCTION == 1)
	FILTER_MIRROR_IN,
	FILTER_MIRROR_OUT,
#endif
	FILTER_OWNER_MAX
};

struct __filter_info {
	volatile int filterindex;
	void * filterctx[2];
};

typedef union 
{
	uint64_t flag1;
	uint8_t flag2[8]; //flag2[0]:mirror in, flag2[1]:mirror out
}control_flag; //use for logic control, in order to reduce some operations in data platment

struct dpdk_log {
    uint32_t dpdk_debug;
	uint32_t flag;
	uint32_t type;  /**< Bitfield with enabled logs. */
    uint32_t atype;  /**< log all enable types. */
	uint32_t level; /**< Log level. */
	FILE *file;     /**< Pointer to current FILE* for logs. */
	FILE *oldfile;
	char filepath[256];
};

struct system_info {
	uint64_t hz;
	volatile uint64_t msec;
	unsigned socket_id;
	unsigned ringsize ;
	uint32_t svr_ready;
	rte_rwlock_t  systemlock;
	struct rte_mempool *pktmbuf_pool;
	struct rte_mempool *pktmbuf_hdr_pool;
	struct portinfo  portinfos;
	struct clientint in;
	struct clientint out;
	struct clientint mirror_in;
	struct clientint mirror_out;
	struct mirror_info mirror_port[2]; //0:in, 1:out
	struct clientext app[MAX_CLIENTS_HASHSIZE];
	struct clientinfo cinfos[MAX_CLINET_PRIORITY][MAX_CLIENT_PARITY];
	struct clientext_warper  entrys[MAX_CLIENTS_HASHSIZE][MAX_CLINET_PRIORITY];
	fp_debug_t debug;
	struct __filter_info filterinfo[FILTER_OWNER_MAX];
	control_flag mirror_flag;
	uint32_t kernel_stack_flag;//0:use linux kernel; 1:use fastepath
	uint32_t detect_virus;
	uint32_t detect_virus_fast;
	uint32_t key_word_filter;
	uint32_t fwaudit;
    uint32_t s_portscan;
	uint32_t ddos_flag;//0:ddos defense disable; 1:ddos defense enable
	struct dpdk_log log;
	struct ndpi_struct_t * ndpist;
	struct Flow_table      ftab;
   	struct PktReassInfo *  pktreass;
	struct rte_ring *rss_rings[RTE_MAX_ETHPORTS];
};
//---------------------------------------------------------------
//for mirror
#if(ENABLE_MIRROR_FUNCTION == 1)
#define bpf_u_int32  int32_t
#define u_char		uint8_t
#define PCAP_ERRBUF_SIZE 256

struct _pcap_pkthdr {
	struct timeval ts;	/* time stamp */
	bpf_u_int32 caplen;	/* length of portion present */
	bpf_u_int32 len;	/* length this packet (off wire) */
};
struct pcap {
	int snapshot;
	int linktype;
	int tzoff;		/* timezone offset */
	int offset;		/* offset for proper alignment */

	int break_loop;		/* flag set to force break from packet-reading loop */

	//struct pcap_sf sf;
	//struct pcap_md md;

	/*
	 * Read buffer.
	 */
	int bufsize;
	u_char *buffer;
	u_char *bp;
	int cc;

	/*
	 * Place holder for pcap_next().
	 */
	u_char *pkt;

	char errbuf[PCAP_ERRBUF_SIZE + 1];
	int dlt_count;
	int *dlt_list;

	struct _pcap_pkthdr pcap_header;
	//add by buluedon
	uint32_t tag;
	int16_t flltarget;
	struct rte_mempool *pool;
};

#define MAX_PCAP_PACKET_SZ 1600
struct pcap_buf {
	struct pcap header;
	uint8_t data[MAX_PCAP_PACKET_SZ];
};
#endif
//---------------------------------------------------------------
#define MIN_SCHEDULE_TIMEMIN 30
//---------------------------------------------------------------
#define MBUF_CACHE_SIZE 512

#define MAX_PACKET_SZ		2048
#define MBUF_PRIVATE_SZ	384
#define DPDK_MBUF_SZ \
	(MAX_PACKET_SZ + sizeof(struct rte_mbuf) + RTE_PKTMBUF_HEADROOM)
	
#if(ENABLE_MIRROR_FUNCTION == 1)
#define PCAP_BUF_SZ \
	(sizeof(struct pcap)+MAX_PCAP_PACKET_SZ)
#endif

#define DPDK_PKTMBUF_POOLNAME  "DPDK_MBUF_POOL"
#define DPDK_NB_MBUFS  1500000
//#define DPDK_NB_MBUFS  (3 << 19) // DPDK_NB_MBUFS % MBUF_CACHE_SIZE == 0 

#if(ENABLE_MIRROR_FUNCTION == 1)
#define PCAP_PKTBUF_POLLNAME "DPDK_PCAP_POOL_%d_%d"
#define PCAP_BUFS_ONE	1024
#define PCAP_NB_BUFS 	(MAX_CLIENT_PARITY*2*PCAP_BUFS_ONE)
#endif

#define HDR_PKTMBUF_POOLNAME  "DPDK_HEADER_POOL"
#define	HDR_MBUF_SIZE	(sizeof(struct rte_mbuf) + 2 * RTE_PKTMBUF_HEADROOM)
#define HDR_MBUF_ONE    8192
#define	HDR_NB_MBUFS	(HDR_MBUF_ONE * RTE_MAX_ETHPORTS)

#define PACKET_READ_SIZE 64

#define ANALYZE_MAX_MBUF 128

#include "clientext_queue.h"
//---------------------------------------------------------------
void * dpdk_shm_alloc(struct system_info *sysinfo,const char *name,int size);
void  dpdk_shm_free(void *addr);
struct system_info * dpdk_queue_system_shm_init(int reset);
struct clientinfo *  client_register(const struct client_reginfo *reginfo);
int  client_unregister( struct clientinfo * client) ;
int  set_process_priority(struct clientinfo * client) ;

void dump_portinfo(void) ;
void dump_client(struct clientinfo * client) ;
void dump_system1(void) ;
void dump_system2(void) ;
void dump_mbuf(struct rte_mbuf * m);

int  dpdk_dequeue1(struct clientinfo * my,unsigned qnum,void **bufs, unsigned n);
int  dpdk_dequeue2(struct clientinfo * my,unsigned *qindex,void **bufs, unsigned n);
int  dpdk_dequeue3(struct clientinfo * my,struct subqueueinfo *sub_queue,unsigned *qindex,void **bufs, unsigned n);
int  dpdk_dequeue4(struct clientinfo * my,unsigned *qindex,void **bufs, unsigned n);
void  client_dequeue_stop( struct clientinfo * client);
int  dpdk_enqueue(struct clientinfo * my,struct rte_mbuf *buf) ;
int dpqk_priv_send(struct clientinfo * my,char *buf,unsigned len,uint8_t outport) ;
int  dpdk_mbuf_drop(struct clientinfo * my,struct rte_mbuf *buf) ;
void burst_free_mbufs(struct rte_mbuf **pkts, unsigned num);
#if ENABLE_MIRROR_FUNCTION == 1
int  dpdk_pcap_drop(struct clientinfo * my,struct pcap_buf *buf) ;
#endif

void detect_client(struct clientinfo *server) ;
void server_exit(struct clientinfo *server);


void idle_task(void);

void list_portmode(void);
int  set_portmode(struct system_info *sysinfo,uint8_t  portid,int mode,int value);
int set_mirror_port_rules(struct system_info *sysinfo, int dir);
//---------------------------------------------------------------
extern fp_debug_t *fpdebug;
extern volatile uint64_t *msec;
extern struct system_info  *get_dpdkshm(char *name,char *file_prefix);
extern struct system_info  *get_dpdk_shm_cpu(const char *name,const char *file_prefix,char *coremask,int dpdkthread);
extern void log2file(const char *format, ...);

#ifdef MCORE_DEBUG
#define FP_LOG(l, t, fmt, args...)                            			\
    do {                                                     			\
        static uint64_t time_last=0; 									\
        if (*msec- time_last > fpdebug->ratelimit) {  					\
            if (unlikely((FP_LOG_##l) <= fpdebug->level &&                			\
                (FP_LOGTYPE_##t) & fpdebug->type)) {             			\
                if (fpdebug->mode == FP_LOG_MODE_CONSOLE)        			\
                    printf( #t ": " fmt, ## args);           	 			\
                else if (fpdebug->mode == FP_LOG_MODE_FILE) {    			\
                    log2file(#t ": " fmt, ## args);           			\
                }                                             			\
                else {                                         			\
					syslog(FP_LOG_##l,#t ": " fmt, ## args); 					\
            	}														\
            }                                                 			\
            time_last = *msec;                           				\
        }                                                     			\
    } while(0)
#else
#define FP_LOG(l, t, fmt, args...)
#endif //MCORE_DEBUG
//---------------------------------------------------------------
void  filter_dump_byclinet(struct clientinfo *client);
void filter_dump_bysystem(struct system_info *system);
void  filter_dump_bymirror(struct mirror_info *m_info);

//---------------------------------------------------------------
#if(ENABLE_MIRROR_FUNCTION == 1)
typedef void (*_pcap_handler)(u_char *, const struct _pcap_pkthdr *,u_char *);
void dump_pcapbuf(struct pcap_buf  *buf);
void * mirror_open(struct client_reginfo *info,char *coremask);
void mirror_close(void *handle);
int mirror_loop(void *handle, int cnt, _pcap_handler callback,u_char *user);
#endif
//---------------------------------------------------------------

#ifdef  CONFIG_DPDK_FRAME_SERVER

enum DEVTYPE{
	E1000,
	E1000E,
	IGB,
	IXGBE,
	I40E,
	OTHER_EHT_TYPE,
	MDX_ETH_TYPE
};

#define RTE_MP_RX_DESC_DEFAULT 2048
#define RTE_MP_TX_DESC_DEFAULT 2048

#define ONE_G_PORT_RX_QUEUES   2
#define ONE_G_PORT_TX_QUEUES   2
#define TEN_G_PORT_RX_QUEUES   2
#define TEN_G_PORT_TX_QUEUES   2

/*
 * Configurable values of RX and TX ring threshold registers.
 */
#define RX_PTHRESH 8 /**< Default value of RX prefetch threshold register. */
#define RX_HTHRESH 8 /**< Default value of RX host threshold register. */
#define RX_WTHRESH 0 /**< Default value of RX write-back threshold register. */

#define TX_PTHRESH 32 /**< Default value of TX prefetch threshold register. */
#define TX_HTHRESH 0 /**< Default value of TX host threshold register. */
#define TX_WTHRESH 0 /**< Default value of TX write-back threshold register. */

struct port_rings {
	uint16_t rx_rings;
	uint16_t tx_rings ;
	uint16_t rx_ring_size;
	uint16_t tx_ring_size ;
};

struct kni_ctl {
	volatile uint32_t *fstop;
	void *get_kni_byport;
};

/* Total octets in ethernet header */
#define KNI_ENET_HEADER_SIZE    14
/* Total octets in the FCS */
#define KNI_ENET_FCS_SIZE       4

int get_ethtype_by_pci_addr(struct rte_pci_device *pci);

int  dpdk_enqueue_byeth(struct system_info *sysinfo,struct rte_mbuf *buf);
int dpdk_sysport_init(struct system_info *sysinfo,uint64_t portmask,void *port_callbk);
int dpdk_port_init(struct system_info *sysinfo,uint8_t port_num,
		 struct rte_eth_conf *port_conf,struct port_rings *portrings);
void dpdk_check_ports_link_status(struct portinfo *portinfos);
void init_kni_um(struct portinfo *portinfos,struct kni_ctl *knictl)  ;
void exit_kni_um(struct portinfo *portinfos);
int setetherstatus(const char *eth,int isup);

int port_input (struct system_info *sysinfo,struct rte_mbuf *buf,int cpu);
int port_input_bulk (struct system_info *sysinfo, struct rte_mbuf ** buf, uint16_t nb_pkts,int qid, int cpu);
int port_output (struct clientinfo *server_tx,struct rte_mbuf *buf,int qid,int cpu);
int port_output_bulk(struct clientinfo *server_tx, struct rte_mbuf * * buf, uint16_t nb_pkts, int qid,int cpu);
#endif
//---------------------------------------------------------------
//lib
int packet_tuple_analyzer(struct rte_mbuf *  mbuf,
                          struct rte_mbuf ** out_pkts,
	                      uint16_t           nb_pkts);

int packet_preprocessing(struct __filter_info *filinfo,struct rte_mbuf *mbuf);

int pingagent(struct rte_mbuf * mbuf);


//---------------------------------------------------------------
//check
#if  (SERVER_TX_QUEUES==0) 
#error  SERVER_TX_QUEUES should not be zero !!!!!!!!!!!!!!
#endif


#ifdef __cplusplus 
} 
#endif

#endif
