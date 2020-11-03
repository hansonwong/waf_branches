/*
 *  Exception Connections Analysis[ECA]
 */
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <signal.h>
#include <errno.h>
#include <fcntl.h>
#include <net/if.h>
#include <netinet/in.h>
#include <linux/netlink.h>
#include <linux/netfilter/nfnetlink.h>
#include <linux/netfilter/nfnetlink_conntrack.h>
#include <linux/netfilter/nf_conntrack_common.h>

#include "policyrun.h"
#include "util.h"
#include "connt.h"
#include "mem_manage.h"
#include "hlist.h"
#include "log.h"

#define TRACE_CONNECT(level, fmt, args...) do {              \
	TSE_LOG(TSE_LOG_##level, CONNECT, fmt "\n", ## args);     \
} while(0)



typedef int ( *CallBack )(struct sockaddr_nl *,struct nlmsghdr *, void * );

typedef struct NFctThreadVars_
{
    ThreadVars *tv;
	void * exdata;   /*public data*/
    char * data;     /** Per function and thread data */
    int    datalen;  /** Length of per function and thread data */
	
} NFctThreadVars;

NFctThreadVars NfctThread = {0};

typedef struct Nlsock_ {
    int sock;
    int seq;
    struct sockaddr_nl snl;
    char *name;
} Nlsock;

Nlsock nlsock = { -1, 0, {0}, "netlink-ct-cmd" };

static int NFctThreadInit(ThreadVars *tv, void *data);

static int NFctThreadDeinit(ThreadVars *t, void *data);

static int NFctLoop(ThreadVars *tv, void *data);

static void NFctThreadExit(ThreadVars *tv, void *data);


void NFctModuleRegister(void) 
{
	/*Global Vars init*/
	/*module*/
	module[NFCT_MODULE].ThreadInit   = NFctThreadInit;
	module[NFCT_MODULE].ThreadDeinit = NFctThreadDeinit;
	module[NFCT_MODULE].ThreadLoop   = NFctLoop;
	module[NFCT_MODULE].ThreadExit   = NFctThreadExit;
}

TseNFctTable * CreateCtTable()
{
	TseNFctTable * nfct;
	uint32_t size_nfct  = sizeof(TseNFctTable);
	uint32_t size_hmem  = mem_manage_memory_bytes(MAX_CT_HASH_NODE,sizeof(TseNFct));
	
	uint32_t base_hmem  = ALGIN_DATA(size_nfct, ALIGN_SIZE);
	uint32_t base       = base_hmem + ALGIN_DATA(size_hmem, ALIGN_SIZE);;
	
	nfct = (TseNFctTable *)malloc(base);
	if (nfct == NULL) {
		TRACE_CONNECT(WARNING,"TseNFctTable memory allocation failed");
		return NULL;
	}
	memset(nfct,0,base);

	nfct->entries = MAX_CT_HASH_NODE;
	nfct->buckets = MAX_CT_HASH_BUCKET;
	
	uint8_t *data = (uint8_t *)nfct + base_hmem;
	nfct->ctbuff  = mem_manage_init(nfct->entries,sizeof(TseNFct),data,size_hmem);
	if(nfct->ctbuff == NULL){
		TRACE_CONNECT(WARNING,"TseNFctTable init memory manage failed");
		free(nfct);
		nfct = NULL;
	}
	
	return nfct;
}

void FreeCtTable(TseNFctTable * nfct)
{
	if(nfct != NULL){
		free(nfct);
	}
}

static void DumpNFctInfo(const TseNFct * ctnode)
{
	if(ctnode == NULL){
		TRACE_CONNECT(WARNING,"nfct is null");
		return;
	}
	TRACE_CONNECT(DEBUG,"origin src ip:" IPQUAD_FORMAT ",dst ip:" IPQUAD_FORMAT ",src port:%u,dst port:%u,proto:%u",
		                 IPQUAD(ctnode->orig.ip_src),
		                 IPQUAD(ctnode->orig.ip_dst),
		                 ctnode->orig.port_src,
		                 ctnode->orig.port_dst,
		                 ctnode->orig.proto);
	TRACE_CONNECT(DEBUG,"reply src ip:" IPQUAD_FORMAT ",dst ip:" IPQUAD_FORMAT ",src port:%u,dst port:%u,proto:%u",
		                 IPQUAD(ctnode->reply.ip_src),
		                 IPQUAD(ctnode->reply.ip_dst),
		                 ctnode->reply.port_src,
		                 ctnode->reply.port_dst,
		                 ctnode->reply.proto);
}

