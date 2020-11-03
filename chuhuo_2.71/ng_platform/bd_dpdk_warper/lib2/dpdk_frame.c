#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <sys/stat.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/ioctl.h>

#include "dpdk_frame.h"
#include "hash.h"
#include "bridge_simple.h"

#include "dpdk_reass.h"
#include "flow.h"
#include "dpi.h"
#include "ddos.h"

fp_debug_t *fpdebug;
volatile uint64_t *msec;
static uint8_t hook2filter[8] = {
	FILTER_DPDK_FRAME,
	FILTER_DPDK_FRAME,
	FILTER_DPDK_FRAME,
	
#if(ENABLE_MIRROR_FUNCTION == 1)
	FILTER_MIRROR_IN,	
	FILTER_MIRROR_OUT,
#endif
};
static const char *filter_name[FILTER_OWNER_MAX] = {
	"FILTER_DPDK_FRAME",
		
#if(ENABLE_MIRROR_FUNCTION == 1)
	"FILTER_MIRROR_IN",
	"FILTER_MIRROR_OUT",
#endif
};
//---------------------------------------------------------------
#ifdef BRIDGE_ON
#define OUTPUT_MODE_CHECK(buf,port)		\
	switch(buf->userdef){						\
		case  DEF_USER_MODE:				\
		case  DEF_KERNEL_MODE:				\
		case ADVANCED:						\
		case INVALID_MODE:                                      \
			break;							\
		case NAT_PORT:						\
			break;							\
		case LOOP:/*port=buf->inport;*/		\
			break;							\
		case DIRECT_CONNECT:/*port=workmode[port].value;*/ \
			break;							\
		case BRIDGE_SIMPLE:					\
		case MIRROR_PORT:					\
			if(unlikely(buf->inport ==port) ){	\
				printf("port %d is loop,drop it!\n",port);\
				rte_pktmbuf_free(buf);		\
				return -1;					\
			}								\
			break;							\
		case BYPASS:							\
		default:								\
			DPDK_LOG(ERR,PLATFORM,"Line:%d OUTPUT_MODE_CHECK buf->userdef=%u\n",__LINE__,buf->userdef); \
			rte_pktmbuf_free(buf);			\
			return 0;							\
	}
#else
#define OUTPUT_MODE_CHECK(buf,port)		\
	switch(buf->userdef){						\
		case  DEF_USER_MODE:				\
		case  DEF_KERNEL_MODE:				\
		case ADVANCED:						\
		case INVALID_MODE:                                      \
			break;							\
		case NAT_PORT:						\
			break;							\
		case LOOP:/*port=buf->inport;*/		\
			break;							\
		case DIRECT_CONNECT:/*port=workmode[port].value;*/ \
			break;							\
		case BRIDGE_SIMPLE:					\
		case MIRROR_PORT:					\
			break;							\
		case BYPASS:							\
		default:								\
			DPDK_LOG(ERR,PLATFORM,"Line:%d OUTPUT_MODE_CHECK buf->userdef=%u\n",__LINE__,buf->userdef); \
			rte_pktmbuf_free(buf);			\
			return 0;							\
	}
#endif
//------------------------------------------------------------------------------
//common
static struct system_info *
get_dpdk_system(void) {
	const struct rte_memzone *mz;
	mz = rte_memzone_lookup(SYSTEM_INFO);
	if (mz == NULL)
		rte_exit(EXIT_FAILURE, "Cannot get %s\n",SYSTEM_INFO);
	return mz->addr;
}
//------------------------------------------------------------------------------
//filter
static uint64_t
filter_name2maks(const char *name){
	printf("filter name=%s\n",name);
	return 1;	
}

 #define DIM_MAX 8
 #define DIM_SIP 0
 #define DIM_DIP 1
 #define DIM_PROTO 2
 #define DIM_SPORT 3
 #define DIM_DPORT 4
 #define DIM_INPORT 5
 #define DIM_TARGET 6
 #define DIM_OUTPORT 7

 #define CLIENT_MAX_FILTER 		16
 #define FILTER_BY_MARK 0
 #define FILTER_BY_TUPLE5  1
struct __filter {
	int type;
	int cnt;
	union {
		uint32_t range[DIM_MAX][2];
		uint64_t mark[CLIENT_MAX_FILTER];
	};
};
static int filter_parse(const char *filter_rule,struct __filter *_filter){
	int k=0,i=0,m,res;
	char *r,*p[20]={0};
	char rule[128];
	char buf[4][16];
	strcpy(rule,filter_rule);
	r=rule;
	p[k++]=r;

	while(*r){
		if(*r==','){
			if(k>20) {
				printf("error: filter rule too long!\n");
				return -1;
			}
			p[k++]=r+1; 
			*r=0;
		}
		r++;
	}
	if(0==strncasecmp(p[0],"mark",strlen("mark"))) {
		_filter->type=FILTER_BY_MARK;
		_filter->cnt=k;
		res=sscanf(p[0],"%*[^:]:%s",buf[0]);
		if(res<1)
			goto err_value;
		p[0]=buf[0];
		for(i=0;i<k;i++){
			m=atol(p[i]);
			if(m==0) 
				m=filter_name2maks(p[i]);
			if(m==-1)
				goto err_value;
			_filter->mark[i]=m;
		}
	}else  {
		_filter->type=FILTER_BY_TUPLE5;
		_filter->cnt=1;
		for(i=0;i<=DIM_DIP;i++) {
			_filter->range[i][0]=0;
			_filter->range[i][1]=0;//(uint32_t)-1;
		}
		_filter->range[DIM_PROTO][1]=255;
		for(i=DIM_SPORT;i<=DIM_INPORT;i++){
			_filter->range[i][0]=0;
			_filter->range[i][1]=(uint16_t)-1;
		}
		_filter->range[DIM_TARGET][0]=_filter->range[DIM_TARGET][1]=0;
		
		for(i=0;i<k;i++){
			int type,j;
			int32_t ip,mask,masklen;
			uint32_t vmin,vmax;

			static const char *name[DIM_MAX+1]={"sip","dip","proto","sport","dport","inport","target","outport","all"};
			static const char *fomat[DIM_MAX]={"%[^/]/%[0-9]","%[^/]/%[0-9]",
						"%[^/]/%[0-9]","%[0-9]-%[0-9]","%[0-9]-%[0-9]","%[0-9]-%[0-9]","%[^/]/%[0-9]","%[0-9]-%[0-9]"};
			
			res=sscanf(p[i],"%[^:]:%s",buf[0],buf[1]);
			
			for(type=DIM_SIP;type<DIM_MAX+1;type++){
				if(0==strncasecmp(buf[0],name[type],strlen(name[type])))
					break;
			}
			if(type==DIM_MAX)//all
				continue;
			if(type==DIM_MAX+1)
				goto usage;
			res=sscanf(buf[1],fomat[type],buf[2],buf[3]);

			if(res<1)
				goto usage;

			if(type==DIM_SIP || type==DIM_DIP){
				
				ip=inet_network/*inet_addr*/(buf[2]);
				if(res==1)
					masklen=32;
				else {
					masklen=atoi(buf[3]);
					if(masklen==-1 || masklen>32)
						goto err_value;
				}
				mask=0;
				for(j=0;j<masklen;j++)
       				 mask |= 0x80000000>>j;
  
				if(ip==-1 || ((ip & mask) !=ip)){
					printf("error:%s ip or mask invalid format!\n",p[i]);
					goto usage;
				}
				_filter->range[type][0]=ip;
				_filter->range[type][1]=mask;
			}else {
				vmin=atoi(buf[2]);
				if(vmin==0 && strcmp(buf[2],"0"))
					goto err_value;
				if(res==1)
					vmax=vmin;
				else {
					vmax=atoi(buf[3]);
					if(vmax==0 && strcmp(buf[3],"0"))
						goto err_value;
				}
				if(type!=DIM_TARGET && vmax<vmin)
					goto err_value; 
				
				if(type==DIM_PROTO) {
					if(vmin>255 || vmax>255)
						goto err_value;
					if(vmax==0 && vmin==0)
						vmax=vmin=255;
					else if (vmax==0xFF && vmin!=0 && vmin!=0xFF)
						vmax=vmin;
					else {
						printf("proto fomat:xx/255,0/0\n");
						goto err_value;
					}
				}else  if(type==DIM_SPORT || type==DIM_DPORT) {
					if(vmin==0 || vmax==0)
						goto err_value;
				}if(type==DIM_TARGET){
					if(vmax==vmin)
						vmax=1;
					if(vmax==0)
						goto err_value;
				}

				if(type == DIM_OUTPORT)
					type = DIM_INPORT;
				_filter->range[type][0]=vmin;
				_filter->range[type][1]=vmax;
			}
		}
	}

#if 0
	if(_filter->type==FILTER_BY_MARK){
		for(i=0;i<_filter->cnt;i++)
			printf("%lu\n",_filter->mark[i]);
	}else {
		for(i=0;i<DIM_MAX;i++) 
			printf("%d %d\n",_filter->range[i][0],_filter->range[i][1]);
	}
#endif

	return 0;
	
err_value:
	printf("error:\"%s\" value invalid format!\n",p[i]);
usage:
	printf("usage:\n");
	printf("\tmark:xxx,xxxx,xxxx\n");
	printf("\tor\n");
	printf("\tsip:xxx/24,dip:xxx/32,proto:6/255,sport:80-81,dport:345-678,inport:0-1\n");
	printf("\tsip:xxx/24,dip:xxx/32,proto:0/0,sport:80-81,dport:345-678,target:1/3\n");
	printf("\tsip:all,target:0/2\n");
	return -1;
}

static int  
get_filter(struct client_filter  *filter,const char * const fiter_rule[],int maxrule) {
	int i,j,m,n,res;
	struct __filter _filter;

	m=n=0;
	for(i=0;i<maxrule;i++) {
		if(NULL==fiter_rule[i])
			break;
		printf("%d:%s\n",i,fiter_rule[i]);
		res=filter_parse(fiter_rule[i],&_filter);
		if(res==-1)
			return -1;
		if(_filter.type==FILTER_BY_MARK){
			if(m+_filter.cnt > CLIENT_MAX_FILTER){
				printf("support a maximum of %d filter marks!\n",CLIENT_MAX_FILTER);
				return -1;
			}
			for(j=0;j<_filter.cnt;j++)
				filter->mark[m+j]=_filter.mark[j];
			m+=_filter.cnt;
		}else {
			if(n+_filter.cnt > CLIENT_MAX_FILTER){
				printf("support a maximum of %d filter rules!\n",CLIENT_MAX_FILTER);
				return -1;
			}
			filter->rule[n].src			=_filter.range[DIM_SIP][0];
			filter->rule[n].src_mask	=_filter.range[DIM_SIP][1];

			filter->rule[n].dst			=_filter.range[DIM_DIP][0];
			filter->rule[n].dst_mask	=_filter.range[DIM_DIP][1];

			filter->rule[n].ul_proto		=_filter.range[DIM_PROTO][1];

			filter->rule[n].vrfid		=0;
			
			filter->rule[n].srcport_min	=_filter.range[DIM_SPORT][0];
			filter->rule[n].srcport_max	=_filter.range[DIM_SPORT][1];

			filter->rule[n].dstport_min	=_filter.range[DIM_DPORT][0];
			filter->rule[n].dstport_max	=_filter.range[DIM_DPORT][1];

			filter->rule[n].inport_min	=_filter.range[DIM_INPORT][0];
			filter->rule[n].inport_max	=_filter.range[DIM_INPORT][1];

			filter->rule[n].cost= (((_filter.range[DIM_TARGET][0]&0xff)<<8)|(_filter.range[DIM_TARGET][1]&0xff));
			filter->rule[n].filtId =n;
			
			n+=_filter.cnt;
		}
	}

	filter->mark_cnt=m;
	filter->rule_cnt=n;
	return 0;
}

static int filter_target_check(struct client_filter *filter,const struct client_reginfo *reginfo){
	uint32_t i;
	uint8_t qs,qn;

	if(filter->rule_cnt==0){
		printf("\n\nwarning:\n");
		printf("\tyou policy is \"BYFILTER\",but you not set filter-rules\n");
		return 0;
	}
	for(i=0;i<filter->rule_cnt;i++){
		qs=(filter->rule[i].cost>>8)&0xff;
		qn=filter->rule[i].cost&0xff;

		if(!qn) {
			printf("\n\nwarning:\n");
			printf("\tyour policy is \"%s\",buf not set target!\n",reginfo->policy);
			printf("\tsystem will use default policy \"SAMESRC_SAMEDEST\" when no target!\n\n");
			qs=0;
			qn=reginfo->qnum;
			filter->rule[i].cost=(((qs&0xff)<<8)|(qn&0xff));
		}
		
		if(qs+qn>reginfo->qnum) {
			printf("here are %d queue numbers,but filter target is %d/%d\n",reginfo->qnum,qs,qn);
			printf("errro filter %d:%s\n",i,reginfo->filter[i]);
			return -1;
		}
	}
	return 0;
}

void  filter_dump_byclinet(struct clientinfo *client)
{
	uint32_t i;
	struct client_filter  *filter=&(client->filter);

	if(!filter->mark_cnt && !filter->rule_cnt) {
		printf("here are no filter rule in client %s!\n",client->name);
		return ;
	}
		
	printf("clinet %s filter info:\n",client->name);
	if(filter->mark_cnt){
		printf("filter mark %d:",filter->mark_cnt);
		for(i=0;i<filter->mark_cnt;i++) 
			printf("0x%lx ",filter->mark[i]);
		printf("\n");
	}
	if(filter->rule_cnt){
		printf("filter rule %d:\n",filter->rule_cnt);
		for(i=0;i<filter->rule_cnt;i++) 
			printf("Rule(%d) fid=%d,cost=0x%x src 0x%x -0x%x  dst 0x%x - 0x%x proto= %d  srcport %d - %d dstport %d - %d,inport %d - %d\n",
			i,
			filter->rule[i].filtId,
			filter->rule[i].cost,
			filter->rule[i].src,
			filter->rule[i].src_mask,
			filter->rule[i].dst,
			filter->rule[i].dst_mask,
			filter->rule[i].ul_proto,
			filter->rule[i].srcport_min,
			filter->rule[i].srcport_max,
			filter->rule[i].dstport_min,
			filter->rule[i].dstport_max,
			filter->rule[i].inport_min,
			filter->rule[i].inport_max);
	}

	if(client->processid == (uint32_t)(getpid())) {
		printf("user config:\n");
		for(i=0;i<CLIENT_MAX_FILTER;i++){
			if(filter->userconf[i]==NULL) 
				break;
			printf("%d:%s\n",i,filter->userconf[i]);
		}
	}
}

void filter_dump_bysystem(struct system_info *system)
{
	struct __filter_info *finfo;
	int i;
	for(i=0;i<FILTER_OWNER_MAX;i++) {
		finfo=&(system->filterinfo[i]);
		if(finfo->filterindex == SYS_FILTER_INVALID) {
			printf("here are no filter rule in %s!\n",filter_name[i]);
			continue;
		}else {
			printf("%s filterindex=%d\n",filter_name[i],finfo->filterindex);
			rfc_print_rules(finfo->filterctx[finfo->filterindex]);
		}
	}
}

void  filter_dump_bymirror(struct mirror_info *m_info)
{
	uint32_t i;
	struct client_filter  *filter=&(m_info->m_filter);

	if(!filter->mark_cnt && !filter->rule_cnt) {
		return ;
	}
		
	if(filter->mark_cnt){
		printf("filter mark %d:",filter->mark_cnt);
		for(i=0;i<filter->mark_cnt;i++) 
			printf("0x%lx ",filter->mark[i]);
		printf("\n");
	}
	if(filter->rule_cnt){
		printf("filter rule %d:\n",filter->rule_cnt);
		for(i=0;i<filter->rule_cnt;i++) 
			printf("Rule(%d) fid=%d,cost=0x%x src 0x%x -0x%x  dst 0x%x - 0x%x proto= %d  srcport %d - %d dstport %d - %d,inport %d - %d\n",
			i,
			filter->rule[i].filtId,
			filter->rule[i].cost,
			filter->rule[i].src,
			filter->rule[i].src_mask,
			filter->rule[i].dst,
			filter->rule[i].dst_mask,
			filter->rule[i].ul_proto,
			filter->rule[i].srcport_min,
			filter->rule[i].srcport_max,
			filter->rule[i].dstport_min,
			filter->rule[i].dstport_max,
			filter->rule[i].inport_min,
			filter->rule[i].inport_max);
	}
}


#if (CLIENT_TRANS_BYFILTER ==1)
static struct clientinfo *
get_client_byfilterlist(struct system_info *sysinfo,struct rte_mbuf *buf){
	uint32_t cost,filtId;
	int k,recovery=0;
	int16_t firstindex,index=buf->flltindex;
	uint8_t priority,fixedid;
	struct eq *filterlist=(struct eq *)(buf->filterlist);
	struct __filter_info *filinfo=&(sysinfo->filterinfo[FILTER_DPDK_FRAME]);
	struct trie_rfc *t=(struct trie_rfc *)(filinfo->filterctx[buf->ctxindex]);
	struct clientinfo *client;

RECOVERY:
	
	if(!filterlist || index>=filterlist->numrules)
		return NULL;
	
	firstindex=filterlist->rulelist[index];
	
	cost=t->rule[firstindex].cost;
	filtId=t->rule[firstindex].filtId;
	
	for(index=index+1;index<filterlist->numrules;index++){
		k=filterlist->rulelist[index];
		if(t->rule[k].filtId!=filtId)
			break;
	}
	
	buf->flltindex=index;
	buf->flltarget=cost&0xffff;
	
	priority=(filtId>>8)&0xff;
	fixedid=filtId&0xff;
	client=&(sysinfo->cinfos[priority][fixedid]);

#if 0
	printf("prioriy=%d,fixed=%d,client=%s\n",priority,fixedid,client->name);
#endif
	
	if(unlikely(client->processid==0)) {
		printf("exception in get_client_byfilterlist(),client %s may existed,skip it!\n ",client->name);
		if(!recovery) {
			recovery=1;
			goto RECOVERY;
		}else {
			printf("---------------but ,have recovery one times!\n ");
			return NULL;
		}
	}
	return client;
}

#endif
static uint32_t client_fiter_update(struct clientinfo *client,void *user_ctx) {
	uint32_t i;
	struct FILTER *rule=client->filter.rule;
	for(i=0;i<client->filter.rule_cnt;i++){
		//rule[i].cost |=(((client->priority&0xff)<<24)|((client->fixedid&0xff)<<16));
		//rule[i].filtId=((struct trie_rfc *)user_ctx )->numrules;
		rule[i].filtId=(((client->priority&0xff)<<8)|(client->fixedid&0xff));
		rfc_update(&rule[i],user_ctx);
	}
	return i;
}

static uint32_t mirror_fiter_update(struct mirror_info *m_info, void *user_ctx) {
	uint32_t i;
	
	struct FILTER *rule=m_info->m_filter.rule;
	
	for(i = 0; i < m_info->m_filter.rule_cnt; i++) {
		rule[i].filtId = (uint32_t)-1;
		rfc_update(&rule[i], user_ctx);
	}
	return i;
}

