#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <signal.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdint.h>
#include <arpa/inet.h>
#include <linux/types.h>
#include <linux/netfilter.h>
#include <linux/netfilter/nfnetlink.h>
#include <linux/netfilter/nfnetlink_queue.h>

#include "policyrun.h"
#include "thread.h"
#include "nfq.h"
#include "tse.h"
#include "util.h"
#include "log.h"

#define MAX_ALREADY_TREATED 5
#define NFQ_VERDICT_RETRY_TIME 3

#ifndef SOL_NETLINK
#define SOL_NETLINK 270
#endif

//#define NFQ_DFT_QUEUE_LEN NFQ_BURST_FACTOR * MAX_PENDING
//#define NFQ_NF_BUFSIZE 1500 * NFQ_DFT_QUEUE_LEN

#define TRACE_NFQ(level, fmt, args...) do {              \
	TSE_LOG(TSE_LOG_##level, NFQ, fmt "\n", ## args);     \
} while(0)


#define NFQEnter(...) do{}while(0)

static NFQThreadVars nfq_t[NFQ_MAX_QUEUE];
static NFQQueueVars  nfq_q[NFQ_MAX_QUEUE];
static uint16_t receive_queue_num = 0;

static int NFQRecvPktThreadInit(ThreadVars *tv, void *data);

static int NFQRecvPktThreadDeinit(ThreadVars *t, void *data);

static int NFQRecvPktLoop(ThreadVars *tv, void *data);

static void NFQRecvPktThreadExit(ThreadVars *tv, void *data);

/**
 *  \brief Get a pointer to the NFQ queue at index
 *
 *  \param number idx of the queue in our array
 *
 *  \retval ptr pointer to the NFQThreadVars at index
 *  \retval NULL on error
 */
static void *
NFQGetQueue(int number) 
{
    if (number >= receive_queue_num)
        return NULL;

    return (void *)&nfq_q[number];
}

/**
 *  \brief Get a pointer to the NFQ thread at index
 *
 *  This function is temporary used as configuration parser.
 *
 *  \param number idx of the queue in our array
 *
 *  \retval ptr pointer to the NFQThreadVars at index
 *  \retval NULL on error
 */
static void *
NFQGetThread(int number) 
{
    if (number >= receive_queue_num)
        return NULL;

    return (void *)&nfq_t[number];
}

/**
 *  \brief Get count of Registered Netfilter queue
 *
 */
static int 
NFQGetQueueCount(void)
{
	return receive_queue_num;
}
void NFQRecvPktModuleRegister(void) 
{
	/*Global Vars init*/
	
	/*module*/
	module[NFQRECVPKT_MODULE].ThreadInit   = NFQRecvPktThreadInit;
	module[NFQRECVPKT_MODULE].ThreadDeinit = NFQRecvPktThreadDeinit;
	module[NFQRECVPKT_MODULE].ThreadLoop   = NFQRecvPktLoop;
	module[NFQRECVPKT_MODULE].ThreadExit   = NFQRecvPktThreadExit;
}

/**
 * \brief Read packet info data buffer,Decode ipv4 5 tuple
 */
static int 
NFQDecodePacket(Packet * p,unsigned char *data)
{
	struct ipv4_hdr *ipv4_hdr;	
	struct udp_hdr  *udp_hdr;
	struct tcp_hdr  *tcp_hdr;
	
	ipv4_hdr = (struct ipv4_hdr *)data;

	if((ipv4_hdr->version_ihl>>4 & 0xf) != 4) {
		TRACE_NFQ(WARNING,"packet is not ipv4");
		return -1;
	}
	
	p->pt5.proto  = ipv4_hdr->next_proto_id;
	p->pt5.ip_src = ntohl(ipv4_hdr->src_addr);
	p->pt5.ip_dst = ntohl(ipv4_hdr->dst_addr);

	uint32_t iphdr_len = (ipv4_hdr->version_ihl & 0xf)<<2;
	
	switch(p->pt5.proto){
		case IPPROTO_TCP:
			tcp_hdr = (struct tcp_hdr *)(data + iphdr_len);
			p->pt5.port_src = ntohs(tcp_hdr->src_port);
			p->pt5.port_dst = ntohs(tcp_hdr->dst_port);
			break;
		case IPPROTO_UDP:
			udp_hdr = (struct udp_hdr *)(data + iphdr_len);
			p->pt5.port_src = ntohs(udp_hdr->src_port);
			p->pt5.port_dst = ntohs(udp_hdr->dst_port);	
			break;
		default:
			TRACE_NFQ(WARNING,"packet protocol is not tcp or udp");
			return -1;
	}
	
	return 0;
}