static Nlsock * 
GetGlobalSock()
{
	return &nlsock;
}

static int 
NFctCreateSocket (Nlsock *nl, unsigned long groups )
{
    int ret;
    struct sockaddr_nl snl;
    uint32_t namelen;
	int sock;

    sock = socket(AF_NETLINK, SOCK_RAW, NETLINK_NETFILTER);
    if (sock < 0) {
		TRACE_CONNECT(ERR,"Can't open %s socket: %s",nl->name,strerror(errno));
        return -1;
    }
#if 0	
    ret = fcntl(sock, F_SETFL, O_NONBLOCK);
    if (ret < 0) {
        printf("Can't set %s socket flags: %s\n",nl->name,strerror(errno));
        goto err;
    }
#endif
    memset(&snl, 0, sizeof(snl));
    snl.nl_family = AF_NETLINK;
    snl.nl_groups = groups;

    /* Bind the socket to the netlink structure for anything. */
    ret = bind(sock, (struct sockaddr *)&snl, sizeof(snl));
    if (ret < 0) {
		TRACE_CONNECT(ERR,"Can't bind %s socket to group 0x%x: %s",
			               nl->name, snl.nl_groups, strerror(errno));
        goto err;
    }

    /* multiple netlink sockets will have different nl_pid */
    namelen = sizeof(snl);
    ret = getsockname(sock, (struct sockaddr *) &snl, &namelen);
    if (ret < 0 || namelen != sizeof(snl)) {
		TRACE_CONNECT(ERR,"Can't get %s socket name: %s",
			               nl->name,strerror(errno));

        goto err;
    }
	if (snl.nl_family != AF_NETLINK) {
		TRACE_CONNECT(ERR,"netlink protocol exception");
        goto err;		
	}
    nl->snl  = snl;
    nl->sock = sock;

    struct timeval tv;
    tv.tv_sec = 2;
    tv.tv_usec = 0;
    if(setsockopt(nl->sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) == -1) {
    	TRACE_CONNECT(WARNING,"can't set socket timeout: %s",strerror(errno));
    }
    return ret;
err:
	close(sock);
	return -1;
}


static int 
NFctThreadInit(ThreadVars *tv, void *data)
{
	//deal all sig at main thread
    sigset_t sigs;
    sigfillset(&sigs);
    pthread_sigmask(SIG_BLOCK, &sigs, NULL);
	
    NFctThreadVars *ctv  = (NFctThreadVars *) data;
	ThreadPool     *pool = (ThreadPool *)tv->threadpool;
	
    ctv->tv     = tv;
	ctv->exdata = pool->data;
	
    ctv->data = malloc(MAX_RECV_MSG_BUF);
	
    if (ctv->data == NULL) {
		TRACE_CONNECT(ERR,"%s():malloc memory fail!",__func__);
        return -1;
    }
    ctv->datalen = MAX_RECV_MSG_BUF;

	int	ret = NFctCreateSocket(GetGlobalSock(),(NF_NETLINK_CONNTRACK_NEW   | 
		                       		            NF_NETLINK_CONNTRACK_UPDATE| 
							   		            NF_NETLINK_CONNTRACK_DESTROY));
    if (ret < 0) {
		TRACE_CONNECT(ERR,"%s():ct thread %s failed to initialize!",__func__,tv->name);
        return -1;
    }
	return 0;
}


static int 
NFctThreadDeinit(ThreadVars *t, void *data)
{
    NFctThreadVars *ctv = (NFctThreadVars *)data;
	
    if (ctv->data != NULL) {
        free(ctv->data);
        ctv->data = NULL;
    }
    ctv->datalen = 0;
    TRACE_CONNECT(NOTICE,"starting... will close socket");
	Nlsock * nlsock = GetGlobalSock();
	if(nlsock->sock >= 0){
		close(nlsock->sock);
		nlsock->sock = -1;
	}
	return 0;
}