static  int system_filter_update(struct system_info *system,int filtype){
	int index;
	void *user_ctx;
	struct clientinfo * p;
	struct __filter_info *filinfo=&(system->filterinfo[filtype]);
	if(filinfo->filterindex==SYS_FILTER_INVALID)
		index=0;
	else
		index=!(filinfo->filterindex);

	user_ctx=filinfo->filterctx[index];
	printf("system_filter %d(%p) update begin..\n",index,user_ctx);

	rfc_init(user_ctx,SYS_FILTER_MEMSIZE);
	
	switch(filtype){
		case FILTER_DPDK_FRAME:
			p=system->in.first;
			while(p) {
				client_fiter_update(p,	user_ctx);
				p=p->next;
			}
			p=system->out.first;
			while(p) {
				client_fiter_update(p,	user_ctx);
				p=p->next;
			}
			break;
	#if(ENABLE_MIRROR_FUNCTION == 1)
		case FILTER_MIRROR_IN:
			mirror_fiter_update(&(system->mirror_port[0]), user_ctx);
			p=system->mirror_in.first;
			while(p) {
				client_fiter_update(p,	user_ctx);
				p=p->next;
			}
			
			if(rfc_rule_isempty(user_ctx))
				system->mirror_flag.flag2[0] = 0;
			else
				system->mirror_flag.flag2[0] = 1;
			break;
		case FILTER_MIRROR_OUT:
			p=system->mirror_out.first;
			while(p) {
				client_fiter_update(p,	user_ctx);
				p=p->next;
			}
			mirror_fiter_update(&(system->mirror_port[1]), user_ctx);
			
			if(rfc_rule_isempty(user_ctx))
				system->mirror_flag.flag2[1] = 0;
			else
				system->mirror_flag.flag2[1] = 1;
			break;
	#endif
		default:
			printf("impossible print this:%s,%d!\n",__FUNCTION__,__LINE__);
			break;
	}
	rfc_final(user_ctx);
	if(rfc_rule_isempty(user_ctx))
		filinfo->filterindex=SYS_FILTER_INVALID;
	else
		filinfo->filterindex=index;
	rte_compiler_barrier();
	printf("%s %d update end..isempty:%s\n",filter_name[filtype],index,rfc_rule_isempty(user_ctx)?"yes":"no");

	return 0;
}
//------------------------------------------------------------------------------
static char *
get_ringname(unsigned priority,unsigned fixedid,unsigned num) {
	static char name[CLINET_STRING_MAX*4];
	sprintf(name,SYSTEM_CLIENT_RING,priority,fixedid,num);
	return name;
}
#include<sys/syscall.h>

int 
set_process_priority(struct clientinfo * client) {
	struct sched_param param;
      int maxpri,minpri;
      int begin[5];
      
	pid_t processid=syscall(SYS_gettid); 
 	if(SCHED_FIFO == sched_getscheduler(processid)) {
		printf("process %u had beed set FIFO schedule!\n",processid);
		return 0;
 	}
      
      maxpri = sched_get_priority_max(SCHED_FIFO);
      minpri = sched_get_priority_min(SCHED_FIFO); 

	begin[3]=minpri;   //mirrir_in
	begin[0]=minpri+20;//IN
	begin[2]=minpri+40;//APP
	begin[1]=maxpri-40;//OUT
	begin[4]=maxpri-20;//mirror_out
	param.sched_priority = begin[client->hook]+client->priority;
	if(param.sched_priority>maxpri)
		param.sched_priority=maxpri;
	if (sched_setscheduler(processid, SCHED_FIFO, &param) == -1){
            perror("sched_setscheduler() failed");
            return -1;
     }      
     return 0;
}

static int 
detect_process(uint32_t pid)  {
	char procfile[32];
	 struct stat state;
	sprintf(procfile,"/proc/%d",pid);
	if(0==stat(procfile,&state))
		return 0;
	else 
		return -1;
}
//------------------------------------------------------------------------------
void * 
dpdk_shm_alloc(struct system_info *sysinfo,const char *name,int size){	
	const struct rte_memzone *mz;
	#define NO_FLAGS 0
	
	mz = rte_memzone_lookup(name);
	if (mz == NULL) { //no existed,create it
		printf("memzone %s has not been created,create it... !\n",name);
		mz = rte_memzone_reserve(name, size,sysinfo->socket_id,NO_FLAGS);
		if (mz == NULL)
			rte_exit(EXIT_FAILURE, "Cannot reserve memory zone for %s information\n",name);

		return mz->addr;			
	}else {
		printf("memzone %s have been created !\n",name);
		return mz->addr;
	}	
}

void  
dpdk_shm_free(void *addr){	
	addr=addr;
}

//------------------------------------------------------------------------------
//system 
struct system_info * 
dpdk_queue_system_shm_init(int reset){	
	struct system_info *system;
	const struct rte_memzone *mz;
	const struct rte_memzone *mz2;
	unsigned socket_id=rte_socket_id();
	struct rte_mempool *pktmbuf_pool=NULL;
	struct rte_mempool *pktmbuf_hdr_pool=NULL;
	int h,i;
	uint16_t mp_init_arg = MAX_PACKET_SZ+RTE_PKTMBUF_HEADROOM;
	char rss_ring_name[16] = {0};
	int cpu_count = rte_lcore_count() - 1;
	#define NO_FLAGS 0
	
	mz = rte_memzone_lookup(SYSTEM_INFO);
	if (mz == NULL) { //no existed,create it
		printf("memzone %s has not been created,create it... !\n",SYSTEM_INFO);
		mz = rte_memzone_reserve(SYSTEM_INFO, sizeof(struct system_info),
				socket_id, NO_FLAGS);
		if (mz == NULL)
			rte_exit(EXIT_FAILURE, "Cannot reserve memory zone for system_info information\n");

		pktmbuf_pool = rte_mempool_lookup(DPDK_PKTMBUF_POOLNAME);
		if (NULL==pktmbuf_pool)
			pktmbuf_pool = rte_mempool_create(DPDK_PKTMBUF_POOLNAME, DPDK_NB_MBUFS,
				DPDK_MBUF_SZ, MBUF_CACHE_SIZE,
				sizeof(struct rte_pktmbuf_pool_private), rte_pktmbuf_pool_init,
				(void *)(uintptr_t)mp_init_arg, rte_pktmbuf_init, NULL, socket_id, NO_FLAGS );
				//NULL, rte_pktmbuf_init, NULL, socket_id, NO_FLAGS );

		if (NULL==pktmbuf_pool ){
			rte_exit(EXIT_FAILURE, "Cannot create mempool %s:numbers %d\n",DPDK_PKTMBUF_POOLNAME,DPDK_NB_MBUFS);
		}

		pktmbuf_hdr_pool = rte_mempool_lookup(HDR_PKTMBUF_POOLNAME);
		if (NULL==pktmbuf_hdr_pool)
			pktmbuf_hdr_pool = rte_mempool_create(HDR_PKTMBUF_POOLNAME, HDR_NB_MBUFS,
	    			HDR_MBUF_SIZE, MBUF_CACHE_SIZE, 
	    			0, NULL, NULL, rte_pktmbuf_init, NULL, socket_id, NO_FLAGS);

		if (NULL==pktmbuf_hdr_pool ){
			rte_exit(EXIT_FAILURE, "Cannot create mempool %s:numbers %d\n",HDR_PKTMBUF_POOLNAME,HDR_NB_MBUFS);
		}

RESET:
		system=mz->addr;
		memset(system,0,sizeof(struct system_info));
		system->socket_id=socket_id;
		system->ringsize=CLIENT_QUEUE_SIZE;
		rte_rwlock_init(&system->systemlock);
		system->pktmbuf_pool=pktmbuf_pool;
		system->pktmbuf_hdr_pool=pktmbuf_hdr_pool;
		system->debug.level = FP_LOG_DEFAULT;
		system->debug.type = FP_LOGTYPE_DEFAULT;
		system->debug.mode = FP_LOG_MODE_CONSOLE;
		system->debug.ratelimit = 100;
		system->portinfos.status_uk_phys=mz->phys_addr
						+offsetof(struct system_info,portinfos)
						+offsetof(struct portinfo,status_uk);
		system->portinfos.stats_uk_phys=mz->phys_addr
						+offsetof(struct system_info,portinfos)
						+offsetof(struct portinfo,stats_uk);
		for(h=0;h<FILTER_OWNER_MAX;h++){
			struct __filter_info *fltinf=&(system->filterinfo[h]);
			fltinf->filterindex=SYS_FILTER_INVALID;
			for(i=0;i<2;i++) {
				char ctxname[64];
				sprintf(ctxname, "%s_%s_%d",SYS_FILTER_NAME,filter_name[h],i);
				mz2=rte_memzone_lookup(ctxname);
				if(mz2==NULL) {
					printf("create filter ctx %s:",ctxname);
					mz2 = rte_memzone_reserve(ctxname, SYS_FILTER_MEMSIZE, /*socket_id*/SOCKET_ID_ANY, NO_FLAGS);
					if(mz2==NULL) 
						rte_exit(EXIT_FAILURE, "Cannot reserve memory zone for %s information\n",ctxname);
				}
				fltinf->filterctx[i]=mz2->addr;
				printf("filter %s addr is %p\n",ctxname,mz2->addr);
			}	
		}

		for(i = 0; i < cpu_count; i++) {
			memset(rss_ring_name, 0x0, sizeof(rss_ring_name));
			sprintf(rss_ring_name, SYSTEM_RSS_RING, i);
			system->rss_rings[i] = rte_ring_lookup(rss_ring_name);
			if(system->rss_rings[i] == NULL)
				system->rss_rings[i] = rte_ring_create(rss_ring_name, system->ringsize, system->socket_id, NO_FLAGS);

			if (system->rss_rings[i] == NULL) {
				rte_exit(EXIT_FAILURE, "Cannot create rss ring %s\n",rss_ring_name);
			}
			printf("server rss_rings[%d] addr is %p\n", i, system->rss_rings[i]);
		}
		
#if 1	//Had been reset by memet() 	
		{
			system->in.clients=0;
			rte_rwlock_init(&system->in.lock);
			system->out.clients=0;
			rte_rwlock_init(&system->out.lock);
			system->mirror_in.clients=0;
			rte_rwlock_init(&system->mirror_in.lock);
			system->mirror_out.clients=0;
			rte_rwlock_init(&system->mirror_in.lock);

			for(i=0;i<MAX_CLIENTS_HASHSIZE;i++) {
				rte_rwlock_init(&system->app[i].lock);
			}
		}
#endif
		system->hz = rte_get_tsc_hz();
		printf("memzone init ok!\n");
	}else {
		printf("memzone %s have been created !\n",SYSTEM_INFO);
		system=mz->addr;
		if(reset)
			goto RESET;
	}
	fpdebug=&system->debug;
	msec=&system->msec;
	return system;	
}

//------------------------------------------------------------------------------
//client
static int 
client_attach_inout(struct clientint *internal,struct clientinfo *client,int op) {
	int first=-1,count=0;
	int i,j=-1;
	
	rte_rwlock_write_lock(&internal->lock);
	if(op) 
		internal->client[client->priority]=client;
	else
		internal->client[client->priority]=NULL;
	for(i=0;i<MAX_CLIENT_PARITY;i++) {
		if(internal->client[i]) {
			count++;
			if(-1==first) {
				first=i;
				j=i;
			}else {
				internal->client[j]->next=internal->client[i];
				j=i;		
			}
		}
	}
	if(j!=-1 && internal->client[j])
		internal->client[j]->next=NULL;
	internal->clients=count;
	if(-1!=first)
		internal->first=internal->client[first];		
	else
		internal->first=NULL;	
	rte_rwlock_write_unlock(&internal->lock);
	return 0;
}

static int 
client_attach_app(struct clientext *app,struct clientext_warper  *entrys,struct clientinfo *client,uint16_t maskhash,int op) {
	struct clientext_warper  *item;
	uint16_t flag=0,i,j;
	int first=-1;
	item=&entrys[client->priority];
	if(op) {
		if(0==item->clients) {
			flag=1;
			item->priority=client->priority;
			item->maskhash=maskhash;
		}
		else if(MAX_CLIENT_PARITY==item->clients) {
			printf("%s:%d should not print this!\n",__FUNCTION__,__LINE__);
			return -1;
		}
	}
	else {
		if(1==item->clients)
			flag=1;
		else if(0==item->clients) {
			printf("%s:%d should not print this!\n",__FUNCTION__,__LINE__);
			return -1;
		}
	}

	rte_rwlock_write_lock(&app->lock);
	if(op) 
		item->client[item->clients++]=client;
	else  for(i=0;i<item->clients;i++) 
			if(item->client[i]==client) {
				item->client[i]=item->client[item->clients-1];
				item->clients--;
		}

	if(flag) {
		for(i=0;i<MAX_CLINET_PRIORITY;i++) {
			if(entrys[i].clients) {
				if(-1==first) {
					first=i;
					j=i;
				}else {
					entrys[j].next=&entrys[i];
					j=i;
				}
			}
		}
		if(-1!=first)
			app->entry=&entrys[first];
		else
			app->entry=NULL;
	}
	rte_rwlock_write_unlock(&app->lock);
	return 0;
}

static int  
client_attach(struct system_info *system,struct clientinfo  *client,int op) {
	int ret=-1;
	rte_rwlock_write_lock(&system->systemlock);
	switch(client->hook) {
		case DPDK_IN: {
			if((op && system->in.client[client->priority]) ||
				(!op && !system->in.client[client->priority])){
				printf("%s,hook in,should not print this!\n",__FUNCTION__);
				goto errorend; 
			}
			ret=client_attach_inout(&(system->in),client,op);
		}
			break;
		case DPDK_OUT: {
			if((op && system->out.client[client->priority]) ||
				(!op && !system->out.client[client->priority])) {
				printf("%s,hook out,should not print this!\n",__FUNCTION__);
				goto errorend; 
			}
			ret=client_attach_inout(&(system->out),client,op);
		}
			break;
		case DPDK_APP: {
			uint16_t i,key,hash;
			for(i=0;i<client->filter.mark_cnt;i++) {
				key=(client->filter.mark[i])&0xffff;
				hash=RTE_JHASH(&key,sizeof(key),0);
				hash=hash&MAX_CLIENTS_HASHMASK;
				ret=client_attach_app(&system->app[hash],system->entrys[hash],client,hash,op);
			}
		}
			break;
	#if(ENABLE_MIRROR_FUNCTION == 1)
		case DPDK_MIRRORIN: {
			if((op && system->mirror_in.client[client->priority]) ||
				(!op && !system->mirror_in.client[client->priority])){
				printf("%s,hook mirror_in,should not print this!\n",__FUNCTION__);
				goto errorend; 
			}
			ret=client_attach_inout(&(system->mirror_in),client,op);
		}
			break;
		case DPDK_MIRROROUT: {
			if((op && system->mirror_out.client[client->priority]) ||
				(!op && !system->mirror_out.client[client->priority])){
				printf("%s,hook mirror_out,should not print this!\n",__FUNCTION__);
				goto errorend; 
			}
			ret=client_attach_inout(&(system->mirror_out),client,op);
		}
			break;
	#endif
		default:
			break;
	}
errorend:
	rte_rwlock_write_unlock(&system->systemlock);
	return ret;
}


