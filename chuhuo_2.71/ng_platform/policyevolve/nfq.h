#ifndef __NFQ_H__
#define __NFQ_H__

#include <libnetfilter_queue/libnetfilter_queue.h>

#include "thread.h"

//max subport 16 queues 
#define NFQ_MAX_QUEUE 16

#define MAX_PACKETS_LEN  8192
#define NFQ_BURST_FACTOR 4

#define NFQ_RECV_DATA_BUF_SIZE 66000 

#define ETHER_HEAD_SIZE 14

#define NFQ_QUEUE_NONE 0x0001
#define NFQ_QUEUE_STOP 0x0002
#define NFQ_QUEUE_USED 0x0004

typedef struct NFQThreadVars_
{
    uint16_t nfq_index;
    ThreadVars *tv;
	void * exdata;   /*public data*/
    char * data;     /** Per function and thread data */
    int    datalen;  /** Length of per function and thread data */
	
} NFQThreadVars;


typedef struct NFQQueueVars_
{
    int fd;
	int flags;
    struct nfq_handle *h;
    struct nfnl_handle *nh;
    struct nfq_q_handle *qh;

    /* this one should be not changing after init */
    uint16_t queue_num;
    /* position into the NFQ queue var array */
    uint16_t nfq_index;
	
    /* counters */
	uint64_t bytes;
    uint32_t pkts;
    uint32_t errs;
    uint32_t accepted;
    uint32_t dropped;
    uint32_t replaced;
    struct {
        uint32_t packet_id; /* id of last processed packet */
        uint32_t verdict;
        uint32_t mark;
        uint8_t mark_valid:1;
        uint8_t len;
        uint8_t maxlen;
    } verdict_cache;
} NFQQueueVars;


void NFQRecvPktModuleRegister(void);

int NFQRegisterQueue(char *queue);

int RunNFQRecvPacket(ThreadPool * tpool);


#endif /* __NFQ_H__ */