static uint32_t
NFctGetHashValue(const PacketTuple * p)
{
	uint32_t a =  p->ip_src;
	uint32_t b =  p->ip_dst;
	uint32_t c = (p->port_src | (p->port_dst << 16));
	
	c += p->proto;
	
	a -= b; a -= c; a ^= (c>>13);
	b -= c; b -= a; b ^= (a<<8); 
	c -= a; c -= b; c ^= (b>>13); 
	a -= b; a -= c; a ^= (c>>12); 
	b -= c; b -= a; b ^= (a<<16); 
	c -= a; c -= b; c ^= (b>>5); 
	a -= b; a -= c; a ^= (c>>3); 
	b -= c; b -= a; b ^= (a<<10); 
	c -= a; c -= b; c ^= (b>>15);
	return c;
}


static TseNFct *
NFctHashLookup(TseNFctTable * nfctab,
			   		 const PacketTuple * p,
			   		 int dir,
			   		 uint32_t hash)
{
	TseNFct *nct;
	struct hlist_node *node;
	if(dir == TSE_IP_CT_DIR_ORIGINAL){
		hlist_for_each_entry(nct,node,&nfctab->cthlist[dir][hash & (nfctab->buckets - 1)],origchain){
			if( memcmp(&nct->orig,p,sizeof(PacketTuple)) == 0 ){
				return nct;
			}
		}
	}
	else{
		hlist_for_each_entry(nct,node,&nfctab->cthlist[dir][hash & (nfctab->buckets - 1)],replychain){
			if( memcmp(&nct->reply,p,sizeof(PacketTuple)) == 0 ){
				return nct;
			}
		}		
	}
	return NULL;
}


static int 
NFctAddCtHash(struct Tacticsevolve * te,
	                const TseNFct *cp_nfct)
{
	uint32_t hash;
	uint32_t hash_reply;
	int dir;
	
	TseNFctTable * nfctab = te->nfctab;

	dir = TSE_IP_CT_DIR_ORIGINAL;   //default original
	hash = NFctGetHashValue(&cp_nfct->orig);
	
	DumpNFctInfo(cp_nfct);
	
	if(NFctHashLookup(nfctab,&cp_nfct->orig,dir,hash)){
		TRACE_CONNECT(INFO,"Already present in table src ip:" IPQUAD_FORMAT ",dst ip:" IPQUAD_FORMAT ",src port:%u,dst port:%u,proto:%u",
							 IPQUAD(cp_nfct->orig.ip_src),
							 IPQUAD(cp_nfct->orig.ip_dst),
							 cp_nfct->orig.port_src,
							 cp_nfct->orig.port_dst,
							 cp_nfct->orig.proto);

		return 0;
	}

	TseNFct * nfct = (TseNFct *)alloc_mem(nfctab->ctbuff);
	if(nfct == NULL){
		TRACE_CONNECT(WARNING,"%s():table is full, unable to add a new entry", __func__);
		return 0;
	}
	
	memset(nfct, 0, sizeof(TseNFct));
	nfct->orig.ip_src    = cp_nfct->orig.ip_src;
	nfct->orig.ip_dst    = cp_nfct->orig.ip_dst;
	nfct->orig.port_src  = cp_nfct->orig.port_src;
	nfct->orig.port_dst  = cp_nfct->orig.port_dst;
	nfct->orig.proto     = cp_nfct->orig.proto;
	nfct->reply.ip_src   = cp_nfct->reply.ip_src;
	nfct->reply.ip_dst   = cp_nfct->reply.ip_dst;
	nfct->reply.port_src = cp_nfct->reply.port_src;
	nfct->reply.port_dst = cp_nfct->reply.port_dst;
	nfct->reply.proto    = cp_nfct->reply.proto;
	
	hash_reply = NFctGetHashValue(&cp_nfct->reply);

	/* Add them to the hash table */
	hlist_add_head(&nfct->origchain,
	               &nfctab->cthlist[TSE_IP_CT_DIR_ORIGINAL][hash & (nfctab->buckets - 1)]);
	hlist_add_head(&nfct->replychain,
				   &nfctab->cthlist[TSE_IP_CT_DIR_REPLY][hash_reply & (nfctab->buckets - 1)]);

	nfctab->entries_used++;
	uint32_t cthash;
	struct TseHashNode * entry = GetHashNode(te,&nfct->orig,&cthash);
	TseCtStat(te,entry,&nfct->orig);

	TRACE_CONNECT(DEBUG,"%s():ADD SUCCESS", __func__);
	return 1;
}