struct clientinfo * 
client_register(const struct client_reginfo *reginfo)
{
	struct system_info *system;
	struct clientinfo *client=NULL,*tmp1,*tmp;
	struct client_filter filter;
	uint32_t rwmode,hook,policy=0;
	uint32_t i,j,k,count=0;
	static const char *mode[2]={"readonly","writealbe"};
	uint32_t sum_qnum=0,tem_qnum=0,sub_client_group=0,is_multiplier_rr=1,is_multiplier_ss=1;
	
	if(!reginfo->name) {
		printf("%s:client name must be not NULL!\n",__FUNCTION__);
		goto errorend;
	}else  if(strlen(reginfo->name)>=CLINET_STRING_MAX) {
		printf("%s error:len of name is too long,which max is %d\n",__FUNCTION__,CLINET_STRING_MAX);
		goto errorend;
	}

	if(reginfo->priority>=MAX_CLINET_PRIORITY){
		printf("priority %d is too max,which should be less than %d!\n",reginfo->priority,MAX_CLINET_PRIORITY);
		goto errorend;
	}

	if(reginfo->fixedid>=MAX_CLIENT_PARITY) {
		printf("fixedid %d is too max,which should be less than %d!\n",reginfo->fixedid,MAX_CLIENT_PARITY);
		goto errorend;
	}

	if(!reginfo->rwmode) {
		printf("error:reginfo rwmode is NULL!\n");
		goto errorend;
	}else  if(!strcmp(reginfo->rwmode,"r"))
		rwmode=MODE_READONLY;
	else if(!strcmp(reginfo->rwmode,"w"))
		rwmode=MODE_WRITEABLE;
	else {
		printf("cannot recognize rwmode  %s ,it should be \"r\" or \"w\" \n",reginfo->rwmode);
		goto errorend;
	}

	if(!reginfo->hook) {
		printf("error:reginfo hook is NULL!\n");
		goto errorend;
	}else if(!strcmp(reginfo->hook,"in"))
		hook=DPDK_IN;
	else if(!strcmp(reginfo->hook,"out"))
		hook=DPDK_OUT;
	else if(!strcmp(reginfo->hook,"app"))
		hook=DPDK_APP;
#if(ENABLE_MIRROR_FUNCTION == 1)
	else if(!strcmp(reginfo->hook,"mirror_in"))
		hook=DPDK_MIRRORIN;
	else if(!strcmp(reginfo->hook,"mirror_out"))
		hook=DPDK_MIRROROUT;
	else {
		printf("cannot recognize hook  %s ,it should be in {in,out,app,mirror_in,mirror_out}\n",reginfo->hook);
		goto errorend;
	}
#else
	else {
		printf("cannot recognize hook  %s ,it should be in {in,out,app}\n",reginfo->hook);
		goto errorend;
	}
#endif

	if(NULL==reginfo->filter)  {
		if(DPDK_APP==hook) {
			printf("error:when hook is %s,reginfo filter is NULL!\n",reginfo->hook);
			goto errorend;
		}
	}else {
		if(-1==get_filter(&filter,reginfo->filter,CLIENT_MAX_FILTER))
			exit(-1);
	}
		
	if(0==reginfo->qnum) {
		printf("error:reginfo qnum=0\n");
		goto errorend;
	}else  if(reginfo->qnum>CLINET_RXQUEUE_MAX) {
		printf("one client have %d receive queues most!\n",CLINET_RXQUEUE_MAX);
		goto errorend;
	}

	if(NULL==reginfo->policy) {
		if(reginfo->qnum>1) {
			printf("error:when qnum=%d,reginfo policy is NULL!\n",reginfo->qnum);
			goto errorend;
		}
	}else if(!strcmp(reginfo->policy,"RR"))
		policy=ROUND_ROBIN;
	else if(!strcmp(reginfo->policy,"SS"))
		policy=SAMESRC_SAMEDEST;
	else if(!strcmp(reginfo->policy,"BYFILTER")) {
#if (CLIENT_TRANS_BYFILTER==1)
		policy=BY_FILTER;
#else 
		if(hook == DPDK_MIRRORIN || hook == DPDK_MIRROROUT) {
			policy=BY_FILTER;
		}else {
			printf("warning:\n");
			printf("\tServer not support CLIENT_TRANS_BYFILTER\n");
			printf("\tdefault policy will be \"SAMESRC_SAMEDEST\"\n");
			policy=SAMESRC_SAMEDEST;
		}
#endif
	} else if(!strcmp(reginfo->policy,"BYOUTPORT")) {
		if(!reginfo->issvr) {
			printf("error:only server can use policy \"BYOUTPORT\"!\n");
			goto errorend;
		}
		policy=BY_OUTPORT;
	}else if(!(is_multiplier_rr=strcmp(reginfo->policy,"BYMULTIPLIER_RR"))||
			 !(is_multiplier_ss=strcmp(reginfo->policy,"BYMULTIPLIER_SS"))) {
	#if(ENABLE_MIRROR_FUNCTION == 1)
		if(hook == DPDK_MIRRORIN || hook == DPDK_MIRROROUT) {
			printf("mirror must forbid to use %s mode\n", reginfo->policy);
			goto errorend;
		}
	#endif
		if(!is_multiplier_rr)
			policy=BY_MULTIPLIER_RR;
		else if(!is_multiplier_ss)
			policy=BY_MULTIPLIER_SS;
		
		i = 0;
		tem_qnum = reginfo->sub_client_qnum[i];
		while(reginfo->sub_client_qnum[i] != 0) {
			if(tem_qnum != reginfo->sub_client_qnum[i]) {
				printf("sub_client_qnum must be equal to each other\n");
				goto errorend;
			}
			sub_client_group++;
			sum_qnum += reginfo->sub_client_qnum[i];
			tem_qnum = reginfo->sub_client_qnum[i];
			i++;
			if(i >= MAX_SUB_CLIENTS)
				break;
		}

		if(sum_qnum != reginfo->qnum) {
			printf("the sum of all group's queues is %d, must be equal to total qnum %d\n", sum_qnum, reginfo->qnum);
			goto errorend;
		}

		if(rwmode!=MODE_READONLY) {
			printf("when policy is %s,rwmode must be 'r' !\n",reginfo->policy);
			goto errorend;
		}
	}else {
		printf("cannot recognize policy  %s ,it should be \"RR\" or \"SS\" or \"BYFILTER\" or \"BYOUTPUT\" or \"BYMULTIPLIER_RR\" or \"BYMULTIPLIER_SS\"\n",reginfo->policy);
		goto errorend;
	}

	if(hook==DPDK_APP){
		if(0==filter.mark_cnt) {
			printf("when hook %s,it need filter mark\n",reginfo->hook);
			goto errorend;
		}
		if(filter.rule_cnt)
			printf("when hook %s,it not need filter rule\n",reginfo->hook);
	}else {
		if(filter.mark_cnt)
			printf("when hook %s,it not need filter mark\n",reginfo->hook);
	}

	filter.userconf=(char **)(reginfo->filter);
	if((policy==BY_FILTER) && filter_target_check(&filter,reginfo)<0)
		goto errorend;
		
	system=get_dpdk_system();
	
	if(detect_process(system->svr_ready)) {
		printf("system server not  ready!\n");
		if(!reginfo->issvr) 
			exit(-1);
	}
	
	rte_rwlock_write_lock(&system->systemlock);

	tmp1=&(system->cinfos[reginfo->priority][reginfo->fixedid]);
	if(tmp1->processid) {
		printf("client %s (processid %u) have the same priority  %d and fixedid %d!\n",
			tmp1->name,tmp1->processid,tmp1->priority,tmp1->fixedid);
		goto errorend1; 
	}
	for(i=0;i<MAX_CLIENT_PARITY;i++) {
		tmp=&(system->cinfos[reginfo->priority][i]);
		if(0 == tmp->processid) 
			continue;	
		
		count++;
		if(hook!=DPDK_APP && hook==tmp->hook  && reginfo->priority==tmp->priority) {
			printf("error:when %s:client %s and %s have the same priority %d!\n",
				reginfo->hook,tmp->name,reginfo->name,reginfo->priority);
			goto errorend1;
		}
		if(count && DPDK_APP==hook &&
			(MODE_WRITEABLE == rwmode || MODE_WRITEABLE == tmp->rwmode)) {
			for(j=0;j<filter.mark_cnt;j++)
				for(k=0;k<tmp->filter.mark_cnt;k++) {
					if(filter.mark[j]==tmp->filter.mark[k]) {
						printf("When hook  APP  mark %lu  priority %d, "
								"customer %s (%s) conflict with  %s (%s)\n",
								filter.mark[j],reginfo->priority,
								reginfo->name,mode[rwmode],
								tmp->name,mode[tmp->rwmode]);
						goto errorend1;
					}	
				}
		}
	}
	tmp=&(system->cinfos[reginfo->priority][reginfo->fixedid]);

#if(ENABLE_MIRROR_FUNCTION == 1)
	if(hook == DPDK_MIRRORIN || hook == DPDK_MIRROROUT) {
		struct rte_mempool *pcapbuf_pool=NULL;
		char pool_name[64];

		sprintf(pool_name,PCAP_PKTBUF_POLLNAME,reginfo->priority,reginfo->fixedid);
		pcapbuf_pool = rte_mempool_lookup(pool_name);
		if(pcapbuf_pool == NULL) {
			printf("memzone %s has not been created,create it... !\n",pool_name);	
			
			pcapbuf_pool = rte_mempool_create(pool_name, PCAP_NB_BUFS,
				PCAP_BUF_SZ, MBUF_CACHE_SIZE,
				0, NULL, NULL, NULL, NULL, SOCKET_ID_ANY, NO_FLAGS );
			
			if (unlikely(NULL==pcapbuf_pool )) {
				client_unregister(client);
				rte_exit(EXIT_FAILURE, "Cannot create mempool %s:numbers %d\n",PCAP_PKTBUF_POLLNAME,PCAP_NB_BUFS);
			}
			tmp->bufpool = pcapbuf_pool;
		}
	}
#endif
	
	strcpy(tmp->name,reginfo->name);
	tmp->processid=getpid();
	tmp->fixedid=reginfo->fixedid;
	tmp->priority=reginfo->priority;
	tmp->rwmode=(uint32_t)rwmode;
	tmp->hook=(uint32_t)hook;
	memcpy(&(tmp->filter),&filter,sizeof(struct client_filter));

	if((policy == BY_MULTIPLIER_RR) || (policy == BY_MULTIPLIER_SS)) {
		tmp->queue.group = sub_client_group;
		tmp->queue.policy=policy;
		for(i = 0; i < sub_client_group; i++) {
			tmp->queue.sub_queue[i].queue_start = reginfo->sub_client_qnum[i]*(i+1)-reginfo->sub_client_qnum[i];
			tmp->queue.sub_queue[i].queue_end = tmp->queue.sub_queue[i].queue_start + reginfo->sub_client_qnum[i];
			tmp->queue.sub_queue[i].queue_num = reginfo->sub_client_qnum[i];
		}
	}else {
		tmp->queue.policy=policy;
	}
	tmp->queue.qnum=reginfo->qnum;
	
#if (SERVER_TX_BULK_MODE==0)
	tmp->queue.txcpu=system->portinfos.txcpu;
#endif
	//tmp->queue.total_rx=0;
	//tmp->queue.total_tx=0;
	//tmp->queue.total_dp=0;
	//tmp->queue.total_dp_byref=0;
	rte_atomic64_init(&(tmp->queue.total_rx));
    rte_atomic64_init(&(tmp->queue.total_tx));
    rte_atomic64_init(&(tmp->queue.total_dp));
    rte_atomic64_init(&(tmp->queue.total_dp_byref));
	tmp->next=0;
	tmp->sysinfo=system;
	tmp->fstop=1;
	if(reginfo->issvr) 
		system->svr_ready=tmp->processid;
	//rte_rwlock_init(&tmp->lock);
	for(i=0;i<reginfo->qnum;i++) {
		char *qname=get_ringname(tmp->priority,tmp->fixedid,i);
		if(tmp->queue.rings[i]==NULL) {
			tmp->queue.rings[i]=rte_ring_lookup(qname);
			
			if (tmp->queue.rings[i]==NULL) {
				tmp->queue.rings[i]= rte_ring_create(qname,
						system->ringsize,system->socket_id,
						0/*RING_F_SP_ENQ | RING_F_SC_DEQ*/);
				if (tmp->queue.rings[i]==NULL){
					printf("Cannot create or lookup rx ring queue %s for client %s(errno=%d)\n", qname,reginfo->name,rte_errno);
					goto errorend1;
				}
			}else
				printf(" found ring <%s>@%p,size=size=%d \n", 
					tmp->queue.rings[i]->name, tmp->queue.rings[i],tmp->queue.rings[i]->prod.size);
		}else 
		    printf("ring %s had existed,which left data %u!\n",tmp->queue.rings[i]->name,rte_ring_count(tmp->queue.rings[i]));

        tmp->queue.usleep_times[i]=MAX_USLEEP_TIMES;        
        rte_atomic64_init(&(tmp->queue.rings_mbuf_cnt[i]));
	}
	client=tmp;
	rte_rwlock_write_unlock(&system->systemlock);
	if(-1==set_process_priority(client))
		return NULL;
	client_attach(system,client,1);
#if (CLIENT_TRANS_BYFILTER==1)
	if(filter.rule_cnt)
		system_filter_update(system,hook2filter[client->hook]);
#else
	if(client->hook == DPDK_MIRRORIN || client->hook == DPDK_MIRROROUT) {
		if(filter.rule_cnt)
			system_filter_update(system,hook2filter[client->hook]);
	}else {
		if (unlikely(!rfc_protocomptab_built))
    		rfc_protocomptab_build();
	}
#endif
	return client;
errorend1:
	rte_rwlock_write_unlock(&system->systemlock);
errorend:
	return client;
 }

int  
client_unregister( struct clientinfo * client) {
	int ret;
	uint32_t i,j,rx_count;
	struct rte_mbuf *bufs[CLIENT_QUEUE_SIZE];
 	struct system_info *system;
 	struct client_rxqueue *queue;
	system=(struct system_info *)(client->sysinfo);

	ret= client_attach(system,client,0);
	if(unlikely(ret))
		return ret;
#if (CLIENT_TRANS_BYFILTER==1)
	if(client->filter.rule_cnt)
		system_filter_update(system,hook2filter[client->hook]);
#else
	if(client->hook == DPDK_MIRRORIN || client->hook == DPDK_MIRROROUT) {
		if(client->filter.rule_cnt)
			system_filter_update(system,hook2filter[client->hook]);
	}
#endif
	queue=&(client->queue);
	for(i=0;i<queue->qnum;i++) {
        rte_atomic64_set(&(queue->rings_mbuf_cnt[i]), 0);
		rx_count = rte_ring_dequeue_burst(queue->rings[i],(void *)bufs, CLIENT_QUEUE_SIZE);
		if(!rx_count)
			continue;
		printf("%s,ring %s left %d\n",__FUNCTION__,queue->rings[i]->name,rx_count);
		for(j=0;j<rx_count;j++) {
			#if(ENABLE_MIRROR_FUNCTION == 0)
			rte_pktmbuf_free(bufs[j]);
			#else
			if(client->hook == DPDK_MIRRORIN || client->hook == DPDK_MIRROROUT) {
				dpdk_pcap_drop(client, (struct pcap_buf *)bufs[j]);
			}else {
				rte_pktmbuf_free(bufs[j]);
			}
			#endif
		}
	}

    rte_rwlock_write_lock(&system->systemlock);
	client->processid=0;
	client_dequeue_stop(client);
    rte_rwlock_write_unlock(&system->systemlock);
    
	return 0;
}


//------------------------------------------------------------------------------
//debug
const  char *portmode[WORK_MODE_MAX]={
	[INVALID_MODE]="invalid",

	[LOOP_SIMPLE]="simple-loop",
	[LOOP]="loop",
	[BYPASS]="bypass",
	[DIRECT_CONNECT_SIMPLE]="simple-direct-con",
	[DIRECT_CONNECT]="direct-con",
	[BRIDGE_SIMPLE]="bridge",
	[MIRROR_PORT]="mirror-port",
	[ADVANCED]="advaced",
	[NAT_PORT]="nat-port",
};


void 
dump_portinfo(void) {
	struct system_info *system;
	struct portinfo  *portinfo;
	int i,k;
	
	system=get_dpdk_system();
	portinfo=&(system->portinfos);
	printf("here are %d ports:\n",portinfo->portn);
	for(i=0;i<portinfo->portn;i++) {
		printf("\t port %d(rxrings %d: txrings:%d) ",i,portinfo->rxrings[i],portinfo->txrings[i]);
		if(portinfo->mode[i].mode <0 || portinfo->mode[i].mode >=WORK_MODE_MAX)
			printf(",mode:error,invalid parameter,");
		else
			printf(",mode %s,value %d,",portmode[portinfo->mode[i].mode],portinfo->mode[i].value);
		if(portinfo->status_uk[i] & USER_STATUS) {
			k=(portinfo->status_uk[i]&IS_IXGBE);
			printf("Status  Link Up,is IXGBE:%s,",k?"yes":"no");
#if (SERVER_TX_BULK_MODE==0)
			{
				int j;
				printf("txcpu:");
				for(j=0;j<(k?SERVER_TX_QUEUES:1);j++)
					printf("%d ",portinfo->txcpu[i][j]);
			}
#endif
			printf("\n");
		}else printf("Status  Link Down\n");
	}
	printf("\n");
}


				
void 
dump_client(struct clientinfo * client) {
	unsigned i;
	const char *rwmode[2]={"readonly","writealbe"};
	const char *hook[5]={"in","out","app","mirror_in","mirror_out"};
	const char *policy[6]={"Round-Robin","SameSrc-SameDest","by-filter","by-outport","by_multiplier_rr","by_multiplier_ss"};
	printf("name:%s\n",client->name);
	printf("processid=%d\nfixedid=%d\nprority=%d\n",client->processid,client->fixedid,client->priority);
	printf("rwmode=%s\n",rwmode[client->rwmode]);
	printf("hook=%s\n",hook[client->hook]);

	filter_dump_byclinet(client);

	printf("queue number %d\n",client->queue.qnum);
	printf("queue policy %s\n",policy[(((client->queue.policy)&0xFF00) >> 8) + ((client->queue.policy)&0xFF)]);
#if (ENABLE_APP_STATISTICS == 1)
	printf("queue rx=%lu,tx=%lu,drop=%lu,drop_by_ref=%lu\n",
		rte_atomic64_read(&(client->queue.total_rx)),rte_atomic64_read(&(client->queue.total_tx)),rte_atomic64_read(&(client->queue.total_dp)),rte_atomic64_read(&(client->queue.total_dp_byref)));

#endif
	printf("queue name is :\n");
	for(i=0;i<client->queue.qnum;i++) 
		printf("\tname: %s, count: %lu, free_count: %d\n",
			get_ringname(client->priority,client->fixedid,i), 
			rte_atomic64_read(&(client->queue.rings_mbuf_cnt[i])),
			rte_ring_free_count(client->queue.rings[i]));
#if(ENABLE_MIRROR_FUNCTION == 1)
	if(client->bufpool)
		printf("bufpool name %s,addr 0x%lx\n",((struct rte_mempool *)client->bufpool)->name,((struct rte_mempool *)client->bufpool)->phys_addr);
#endif
	printf("\n");
}

void 
dump_system1(void) {
	struct system_info *system;
	int i,j;
	
	system=get_dpdk_system();

	printf("dump system by priority===========================\n");
	for(i=0;i<MAX_CLINET_PRIORITY;i++)
		for(j=0;j<MAX_CLIENT_PARITY;j++){
			if(0==system->cinfos[i][j].processid)
				continue;
			dump_client(&system->cinfos[i][j]);
	}
}

void 
dump_system2(void) {
	struct system_info *system;
	struct clientinfo * p;
	struct clientext_warper *q;
	uint32_t i,j;
	
	system=get_dpdk_system();

	printf("dump system by hook===========================\n");
	printf("hook IN=================\n");
	rte_rwlock_read_lock(&system->in.lock);
	p=system->in.first;
	while(p) {
		dump_client(p);
		p=p->next;
	}
	rte_rwlock_read_unlock(&system->in.lock);
	
	printf("hook APP=================\n");
	for(i=0;i<MAX_CLIENTS_HASHSIZE;i++) {
		if(!system->app[i].entry)
			continue;
		q=system->app[i].entry;
		rte_rwlock_read_lock(&system->app[i].lock);
		while(q) {
			printf("Markhash %u priority %u have %u clients:\n",q->maskhash,q->priority,q->clients);
			for(j=0;j<q->clients;j++)
				dump_client(q->client[j]);
			q=q->next;			
		}
		rte_rwlock_read_unlock(&system->app[i].lock);
	}
	
	printf("hook OUT=================\n");
	rte_rwlock_read_lock(&system->out.lock);
	p=system->out.first;
	while(p) {
		dump_client(p);
		p=p->next;
	}
	rte_rwlock_read_unlock(&system->out.lock);
#if(ENABLE_MIRROR_FUNCTION == 1)
	printf("hook MIRROR_IN=================\n");
	rte_rwlock_read_lock(&system->mirror_in.lock);
	p=system->mirror_in.first;
	while(p) {
		dump_client(p);
		p=p->next;
	}
	rte_rwlock_read_unlock(&system->mirror_in.lock);
	printf("hook MIRROR_OUT=================\n");
	rte_rwlock_read_lock(&system->mirror_out.lock);
	p=system->mirror_out.first;
	while(p) {
		dump_client(p);
		p=p->next;
	}
	rte_rwlock_read_unlock(&system->mirror_out.lock);
#endif
}

void dump_mbuf(struct rte_mbuf * m)
{
#if 0	
	rte_pktmbuf_dump(stdout,m , 1464);
#else 
	unsigned int j;
	unsigned char *p;
	unsigned int len;
	printf("mbuf dataoff=%d,len=%d:%d\n",m->data_off,m->pkt_len,m->data_len);
	printf("in_port=%d\n",m->port);
	p=rte_pktmbuf_mtod(m, unsigned char *);
	len=m->pkt_len;
	for(j=0;j<len;j++) {
		if(j&&j%8==0)
			printf("\n");
		printf("%02x ",p[j]);
	}
	printf("\n");

	printf("(proto)%d-(sip)0x%x-(dip)0x%x-(sport)%d-(dport)%d\n",
			m->tuple.ipv4.proto, 
			m->tuple.ipv4.ip_src, 
			m->tuple.ipv4.ip_dst,
			m->tuple.ipv4.port_src,
			m->tuple.ipv4.port_dst);

}	
#endif