/**
 * \brief Read data from nfq message and setup Packet
 *
 * \note
 * In case of error, this function verdict the packet
 * to avoid skb to get stuck in kernel.
 */
static int 
NFQSetupPkt (Packet *p, struct nfq_q_handle *qh, void *data)
{
	int ret;
	unsigned char * pktdata;
	struct nfqnl_msg_packet_hdr * ph;
	struct nfqnl_msg_packet_hw	* hwph;
	struct nfq_data *nfa = (struct nfq_data *)data;
	
	ph = nfq_get_msg_packet_hdr(nfa);
	if (ph){
		p->packet_id = ntohl(ph->packet_id);
		p->hw_proto	 = ntohs(ph->hw_protocol);
		p->hook		 = ph->hook;
	}
	
	hwph = nfq_get_packet_hw(nfa);
	if(hwph){
		p->hw_addrlen = ntohs(hwph->hw_addrlen);
		memcpy(p->hw_addr,hwph->hw_addr,sizeof(hwph->hw_addr));	
	}
	
	p->indev 	  = nfq_get_indev(nfa);
	p->outdev	  = nfq_get_outdev(nfa);
	p->physindev  = nfq_get_physindev(nfa);
	p->physoutdev = nfq_get_physoutdev(nfa);
	p->mark		  = nfq_get_nfmark(nfa);
	
    p->verdicted  = 0;

	ret = nfq_get_payload(nfa, &pktdata);

    if (ret > 0) {
		p->pkt_len = ret + ETHER_HEAD_SIZE;
    } else if (ret ==  -1) {
    	p->pkt_len = 0;
    }

    ret = nfq_get_timestamp(nfa, &p->ts);
    if (ret != 0) {
        memset (&p->ts, 0, sizeof(struct timeval));
        gettimeofday(&p->ts, NULL);
    }

	ret = NFQDecodePacket(p,pktdata);

	if(ret < 0) return -1;
	
    return 0;
}

static int 
NFQCallBack(struct nfq_q_handle *qh, 
                struct nfgenmsg *nfmsg,
                struct nfq_data *nfa,
                void *data)
{
    NFQThreadVars *ntv   = (NFQThreadVars *)data;
    //ThreadVars    *tv    = ntv->tv;
	NFQQueueVars  *nfq_q = NFQGetQueue(ntv->nfq_index);
    int ret;

	//get packet id
	Packet p = {0};

	p.nfq_index = ntv->nfq_index;
	ret = NFQSetupPkt(&p, qh, (void *)nfa);

	if(ret < 0){
#ifdef COUNTERS
        nfq_q->errs++;
        nfq_q->pkts++;
        nfq_q->bytes += p->pkt_len;
#endif /* COUNTERS */
		goto verdict;
	}

#ifdef COUNTERS
	nfq_q->pkts++;
	nfq_q->bytes += p->pkt_len;
#endif /* COUNTERS */

	ret = TsePacketRelease(ntv->exdata,&p);
	//printf("%s\n",ret == 0 ? "DROP":"ACCEPT");
verdict:
	return nfq_set_verdict(nfq_q->qh,p.packet_id,NF_ACCEPT,0,NULL);
}