static int 
NFctDelCtHash(struct Tacticsevolve * te,
                   const TseNFct *cp_nfct)
{
	uint32_t hash;
	uint32_t hash_reply;
	int dir;
	
	TseNFctTable * nfctab = te->nfctab;

	dir = TSE_IP_CT_DIR_ORIGINAL;   //default original
	hash = NFctGetHashValue(&cp_nfct->orig);
	
	DumpNFctInfo(cp_nfct);
	
	TseNFct * hct = NFctHashLookup(nfctab,&cp_nfct->orig,dir,hash);
	if(hct == NULL){
		TRACE_CONNECT(INFO,"Not in table src ip:" IPQUAD_FORMAT ",dst ip:" IPQUAD_FORMAT ",src port:%u,dst port:%u,proto:%u",
							 IPQUAD(cp_nfct->orig.ip_src),
							 IPQUAD(cp_nfct->orig.ip_dst),
							 cp_nfct->orig.port_src,
							 cp_nfct->orig.port_dst,
							 cp_nfct->orig.proto);

		return 0;
	}
	
	//hash_reply = NFctGetHashValue(&cp_nfct->reply);
	if(hlist_unhashed(&hct->origchain)==0){
		hlist_del(&hct->origchain);
	}
	if(hlist_unhashed(&hct->replychain)==0){
		hlist_del(&hct->replychain);
	}

	nfctab->entries_used--;
	free_mem(nfctab->ctbuff,hct);

	TRACE_CONNECT(DEBUG,"%s():DEL SUCCESS", __func__);
	return 1;
}


static void 
NFctParseNfattr(struct nfattr *tb[], int maxattr, struct nfattr *nfa, int len)
{
	while (NFA_OK(nfa, len)) {
		unsigned flavor = NFA_TYPE(nfa);
		if (flavor && flavor <= (unsigned)maxattr)
			tb[flavor] = nfa;

		nfa = NFA_NEXT(nfa, len);
	}
}

static int 
NFctParseCtIp(struct nfattr *attr,
			 	  TseNFct *nfct,
			 	  int mode)
{
	struct nfattr *tb[CTA_IP_MAX];

	NFctParseNfattr(tb, CTA_IP_MAX, NFA_DATA(attr), NFA_PAYLOAD(attr));
	
	if (!tb[CTA_IP_V4_SRC])
		return -1;
	if (mode == CTA_TUPLE_ORIG)
		nfct->orig.ip_src  = ntohl(*(uint32_t *)NFA_DATA(tb[CTA_IP_V4_SRC]));
	else
		nfct->reply.ip_src = ntohl(*(uint32_t *)NFA_DATA(tb[CTA_IP_V4_SRC]));

	if (!tb[CTA_IP_V4_DST])
		return -1;
	if (mode == CTA_TUPLE_ORIG)
		nfct->orig.ip_dst  = ntohl(*(uint32_t *)NFA_DATA(tb[CTA_IP_V4_DST]));
	else
		nfct->reply.ip_dst = ntohl(*(uint32_t *)NFA_DATA(tb[CTA_IP_V4_DST]));

	return 0;
}

static int
NFctParseCtProto(struct nfattr *attr,
			          TseNFct *nfct,
			          int mode)
{
	uint8_t proto;
	struct nfattr *tb[CTA_PROTO_MAX];
	
	NFctParseNfattr(tb, CTA_PROTO_MAX, NFA_DATA(attr), NFA_PAYLOAD(attr));

	if (!tb[CTA_PROTO_NUM]){
		return -1;
	}
	proto = *(uint8_t *)NFA_DATA(tb[CTA_PROTO_NUM]);
	if (proto == IPPROTO_TCP ||
	    proto == IPPROTO_UDP ||
	    proto == IPPROTO_SCTP||
	    proto == IPPROTO_GRE) 
	{
		if (!tb[CTA_PROTO_SRC_PORT] || !tb[CTA_PROTO_DST_PORT])
			return -1;

		if (proto == IPPROTO_GRE) {
			if (mode == CTA_TUPLE_ORIG) {
				nfct->orig.port_src  = 0;
				nfct->orig.port_dst  = 0;
				nfct->orig.proto     = proto;
			} else {
				nfct->reply.port_src = 0;
				nfct->reply.port_dst = 0;
				nfct->orig.proto     = proto;
			}
		} else {
			if (mode == CTA_TUPLE_ORIG) {
				nfct->orig.port_src  = ntohs(*(uint16_t *)NFA_DATA(tb[CTA_PROTO_SRC_PORT]));
				nfct->orig.port_dst  = ntohs(*(uint16_t *)NFA_DATA(tb[CTA_PROTO_DST_PORT]));
				nfct->orig.proto     = proto;
			} else {
				nfct->reply.port_src = ntohs(*(uint16_t *)NFA_DATA(tb[CTA_PROTO_SRC_PORT]));
				nfct->reply.port_dst = ntohs(*(uint16_t *)NFA_DATA(tb[CTA_PROTO_DST_PORT]));
				nfct->orig.proto     = proto;
			}
		} 
	}
	return 0;
}