//------------------------------------------------------------------------------
//enqueue and dequeue
int  dpdk_dequeue1(struct clientinfo * my,unsigned qnum,void **bufs, unsigned n)
{
	struct rte_ring *queue;
	uint16_t nb_rx=0 ;
	int i;
	volatile int *usleep_times;
	volatile uint32_t *fstop=&(my->fstop);
	/*if (qnum > my->queue.qnum) {
		printf("%s:parameter error!\n",__FUNCTION__);
		return -1;
	}*/
	usleep_times=&(my->queue.usleep_times[qnum]);
	while(*fstop) {
		for(i=0;i<*usleep_times;i++)
			usleep(MIN_SCHEDULE_TIMEMIN);
		queue=my->queue.rings[qnum];
		nb_rx = rte_ring_dequeue_burst(queue,(void *)bufs, n);
		if(!nb_rx)
			*usleep_times=MAX_USLEEP_TIMES;
		else 
			return nb_rx;	
	}
	return 0;
}
/*
	qindex:
		when input,iterate from qindex
		wen output,here is output over index
*/
int  dpdk_dequeue2(struct clientinfo * my,unsigned *qindex,void **bufs, unsigned n)
{
	struct rte_ring *queue;
	uint16_t nb_rx=0 ;
	unsigned i,j,start,qnum= my->queue.qnum;
	unsigned int sleeptime=MIN_SCHEDULE_TIMEMIN/qnum;
	volatile int *usleep_times=my->queue.usleep_times;
	volatile uint32_t *fstop=&(my->fstop);
	start=*qindex;
	while(*fstop) {
		for(i=start,j=0;i<qnum;i++,j++) {
			if(0==usleep_times[i]) {
				queue=my->queue.rings[i];
				nb_rx = rte_ring_dequeue_burst(queue,(void *)bufs, n);
				if(!nb_rx)
					usleep_times[i]=MAX_USLEEP_TIMES;
				else {
					*qindex=i;
					return nb_rx;
				}
			}
		}
		start=0;
		if(j>=qnum)
			usleep(sleeptime);
	}
	return 0;
}

int  dpdk_dequeue3(struct clientinfo * my,struct subqueueinfo *sub_queue,unsigned *qindex,void **bufs,unsigned n)
{
	struct rte_ring *queue;
	uint16_t nb_rx=0 ;
	uint32_t i,j;
	unsigned int sleeptime=MIN_SCHEDULE_TIMEMIN/sub_queue->queue_num;
	volatile int *usleep_times=my->queue.usleep_times;
	volatile uint32_t *fstop=&(my->fstop);
	
	while(*fstop) {
		for(i=*qindex,j=0;i<sub_queue->queue_end;i++,j++) {
			if(0==usleep_times[i]) {
				queue=my->queue.rings[i];
				nb_rx = rte_ring_dequeue_burst(queue,(void *)bufs, n);
				if(!nb_rx)
					usleep_times[i]=MAX_USLEEP_TIMES;
				else {
					*qindex=i;
					return nb_rx;
				}
			}
		}
		*qindex = sub_queue->queue_start;
		if(j >= sub_queue->queue_num)
			usleep(sleeptime);
	}
	return 0;
}

int  dpdk_dequeue4(struct clientinfo * my,unsigned *qindex,void **bufs, unsigned n)
{
	struct rte_ring *queue;
	uint16_t nb_rx=0 ;
	unsigned i,j,start,qnum= my->queue.qnum;
	unsigned int sleeptime=10;//MIN_SCHEDULE_TIMEMIN/qnum;
	volatile int *usleep_times=my->queue.usleep_times;
	volatile uint32_t *fstop=&(my->fstop);
	while(*fstop) {
		for(i=start,j=0;i<qnum;i++,j++) {			
			if(0==usleep_times[i]) {	
				if(!__sync_bool_compare_and_swap(&(my->queue.q_handle_flag[i]), 0, 1))
					continue;
					
				queue=my->queue.rings[i];
				nb_rx = rte_ring_dequeue_burst(queue,(void *)bufs, n);
				if(!nb_rx) {
					my->queue.q_handle_flag[i] = 0;
					usleep_times[i]=MAX_USLEEP_TIMES;
				}
				else {
					*qindex=i;
					return nb_rx;
				}
			}
		}
		start=0;
		if(j>=qnum)
			usleep(sleeptime);
	}
	return 0;
}


void  client_dequeue_stop( struct clientinfo * client){
	client->fstop=0;
}

static int
queue_eneque_help(struct client_rxqueue *tx,struct rte_mbuf *buf)
{	
	uint16_t nb_tx;
	uint32_t rindex;

	if(1==tx->qnum)
		rindex=0;
	else  {
		switch(tx->policy){
			case ROUND_ROBIN:
				rindex=rte_atomic64_read(&(tx->total_rx))%tx->qnum;
				break;
			case SAMESRC_SAMEDEST:
				rindex=buf->tag%tx->qnum;
				break;
#if (CLIENT_TRANS_BYFILTER==1)
			case BY_FILTER:{
				int qs=((buf->flltarget)>>8)&0xff;
				int qn=(buf->flltarget&0xff);
				
				if(qn==1)
					rindex=qs;
				else {
					rindex=qs+buf->tag%qn;
				}
			}
			break;	
#endif
			case BY_OUTPORT:{
				uint8_t port=buf->port;
				if(unlikely(port>=RTE_MAX_ETHPORTS)){
					printf("%s:outport=%d,crossing the max line(%d\n)\n",__FUNCTION__,port,RTE_MAX_ETHPORTS);
				#if (ENABLE_APP_STATISTICS == 1)
					rte_atomic64_inc(&(tx->total_dp));
				#endif  
					/*if((buf->rings_cnt != NULL) && (rte_atomic64_read(buf->rings_cnt) > 0)) {
						rte_atomic64_dec(buf->rings_cnt);
					}*/
					rte_pktmbuf_free(buf);
					return 0;					
				}
			#if (SERVER_TX_BULK_MODE==1)
				//OUTPUT_MODE_CHECK(buf,port);
				rindex=port;
			#else
				uint8_t (*txcpu)[SERVER_TX_QUEUES];
				txcpu=tx->txcpu;
				rindex=txcpu[buf->port][rte_atomic64_read(&(tx->total_rx))%SERVER_TX_QUEUES];
			#endif	
			}break;
			case BY_MULTIPLIER_RR:
			case BY_MULTIPLIER_SS:{				
				uint32_t i = 0;
				for(i = 1; i < tx->group; i++) {
					if(!(tx->policy & 0xFF)) { //ROUND_ROBIN
						rindex = tx->sub_queue[i].queue_start + rte_atomic64_read(&(tx->total_rx)) % tx->sub_queue[i].queue_num;
					}
					else { //SAMESRC_SAMEDEST
						rindex = tx->sub_queue[i].queue_start + buf->tag % tx->sub_queue[i].queue_num;
					}

					rte_ring_enqueue_burst(tx->rings[rindex],(void **)&buf,1);
					tx->usleep_times[rindex]=0;
				}
				
				if(!(tx->policy & 0xFF)) //ROUND_ROBIN
					rindex = tx->sub_queue[0].queue_start + rte_atomic64_read(&(tx->total_rx)) % tx->sub_queue[0].queue_num;
				else //SAMESRC_SAMEDEST
					rindex = tx->sub_queue[0].queue_start + buf->tag % tx->sub_queue[0].queue_num;			
			}break;
			default:
				printf("%s,%d:impossible",__FUNCTION__,__LINE__);
				rindex=0;
				break;
		}
	}

	/*if((buf->rings_cnt != NULL) && (rte_atomic64_read(buf->rings_cnt) > 0)) {
		rte_atomic64_dec(buf->rings_cnt); //previous ring's count decrease 1
	}

	if(tx->policy != BY_OUTPORT) {
		if(rte_atomic64_read(&(tx->rings_mbuf_cnt[rindex])) >= CLIENT_QUEUE_SIZE) {	
		#if (ENABLE_APP_STATISTICS == 1)
			rte_atomic64_inc(&(tx->total_dp));
		#endif
			DPDK_LOG(WARNING,PLATFORM,"Line:%d tx next client,over client queue threshold\n",__LINE__);
			rte_pktmbuf_free(buf);
			return 0;
		}

		buf->rings_cnt = &(tx->rings_mbuf_cnt[rindex]); //new ring's ring_count
	}*/	
	
	nb_tx=rte_ring_enqueue_burst(tx->rings[rindex],(void **)&buf,1);
	
	if(!nb_tx) {
	#if (ENABLE_APP_STATISTICS == 1)
		rte_atomic64_inc(&(tx->total_dp));
	#endif
		DPDK_LOG(WARNING,PLATFORM,"Line:%d tx next client %s failed\n",
		         __LINE__,(tx->policy==BY_OUTPORT?"servtx":"waf or ips"));
		rte_pktmbuf_free(buf);
	}
	else  {
		tx->usleep_times[rindex]=0;
		/*if(tx->policy != BY_OUTPORT) {
			rte_atomic64_add(&(tx->rings_mbuf_cnt[rindex]), nb_tx); //new ring's ring_count increase 1
		}*/
	#if (ENABLE_APP_STATISTICS == 1)
		rte_atomic64_inc(&(tx->total_rx));
	#else
		#if (SERVER_TX_BULK_MODE==1)
			if((tx->policy == ROUND_ROBIN) || (tx->policy == BY_MULTIPLIER_RR))
				rte_atomic64_inc(&(tx->total_rx));
		#else
			if((tx->policy == ROUND_ROBIN) || (tx->policy == BY_MULTIPLIER_RR) || (tx->policy == BY_OUTPORT))
				rte_atomic64_inc(&(tx->total_rx));
		#endif
	#endif
	}
	return nb_tx;
}

static int 
dpdk_enqueue_app(struct clientinfo * my,struct rte_mbuf *buf) {
	struct system_info *sysinfo=my->sysinfo;
	struct  clientext_warper *warper,*next;

	uint16_t i;
	if(rte_atomic16_sub_return(&(buf->ref),1)) {//someone still holding the mbuf
	#if (ENABLE_APP_STATISTICS == 1)
		rte_atomic64_inc(&(my->queue.total_dp_byref));
	#endif
		return 0;
	}

	if(rte_atomic16_read(&buf->isdrop)) {  //need drop
		rte_atomic16_set(&buf->isdrop,0);
		/*if(rte_atomic64_read(buf->rings_cnt) > 0)
			rte_atomic64_dec(buf->rings_cnt);*/
		rte_pktmbuf_free(buf);	
		return 0;
	}
	
	warper=&(sysinfo->entrys[buf->markhash][my->priority]);
	next=warper->next;
	if(next) {
		rte_atomic16_set(&buf->ref,next->clients);
		for(i=0;i<next->clients;i++) {
		#if (ENABLE_APP_STATISTICS == 1)
			rte_atomic64_add(&(my->queue.total_tx), queue_eneque_help(&(next->client[i]->queue),buf));
		#else
			queue_eneque_help(&(next->client[i]->queue),buf);
		#endif
		}
		return 0;
	}
	//goto out
#if (CLIENT_TRANS_BYFILTER ==1)
	struct clientinfo * nextout;
	nextout=get_client_byfilterlist(my->sysinfo,buf);
	if(!nextout) {
		printf("app:not found out ,drop it!\n");
		/*if(rte_atomic64_read(buf->rings_cnt) > 0)
			rte_atomic64_dec(buf->rings_cnt);*/
		rte_pktmbuf_free(buf);
		return -1;
	}
#if (ENABLE_APP_STATISTICS == 1)
	rte_atomic64_add(&(my->queue.total_tx), queue_eneque_help(&(nextout->queue),buf));
#else
	queue_eneque_help(&(nextout->queue),buf);
#endif
#else
	if(sysinfo->out.first) {
	#if (ENABLE_APP_STATISTICS == 1)
		rte_atomic64_add(&(my->queue.total_tx), queue_eneque_help(&(sysinfo->out.first->queue),buf));
	#else
		queue_eneque_help(&(sysinfo->out.first->queue),buf);
	#endif
	}else {//impossible
		printf("system out is not existed!\n");
		return -1;
	}
#endif
	return 0;
}

static int 
dpdk_enqueue_in2app(struct clientinfo * my,struct rte_mbuf *buf){
	struct system_info *sysinfo=my->sysinfo;
	struct  clientext_warper *warper;
	uint32_t key;
	uint16_t maskhash,i;
	
	if(buf->mark)  { 
		key=buf->mark&0xffff;
		maskhash=RTE_JHASH(&key,sizeof(key),0);
		maskhash=maskhash&MAX_CLIENTS_HASHMASK;
		buf->markhash=maskhash;
		warper=sysinfo->app[maskhash].entry;
		if(warper) {  //goto app
			rte_atomic16_set(&buf->ref,warper->clients);
			for(i=0;i<warper->clients;i++) {
			#if (ENABLE_APP_STATISTICS == 1)
				rte_atomic64_add(&(my->queue.total_tx), queue_eneque_help(&(warper->client[i]->queue),buf));
			#else
				queue_eneque_help(&(warper->client[i]->queue),buf);
			#endif
			}
			return 0;
		}
	}
	return -1;
}

static int 
dpdk_enqueue_in(struct clientinfo * my,struct rte_mbuf *buf) {
	struct clientinfo * next;
#if (CLIENT_TRANS_BYFILTER ==1)	
	next=get_client_byfilterlist(my->sysinfo,buf);

#if (ENABLE_CLIENT_APP == 1)
	if(next==NULL) {
		if(-1==dpdk_enqueue_in2app(my,buf)){ //try to goto app
			printf("in:no found app and out ,drop it!\n");
			/*if(rte_atomic64_read(buf->rings_cnt) > 0)
				rte_atomic64_dec(buf->rings_cnt);*/
			rte_pktmbuf_free(buf);
			return -1;
		}
		return 0;
	}

	if(next->hook==DPDK_OUT){
		int16_t index=buf->flltindex;
		if(0==dpdk_enqueue_in2app(my,buf)){ //goto app firstly
			buf->flltindex=index;  //Restore the next client
			return 0;
		}	
	}
#else
    if (next == NULL) {
        rte_pktmbuf_free(buf);
        return -1;
    }
#endif

#if (ENABLE_APP_STATISTICS == 1)
	rte_atomic64_add(&(my->queue.total_tx), queue_eneque_help(&(next->queue),buf));
#else
	queue_eneque_help(&(next->queue),buf);
#endif
#else
	struct system_info *sysinfo=my->sysinfo;
	next=my->next;
	if(next) { //no last at hook-in
	#if (ENABLE_APP_STATISTICS == 1)
		rte_atomic64_add(&(my->queue.total_tx), queue_eneque_help(&(next->queue),buf));
	#else
		queue_eneque_help(&(next->queue),buf);
	#endif
		return 0;
	}
    
#if (ENABLE_CLIENT_APP == 1)
	if(0==dpdk_enqueue_in2app(my,buf))//last at hook-in,goto app
		return 0;
#endif
    
	if(sysinfo->out.first) {//goto out
	#if (ENABLE_APP_STATISTICS == 1)
		rte_atomic64_add(&(my->queue.total_tx), queue_eneque_help(&(sysinfo->out.first->queue),buf));
	#else
		queue_eneque_help(&(sysinfo->out.first->queue),buf);
	#endif
		return 0;
	}else {//impossible
		printf("system out is not existed!\n");
		return -1;
	}	
#endif	
	return 0;
}

static int 
dpdk_enqueue_out(struct clientinfo * my,struct rte_mbuf *buf) {
	struct clientinfo * next;

#if (CLIENT_TRANS_BYFILTER ==1)
	next=get_client_byfilterlist(my->sysinfo,buf);
	if(!next) {
		/*if(rte_atomic64_read(buf->rings_cnt) > 0)
			rte_atomic64_dec(buf->rings_cnt);*/
		rte_pktmbuf_free(buf);
		return -1;
	}
#if (ENABLE_APP_STATISTICS == 1)
	rte_atomic64_add(&(my->queue.total_tx), queue_eneque_help(&(next->queue),buf));
#else
	queue_eneque_help(&(next->queue),buf);
#endif
#else
	next=my->next;
	if(next) {
	#if (ENABLE_APP_STATISTICS == 1)
		rte_atomic64_add(&(my->queue.total_tx), queue_eneque_help(&(next->queue),buf));
	#else
		queue_eneque_help(&(next->queue),buf);
	#endif
		return 0;
	}else {//impossible
		printf("client %s hook out report error:next client is not exist!\n",my->name);
		return -1;			
	}
#endif
	return 0;
}


int  dpdk_enqueue(struct clientinfo * my,struct rte_mbuf *buf) {
	static  int (*enqueue[3])(struct clientinfo * my,struct rte_mbuf *buf)={dpdk_enqueue_in,dpdk_enqueue_out,dpdk_enqueue_app,};
	return  enqueue[my->hook](my,buf);
}

int dpqk_priv_send(struct clientinfo * my,char *buf,unsigned len,uint8_t outport) {
	struct system_info *sysinfo=my->sysinfo;
	struct rte_mbuf *mbuf;
	char *p;
    
    if (outport >= RTE_MAX_ETHPORTS) {
        return -1;
    }

	if(len>MAX_PACKET_SZ) {
		printf("%s,len=%d should smaller than %d\n",__FUNCTION__,len,MAX_PACKET_SZ);
		return -1;
	}

	if(my->hook==DPDK_OUT) {
		printf("hook out is not allow for %s\n",__FUNCTION__);
		return -1;
	}
	
	if((mbuf = rte_pktmbuf_alloc(sysinfo->pktmbuf_pool)) == NULL) {
		printf("%s:mbuf alloc error!\n",__FUNCTION__);
		return -1;
	}

	p = rte_pktmbuf_mtod(mbuf, char *);
    memset(p, 0x0, MAX_PACKET_SZ);
	memcpy(p, buf, len);    
	mbuf->userdef = sysinfo->portinfos.mode[outport].mode;
	mbuf->pkt_len = len;
	mbuf->data_len = len;
	mbuf->port = outport;
    mbuf->rings_cnt = NULL;
	
	if(sysinfo->out.first) {
		return queue_eneque_help(&(sysinfo->out.first->queue),mbuf);
	}else {//impossible
		printf("system out is not existed!\n");
		return -1;
	}
}
int  dpdk_mbuf_drop(struct clientinfo * my,struct rte_mbuf *buf) {
#if 0
	if(DPDK_APP != my->hook) { 
		if(rte_atomic64_read(buf->rings_cnt) > 0)
			rte_atomic64_dec(buf->rings_cnt);
		rte_pktmbuf_free(buf);  //direct drop it
	}
	else {
		if(!rte_atomic16_sub_return(&(buf->ref),1)) {
			if(rte_atomic64_read(buf->rings_cnt) > 0)
				rte_atomic64_dec(buf->rings_cnt);	
			rte_pktmbuf_free(buf);
		}
		else 
			rte_atomic16_set(&buf->isdrop,1);
	}
	return 0;
#else
    /*if(rte_atomic64_read(buf->rings_cnt) > 0) {
        rte_atomic64_dec(buf->rings_cnt);
    }*/
    rte_pktmbuf_free(buf);  //direct drop it
    return 0;
#endif
}