static int 
NFQInitThread(NFQThreadVars *nfq_t, uint32_t queue_maxlen)
{
	int nfq_index = nfq_t->nfq_index;

    NFQQueueVars *nfq_q = NFQGetQueue(nfq_index);
    if (nfq_q == NULL) {
        TRACE_NFQ(WARNING,"no queue for given index %d",nfq_index);
        return -1;
    }

    TRACE_NFQ(INFO,"%d:opening nfq library handle",nfq_index);
    nfq_q->h = nfq_open();
    if (!nfq_q->h) {
        TRACE_NFQ(WARNING,"%d:error during nfq_open()",nfq_index);
        return -1;
    }

	TRACE_NFQ(INFO,"%d:unbinding existing nf_queue handler for AF_INET (if any)",nfq_index);
	if (nfq_unbind_pf(nfq_q->h,AF_INET) < 0){
		TRACE_NFQ(WARNING,"%d:error during nfq_unbind_pf()",nfq_index);
		return -1;
  	}
	TRACE_NFQ(INFO,"%d:binding nfnetlink_queue as nf_queue handler for AF_INET",nfq_index);
	if (nfq_bind_pf(nfq_q->h,AF_INET) < 0) {
		TRACE_NFQ(WARNING,"error during nfq_bind_pf()");
    	return -1;
	}
	
    TRACE_NFQ(INFO,"binding this thread %d to queue '%u'",nfq_index,nfq_q->queue_num);
	
    nfq_q->qh = nfq_create_queue(nfq_q->h, nfq_q->queue_num, &NFQCallBack, (void *)nfq_t);
	
    if (nfq_q->qh == NULL){
    	TRACE_NFQ(WARNING,"%d:error during nfq_create_queue()",nfq_index);
        return -1;
    }
	
    TRACE_NFQ(INFO,"%d:setting copy_packet mode",nfq_index);

    /* 05DC = 1500 */
    //if (nfq_set_mode(nfq_t->qh, NFQNL_COPY_PACKET, 0x05DC) < 0) {
    if (nfq_set_mode(nfq_q->qh, NFQNL_COPY_PACKET, 0xFFFF) < 0) {
        TRACE_NFQ(WARNING,"%d:can't set packet_copy mode",nfq_index);
        return -1;
    }
	
    if (queue_maxlen > 0) {
		
        TRACE_NFQ(INFO,"%d:setting queue length to %u",nfq_index,queue_maxlen);
		
        /* non-fatal if it fails */
        if (nfq_set_queue_maxlen(nfq_q->qh, queue_maxlen) < 0) {
            TRACE_NFQ(WARNING,"%d:can't set queue maxlen: your kernel probably "
                              "doesn't support setting the queue length %u",
                              nfq_index,queue_maxlen);
        }
    }
	
	nfq_q->nh = nfq_nfnlh(nfq_q->h);
	nfq_q->fd = nfnl_fd(nfq_q->nh);
	
    /* set netlink buffer size to a decent value */
    nfnl_rcvbufsiz(nfq_q->nh, queue_maxlen * 1500);
    TRACE_NFQ(INFO,"%d:setting nfnl bufsize to %u",nfq_index,queue_maxlen * 1500);
	
    //lock init

    /* Set some netlink specific option on the socket to increase performance */
	int opt = 1;
	
#ifdef NETLINK_BROADCAST_SEND_ERROR
    if (setsockopt(nfq_q->fd, SOL_NETLINK,
                   NETLINK_BROADCAST_SEND_ERROR, &opt, sizeof(int)) == -1) {
        TRACE_NFQ(WARNING,"%d:can't set netlink broadcast error: %s",nfq_index,strerror(errno));
    }
#endif
    /* Don't send error about no buffer space available but drop the
	packets instead */
#ifdef NETLINK_NO_ENOBUFS
    if (setsockopt(nfq_q->fd, SOL_NETLINK,NETLINK_NO_ENOBUFS, &opt, sizeof(int)) == -1) {
        TRACE_NFQ(WARNING,"%d:can't set netlink enobufs: %s",nfq_index,strerror(errno));
    }
#endif

#ifdef HAVE_NFQ_SET_QUEUE_FLAGS
	/*
    requires Linux kernel >= 3.6
    the kernel will accept the packets if the kernel queue gets full. 
    If this flag is not set, the default action in this case is to drop packets.
    */
	uint32_t flags = NFQA_CFG_F_FAIL_OPEN;
	uint32_t mask  = NFQA_CFG_F_FAIL_OPEN;
	int r = nfq_set_queue_flags(nfq_q->qh, mask, flags);
	if (r == -1) {
		TRACE_NFQ(WARNING,"%d:can't set fail-open mode: %s",nfq_index,strerror(errno));
	} else {
		TRACE_NFQ(WARNING,"%d:fail-open mode should be set on queue",nfq_index);
	}
#endif

    /* set a timeout to the socket so we can check for a signal
     * in case we don't get packets for a longer period. */
    struct timeval tv;
    tv.tv_sec = 1;
    tv.tv_usec = 0;
	
    if(setsockopt(nfq_q->fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) == -1) {
        TRACE_NFQ(WARNING,"%d:can't set socket timeout: %s",nfq_index,strerror(errno));
    }
	
    return 0;
	
}