static int
NFctGetTupleInfo(struct nfattr *cda[],
               		  TseNFct * nct)
{
	TseNFct *nfct = nct;
	struct nfattr  *attr;
	struct nfattr  *tb[CTA_TUPLE_MAX+1];
	int ret = 0;
	
	if (cda[CTA_TUPLE_ORIG] && cda[CTA_TUPLE_REPLY]){
		
		/* Parse ORIG tuple */
		attr = cda[CTA_TUPLE_ORIG];
		NFctParseNfattr(tb, CTA_TUPLE_MAX, NFA_DATA(attr), NFA_PAYLOAD(attr));

		if (!tb[CTA_TUPLE_PROTO]){
			TRACE_CONNECT(WARNING,"%s():Orig.message packet 5-tuple port error!",__func__);
			return -1;
		}
		ret = NFctParseCtProto(tb[CTA_TUPLE_PROTO], nfct, CTA_TUPLE_ORIG);
		if (ret < 0){
			TRACE_CONNECT(WARNING,"%s():Orig.parse conntrack proto fail!",__func__);
			return -1;
		}

		if (!tb[CTA_TUPLE_IP]){
			TRACE_CONNECT(WARNING,"%s():Orig.message packet 5-tuple ipaddr error!",__func__);
			return -1;			
		}
		
		ret = NFctParseCtIp(tb[CTA_TUPLE_IP], nfct, CTA_TUPLE_ORIG);
		if (ret < 0){
			TRACE_CONNECT(WARNING,"%s():Orig.parse conntrack ip fail!",__func__);
			return -1;
		}
		//printf("Parse ORIG tuple!\n");
		/* Parse REPLY tuple */
		attr = cda[CTA_TUPLE_REPLY];
		NFctParseNfattr(tb, CTA_TUPLE_MAX, NFA_DATA(attr), NFA_PAYLOAD(attr));
		
		if (!tb[CTA_TUPLE_PROTO]){
			TRACE_CONNECT(WARNING,"%s():Reply.message packet 5-tuple port error!",__func__);
			return -1;
		}

		ret = NFctParseCtProto(tb[CTA_TUPLE_PROTO], nfct, CTA_TUPLE_REPLY);
		if (ret < 0){
			TRACE_CONNECT(WARNING,"%s():Reply.parse conntrack proto fail!",__func__);
			return -1;
		}
		if (!tb[CTA_TUPLE_IP]){
			TRACE_CONNECT(WARNING,"%s():Reply.message packet 5-tuple ipaddr error!",__func__);
			return -1;			
		}
		
		ret = NFctParseCtIp(tb[CTA_TUPLE_IP], nfct, CTA_TUPLE_REPLY);
		if (ret < 0){
			TRACE_CONNECT(WARNING,"%s():Reply.parse conntrack ip fail!",__func__);
			return -1;
		}
		//printf("Parse REPLY tuple!\n");
	}
	return 0;
}