#if ENABLE_MIRROR_FUNCTION == 1
int  dpdk_pcap_drop(struct clientinfo * my, struct pcap_buf *buf)
{
	rte_mempool_put(my->bufpool,(void *)buf);
		  
	return 0;
}
#endif

void
burst_free_mbufs(struct rte_mbuf **pkts, unsigned num){
	unsigned i;
	if (pkts == NULL)
		return;
	for (i = 0; i < num; i++) {
		/*if(rte_atomic64_read(pkts[i]->rings_cnt) > 0)
			rte_atomic64_dec(pkts[i]->rings_cnt);*/
		rte_pktmbuf_free(pkts[i]);
		pkts[i] = NULL;
	}
}
//------------------------------------------------------------------------------
//server only
void detect_client(struct clientinfo *server) {
	struct system_info *system;
	struct clientinfo *tmp;
	int i,j;
	
	if(NULL==server) 
		return;
	system=server->sysinfo;
	if(system->svr_ready!=server->processid) {
		printf("you are not server,no right to detect other client!\n");
		return ;
	}

	for(i=0;i<MAX_CLINET_PRIORITY;i++)
		for(j=0;j<MAX_CLIENT_PARITY;j++) {
			tmp=&system->cinfos[i][j];
			if(!tmp->processid)
				continue;
			if(detect_process(tmp->processid) ){
				printf("client %s:%d had exited!\n",tmp->name,tmp->processid);
				client_unregister(tmp);
			}
		}
	sleep(1);
}


//------------------------------------------------------------------------------
void log2file(const char *format, ...)
{
    FILE* fp = NULL;
    va_list ap;

    fp = fopen(LOG_FILE_NAME, "a+");
    if (!fp)
		return;

	va_start(ap, format);
	vfprintf(fp,format, ap);
	va_end(ap);

	fflush(fp);
	fclose(fp);
	
    return;
}

struct system_info  *get_dpdkshm(char *name,char *file_prefix){
	struct system_info *sysinfo;
	if(rte_eal_init_for_shm(name,file_prefix)<0)		
		return NULL;	
	if(rte_eal_init_mm()<0)				
		return NULL;
	sysinfo=dpdk_queue_system_shm_init(0);
	if (!sysinfo)
		return NULL;
	return sysinfo;
}

struct system_info  *get_dpdk_shm_cpu(const char *name,const char *file_prefix,char *coremask,int dpdkthread){
	struct system_info *sysinfo;
	if(rte_eal_init_for_shm_cpu(name,file_prefix,coremask)<0)		
		return NULL;	
	if(rte_eal_init_mm()<0)				
		return NULL;
	if(dpdkthread && rte_eal_init_cpu()<0)
		return NULL;
	sysinfo=dpdk_queue_system_shm_init(0);
	if (!sysinfo)
		return NULL;
	return sysinfo;
}
//------------------------------------------------------------------------------
struct ether_vlan_hdr {
	struct ether_addr d_addr; /**< Destination address. */
	struct ether_addr s_addr; /**< Source address. */
	uint16_t ether_type1;     /**< Frame type. */
	uint16_t vlanout;
	uint16_t ether_type2;
	uint16_t vlanin;
	uint16_t ether_type3; 
} __attribute__((__packed__));

struct ipv4_tuple3 {
	uint32_t ip_src;
	uint32_t ip_dst;
	uint8_t  proto;
}__rte_cache_aligned;

struct ipv6_tuple3{
	uint8_t ip_src[16];
	uint8_t ip_dst[16];
	uint8_t  proto;
}__rte_cache_aligned;

int packet_tuple_analyzer(struct rte_mbuf *  mbuf,
	                            struct rte_mbuf ** out_pkts,
	                            uint16_t           nb_pkts)
{
	struct ether_hdr 	  *eth_hdr;
	struct ether_vlan_hdr *vlan_hdr;
	struct ipv4_hdr 	  *ipv4_hdr;	
	struct ipv6_hdr 	  *ipv6_hdr;
	struct udp_hdr  	  *udp_hdr;
	struct tcp_hdr   	  *tcp_hdr;
	struct icmp_hdr       *icmphdr;
	struct ipv4_tuple5    *ipv4tuple=&mbuf->tuple.ipv4;
	struct ipv6_tuple5    *ipv6tuple=&mbuf->tuple.ipv6;
	struct ipv4_tuple3    ipv4tuple3 = {0};
	struct ipv6_tuple3    ipv6tuple3;
	//uint64_t ol_flags=mbuf->ol_flags;
	uint16_t *port_src=NULL;
	uint16_t *port_dst=NULL;
	uint8_t proto=0,vlans=0;
	uint8_t ipv;
	uint16_t eth_type;	
	
	mbuf->pktmark = 0;
	mbuf->mac_header=mbuf->data_off;
	eth_hdr = rte_pktmbuf_mtod_mac(mbuf, struct ether_hdr *);
	eth_type=rte_be_to_cpu_16(eth_hdr->ether_type);
	if(unlikely(eth_type == 0x8100 || eth_type == 0x9100)){
		vlan_hdr=(struct ether_vlan_hdr	*)eth_hdr;
		vlans=4;
		eth_type=rte_be_to_cpu_16(vlan_hdr->ether_type2);
		if(unlikely(eth_type == 0x8100 || eth_type == 0x9100)){
			vlans=8;
			eth_type=rte_be_to_cpu_16(vlan_hdr->ether_type3);
		}
	}
	mbuf->eth_type=eth_type;
	mbuf->network_header=mbuf->mac_header+ sizeof(struct ether_hdr)+vlans;

	if(mbuf->eth_type == 0x0800)/*if (ol_flags & (PKT_RX_IPV4_HDR | PKT_RX_IPV4_HDR_EXT))*/ {
		ipv4_hdr = rte_pktmbuf_mtod_network(mbuf,struct ipv4_hdr *) ;
		proto=ipv4tuple->proto=ipv4_hdr->next_proto_id;
		ipv4tuple->ip_src=rte_be_to_cpu_32(ipv4_hdr->src_addr);
		ipv4tuple->ip_dst=rte_be_to_cpu_32(ipv4_hdr->dst_addr);
		mbuf->transport_header=mbuf->network_header+((ipv4_hdr->version_ihl & 0xf)<<2) ;
		if(ipv4_pkt_is_fragmented(ipv4_hdr)){
			mbuf->ol_flags |= PKT_RX_IP_REASS;
		}
#ifdef ENABLE_PACKET_REASS
		if(pkt_reass_enable() &&
		   ipv4_pkt_is_fragmented(ipv4_hdr) && 
		   !(mbuf->ol_flags & PKT_RX_IP_REASS)){
			return ipv4_reassemble(mbuf,out_pkts,nb_pkts);
		}
#endif
		port_src=&ipv4tuple->port_src;
		port_dst=&ipv4tuple->port_dst;
		ipv=4;
	} else if(mbuf->eth_type == 0x86dd)/*if(ol_flags & PKT_RX_IPV6_HDR)*/ {
		ipv6_hdr = rte_pktmbuf_mtod_network(mbuf,struct ipv6_hdr *) ;
		proto=ipv6tuple->proto = ipv6_hdr->proto;
		rte_mov16(ipv6tuple->ip_src,ipv6_hdr->src_addr);
		rte_mov16(ipv6tuple->ip_dst,ipv6_hdr->dst_addr);
		ipv6tuple3.proto = ipv6tuple->proto;
		rte_mov16(ipv6tuple3.ip_src,ipv6_hdr->src_addr);
		rte_mov16(ipv6tuple3.ip_dst,ipv6_hdr->dst_addr);
		mbuf->transport_header=mbuf->network_header+sizeof(struct ipv6_hdr);
		port_src=&ipv6tuple->port_src;
		port_dst=&ipv6tuple->port_dst;
		ipv=6;
	}else {	
		//mbuf->transport_header=??? //reset to what?no need
		memset(&(mbuf->tuple),0,sizeof(mbuf->tuple));
		ipv=0 ;
	}

	switch (proto) {
		case IPPROTO_TCP:
			tcp_hdr = rte_pktmbuf_mtod_transport(mbuf,struct tcp_hdr *) ;
			*port_src=rte_be_to_cpu_16(tcp_hdr->src_port);
			*port_dst=rte_be_to_cpu_16(tcp_hdr->dst_port);
			mbuf->ifnfct = 1;
			break;
		case IPPROTO_UDP:
			udp_hdr = rte_pktmbuf_mtod_transport(mbuf,struct udp_hdr *) ;
			*port_src=rte_be_to_cpu_16(udp_hdr->src_port);
			*port_dst=rte_be_to_cpu_16(udp_hdr->dst_port);
			mbuf->ifnfct = 1;
			break;
		case IPPROTO_ICMP:
			icmphdr = rte_pktmbuf_mtod_transport(mbuf,struct icmp_hdr *) ;
			*port_src = rte_be_to_cpu_16(icmphdr->icmp_ident);
			*port_dst = *port_src;//(icmphdr->icmp_code << 8 | icmphdr->icmp_type);
			mbuf->ifnfct = 1;
			break;
		default:
			break;
	}
#if 0
	if(mbuf->hash.rss != 0) {
		mbuf->tag = mbuf->hash.rss;
	}else if(ipv==4)  {
#if 1
		static struct ipv4_tuple5 ipv4tmp;
		ipv4tmp.proto=ipv4tuple->proto;
		if(ipv4tuple->ip_src > ipv4tuple->ip_dst){
			ipv4tmp.ip_src=ipv4tuple->ip_src;
			ipv4tmp.ip_dst=ipv4tuple->ip_dst;
		}else {
			ipv4tmp.ip_dst=ipv4tuple->ip_src;
			ipv4tmp.ip_src=ipv4tuple->ip_dst;
		}
		if(ipv4tuple->port_src > ipv4tuple->port_dst){
			ipv4tmp.port_src=ipv4tuple->port_src;
			ipv4tmp.port_dst=ipv4tuple->port_dst;
		}else{
			ipv4tmp.port_src=ipv4tuple->port_dst;
			ipv4tmp.port_dst=ipv4tuple->port_src;
		}
		ipv4tuple=&ipv4tmp;
#endif
		mbuf->tag=RTE_JHASH((void *)ipv4tuple,sizeof(struct ipv4_tuple5 ),0);
	}else if(ipv==6)
		mbuf->tag=RTE_JHASH((void *)ipv6tuple,sizeof(struct ipv6_tuple5 ),0);
	else
		mbuf->tag=0;
#else
    if(ipv == 4) {
        ipv4tuple3.proto  = ipv4tuple->proto;
        if(ipv4tuple->ip_src > ipv4tuple->ip_dst) {
            ipv4tuple3.ip_src = ipv4tuple->ip_src;
            ipv4tuple3.ip_dst = ipv4tuple->ip_dst;
        }else {
            ipv4tuple3.ip_src = ipv4tuple->ip_dst;
            ipv4tuple3.ip_dst = ipv4tuple->ip_src;
        }       
        mbuf->tag=RTE_JHASH((void *)&ipv4tuple3, sizeof(struct ipv4_tuple3),0);
    }
    else if(ipv == 6)
        mbuf->tag=RTE_JHASH((void *)&ipv6tuple3, sizeof(struct ipv6_tuple3),0);
    else
        mbuf->tag=0;
#endif		

#if 0
	printf("eth_type=0x%x,IP dst = %08x, IP src = %08x, port dst = %d, port src = %d, "
		"proto = %d,inport = %d,tag=0x%x\n",mbuf->eth_type, (unsigned)ipv4tuple->ip_dst, (unsigned)ipv4tuple->ip_src,
				ipv4tuple->port_dst, ipv4tuple->port_src, ipv4tuple->proto,mbuf->inport,mbuf->tag);
#endif
	out_pkts[0] = mbuf;
	return 1;
}

int packet_preprocessing(struct __filter_info *filinfo,struct rte_mbuf *mbuf){
	int match;
	int filterindex=filinfo->filterindex;
	uint32_t index;
	struct ipv4_tuple5 *ipv4tuple=&mbuf->tuple.ipv4;

	Flow_table_lookup(mbuf);
	packet_dpi_analyzer(mbuf);
	Flow_TS(mbuf);
	
	mbuf->flltindex=0;
	mbuf->filterlist=NULL;
	mbuf->ctxindex=filterindex;

	if(unlikely(filterindex==SYS_FILTER_INVALID))
		return 0;
	match = rfc_lookup(filinfo->filterctx[filterindex],
		ipv4tuple->ip_src,
		ipv4tuple->ip_dst,
		ipv4tuple->proto,
		ipv4tuple->port_src,
		ipv4tuple->port_dst,
		0,
		mbuf->inport,
		(void **)&(mbuf->filterlist),
		&index);
	if(match<0) {
		printf("No rule matches packet %u.%u.%u.%u -- %u.%u.%u.%u,%d,%u-%u,drop it\n",
			NIPQUAD(ipv4tuple->ip_src),
			NIPQUAD(ipv4tuple->ip_dst),
			ipv4tuple->proto,
			ipv4tuple->port_src,
			ipv4tuple->port_dst );
		return -1;
	}
	
#if 0  //for debug
	{
		int i,k;
		struct eq *filterlist=(struct eq *)(mbuf->filterlist);
		struct trie_rfc *t=(struct trie_rfc *)(filinfo->filterctx[filterindex]);

		printf("Match OK.index=0x%x\n",index);
		printf("numrules=%d: ", filterlist->numrules);
		for (i= 0; i <filterlist->numrules; i++) {
			k=filterlist->rulelist[i];
			printf(" %d(0x%x:0x%x)--",k ,t->rule[k].filtId,t->rule[k].cost);
		}
		printf("firstid=0x%x\n", filterlist->first_rule_id);	
		printf("\n");
	}
#endif
	return 0;
}
//------------------------------------------------------------------------------
void list_portmode(void){
	int i;
	for(i=LOOP_SIMPLE;i<WORK_MODE_MAX;i++){
		printf("%d:%s\n",i,portmode[i]);
	}
}

int  set_portmode(struct system_info *sysinfo,uint8_t  portid,int mode,int value){
	struct portinfo *portinfos = &(sysinfo->portinfos);
	
	if(mode<LOOP_SIMPLE || mode>NAT_PORT){
		printf("error:mode=%d,invalid!\n",mode);
		return -1;
	}
	
	if(portid>=portinfos->portn){
		printf("port %d not found!\n",portid);
		return -1;
	}

	/*if(portinfos->mode[portid].mode == MIRROR_PORT) {
		printf("can not change mirror port %d work mode\n", portid);
		return -1;
	}*/
	
	if(mode==DIRECT_CONNECT_SIMPLE || 
		mode==DIRECT_CONNECT){
		if(value>=portinfos->portn){
			printf("port %d not found!\n",value);
			return -1;
		}
		if((portinfos->mode[value].mode == MIRROR_PORT) || 
		   (portinfos->mode[value].mode == BRIDGE_SIMPLE))
		{
			printf("port %d is %s, can not change to %s\n",
				value,
				(portinfos->mode[value].mode == MIRROR_PORT) ? "mirror_port" : "bridge",
				(mode == DIRECT_CONNECT_SIMPLE) ? "simple-direct-con" : "direct-con");
			return -1;
		}
		portinfos->mode[portid].mode=mode;
		portinfos->mode[portid].value=value;

		portinfos->mode[value].mode=mode;
		portinfos->mode[value].value=portid;

	}else if(mode == MIRROR_PORT) {
		int i = 0;		
		for(i = 0; i < portinfos->portn; i++) {
			if(mode == portinfos->mode[i].mode) 
				return -1;
		}
		portinfos->mode[portid].mode=mode;
		portinfos->mode[portid].value=value;
		sysinfo->mirror_port[0].portid = portid;
		sysinfo->mirror_port[1].portid = portid;
	}else {
		#ifdef BRIDGE_ON
		if(port_brid_update(portinfos,portid,mode,value)==-1)
			return -1;
		#endif
		portinfos->mode[portid].mode=mode;
		portinfos->mode[portid].value=value;
	}
	return 0;
}
//------------------------------------------------------------------------------
//mirror
#if(ENABLE_MIRROR_FUNCTION == 1)
static int
get_mirror_client_byfilterlist(struct __filter_info *filinfo,struct rte_mbuf *mbuf,void **filterlist,uint8_t port){
	int match;
	int filterindex=filinfo->filterindex;
	uint32_t index;
	struct ipv4_tuple5 *ipv4tuple=&mbuf->tuple.ipv4;
	
	if(unlikely(filterindex==SYS_FILTER_INVALID))
		return -1;
	
	match = rfc_lookup(filinfo->filterctx[filterindex],
		ipv4tuple->ip_src,
		ipv4tuple->ip_dst,
		ipv4tuple->proto,
		ipv4tuple->port_src,
		ipv4tuple->port_dst,
		0,
		port,
		filterlist,
		&index);
	if(match<0) {
		#if 0
		printf("No rule matches packet %u.%u.%u.%u -- %u.%u.%u.%u,%d,%u-%u,drop it\n",
			NIPQUAD(ipv4tuple->ip_src),
			NIPQUAD(ipv4tuple->ip_dst),
			ipv4tuple->proto,
			ipv4tuple->port_src,
			ipv4tuple->port_dst );
		#endif
		return -1;
	}
#if 0  //for debug
	{
		int i,k;
		struct eq *fltlist=(struct eq *)(*filterlist);
		struct trie_rfc *t=(struct trie_rfc *)(filinfo->filterctx[filterindex]);

		//printf("Match OK.index=0x%x\n",index);
		printf("mirrror Match OK.index=0x%x\n",index);
		printf("numrules=%d: ", fltlist->numrules);
		for (i= 0; i <fltlist->numrules; i++) {
			k=fltlist->rulelist[i];
			printf(" %d(0x%x:0x%x)--",k ,t->rule[k].filtId,t->rule[k].cost);
		}
		printf("firstid=0x%x\n", fltlist->first_rule_id);	
		//printf("\n");
		printf("end of mirror match\n");
	}
#endif
	return 0;
}

static int
queue_eneque_help_for_mirror(struct client_rxqueue *tx,struct pcap_buf  *pbuf)
{	
	uint16_t nb_tx;
	uint32_t rindex;

	if(1==tx->qnum)
		rindex=0;
	else  {
		switch(tx->policy){
			case ROUND_ROBIN:
				rindex=rte_atomic64_read(&(tx->total_rx))%tx->qnum;
				break;
			case SAMESRC_SAMEDEST:
				rindex=pbuf->header.tag%tx->qnum;
				break;
			case BY_FILTER:{
				int qs=((pbuf->header.flltarget)>>8)&0xff;
				int qn=(pbuf->header.flltarget&0xff);
				
				if(qn==1)
					rindex=qs;
				else {
					rindex=qs+pbuf->header.tag%qn;
				}
			}
			break;	
			default:
				printf("%s,%d:impossible",__FUNCTION__,__LINE__);
				rindex=0;
				break;
		}
	}
	nb_tx=rte_ring_enqueue_burst(tx->rings[rindex],(void **)&pbuf,1);
	
	if(!nb_tx) {
	#if (ENABLE_APP_STATISTICS == 1)
		rte_atomic64_inc(&(tx->total_dp));
	#endif
		rte_mempool_put(pbuf->header.pool, pbuf);
	}
	else  {
		tx->usleep_times[rindex]=0;
	#if (ENABLE_APP_STATISTICS == 1)
		rte_atomic64_inc(&(tx->total_rx));
	#else 
		if(tx->policy == ROUND_ROBIN)
			rte_atomic64_inc(&(tx->total_rx));
	#endif
	}
	return nb_tx;
}