static int 
NFQRecvPktThreadInit(ThreadVars *tv, void *data) 
{
	int ret;

	//deal all sig at main thread
    sigset_t sigs;
    sigfillset(&sigs);
    pthread_sigmask(SIG_BLOCK, &sigs, NULL);
	
    NFQThreadVars *ntv  = (NFQThreadVars *) data;
	ThreadPool    *pool = (ThreadPool *)tv->threadpool;
	
    ntv->tv = tv;
	ntv->exdata = pool->data;
	
    ret = NFQInitThread(ntv, (MAX_PACKETS_LEN * NFQ_BURST_FACTOR));
    if (ret < 0) {
        TRACE_NFQ(ERR,"%s:nfq thread %d failed to initialize!",__func__,ntv->nfq_index);
        exit(-1);
    }
	
    ntv->data = malloc(NFQ_RECV_DATA_BUF_SIZE);
	
    if (ntv->data == NULL) {
		TRACE_NFQ(ERR,"%s:malloc memory fail!",__func__);
        return -1;
    }
    ntv->datalen = NFQ_RECV_DATA_BUF_SIZE;
	
    return 0;
}


static int 
NFQRecvPktThreadDeinit(ThreadVars *t, void *data)
{
    NFQThreadVars *ntv = (NFQThreadVars *)data;
    NFQQueueVars  *nq  = NFQGetQueue(ntv->nfq_index);

    if (ntv->data != NULL) {
        free(ntv->data);
        ntv->data = NULL;
    }
    ntv->datalen = 0;

    TRACE_NFQ(INFO,"starting... will close queuenum %u", nq->queue_num);
    if (nq->qh) {
        nfq_destroy_queue(nq->qh);
        nq->qh = NULL;
    }
	
    return 0;
}

/**
 *  \brief Add a Netfilter queue
 *
 *  \param string with the queue name
 *
 *  \retval 0 on success.
 *  \retval -1 on failure.
 */
int 
NFQRegisterQueue(char *queue)
{
    NFQThreadVars *ntv = NULL;
    NFQQueueVars  *nq  = NULL;
	
    if (receive_queue_num >= NFQ_MAX_QUEUE) {
        TRACE_NFQ(WARNING,"too much Netfilter queue registered (%d)",
			    receive_queue_num);
        return -1;
    }
    if (receive_queue_num == 0) {
        memset(&nfq_t, 0, sizeof(nfq_t));
        memset(&nfq_q, 0, sizeof(nfq_q));
    }
	
    /* Extract the queue number from the specified command line argument */
    uint16_t queue_num = 0;
    if ((ByteExtractStringUint16(&queue_num, 10, strlen(queue), queue)) < 0){
        TRACE_NFQ(WARNING,"specified queue number %s is not valid", queue);
        return -1;
    }
	
    ntv = &nfq_t[receive_queue_num];
    ntv->nfq_index = receive_queue_num;

    nq = &nfq_q[receive_queue_num];
    nq->queue_num = queue_num;
	
    receive_queue_num++;

    TRACE_NFQ(INFO,"Queue \"%s\" registered.", queue);
    return 0;
}

/**
 * \brief NFQ function to get a packet from the kernel
 */