static void 
NFctNewConntrack (struct Tacticsevolve * te,const struct nlmsghdr *h)
{
	struct nfgenmsg * nfmsg;
	struct nfattr   * tb[CTA_MAX+1];
	uint32_t status = 0;
	int len;
	int ret = 0;

	nfmsg = NLMSG_DATA(h);
	len = h->nlmsg_len - NLMSG_SPACE (sizeof(struct nfgenmsg));
	
	if (len < 0) {
		TRACE_CONNECT(WARNING,"%s():bad length %d!",__func__,len);
		return ;
	}
	memset(tb, 0, sizeof(tb));
	NFctParseNfattr(tb, CTA_MAX, NFM_NFA(nfmsg), len);
	
	if (tb[CTA_STATUS]){
		status = ntohl(*(uint32_t *)NFA_DATA(tb[CTA_STATUS]));
		//printf("ntohl(%u) = %u\n",*(uint32_t *)NFA_DATA(tb[CTA_STATUS]),status);
	}

	TseNFct nct;
	memset(&nct,0,sizeof(TseNFct));
	
	if ( IPS_SEEN_REPLY & status){
		ret = NFctGetTupleInfo(tb,&nct);
		if (ret < 0){
			te->nfctab->errct++;
			return;
		}
		if (nct.orig.proto == IPPROTO_TCP  ||
		    nct.orig.proto == IPPROTO_UDP  ||
		    nct.orig.proto == IPPROTO_SCTP ||
		    nct.orig.proto == IPPROTO_GRE)
		{
			te->nfctab->newct += NFctAddCtHash(te,&nct);
		}
	}
	
	if ((IPS_CONFIRMED & status) && !(IPS_SEEN_REPLY & status)) {
		ret = NFctGetTupleInfo(tb,&nct);
		if (ret < 0){
			te->nfctab->errct++;
			return;
		}
		if (nct.orig.proto == IPPROTO_TCP || nct.orig.proto == IPPROTO_UDP) {
			te->nfctab->newct += NFctAddCtHash(te,&nct);
		}
	}
	return;
	
}


static void 
NFctDelConntrack (struct Tacticsevolve * te,const struct nlmsghdr *h)
{
	struct nfgenmsg *nfmsg;
	struct nfattr *tb[CTA_MAX + 1];
	int len;
	int ret;
	
	nfmsg = NLMSG_DATA(h);

	len = h->nlmsg_len - NLMSG_SPACE (sizeof(struct nfgenmsg));
	if (len < 0) {
		TRACE_CONNECT(WARNING,"%s():bad length %d!",__func__,len);
		return;
	}

	memset(tb, 0, sizeof(tb));
	NFctParseNfattr(tb, CTA_MAX, NFM_NFA(nfmsg), len);

	TseNFct nct;
	memset(&nct,0,sizeof(TseNFct));
	
	ret = NFctGetTupleInfo(tb,&nct);
	if (ret < 0){
		te->nfctab->errct++;
		return;
	}
	te->nfctab->delct += NFctDelCtHash(te,&nct);
	return;
}

static int 
NFctCallBack( struct sockaddr_nl *snl, struct nlmsghdr *h, void *arg )
{
	if(h == NULL)
		return 0;

	if(NFNL_SUBSYS_ID(h->nlmsg_type) != NFNL_SUBSYS_CTNETLINK){
		return 0;
	}

	struct Tacticsevolve * te = (struct Tacticsevolve *)arg;
	if(!te->enable[TSE_CONNECT]) return 0;
	switch(NFNL_MSG_TYPE(h->nlmsg_type)){

		case IPCTNL_MSG_CT_NEW:
			NFctNewConntrack(te,h);
			break;
		case IPCTNL_MSG_CT_DELETE:
			NFctDelConntrack(te,h);
			break;
		default:
			break;
	}
	return 0;
}
static void 
NFctMsgParse(Nlsock * nl,
				  NFctThreadVars *ntv,
				  CallBack func,
				  void *cb_arg)
{
	int status;
	int ret = 0;

	struct sockaddr_nl snl	 = {AF_NETLINK,0,0,0};
	struct nlmsghdr *nlmhdr;
	struct iovec  iov = { ntv->data, ntv->datalen };
	struct msghdr msg = {(void*)&snl, sizeof(snl), &iov, 1, NULL, 0, 0};

	//recv message
	status = recvmsg ( nl->sock, &msg, 0 );

	if ( status < 0 ) {
		switch(errno){
			case EINTR: 
				TRACE_CONNECT(WARNING,"Recv Message:The operation is interrupted by signal");
				break;//continue;
			case EBADF:
				TRACE_CONNECT(WARNING,"Invalid socket descriptor");
				/*exception*/
				break;
			case EINVAL:
				TRACE_CONNECT(WARNING,"Invalid parameter!");
				/*exception*/
				break;
			case EFAULT:
				TRACE_CONNECT(WARNING,"access memory space error!");
				/*exception*/
				break;
			case ENOMEM:
				TRACE_CONNECT(WARNING,"Don't have enough memory!");
				/*exception*/
				break;
			case ECONNREFUSED:
				TRACE_CONNECT(WARNING,"server refuse connect!");
				/*exception*/
				break;
			case EAGAIN:
				TRACE_CONNECT(WARNING,"block or timeout!");
				break;//continue;
			default:
				TRACE_CONNECT(WARNING,"%s recvmsg overrun!", nl->name);
				break;//continue;
		}
	}
	if (status == 0) {
		TRACE_CONNECT(NOTICE,"%s EOF\n",nl->name);
		/*exception*/
		return;
	}
	if (msg.msg_namelen != sizeof(snl)) {
		TRACE_CONNECT(WARNING,"%s sender address length error: length %d",nl->name,msg.msg_namelen );
		/*exception*/
		return;
	}
/*	
	msg parse
	for ( nlmhdr = ( struct nlmsghdr * ) msgbuf;
	      NLMSG_OK ( nlmhdr, status );
	      nlmhdr = NLMSG_NEXT ( nlmhdr, status ) ) {
*/
	for ( nlmhdr = ( struct nlmsghdr * ) ntv->data; 
		  NLMSG_OK ( nlmhdr, status );
		  status -= NLMSG_ALIGN(status),
		  nlmhdr = (struct nlmsghdr*)((char*)nlmhdr + NLMSG_ALIGN(status)))
	{
		/* Finish of reading. */
		if ( nlmhdr->nlmsg_type == NLMSG_DONE )
			//end of all message
			break;

            /* Error message. */
		if ( nlmhdr->nlmsg_type == NLMSG_ERROR ) {
			break;
		}

		/* skip unsolicited messages originating from command socket */
		if ( nlmhdr->nlmsg_pid == nl->snl.nl_pid) {
			continue;
		}

		ret = ( *func ) ( &snl, nlmhdr, cb_arg );
		if ( ret < 0 ) {
			TRACE_CONNECT(NOTICE, "%s callback function error", nl->name );
		}
	}

	/* After error care. */
	if ( msg.msg_flags & MSG_TRUNC ) {
		TRACE_CONNECT(NOTICE,"%s error: message truncated",nl->name);
		/*exception*/
		return;
	}
	if ( status ) {
		TRACE_CONNECT(NOTICE,"%s error: data remnant size %d",nl->name,status);
		/*exception*/
		return;
	}
    return;	
}