static int do_mirror_help(struct clientinfo *client,struct rte_mbuf *mbuf){
	struct pcap_buf  *pbuf;
	struct _pcap_pkthdr  *pkthdr;
	
	//malloc
	if (rte_mempool_get(client->bufpool,(void **) &pbuf) < 0) {
		printf("clinet %s ,get mempool fail,count=%d,free_count=%d\n",
			client->name,rte_mempool_count(client->bufpool),rte_mempool_free_count(client->bufpool));
		return -1;
	}
	//clone,fill pcap header
	if(unlikely(mbuf->data_len > MAX_PCAP_PACKET_SZ)) {
		printf("impossbile print:%s %d,mbuf len = %d > pcap max len %d\n",
				__FUNCTION__,__LINE__,mbuf->data_len , MAX_PCAP_PACKET_SZ);
		return -1;
	}
	rte_memcpy(pbuf->data,rte_pktmbuf_mtod(mbuf,char *),mbuf->data_len);
	pkthdr=&(pbuf->header.pcap_header);
	pkthdr->caplen=mbuf->data_len;
	pkthdr->len=mbuf->data_len;
	pkthdr->ts.tv_sec=(*msec)/1000;
	pkthdr->ts.tv_usec=(*msec)%1000*1000;
	pbuf->header.tag=mbuf->tag;
	pbuf->header.flltarget=mbuf->flltarget;
	pbuf->header.pool=client->bufpool;
	
	//send
	queue_eneque_help_for_mirror(&(client->queue),pbuf); //note:free when fail

	return 0;
}

int
set_mirror_port_rules(struct system_info *sysinfo, int dir)
{
	int i = 0;
	char *filter[CLIENT_MAX_FILTER];
	
	for(i = 0; i < CLIENT_MAX_FILTER; i++) {
		if(!strlen(sysinfo->mirror_port[dir].user_rule[i])){
			filter[i] = NULL;
			break;
		}
		printf("user_rule[%d] = %s\n", i, sysinfo->mirror_port[dir].user_rule[i]);
		filter[i] = sysinfo->mirror_port[dir].user_rule[i];
	}
	
	if(-1 == get_filter(&(sysinfo->mirror_port[dir].m_filter),(const char * const *)filter, CLIENT_MAX_FILTER))
		return -1;
	
	system_filter_update(sysinfo, dir + 1);

	filter_dump_bymirror(&(sysinfo->mirror_port[dir]));

	return 0;
}

static int
do_mirror_port(struct system_info *sysinfo, struct rte_mbuf *src_mbuf, int dir) {
	struct rte_mbuf *m_clone;
		
	if(src_mbuf->port == sysinfo->mirror_port[dir].portid)
		return -1;
	
	// clone
	m_clone = rte_pktmbuf_clone(src_mbuf, sysinfo->pktmbuf_hdr_pool); 
	if(unlikely(m_clone == NULL)) {
		printf("impossible:%s,%d,rte_pktmbuf_clone fail!\n", __FUNCTION__, __LINE__);
		return -1;
	}
	m_clone->port = sysinfo->mirror_port[dir].portid;
	m_clone->userdef = MIRROR_PORT;

	// send to server-tx
	queue_eneque_help(sysinfo->mirror_port[dir].svrtx_queue, m_clone);
	
	return 0;
}

static int 
do_mirror(struct system_info *sysinfo,struct rte_mbuf *buf,uint8_t port,int inout){
	struct eq  *filterlist;
	struct clientinfo *client;
	struct __filter_info *filinfo=&(sysinfo->filterinfo[inout]);
	struct trie_rfc *t=(struct trie_rfc *)(filinfo->filterctx[filinfo->filterindex]);
	int index;
	uint32_t cost = 0;
	uint32_t filtId=(uint32_t)-2;
	uint8_t priority,fixedid;
	int k;
	if(-1==get_mirror_client_byfilterlist(filinfo,buf,(void **)&filterlist,port))
		return -1;

	for(index=0;index < filterlist->numrules;index++){
		k=filterlist->rulelist[index];
		if(t->rule[k].filtId!=filtId) {
			filtId=t->rule[k].filtId;
			cost=t->rule[k].cost;
			if(filtId == (uint32_t)-1) {
				do_mirror_port(sysinfo, buf, inout - 1);
				continue;
			}
			priority=(filtId>>8)&0xff;
			fixedid=filtId&0xff;
			buf->flltarget=cost&0xffff;
			client=&(sysinfo->cinfos[priority][fixedid]);
#if 0
			printf("prioriy=%d,fixed=%d,client=%s\n\n",priority,fixedid,client->name);
#endif
	
			if(unlikely(client->processid==0)) {
				printf("exception in get_client_byfilterlist(),client %s may existed,skip it!\n ",client->name);
				continue;
			}
			do_mirror_help(client,buf);
		}
	}
	return 0;
}

static int 
do_mirror_inout(struct system_info *sysinfo,struct rte_mbuf *buf){
	struct rte_mbuf * out_pkts[ANALYZE_MAX_MBUF];
	int pkts_num;
	uint16_t index;
	if(sysinfo->mirror_flag.flag1) {
		pkts_num = packet_tuple_analyzer(buf,out_pkts,ANALYZE_MAX_MBUF);
		for (index = 0; index < pkts_num; index++)
		{
			if(sysinfo->mirror_flag.flag2[0])
				do_mirror(sysinfo,out_pkts[index],out_pkts[index]->inport,FILTER_MIRROR_IN);
			if(sysinfo->mirror_flag.flag2[1])
				do_mirror(sysinfo,out_pkts[index],out_pkts[index]->port,FILTER_MIRROR_OUT);
		}
	}
	return 0;
} 

static int 
do_mirror_in_bulk(struct system_info *sysinfo,struct rte_mbuf ** buf, uint16_t nb_pkts){
	int i;
	struct rte_mbuf *out_pkts[ANALYZE_MAX_MBUF];
	int pkts_num;
	uint16_t index;
	if(sysinfo->mirror_flag.flag1) {
		for(i=0;i<nb_pkts;i++) {
			pkts_num = packet_tuple_analyzer(buf[i],out_pkts,ANALYZE_MAX_MBUF);
			for (index = 0; index < pkts_num; index++)
			{
				if(sysinfo->mirror_flag.flag2[0])
					do_mirror(sysinfo,out_pkts[index],out_pkts[index]->inport,FILTER_MIRROR_IN);
				if(sysinfo->mirror_flag.flag2[1])
					do_mirror(sysinfo,out_pkts[index],out_pkts[index]->port,FILTER_MIRROR_OUT);
			}
		}
	}
	return 0;
}

static int 
do_mirror_out_bulk(struct system_info *sysinfo,struct rte_mbuf ** buf, uint16_t nb_pkts){
	int i;
	
	if(sysinfo->mirror_flag.flag2[1]) {
		for(i=0;i<nb_pkts;i++) 
			do_mirror(sysinfo,buf[i],buf[i]->port,FILTER_MIRROR_OUT);
	}
	return 0;
}

void dump_pcapbuf(struct pcap_buf  *buf)
{	
	int i;
	//print header
	printf("buf %p info:\n",buf);
	printf("pcap time:%lu-%lu\n",buf->header.pcap_header.ts.tv_sec,buf->header.pcap_header.ts.tv_usec);
	printf("caplen=%d,len=%d\n",buf->header.pcap_header.caplen,buf->header.pcap_header.len);
	printf("tag=0x%x,flltarget=0x%x\n",buf->header.tag,buf->header.flltarget);
	//print data
	for(i=0;i<buf->header.pcap_header.len;i++){
		if(i&&i%8==0)
			printf("\n");
		printf("%02x ",buf->data[i]);
	}
	printf("\n");
}

void *mirror_open(struct client_reginfo *info,char *coremask)
{
	struct system_info *sysinfo;
	struct clientinfo *client;	
	
	sysinfo=get_dpdk_shm_cpu(info->name,"program1",coremask,1);
	if (!sysinfo)
		return NULL;
	
	client=client_register(info);
	if(!client)
		return NULL;
	
	return client;
}

void mirror_close(void *handle)
{
	client_unregister(handle);
}

struct mirror_arg {
	int cntflag;
	void *handle;
	int cnt;
	_pcap_handler callback;
	u_char *user;
};

static int  
mirror_loop_help( void *arg) {
	struct mirror_arg  *parg=(struct mirror_arg *)arg;
	int flag=parg->cntflag;
	int * cnt=&(parg->cnt);
	struct clientinfo *client=parg->handle;
	unsigned lcore_count,lcore,index;
	struct pcap_buf  *buf[PACKET_READ_SIZE];
	uint32_t rx_count=0,j;
	
	lcore_count=rte_lcore_count();
	lcore = rte_lcore_id();
	printf("server are %d  cores,my is %d.\n",lcore_count,lcore);
	index=lcore%lcore_count;
	
	while(*cnt>=-1){
		rx_count=dpdk_dequeue1(client, index, (void **)buf, PACKET_READ_SIZE);
		//if(!rx_count)
		//	break;
		if(flag)
			*cnt-=rx_count;
		for(j=0;j<rx_count;j++) {
			if(parg->callback)
				parg->callback(parg->user,&(buf[j]->header.pcap_header),buf[j]->data);
			//free 
			rte_mempool_put(client->bufpool,(void *)buf[j]);
		}
	}
	return 0;
}

int mirror_loop(void *handle, int cnt, _pcap_handler callback,u_char *user)
{
	uint32_t lcore;
	struct mirror_arg  arg={(cnt>0),handle,cnt,callback,user};
	if(!cnt)
		return 0;
	rte_eal_mp_remote_launch(mirror_loop_help, &arg, CALL_MASTER);
	RTE_LCORE_FOREACH_SLAVE(lcore) {
		if (rte_eal_wait_lcore(lcore) < 0) {
			return -1;
		}
	}
	return 0;
}
#endif

//------------------------------------------------------------------------------
#ifdef  CONFIG_DPDK_FRAME_SERVER
int  dpdk_enqueue_byeth(struct system_info *sysinfo,struct rte_mbuf *buf) {
	int ret=0;

#if(ENABLE_MIRROR_FUNCTION == 1)
	if(sysinfo->mirror_flag.flag2[0]) {
		do_mirror(sysinfo,buf,buf->inport,FILTER_MIRROR_IN);
	}
#endif
	
#if (CLIENT_TRANS_BYFILTER ==1)
	struct clientinfo *next;
	next=get_client_byfilterlist(sysinfo,buf);
	if(next) 
		queue_eneque_help(&(next->queue),buf);
	else {
		rte_pktmbuf_free(buf);
		ret=-1;
	}
#else 
	if(sysinfo->in.first) 
		queue_eneque_help(&(sysinfo->in.first->queue),buf);
	else if (sysinfo->out.first) 
		queue_eneque_help(&(sysinfo->out.first->queue),buf);
	else {
		rte_pktmbuf_free(buf);
		ret=-1;
	}
#endif
	return ret;
}

static void (*p_update_port_status)(uint8_t port_id)=NULL;

static void
port_check_callback(uint8_t port_id, enum rte_eth_event_type type, void *param)
{
	RTE_SET_USED(param);
	
	printf("%s : Event type: %s\n", __func__, type == RTE_ETH_EVENT_INTR_LSC ? "LSC interrupt" : "unknown event");

	if(p_update_port_status)
		p_update_port_status(port_id);
}

int
dpdk_port_init(struct system_info *sysinfo,uint8_t port_num,
		struct rte_eth_conf *port_conf,struct port_rings *portrings)
{
	static struct rte_eth_conf port_conf_default = {
		.rxmode = {
			.split_hdr_size = 0,
			.header_split   = 0, /**< Header Split disabled */
			.hw_ip_checksum = 0, /**< IP checksum offload disabled */
			.hw_vlan_filter = 0, /**< VLAN filtering disabled */
			.jumbo_frame    = 0, /**< Jumbo Frame Support disabled */
			.hw_strip_crc   = 0, /**< CRC stripped by hardware */
			.mq_mode = ETH_MQ_RX_RSS
		},
		.rx_adv_conf = {
			.rss_conf = {
				.rss_key = NULL,
				.rss_hf = ETH_RSS_IP | ETH_RSS_TCP | ETH_RSS_UDP,
			},
		},
		.txmode = {
			.mq_mode = ETH_MQ_TX_NONE,
		},
		.intr_conf = {
			.lsc = 1, /**< lsc interrupt feature enabled */
		},
	};

	static const struct rte_eth_rxconf rx_conf_default = {
		.rx_thresh = {
			.pthresh = RX_PTHRESH,
			.hthresh = RX_HTHRESH,
			.wthresh = RX_WTHRESH,
		},
		.rx_free_thresh = 32,
		.rx_drop_en = 0,
	};

	static struct rte_eth_txconf tx_conf_default = {
		.tx_thresh = {
			.pthresh = TX_PTHRESH,
			.hthresh = TX_HTHRESH,
			.wthresh = TX_WTHRESH,
		},
		.tx_free_thresh = 0,
		.tx_rs_thresh = 0,
		.txq_flags = 0,
	};

	uint16_t rx_rings=0,tx_rings=0,rx_ring_size=0,tx_ring_size=0;
	uint16_t q;
	int retval;
	struct rte_eth_dev_info dev_infos;

	rte_eth_dev_info_get(port_num, &dev_infos);
	
	if(!port_conf)
		port_conf=&port_conf_default;

	if(!strcmp(dev_infos.driver_name, "rte_igb_pmd") ||
	   !strcmp(dev_infos.driver_name, "rte_em_pmd"))
	{
		if(portrings) {
			if(portrings->rx_rings > dev_infos.max_rx_queues) {
				if(dev_infos.max_rx_queues < ONE_G_PORT_RX_QUEUES)
					rx_rings = dev_infos.max_rx_queues;
				else
					rx_rings = ONE_G_PORT_RX_QUEUES;
			}
			else {
				if(portrings->rx_rings < ONE_G_PORT_RX_QUEUES)
					rx_rings = portrings->rx_rings;
				else
					rx_rings = ONE_G_PORT_RX_QUEUES;
			}

			if(portrings->tx_rings > dev_infos.max_tx_queues) {
				if(dev_infos.max_tx_queues < ONE_G_PORT_TX_QUEUES)
					tx_rings = dev_infos.max_tx_queues;
				else
					tx_rings = ONE_G_PORT_TX_QUEUES;
			}else {
				if(portrings->tx_rings < ONE_G_PORT_TX_QUEUES)
					tx_rings = portrings->tx_rings;
				else
					tx_rings = ONE_G_PORT_TX_QUEUES;
			}
			
			rx_ring_size=portrings->rx_ring_size;
			tx_ring_size=portrings->tx_ring_size;
		}else {
			if(dev_infos.max_rx_queues < ONE_G_PORT_RX_QUEUES)
				rx_rings = dev_infos.max_rx_queues;
			else
				rx_rings = ONE_G_PORT_RX_QUEUES;
			
			if(dev_infos.max_tx_queues < ONE_G_PORT_TX_QUEUES)
				tx_rings = dev_infos.max_tx_queues;
			else
				tx_rings = ONE_G_PORT_TX_QUEUES;
			
			rx_ring_size = RTE_MP_RX_DESC_DEFAULT;
			tx_ring_size = RTE_MP_TX_DESC_DEFAULT;
		}
		if(!strcmp(dev_infos.driver_name, "rte_igb_pmd"))
			tx_conf_default.tx_thresh.wthresh = 4;
		else
			tx_conf_default.tx_thresh.wthresh = 0;
	}else if((!strcmp(dev_infos.driver_name, "rte_ixgbe_pmd")) 
	      || (!strcmp(dev_infos.driver_name, "rte_i40e_pmd"))) 
	{
		if(portrings) {
			rx_rings=portrings->rx_rings;
			tx_rings=portrings->tx_rings;
			rx_ring_size=portrings->rx_ring_size;
			tx_ring_size=portrings->tx_ring_size;
		
			if(rx_rings > TEN_G_PORT_RX_QUEUES)
				rx_rings = TEN_G_PORT_RX_QUEUES;
			if(tx_rings > TEN_G_PORT_TX_QUEUES)
				tx_rings = TEN_G_PORT_TX_QUEUES;
		}else {		
			if(dev_infos.max_rx_queues < TEN_G_PORT_RX_QUEUES)
				rx_rings = dev_infos.max_rx_queues;
			else
				rx_rings = TEN_G_PORT_RX_QUEUES;
			
			if(dev_infos.max_tx_queues < TEN_G_PORT_TX_QUEUES)
				tx_rings = dev_infos.max_tx_queues;
			else
				tx_rings = TEN_G_PORT_TX_QUEUES;
			rx_ring_size = RTE_MP_RX_DESC_DEFAULT;
			tx_ring_size = RTE_MP_TX_DESC_DEFAULT;
		}
		tx_conf_default.tx_thresh.wthresh = 0;
	}

	printf("Port %u init ... ", (unsigned)port_num);
	
	/* Standard DPDK port initialisation - config port, then set up
	 * rx and tx rings */
	if ((retval = rte_eth_dev_configure(port_num, rx_rings, tx_rings,
		port_conf)) != 0)
		return retval;

	for (q = 0; q < rx_rings; q++) {
		retval = rte_eth_rx_queue_setup(port_num, q, rx_ring_size,
				rte_eth_dev_socket_id(port_num),
				&rx_conf_default, sysinfo->pktmbuf_pool);
		if (retval < 0) return retval;
	}

	for ( q = 0; q < tx_rings; q ++ ) {
		retval = rte_eth_tx_queue_setup(port_num, q, tx_ring_size,
				rte_eth_dev_socket_id(port_num),
				&tx_conf_default);
		if (retval < 0) return retval;
	}
	sysinfo->portinfos.rxrings[port_num]=rx_rings;
	sysinfo->portinfos.txrings[port_num]=tx_rings;
#if (SERVER_TX_BULK_MODE==0)
	{
		int i;
		for(i=0;i<SERVER_TX_QUEUES;i++)
			sysinfo->portinfos.txcpu[port_num][i]=(uint8_t)-1;
	}
#endif
	memcpy(&sysinfo->portinfos.portconf[port_num],port_conf,sizeof( struct rte_eth_conf));
	
	rte_eth_promiscuous_enable(port_num);
	
	rte_eth_dev_callback_register(port_num, RTE_ETH_EVENT_INTR_LSC, port_check_callback, NULL);