static void 
NFQRecvPkt(NFQQueueVars *t, NFQThreadVars *tv) 
{
    int recv_bytes, ret;
	
    int flag = 0 ? MSG_DONTWAIT : 0;  //wait or nowait
	
    recv_bytes = recv(t->fd, tv->data, tv->datalen, flag);

    if (recv_bytes < 0) {
        if (errno == EINTR || errno == EWOULDBLOCK) {
            /* no error on timeout */
            if (flag)
                //NFQVerdictCacheFlush(t);
                NFQEnter();
        } 
		else {
			t->errs++;
		}
		
    } else if(recv_bytes == 0) {
    
    	TRACE_NFQ(WARNING,"%s:recv got return code 0",__func__);
		
    } else {
    
        //printf("NFQRecvPkt: t %p, rv = %" PRId32 "\n", t, rv);
        
        if (t->qh != NULL) {
			
            ret = nfq_handle_packet(t->h, tv->data, recv_bytes);
			
        } else {
        
            TRACE_NFQ(WARNING,"%s:NFQ handle %d has been destroyed",__func__,t->nfq_index);
            ret = -1;
			
        }
		
        if (ret != 0) {
            TRACE_NFQ(WARNING,"nfq_handle_packet error %u", ret);
        }
    }
}

/**
 *  brief Main NFQ reading Loop function
 */
static int 
NFQRecvPktLoop(ThreadVars *tv, void *data)
{

    NFQThreadVars *ntv = (NFQThreadVars *)data;
    NFQQueueVars  *nq  =  NFQGetQueue(ntv->nfq_index);
	
    while(1) {
        if (tce_ctl_flags != 0) {
			
            if (nq->qh) {
                nfq_destroy_queue(nq->qh);
                nq->qh = NULL;
            } 
            break;
        }
        NFQRecvPkt(nq, ntv);
    }
	
	return 0;
	
}

static void 
NFQRecvPktThreadExit(ThreadVars *tv, void *data) 
{
    NFQThreadVars *ntv = (NFQThreadVars *)data;
    NFQQueueVars  *nq  = NFQGetQueue(ntv->nfq_index);

    TRACE_NFQ(NOTICE,"(%s) Treated: Pkts %u, Bytes %lu, Errors %u",
              tv->name, nq->pkts, nq->bytes, nq->errs);
    TRACE_NFQ(NOTICE,"(%s) Verdict: Accepted %u, Dropped %u, Replaced %u",
              tv->name, nq->accepted, nq->dropped, nq->replaced);

}


int RunNFQRecvPacket(ThreadPool * tpool)
{
    ThreadVars *tv = NULL;

    int nqueue = NFQGetQueueCount();

	int i;
    for (i = 0; i < nqueue; i++) {

		NFQQueueVars * nfa_q = NFQGetQueue(i);
		
		if(nfa_q->flags & NFQ_QUEUE_NONE){
			TRACE_NFQ(WARNING,"Config queue %d fail!",i);
			return -1;
		}
		
		tv = ThreadAlloc(tpool);
		if(tv == NULL){
			TRACE_NFQ(WARNING,"%d:install thread fail!",i);
			return -1;
		}

		memset(tv, 0, sizeof(ThreadVars));

		snprintf(tv->name, sizeof(tv->name), "Worker-Q-%d", nfa_q->queue_num);

		/* default state for every newly created thread */
		ThreadsSetFlag(tv,THV_PAUSE);
		ThreadsSetFlag(tv,THV_USE);

		/* default aof for every newly created thread */
		tv->trf     = &module[NFQRECVPKT_MODULE];	
		tv->aof     = THV_RESTART_THREAD;
		tv->id      = GetThreadID();
		tv->type    = TVT_PPT;
		tv->tm_func = ThreadRun;
		
		tv->data    = NFQGetThread(i);
		tv->threadpool = (void *)tpool;
	
        if (ThreadStart(tv) != 0) {
			TRACE_NFQ(ERR,"start thread %d fail!",i);
            exit(-1);
        }
    }

    return 0;
}