static int 
NFctLoop(ThreadVars *tv, void *data)
{
    NFctThreadVars *ntv = (NFctThreadVars *)data;
	Nlsock * nlsock = GetGlobalSock();
    while(1) {
        if (tce_ctl_flags != 0) {
			
			if(nlsock->sock >= 0){
				close(nlsock->sock);
				nlsock->sock = -1;
			}
            break;
        }
        NFctMsgParse(nlsock, ntv, NFctCallBack, ntv->exdata);
		//usleep(1);
    }
	return 0;
	
}


static void 
NFctThreadExit(ThreadVars *tv, void *data)
{
    NFctThreadVars *ctv = (NFctThreadVars *)data;
	struct Tacticsevolve * te = (struct Tacticsevolve *)ctv->exdata;
	TseNFctTable * ctb = te->nfctab;
	TRACE_CONNECT(NOTICE,"(%s) Add CT: %u, Del CT: %u, Err CT: %u",
                        tv->name,ctb->newct,ctb->delct,ctb->errct);
	TRACE_CONNECT(NOTICE,"Total HashNode: %u,Used HashNode: %u",ctb->entries, ctb->entries_used);

}

static NFctThreadVars * NFctGetCtThreadVar()
{
	return &NfctThread;
}

int RunNFctDoCT(ThreadPool * tpool)
{
    ThreadVars *tv = ThreadAlloc(tpool);
	if(tv == NULL){
		TRACE_CONNECT(ERR,"%s():install CT thread fail!",__func__);
		return -1;
	}

	memset(tv, 0, sizeof(ThreadVars));
	snprintf(tv->name, sizeof(tv->name), "NFct-DO-CT");

	/* default state for every newly created thread */
	ThreadsSetFlag(tv,THV_PAUSE);
	ThreadsSetFlag(tv,THV_USE);

	/* default aof for every newly created thread */
	tv->trf     = &module[NFCT_MODULE];
	tv->aof     = THV_RESTART_THREAD;
	tv->id      = GetThreadID();
	tv->type    = TVT_PPT;
	tv->tm_func = ThreadRun;

	tv->data    = NFctGetCtThreadVar();
	tv->threadpool = (void *)tpool;

	if (ThreadStart(tv) != 0) {
		TRACE_CONNECT(ERR,"%s():start connect thread %s fail!",__func__,tv->name);
		exit(-1);
	}
    return 0;
}