	rte_eth_stats_reset(port_num);

	retval  = rte_eth_dev_start(port_num);
	if (retval < 0) return retval;

	printf( "done: \n");

	return 0;
}

int dpdk_sysport_init(struct system_info *sysinfo,uint64_t portmask,void *port_callbk) {
	unsigned i;
	unsigned total_ports = rte_eth_dev_count(); 

	if(total_ports > RTE_MAX_ETHPORTS){
		printf("total_ports=%d,but RTE_MAX_ETHPORTS=%d\n",total_ports,RTE_MAX_ETHPORTS);
		exit(-1);
	}

	for(i=0;i<total_ports;i++) {
		if(portmask&(1<<i)) {
			sysinfo->portinfos.mode[i].mode=DEAULT_MODE;
			sysinfo->portinfos.mode[i].value=0;
		}	
	}
	sysinfo->portinfos.portn=total_ports;
	p_update_port_status=(void (*)(uint8_t port_id))port_callbk;
	return 0;
}

void
dpdk_check_ports_link_status(struct portinfo *portinfos)
{
#define CHECK_INTERVAL 100 /* 100ms */
#define MAX_CHECK_TIME 90 /* 9s (90 * 100ms) in total */
	uint8_t portid, count, all_ports_up, print_flag = 0;
	uint8_t port_num=portinfos->portn;
	struct rte_eth_link  link;

	printf("\nChecking link status");
	for (count = 0; count <= MAX_CHECK_TIME; count++) {
		all_ports_up = 1;
		for (portid = 0; portid < port_num; portid++) {
			memset(&link, 0, sizeof(link));
			rte_eth_link_get_nowait(portid, &link);
			if(link.link_status) {
				portinfos->status_uk[portid]|=USER_STATUS;
				if(link.link_speed==10000)
					portinfos->status_uk[portid]|=IS_IXGBE;
			}
			else
				portinfos->status_uk[portid]&=~USER_STATUS;
			/* print link status if flag set */
			if (print_flag == 1) {
				if (link.link_status)
					printf("Port %d Link Up - speed %u "
						"Mbps - %s\n", portid,
						(unsigned)link.link_speed,
						(link.link_duplex == ETH_LINK_FULL_DUPLEX) ?
							("full-duplex") : ("half-duplex\n"));
				else
					printf("Port %d Link Down\n",portid);
				continue;
			}
			/* clear all_ports_up flag if any link down */
			if (link.link_status == 0) {
				all_ports_up = 0;
				break;
			}
		}
		/* after finally printing all link status, get out */
		if (print_flag == 1)
			break;

		if (all_ports_up == 0) {
			printf(".");
			rte_delay_ms(CHECK_INTERVAL);
		}

		/* set the print_flag if all ports up or timeout */
		if (all_ports_up == 1 || count == (MAX_CHECK_TIME - 1)) {
			print_flag = 1;
			printf("done\n");
		}
	}
}


void idle_task(void) {
	while(1)
		sleep(100);
}
//------------------------------------------------------------------------------
#include <sys/socket.h>
#include <netinet/in.h>
#include <linux/if.h>
#include <arpa/inet.h>
#include <linux/sockios.h>

int setetherstatus(const char *eth,int isup)
{
        struct ifreq ifr;
        int sockfd;
        int ret=-1;

        if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0){
                perror("Create socket fails:");
                return -1;
        }

        strcpy(ifr.ifr_name, eth);
        if (ioctl(sockfd, SIOCGIFFLAGS, (char *)&ifr) < 0){
                perror("ioctl SIOCGIFFLAGS fails:");
                goto end;
        }
        if(!isup)
                ifr.ifr_flags &= ~IFF_UP;
        else
                ifr.ifr_flags |= IFF_UP;
        if (ioctl(sockfd, SIOCSIFFLAGS, (char *)&ifr) < 0){
                perror("ioctl SIOCSIFFLAGS fails:");
                goto end;
        }
        ret=0;
end:
        close(sockfd);
        return ret;
}

#if 0 /* remain, may be used in the future */
static int getetherstatus(const char *eth){
        int s;
        int err;
        struct ifreq ifr;
        s=socket(AF_INET,SOCK_DGRAM,0);
        if(s<0){
                perror("socket error");
                return -1;
        }

        strcpy(ifr.ifr_name,eth);
        err=ioctl(s,SIOCGIFFLAGS,&ifr);
        if(!err){
                printf("SIOCGIFFLAGS:%d\n",(ifr.ifr_flags&IFF_UP));
        }
        close(s);
        return 0;
}
#endif

static int kni_check_status_when_init(struct portinfo *portinfos){
	int i,user_status,kern_status;
	printf("%s--------------->\n",__FUNCTION__);
	for(i=0;i<portinfos->portn;i++){
		user_status = portinfos->status_uk[i] & USER_STATUS;
		kern_status = portinfos->status_uk[i] & KERN_STATUS;
		printf("%d:status=%x:user=%d,kernel=%d\n",i,portinfos->status_uk[i],user_status,kern_status);
		if(user_status && ! kern_status ){
			printf("Autostat %s..\n",portinfos->kni[i]->name);
			if(portinfos->status_uk[i] & KNI_STATUS)
				setetherstatus((const char *)(portinfos->kni[i]->name),1);
				
		}
	}
	return -1;
}


/* Callback for request of changing MTU */
static int
kni_change_mtu(uint8_t port_id, unsigned new_mtu)
{
	int ret;
	struct rte_eth_conf *conf;
	struct system_info *system;
	uint16_t nb_rx_q = 0, nb_tx_q = 0;

	if (port_id >= rte_eth_dev_count()) {
		printf("Invalid port id %d\n", port_id);
		return -EINVAL;
	}

	system=get_dpdk_system();
	conf=&system->portinfos.portconf[port_id];

	printf("Change MTU of port %d to %u\n", port_id, new_mtu);

	/* Stop specific port */
	rte_eth_dev_stop(port_id);

	/* Set new MTU */
	if (new_mtu > ETHER_MAX_LEN)
		conf->rxmode.jumbo_frame = 1;
	else
		conf->rxmode.jumbo_frame = 0;

	/* mtu + length of header + length of FCS = max pkt length */
	conf->rxmode.max_rx_pkt_len = new_mtu + KNI_ENET_HEADER_SIZE +
							KNI_ENET_FCS_SIZE;
	
	ret = rte_eth_dev_set_mtu(port_id, new_mtu);
	if (ret < 0) {
		printf("Fail to set mtu port %d\n", port_id);
		return ret;
	}

	if(system->portinfos.status_uk[port_id] & IS_IXGBE) {
		nb_rx_q = TEN_G_PORT_RX_QUEUES;
		nb_tx_q = TEN_G_PORT_TX_QUEUES;
	}else {
		nb_rx_q = ONE_G_PORT_RX_QUEUES;
		nb_tx_q = ONE_G_PORT_TX_QUEUES;
	}
	ret = rte_eth_dev_configure(port_id, nb_rx_q, nb_tx_q, conf);
	if (ret < 0) {
		printf("Fail to reconfigure port %d\n", port_id);
		return ret;
	}

	/* Restart specific port */
	ret = rte_eth_dev_start(port_id);
	if (ret < 0) {
		printf("Fail to restart port %d\n", port_id);
		return ret;
	}

	return 0;
}


/* Callback for request of configuring network interface up/down */
static int
kni_config_network_interface(uint8_t port_id, uint8_t if_up)
{
	int ret = 0;

	if (port_id >= rte_eth_dev_count() || port_id >= RTE_MAX_ETHPORTS) {
		printf("Invalid port id %d\n", port_id);
		return -EINVAL;
	}

	printf("Configure network interface of %d %s\n",
					port_id, if_up ? "up" : "down");

	if (if_up != 0) { /* Configure network interface up */
		rte_eth_dev_stop(port_id);
		ret = rte_eth_dev_start(port_id);
	} else { /* Configure network interface down */
		rte_eth_dev_stop(port_id);
		if(p_update_port_status)
			p_update_port_status(port_id);
	}

	if (ret < 0)
		printf("Failed to start port %d\n", port_id);

	return ret;
}

static struct rte_kni *
kni_alloc(struct portinfo *portinfos,uint8_t port_id)
{
	struct rte_kni_conf conf;
	struct rte_kni_ops ops;
	struct rte_eth_dev_info dev_info;
	struct rte_kni *kni;
	struct system_info *system=get_dpdk_system();
	
	/* Clear conf at first */
	memset(&conf, 0, sizeof(conf));
		
	snprintf(conf.name, RTE_KNI_NAMESIZE,
					"vEth%u", port_id);
	//conf.core_id = 0;//later optimize
	conf.force_bind = 1;
	if(port_id % 2 == 0)
		conf.core_id = 5;//2;//later optimize
	else
		conf.core_id = 1;//later optimize
	conf.group_id = (uint16_t)port_id;
	conf.mbuf_size = MAX_PACKET_SZ;
	conf.status_uk=(void *)(portinfos->status_uk_phys);
	conf.stats_uk = (void *)(portinfos->stats_uk_phys);
	
	memset(&dev_info, 0, sizeof(dev_info));
	rte_eth_dev_info_get(port_id, &dev_info);
	conf.addr = dev_info.pci_dev->addr;
	conf.id = dev_info.pci_dev->id;

	memset(&ops, 0, sizeof(ops));
	ops.port_id = port_id;
	ops.change_mtu = kni_change_mtu;
	ops.config_network_if = kni_config_network_interface;

	kni=rte_kni_alloc(system->pktmbuf_pool, &conf,&ops);
	if(kni==NULL) {
		rte_exit(EXIT_FAILURE, "Fail to create kni for "
						"port: %d\n", port_id);
	}
	return kni;
}

static void *kni_process(void *vargp ){
	struct kni_ctl *knictl=(struct kni_ctl *)vargp;
	volatile uint32_t *fstop=knictl->fstop;
	printf("%s----------------->\n",__FUNCTION__);
	while(*fstop) {
		if(-2==rte_kni_handle_request2(knictl->get_kni_byport))
			break;
	}
	printf("%s exit!\n",__FUNCTION__);
	return 0;
}

static pthread_t kni_thread;
/* Initialize KNI subsystem */
void 
init_kni_um(struct portinfo *portinfos,struct kni_ctl *knictl) {
	unsigned int i;
	unsigned int port_num_max=portinfos->portn;
	rte_kni_init(port_num_max); 
	pthread_create(&kni_thread, NULL, kni_process, knictl);
	usleep(10);
	for(i=0;i<port_num_max;i++) {
		portinfos->kni[i]=kni_alloc(portinfos,i);
		portinfos->status_uk[i] |= KNI_STATUS;
		kni_allocate_mbufs(portinfos->kni[i],-1);
	}
	kni_check_status_when_init(portinfos);
}

static void 
kni_free_kni(struct portinfo *portinfos){
	unsigned int i;
	unsigned int port_num_max=portinfos->portn;
	printf("kni_free_kni...\n");
	for(i=0;i<port_num_max;i++) {
		if(portinfos->kni[i]) {
			rte_kni_release(portinfos->kni[i]);
			portinfos->kni[i]=NULL;
		}
	}	
}
void 
exit_kni_um(struct portinfo *portinfos)
{
	void*status;
	printf("notify kni exit!\n");
	kni_free_kni(portinfos);
	rte_kni_stop();
	pthread_join(kni_thread,&status);
}
//------------------------------------------------------------------------------

int port_input (struct system_info *sysinfo,struct rte_mbuf *buf,int cpu){
	struct port_workmode	*workmode=sysinfo->portinfos.mode;
	uint8_t *status;
	
	uint8_t port=buf->port;
	uint8_t mode=workmode[port].mode;
	
	struct rte_mbuf * out_pkts[ANALYZE_MAX_MBUF];
	int pkts_num;
	uint16_t index;
	unsigned rss_ring_index = 0;
	unsigned cpu_count = rte_lcore_count() - 1;
	uint16_t ret = 0;
	
	switch(mode){
		case LOOP_SIMPLE:
			#if(ENABLE_MIRROR_FUNCTION == 1)
			do_mirror_inout(sysinfo,buf);
			#endif
			if(0==rte_eth_tx_burst(port, 0, &buf, 1)) {
				rte_pktmbuf_free(buf);
			}
			return 0;
		case DIRECT_CONNECT_SIMPLE:
			#if(ENABLE_MIRROR_FUNCTION == 1)
			do_mirror_inout(sysinfo,buf);
			#endif
			status=sysinfo->portinfos.status_uk;
			port=workmode[port].value;
			if(unlikely(!(status[port]&USER_STATUS))) {
					printf("port %d is not up !\n",port);
					rte_pktmbuf_free(buf);
					return -1;
			}
			if(0==rte_eth_tx_burst(port, 0, &buf, 1)) {
				rte_pktmbuf_free(buf);
			}
			return 0;
		case INVALID_MODE:
			#if(ENABLE_MIRROR_FUNCTION == 1)
			do_mirror_inout(sysinfo,buf);
			#endif
			printf("port mode is invalid,drop it!\n");
			rte_pktmbuf_free(buf);
			return -1;
		case DIRECT_CONNECT:
			buf->inport=buf->port;
			buf->userdef=mode;
            buf->rings_cnt = NULL;
			//if(sysinfo->kernel_stack_flag == 1)
				buf->port=workmode[port].value;

			pkts_num = packet_tuple_analyzer(buf,out_pkts,ANALYZE_MAX_MBUF);
			
			for (index = 0; index < pkts_num; index++ )
			{
#ifdef ANTI_DDOS_ON
				if (sysinfo->ddos_flag == 1 && 
					fp_ddos_defense(out_pkts[index]) == DDOS_PACKET_DROP) {
					rte_pktmbuf_free(out_pkts[index]);
					continue;
				}		
#endif
				rss_ring_index = out_pkts[index]->tag % cpu_count;
				ret = rte_ring_enqueue_burst(sysinfo->rss_rings[rss_ring_index],(void **)&out_pkts[index],1);
				if(!ret) {
					rte_pktmbuf_free(out_pkts[index]);
				}
			}			
			return 0;
		case BRIDGE_SIMPLE:
			buf->inport=buf->port;
			buf->userdef=mode;
            buf->rings_cnt = NULL;

#ifdef BRIDGE_ON
			do_bridge(buf);
#endif

			pkts_num = packet_tuple_analyzer(buf,out_pkts,ANALYZE_MAX_MBUF);
			
			for (index = 0; index < pkts_num; index++ )
			{
				if(out_pkts[index]->eth_type == 0x86dd) {
					if(sysinfo->kernel_stack_flag == 0) {
						if(!rte_kni_tx_burst(sysinfo->portinfos.kni[out_pkts[index]->port], &out_pkts[index], 1)) {
							rte_pktmbuf_free(out_pkts[index]);
						}
					}else {
						rte_pktmbuf_free(out_pkts[index]);
					}
					continue;
				}
#ifdef ANTI_DDOS_ON
				if (sysinfo->ddos_flag == 1 && 
					fp_ddos_defense(out_pkts[index]) == DDOS_PACKET_DROP) {
					rte_pktmbuf_free(out_pkts[index]);
					continue;
				}		
#endif	
				rss_ring_index = out_pkts[index]->tag % cpu_count;
				ret = rte_ring_enqueue_burst(sysinfo->rss_rings[rss_ring_index],(void **)&out_pkts[index],1);
				if(!ret) {
					rte_pktmbuf_free(out_pkts[index]);
				}
			}		
			return 0;
		case MIRROR_PORT:
			rte_pktmbuf_free(buf);
			return 0;
		case NAT_PORT:
			buf->inport = buf->port;
			buf->userdef = mode;
            buf->rings_cnt = NULL;
				
			pkts_num = packet_tuple_analyzer(buf,out_pkts,ANALYZE_MAX_MBUF);
			
			for (index = 0; index < pkts_num; index++) {
				if(out_pkts[index]->eth_type == 0x86dd) {
					if(sysinfo->kernel_stack_flag == 0) {
						if(!rte_kni_tx_burst(sysinfo->portinfos.kni[out_pkts[index]->port], &out_pkts[index], 1)) {
							rte_pktmbuf_free(out_pkts[index]);
						}
					}else {
						rte_pktmbuf_free(out_pkts[index]);
					}
					continue;
				}
#ifdef ANTI_DDOS_ON
				if (sysinfo->ddos_flag == 1 && 
					fp_ddos_defense(out_pkts[index]) == DDOS_PACKET_DROP) {
					rte_pktmbuf_free(out_pkts[index]);
					continue;
				}
#endif			
				if(sysinfo->kernel_stack_flag == 0) {
					if(!rte_kni_tx_burst(sysinfo->portinfos.kni[out_pkts[index]->port], &out_pkts[index], 1)) {
						rte_pktmbuf_free(out_pkts[index]);
					}
				}else {
					rte_pktmbuf_free(out_pkts[index]);
				}
			}
			return 0;
		default:
			buf->inport=buf->port;
			buf->userdef=mode;
            buf->rings_cnt = NULL;
			pkts_num = packet_tuple_analyzer(buf,out_pkts,ANALYZE_MAX_MBUF);
			
			for (index = 0; index < pkts_num; index++ )
			{
				if(out_pkts[index]->eth_type == 0x86dd) {
					if(sysinfo->kernel_stack_flag == 0) {
						if(!rte_kni_tx_burst(sysinfo->portinfos.kni[out_pkts[index]->port], &out_pkts[index], 1)) {
							rte_pktmbuf_free(out_pkts[index]);
						}
					}else {
						rte_pktmbuf_free(out_pkts[index]);
					}
					continue;
				}
#ifdef ANTI_DDOS_ON
				if (sysinfo->ddos_flag == 1 && 
					fp_ddos_defense(out_pkts[index]) == DDOS_PACKET_DROP) {
					rte_pktmbuf_free(out_pkts[index]);
					continue;
				}		
#endif
				if(pingagent(out_pkts[index])){
					if(!rte_eth_tx_burst(port, 0, &out_pkts[index], 1)){
						rte_pktmbuf_free(out_pkts[index]);
					}
					continue;
				}
				
				rss_ring_index = out_pkts[index]->tag % cpu_count;
				ret = rte_ring_enqueue_burst(sysinfo->rss_rings[rss_ring_index],(void **)&out_pkts[index],1);
				if(!ret) {
					rte_pktmbuf_free(out_pkts[index]);
				}
			}
			return 0;	
	}
	return 0;			
}

int port_input_bulk (struct system_info *sysinfo, struct rte_mbuf ** buf, uint16_t nb_pkts,int qid, int cpu){
	struct port_workmode	*workmode=sysinfo->portinfos.mode;
	uint8_t *status;
	uint8_t inport=buf[0]->port;
	uint8_t outport;
	uint16_t i,ret=0;
	uint8_t mode=workmode[inport].mode;

	struct rte_mbuf * out_pkts[ANALYZE_MAX_MBUF];
	int pkts_num;
	uint16_t index;
	unsigned rss_ring_index = 0;
	unsigned cpu_count = rte_lcore_count() - 1;

	if(unlikely(qid>=sysinfo->portinfos.txrings[inport])){
		DPDK_LOG(ERR,PLATFORM,"port_input_bulk Line: %d qid %d is crosssing the max qid %d!\n",
							   __LINE__,qid,sysinfo->portinfos.txrings[inport]);
		goto SENDRESULT;
	}

	switch(mode){
		case LOOP_SIMPLE:
			#if(ENABLE_MIRROR_FUNCTION == 1)
			do_mirror_in_bulk(sysinfo,buf,nb_pkts);
			#endif
			if(unlikely(qid>=sysinfo->portinfos.txrings[inport])){
				printf("qid %d is crosssing the max qid %d!\n",qid,sysinfo->portinfos.txrings[inport]);
				goto SENDRESULT;
			}
			ret=rte_eth_tx_burst(inport, qid, buf, nb_pkts);
			goto SENDRESULT;
		case DIRECT_CONNECT_SIMPLE:
			#if(ENABLE_MIRROR_FUNCTION == 1)
			do_mirror_in_bulk(sysinfo,buf,nb_pkts);
			#endif
			status=sysinfo->portinfos.status_uk;
			outport=workmode[inport].value;
			if(unlikely(qid>=sysinfo->portinfos.txrings[outport])){
				printf("qid %d is crosssing the max qid %d!\n",qid,sysinfo->portinfos.txrings[outport]);
				goto SENDRESULT;
			}
			if(unlikely(!(status[outport]&USER_STATUS))) {
				printf("port %d is not up !\n",outport);
				goto SENDRESULT;
			}
			ret=rte_eth_tx_burst(outport, qid,  buf, nb_pkts);
			goto SENDRESULT;
		case INVALID_MODE:
			#if(ENABLE_MIRROR_FUNCTION == 1)
			do_mirror_in_bulk(sysinfo,buf,nb_pkts);
			#endif
			printf("port mode is invalid,drop it!\n");
			goto SENDRESULT;
		case DIRECT_CONNECT:
			outport=workmode[inport].value;
			for(i=0;i<nb_pkts;i++) {
				buf[i]->inport=buf[i]->port;
				buf[i]->userdef=mode;
                buf[i]->rings_cnt = NULL;
				//if(sysinfo->kernel_stack_flag == 1)
					buf[i]->port=outport;
				pkts_num = packet_tuple_analyzer(buf[i],out_pkts,ANALYZE_MAX_MBUF);
				
				for (index = 0; index < pkts_num; index++){
#ifdef ANTI_DDOS_ON
					if (sysinfo->ddos_flag == 1 && 
						fp_ddos_defense(out_pkts[index]) == DDOS_PACKET_DROP) {
						rte_pktmbuf_free(out_pkts[index]);
						continue;
					}		
#endif					
					rss_ring_index = out_pkts[index]->tag % cpu_count;
					ret = rte_ring_enqueue_burst(sysinfo->rss_rings[rss_ring_index],(void **)&out_pkts[index],1);
					if(!ret) {
						rte_pktmbuf_free(out_pkts[index]);
					}
				}

			}
			return nb_pkts;	
		case BRIDGE_SIMPLE:
			for(i=0;i<nb_pkts;i++) {
				if(unlikely(buf[i]->port > rte_eth_dev_count())){
					DPDK_LOG(ERR,PLATFORM,"Line:%d BRIDGE_SIMPLE but buf->port=%u,i=%d\n",__LINE__,buf[i]->port,i);
				}
				buf[i]->inport=buf[i]->port;
				buf[i]->userdef=mode;
                buf[i]->rings_cnt = NULL;
#ifdef BRIDGE_ON
				do_bridge(buf[i]);
#endif
				pkts_num = packet_tuple_analyzer(buf[i],out_pkts,ANALYZE_MAX_MBUF);
				
				for (index = 0; index < pkts_num; index++){
					if(out_pkts[index]->eth_type == 0x86dd) {
						if(sysinfo->kernel_stack_flag == 0) {
							if(!rte_kni_tx_burst(sysinfo->portinfos.kni[out_pkts[index]->port], &out_pkts[index], 1)) {
								rte_pktmbuf_free(out_pkts[index]);
							}
						}else {
							rte_pktmbuf_free(out_pkts[index]);
						}
						continue;
					}
#ifdef ANTI_DDOS_ON
					if (sysinfo->ddos_flag == 1 && 
						fp_ddos_defense(out_pkts[index]) == DDOS_PACKET_DROP) {
						rte_pktmbuf_free(out_pkts[index]);
						continue;
					}		
#endif				
					rss_ring_index = out_pkts[index]->tag % cpu_count;
					ret = rte_ring_enqueue_burst(sysinfo->rss_rings[rss_ring_index],(void **)&out_pkts[index],1);
					if(!ret) {
						DPDK_LOG(WARNING,PLATFORM,"Line:%d BRIDGE_SIMPLE software rss rings failed\n", __LINE__);
						rte_pktmbuf_free(out_pkts[index]);
					}
				}

			}
			return nb_pkts;		
		case MIRROR_PORT:
			goto SENDRESULT;
		case NAT_PORT:
			for(i = 0; i < nb_pkts; i++) {
				if(unlikely(buf[i]->port > rte_eth_dev_count())){
					DPDK_LOG(ERR,PLATFORM,"Line:%d NAT_PORT but buf->port=%u,i=%d\n",__LINE__,buf[i]->port,i);
				}
				buf[i]->inport = buf[i]->port;
				buf[i]->userdef = mode;
                buf[i]->rings_cnt = NULL;
				
				pkts_num = packet_tuple_analyzer(buf[i],out_pkts,ANALYZE_MAX_MBUF);
				
				for (index = 0; index < pkts_num; index++) {
					if(out_pkts[index]->eth_type == 0x86dd) {
						if(sysinfo->kernel_stack_flag == 0) {
							if(!rte_kni_tx_burst(sysinfo->portinfos.kni[out_pkts[index]->port], &out_pkts[index], 1)) {
								rte_pktmbuf_free(out_pkts[index]);
							}
						}else {
							rte_pktmbuf_free(out_pkts[index]);
						}
						continue;
					}
#ifdef ANTI_DDOS_ON
					if (sysinfo->ddos_flag == 1 && 
						fp_ddos_defense(out_pkts[index]) == DDOS_PACKET_DROP) {
						rte_pktmbuf_free(out_pkts[index]);
						continue;
					}
#endif			
					if(sysinfo->kernel_stack_flag == 0) {
						Flow_table_natlookup(out_pkts[index]);
						if(!rte_kni_tx_burst(sysinfo->portinfos.kni[out_pkts[index]->port], &out_pkts[index], 1)) {
							DPDK_LOG(WARNING,PLATFORM,"Line:%d NAT_PORT Tx kernel queue full mbuf->port=%u\n",
								__LINE__,out_pkts[index]->port);
							rte_pktmbuf_free(out_pkts[index]);
						}
					}else {
						rte_pktmbuf_free(out_pkts[index]);
					}
				}
			}
			return nb_pkts;
		default:
			for(i=0;i<nb_pkts;i++) {
				if(unlikely(buf[i]->port > rte_eth_dev_count())){
					DPDK_LOG(ERR,PLATFORM,"Line:%d ADVACED but buf->port=%u,i=%d\n",__LINE__,buf[i]->port,i);
				}
				buf[i]->inport=buf[i]->port;
				buf[i]->userdef=mode;
                buf[i]->rings_cnt = NULL;
				pkts_num = packet_tuple_analyzer(buf[i],out_pkts,ANALYZE_MAX_MBUF);
				
				for (index = 0; index < pkts_num; index++){
					if(out_pkts[index]->eth_type == 0x86dd) {
						if(sysinfo->kernel_stack_flag == 0) {
							if(!rte_kni_tx_burst(sysinfo->portinfos.kni[out_pkts[index]->port], &out_pkts[index], 1)) {
								rte_pktmbuf_free(out_pkts[index]);
							}
						}else {
							rte_pktmbuf_free(out_pkts[index]);
						}
						continue;
					}
#ifdef ANTI_DDOS_ON
					if (sysinfo->ddos_flag == 1 && 
						fp_ddos_defense(out_pkts[index]) == DDOS_PACKET_DROP) {
						rte_pktmbuf_free(out_pkts[index]);
						continue;
					}
#endif
					if(pingagent(out_pkts[index])){
						if(!rte_eth_tx_burst(inport, qid, &out_pkts[index], 1)){
							DPDK_LOG(WARNING,PLATFORM,"Line:%d ADVACED pingagent tx failed inport=%u  qid=%d\n",
									 __LINE__,inport,qid);
							rte_pktmbuf_free(out_pkts[index]);
						}
						continue;
					}

					rss_ring_index = out_pkts[index]->tag % cpu_count;
					ret = rte_ring_enqueue_burst(sysinfo->rss_rings[rss_ring_index],(void **)&out_pkts[index],1);
					if(!ret) {
						DPDK_LOG(WARNING,PLATFORM,"Line:%d ADVACED software rss rings failed\n", __LINE__);
						rte_pktmbuf_free(out_pkts[index]);
					}
				}

			}
			return nb_pkts;	
	}
	return 0;	
SENDRESULT:
	if (unlikely(ret < nb_pkts)) {
		do {
			rte_pktmbuf_free(buf[ret]);
		} while (++ret < nb_pkts);
	}
	return ret;
}

int port_output (struct clientinfo *server_tx,struct rte_mbuf *buf,int qid,int cpu){
	struct portinfo * portinfo=&((struct system_info *)(server_tx->sysinfo))->portinfos;
	uint8_t port=buf->port;
	uint16_t j,n;
	struct rte_mbuf *mbuf_brd[RTE_MAX_ETHPORTS];
	struct system_info *sysinfo =(struct system_info *)(server_tx->sysinfo);

	Flow_table_postlookup(buf);
	#if(ENABLE_MIRROR_FUNCTION == 1)
		if(((struct system_info *)(server_tx->sysinfo))->mirror_flag.flag2[1])
			do_mirror((struct system_info *)(server_tx->sysinfo), buf, buf->port, FILTER_MIRROR_OUT);
	#endif
	OUTPUT_MODE_CHECK(buf, port);
	
	if(unlikely(port>=RTE_MAX_ETHPORTS)) {
		printf("port %d is crosssing the max port %d !\n",port,RTE_MAX_ETHPORTS);
		goto error;
	}

#ifdef BRIDGE_ON
	if(unlikely(port==VIRTUAL_PORT)){
		n=do_bridge_broadcast(mbuf_brd,buf);
		if(unlikely(!n))
			goto error;
		for(j=0;j<n;j++) {			
			queue_eneque_help(&(server_tx->queue),mbuf_brd[j]);
		}
		return 0;
	}
#endif

	if(unlikely(!(portinfo->status_uk[port]&USER_STATUS))) {
		DPDK_LOG(ERR,PLATFORM,"Line: %d port %d is not up !\n",__LINE__,port);
		goto error;
	}

	if(unlikely(qid>=portinfo->txrings[port])){
		DPDK_LOG(ERR,PLATFORM,"Line: %d qid %d is crosssing the max qid %d!\n",
			__LINE__,qid,portinfo->txrings[port]);
		goto error;
	}

	/* dataplane tc
	if(portinfo->tc_ctl_switch){
		struct sched_port * schport = &portinfo->schport[port];
		if (schport->enable){
			int ret,nb_pkts;
			struct rte_mbuf * mbuf[PACKET_READ_SIZE];
			if(0==sched_port_enqueue(schport,buf,DOWN_LINK)){
			#if (ENABLE_APP_STATISTICS == 1)
				rte_atomic64_inc(&(server_tx->queue.total_dp));
				rte_atomic64_inc(&(portinfo->port_tx_dp[port]));
			#endif				
			}
			nb_pkts = sched_port_dequeue(schport,mbuf,PACKET_READ_SIZE,DOWN_LINK);

			ret = rte_eth_tx_burst(port, qid, mbuf, nb_pkts);
			#if (ENABLE_APP_STATISTICS == 1)
			rte_atomic64_add(&(server_tx->queue.total_tx), ret);
			#endif
			if (unlikely(ret < nb_pkts)) {
				do {
					rte_pktmbuf_free(mbuf[ret]);
				#if (ENABLE_APP_STATISTICS == 1)
					rte_atomic64_inc(&(server_tx->queue.total_dp));
					rte_atomic64_inc(&(portinfo->port_tx_dp[port]));
				#endif
				} while (++ret < nb_pkts);
			}
			return ret;
		}
	}
	*/

	//Flow_TS(buf);
	
	if(0==rte_eth_tx_burst(port, qid, &buf, 1)) {
	#if (ENABLE_APP_STATISTICS == 1)
		rte_atomic64_inc(&(server_tx->queue.total_dp));
		rte_atomic64_inc(&(portinfo->port_tx_dp[port]));
	#endif
		DPDK_LOG(WARNING,PLATFORM,"Line: %d tx eth %d qid %d failed!\n",__LINE__,port,qid);
		goto error;
	}
	return 0;

error:
	rte_pktmbuf_free(buf);
	return -1;
}

int port_output_bulk(struct clientinfo *server_tx, struct rte_mbuf * * buf, uint16_t nb_pkts, int qid,int cpu){
	struct portinfo * portinfo=&((struct system_info *)(server_tx->sysinfo))->portinfos;
	uint8_t port=buf[0]->port;
	uint16_t ret,i,j,n;
	struct system_info *sysinfo =(struct system_info *)(server_tx->sysinfo);

	#if(ENABLE_MIRROR_FUNCTION == 1)
		do_mirror_out_bulk((struct system_info *)(server_tx->sysinfo), buf,nb_pkts);
	#endif

	for(i = 0; i < nb_pkts; i++) {
		switch(buf[i]->userdef) {						
			case  DEF_USER_MODE:				
			case  DEF_KERNEL_MODE:				
			case ADVANCED:
			case INVALID_MODE:						
				break;		
			case NAT_PORT:						
				break;	
			case LOOP:
				break;							
			case DIRECT_CONNECT:
				break;							
			case BRIDGE_SIMPLE:					
			case MIRROR_PORT:	
		#ifdef BRIDGE_ON
				if(unlikely(buf[i]->inport ==buf[i]->port) ){	
					printf("port %d is loop,drop it!\n",port);
					goto error;
				}		
		#endif
				break;							
			case BYPASS:							
			default:						
				goto error;
		}
	}

#ifdef BRIDGE_ON
	struct rte_mbuf *mbuf_brd[RTE_MAX_ETHPORTS];
	if(unlikely(port==VIRTUAL_PORT)){
		for(i=0;i<nb_pkts;i++){
			n=do_bridge_broadcast(mbuf_brd,buf[i]);
			if(unlikely(!n))
				goto error;
			for(j=0;j<n;j++) {
				queue_eneque_help(&(server_tx->queue),mbuf_brd[j]);
			}
		}
		return 0;
	}
#endif
	
	if(unlikely(!(portinfo->status_uk[port]&USER_STATUS))) {
		printf("port %d is not up !\n",port);
		goto error;
	}

	if(unlikely(qid>=portinfo->txrings[port])){
		printf("qid %d is crosssing the max qid %d!\n",qid,portinfo->txrings[port]);
		goto error;
	}
	/* dataplane tc
	if(portinfo->tc_ctl_switch){
		struct sched_port * schport = &portinfo->schport[port];
		if (schport->enable){
			int cnt = sched_port_bulk_enqueue(schport,buf,nb_pkts,DOWN_LINK);
			if(cnt < nb_pkts){
			#if (ENABLE_APP_STATISTICS == 1)
				rte_atomic64_add(&(server_tx->queue.total_dp),nb_pkts-cnt);
				rte_atomic64_add(&(portinfo->port_tx_dp[port]),nb_pkts-cnt);
			#endif
			}
			nb_pkts = sched_port_dequeue(schport,buf,PACKET_READ_SIZE,DOWN_LINK);
		}	
	}
	*/
	//Flow_TS_bulk(buf,nb_pkts);
	
	ret = rte_eth_tx_burst(port, qid, buf, nb_pkts);
#if (ENABLE_APP_STATISTICS == 1)
	rte_atomic64_add(&(server_tx->queue.total_tx), ret);
#endif
	if (unlikely(ret < nb_pkts)) {
		do {
			rte_pktmbuf_free(buf[ret]);
		#if (ENABLE_APP_STATISTICS == 1)
			rte_atomic64_inc(&(server_tx->queue.total_dp));
			rte_atomic64_inc(&(portinfo->port_tx_dp[port]));
		#endif
		} while (++ret < nb_pkts);
	}
	return ret;
error:
	for(ret=0;ret<nb_pkts;ret++)
		rte_pktmbuf_free(buf[ret]);
	return -1;
}
//------------------------------------------------------------------------------
static const char * const eth_dev[MDX_ETH_TYPE][32]={
	[E1000]={"82540","82545", "82546"},
	[E1000E]={"82571","82574","82583","ICH8","ICH10", "PCH","PCH2"},
	[IGB]={"82575","82576","82580","I210","I211","I350","I354","DH89"},
	[IXGBE]={"82598","82599","X540","X550"},
	[I40E]={"X710", "XL710"},
};

int get_ethtype_by_pci_addr(struct rte_pci_device *pci){	
	char cmd[128];
	char tmp[1024];
	FILE *pp;
	int i,j,ret=OTHER_EHT_TYPE;

	sprintf(cmd,"lspci | grep \"%02d:%02d.%d\"",pci->addr.bus,pci->addr.devid,pci->addr.function);
	pp = popen(cmd, "r"); 
	if (!pp) 
		goto ERR1;
	if(!fgets(tmp, sizeof(tmp), pp))
		goto ERR2;
	for(i=0;i<MDX_ETH_TYPE;i++) 
		for(j=0;j<32;j++){
			if(!eth_dev[i][j])
				break;
			if(strstr(tmp,eth_dev[i][j])){
				ret=i;
				goto ERR2;
			}
	}
ERR2:
	pclose(pp);
ERR1:
	if(ret==OTHER_EHT_TYPE)
		printf("pci addr : \"%02d:%02d.%d\",ether type can't be recognized!\n",pci->addr.bus,pci->addr.devid,pci->addr.function);
	return ret;
}
//------------------------------------------------------------------------------
#include "clientext_queue.c"


#endif
//------------------------------------------------------------------------------
struct module_list module_list_init[MAX_MODULES];
volatile uint16_t module_list_init_num;

struct module_list module_list_exit[MAX_MODULES];
volatile uint16_t module_list_exit_num;


void do_module_inits(void *arg){
	uint16_t i;
	printf("do_module_inits:%d\n",module_list_init_num);
	for(i=0;i<module_list_init_num;i++){
		printf("%s...\n",module_list_init[i].name);
		module_list_init[i].func(arg);

	}
}

void do_module_exits(void *arg){
	uint16_t i;
	printf("do_module_exits:%d\n",module_list_exit_num);
	for(i=0;i<module_list_exit_num;i++){
		printf("%s...\n",module_list_exit[i].name);
		module_list_exit[i].func(arg);

	}
}


