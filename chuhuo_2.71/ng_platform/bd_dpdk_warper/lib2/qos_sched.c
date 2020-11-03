/*
 * Copyright(c) 2007 BDNS
 */
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <sys/stat.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/ioctl.h>
#include <sys/queue.h>
#include <sys/msg.h>
#include <rte_malloc.h>
#include <rte_cycles.h>
#include <rte_memcpy.h>
#include <rte_byteorder.h>
#include <rte_branch_prediction.h>
#include <rte_sched.h>
#include <rte_hash.h>
#include <rte_jhash.h>
#include <rte_approx.h>

#include "dpdk_frame.h"
#include "qos_sched.h"

static int msqid = -1;

#if 0
/*used for traffic flow*/
#define MAX_BUCKETS 1024
static struct rte_table_hash_ext_params table_params={
	.key_size  = sizeof(struct traffic_key);  /** Key size (number of bytes) */
	.n_keys    = MAX_BUCKETS * 4;             /** Maximum number of keys */
	.n_buckets = MAX_BUCKETS;                 /** Number of hash table buckets. Each bucket stores up to 4 keys. */               
	/** Number of hash table bucket extensions. Each bucket extension has
	space for 4 keys and each bucket can have 0, 1 or more extensions. */
	.n_buckets_ext = 2;
	.f_hash    = rte_jhash;                   /** Hash function */
	.seed      = 0;                           /** Seed value for the hash function */
	
	/** Byte offset within packet meta-data where the 4-byte key signature
	is located. Valid for pre-computed key signature tables, ignored for do-sig tables. */
	.signature_offset = 0;
	.key_offset = 0;                          /** Byte offset within packet meta-data where the key is located */
};
#endif

struct rte_hash_parameters hash_params = {
	.entries            = MAX_HASH_ENTRIES,		      /**< Total hash table entries. */
	.bucket_entries     = HASH_ENTRIES_PER_BUCKET,	  /**< Bucket entries. */
	.key_len            = sizeof(struct ip_addr_key), /**< Length of hash key. */
	.hash_func	        = rte_jhash,                  /**< Function used to calculate hash. */
	.hash_func_init_val = 0,	                      /**< Init value used by hash_func. */
	.socket_id          = SOCKET_ID_ANY,			  /**< NUMA Socket ID for memory. */
};

/*default setting*/
static struct msg_ds default_params = 
{
	.type          = DEFAULT_PIPE,
	.priority      = 0,
	.virlinekey    = DEFAULT_VIRLINE_ID,
	.subportkey    = 0,
	.users         = 0,
	.qsize		   = MAX_QUEUE_SIZE,
	.protomask	   = {UINT64_MAX,UINT64_MAX,UINT64_MAX,UINT64_MAX},
	.tb_vir_rate   = {TB_DEFAULT_VIR_RATE,TB_DEFAULT_VIR_RATE},
	.tb_pir_sport  = {TB_DEFAULT_PIR,TB_DEFAULT_PIR},
	.tb_cir_sport  = {0,0},
	.tb_pir_pipe   = {0,0},
	.tb_size       = TB_DEFAULT_BUCKETSIZE,
};

/********************************hash table options**********************************************/
/*
static struct hierarchy_map_entry * alloc_hierarchy_map_entry(struct sched_port * port)
{
	uint32_t index;
	struct hierarchy_map_entry * hentry;

	for ( index = 0; index < MAX_HIERARCHY_MAP_ENTRY; index++ )
	{
		hentry = &port->hentry[port->hentry_index];
		port->hentry_index = (port->hentry_index+1) % MAX_HIERARCHY_MAP_ENTRY;
		if (hentry->used== 0){
			hentry->used = 1;
			hentry->value.sched = 0;
			hentry->next = NULL;
			return hentry;
		}
	}
	return NULL;	
}

static void free_hierarchy_map_entry(struct hierarchy_map_entry * entry)
{
	if (entry!=NULL){
		entry->next        = NULL;
		entry->used        = 0;
		entry->value.sched = 0;
	}
}

static void add_hierarchy_map_entry(struct sched_port    * port,
										    struct traffic_value * ptr,
	                                        struct hierarchy_map_entry * entry)
{

	if (ptr->head == NULL){
		ptr->head = entry;
		return;
	}	
	struct hierarchy_map_entry *  pnode =  ptr->head;
	struct hierarchy_map_entry ** paddr = &ptr->head;
	
	while(pnode!= NULL){
		if (port->subport[entry->value.hierarchy.subport].priority < 
			port->subport[pnode->value.hierarchy.subport].priority){
			entry->next = *paddr;
			*paddr      = entry;
			paddr       = &entry->next;
			return;
		}
		paddr = &pnode->next;
		pnode = pnode->next;
	}
	*paddr = entry;
	return;
}

static int del_hierarchy_map_entry(struct traffic_value * ptr,
	                                      uint32_t groupid)
{
	if (unlikely(ptr == NULL)) return 0;
	
	struct hierarchy_map_entry *  pnode =  ptr->head;
	struct hierarchy_map_entry ** paddr = &ptr->head;
	struct hierarchy_map_entry * tmp;
	
	while(pnode!= NULL){
		if (pnode->value.hierarchy.subport == groupid){
			tmp    = pnode;
			*paddr = pnode->next;
			free_hierarchy_map_entry(tmp);
			return 1;
		}
		paddr = &pnode->next;
		pnode = pnode->next;
	}	
	return 0;
}
*/

static int add_hierarchy_map_entry(struct sched_port    * port,
										   struct traffic_value * ptr,
	                                       union hierarchy_map_entry * entry)
{
	int index;
	union hierarchy_map_entry * pntry;

	if(ptr->nums >= APP_TYPE_NUMS_PER_IP){
		return -1;
	}

	if(ptr->nums == 0){
		ptr->entry[0].sched = entry->sched;
		ptr->nums++;
		return 0;
	}
	
	index = (int)(ptr->nums - 1);
	for(; index >= 0 && index < APP_TYPE_NUMS_PER_IP; index--){
		pntry = &ptr->entry[index];
		if ( port->subport[pntry->hierarchy.subport].priority<
		     port->subport[entry->hierarchy.subport].priority)
		{
			break;
		}
		else
		{
			ptr->entry[index+1].sched = ptr->entry[index].sched;
		}
	}
	ptr->entry[index+1].sched = entry->sched;
	ptr->nums++;
	return 0;
}

static int del_hierarchy_map_entry(struct traffic_value * ptr,
	                                      uint32_t groupid)
{
	if(ptr->nums == 0){
		return 0;
	}

	uint32_t index = 0;
	uint32_t flag  = 0;
	
	for (; index < ptr->nums && index < APP_TYPE_NUMS_PER_IP; index++){

		if(ptr->entry[index].hierarchy.subport == groupid){
			flag = 1;
			index++;
			break;
		}
	}
	if(flag == 0) return 0;
	for (; index < ptr->nums && index < APP_TYPE_NUMS_PER_IP; index++){
		ptr->entry[index-1].sched = ptr->entry[index].sched;
	}
	ptr->entry[index-1].sched = 0;
	ptr->nums--;
	return 0;
}

static void shift_hierarchy_map_entry(struct sched_port * port,
											 struct traffic_value * ptr,
	                                         uint32_t oldid,
	                                         uint32_t newid)
{
	if(oldid == newid || ptr->nums <= 1) return;

	uint32_t index;
	uint32_t sched;
	
	if(oldid < newid){
	
		for (index = 0; index < ptr->nums-1; index++){

			
			if(port->subport[ptr->entry[index].hierarchy.subport].priority> 
		  	   port->subport[ptr->entry[index+1].hierarchy.subport].priority)
			{
				sched = ptr->entry[index].sched;
				ptr->entry[index].sched = ptr->entry[index+1].sched;
				ptr->entry[index+1].sched = sched;
			}
		    	
		}
		
	}

	if(oldid > newid){
		
		for (index = ptr->nums-1; index >= 1; index--){

			
			if(port->subport[ptr->entry[index].hierarchy.subport].priority < 
		  	   port->subport[ptr->entry[index-1].hierarchy.subport].priority)
			{
				sched = ptr->entry[index].sched;
				ptr->entry[index].sched = ptr->entry[index-1].sched;
				ptr->entry[index-1].sched = sched;
			}
		    	
		}		
	}
}


static int sched_port_hashtab_loolup(struct sched_port * port,uint32_t ipaddr)
{
	struct ip_addr_key key;

	int32_t pos;

	key.ip_addr = ipaddr;
	pos = rte_hash_lookup(port->hkey,(void*)&key);
	if(pos == -ENOENT) //if it don't find pos, it must be added 
	{
		pos = rte_hash_add_key(port->hkey,(void*)&key);
		if(pos == -ENOSPC){
			printf("%s:hash table is run out!\n",__func__);
			return -1;
		}
		port->hvalue[pos].nums = 0;
		port->hvalue[pos].key.ip_addr = key.ip_addr;
		memset(port->hvalue[pos].entry,0,sizeof(port->hvalue[pos].entry));
	}
	return pos;
}

/******************************init data*********************************/
/*for sched subport*/

static void get_tb_params(uint64_t rate, uint64_t *tb_period, uint64_t *tb_bytes_per_period,uint64_t hz)
{
	if(rate == 0){
		*tb_period = UINT64_MAX;
		*tb_bytes_per_period = 1;
		return;
	}
	double period = ((double) hz) / ((double) rate);

	if (period >= TOKEN_BUCKET_MIN_PERIOD) {
		*tb_bytes_per_period = 1;
		*tb_period = (uint64_t) period;
	} else {
		*tb_bytes_per_period = (uint64_t) ceil(TOKEN_BUCKET_MIN_PERIOD / period);
		*tb_period = (hz * (*tb_bytes_per_period)) / rate;
	}
}


static int token_bucket_config(struct token_bucket_data  * tb,
									 uint32_t rate,
									 uint32_t tb_size,
                                     uint64_t time,
                                     uint64_t hz)
{
	tb->tb_time    = time;
	tb->tb_size    = tb_size;
	tb->tb_credits = tb_size; 

	get_tb_params(rate, &tb->tb_period, &tb->tb_bytes_per_period,hz);
	
	return 0;
}

/*****************************virtual line*******************************/
static struct sched_virtual_line * alloc_sched_virtual_line(struct sched_port * port)
{
	static uint32_t index = 0;
	uint32_t i;
	uint32_t lineroadindex;
	struct sched_virtual_line * line;
	for (i = 0; i < MAX_VIRTUAL_LINE; i++)
	{
		line = &port->virline[index];
		lineroadindex = index;
		index = (index + 1) % MAX_VIRTUAL_LINE;
		if (line->used == 0){
			line->used = 1;
			line->lineroadindex = lineroadindex;
			return line;
		}
	}
	return NULL;
}

static void free_sched_virtual_line(struct sched_virtual_line * line)
{
	if (line != NULL){
		memset(line,0,sizeof(struct sched_virtual_line));
	}
}

struct sched_virtual_line ** virtual_line_lookup(struct sched_port * port,uint32_t lineroadid)
{
	struct sched_virtual_line ** line;
	for(line = &port->list_line; *line != NULL; line = &(*line)->next){
		if((*line)->lineroadid == lineroadid){
			return line;
		}
	}
	return NULL;
}

static int 
virtual_line_add(struct sched_port * port,struct msg_ds * params)
{

	uint32_t lineroadid = params->virlinekey;
	uint64_t up_rate    = params->tb_vir_rate[UP_LINK];
	uint64_t down_rate  = params->tb_vir_rate[DOWN_LINK];
	
	struct sched_virtual_line ** lookline = virtual_line_lookup(port,lineroadid);
	if(lookline != NULL){
		printf("virtual line %u exists!\n",lineroadid);
		return -1;
	}
	struct sched_virtual_line * line = alloc_sched_virtual_line(port);
	if(line == NULL){
		printf("virtual line is full!\n");
		return -1;
	}

	if(port->hz == 0){
		printf("System parameter:basic frequency is zero!\n");
		goto err;
	}

	uint64_t rate_left;
	
	rate_left = port->rate_total[DOWN_LINK] - port->rate_used[DOWN_LINK];
	if(rate_left < down_rate){
		printf("Don't have enough bandwidth for vir_line:%u!\n",lineroadid);
		goto err;
	}
	
	rate_left = port->rate_total[UP_LINK] - port->rate_used[UP_LINK];
	if(rate_left < up_rate){
		printf("Don't have enough bandwidth for vir_line:%u!\n",lineroadid);
		goto err;
	}
	
	line->lineroadid                        = lineroadid;
	line->bwinfo[UP_LINK].total_bandwidth   = up_rate;
	line->bwinfo[UP_LINK].total_ceil        = up_rate;
	line->bwinfo[DOWN_LINK].total_bandwidth = down_rate;
	line->bwinfo[DOWN_LINK].total_ceil      = down_rate;	
	port->rate_used[UP_LINK]               += up_rate;
	port->rate_used[DOWN_LINK]             += down_rate;
	
	get_tb_params(line->bwinfo[UP_LINK].total_ceil,
		         &line->bwinfo[UP_LINK].period,
		         &line->bwinfo[UP_LINK].bytes_per_period,
		          port->hz);
	get_tb_params(line->bwinfo[DOWN_LINK].total_ceil,
		         &line->bwinfo[DOWN_LINK].period,
		         &line->bwinfo[DOWN_LINK].bytes_per_period,
		          port->hz);

	*port->list_line_tail = line;
	 port->list_line_tail = &line->next;
	
	return 0;
err:
	free_sched_virtual_line(line);
	return -1;
}

static int virtual_line_delete(struct sched_port * port,uint32_t lineroadid)
{
	struct sched_virtual_line ** line = virtual_line_lookup(port,lineroadid);
	if(line == NULL){
		printf("%s:don't find virtual line %u.\n",__func__,lineroadid);
		return -1;
	}

	struct sched_virtual_line * p = *line;
	uint32_t index;
	uint32_t groupid;
	uint32_t flag;
	for(index = 0; index < MAX_SUBPORT_PER_VIRLINE; index++){
		groupid = p->subportid[index].value.id;
		flag    = p->subportid[index].value.flag;
		if(flag == 1 && groupid > 0 && groupid < MAX_SUBPORT_NUMS){
			uninstall_sched_subport(port,&port->subport[groupid]);
		}
	}
	if((*line)->next == NULL ){
		port->list_line_tail = line;
	}
	*line = (*line)->next;
	port->rate_used[UP_LINK]   -= p->bwinfo[UP_LINK].total_bandwidth;
	port->rate_used[DOWN_LINK] -= p->bwinfo[DOWN_LINK].total_bandwidth;
	
	free_sched_virtual_line(p);
	return 0;
}


static int virtual_line_add_groupid(struct sched_port    * port,
									     struct sched_subport * sport)
{
	uint32_t vindex;
	uint32_t flag;
	struct sched_virtual_line * line = &port->virline[sport->lineroadindex];
	
	for(vindex = 0; vindex < MAX_SUBPORT_PER_VIRLINE; vindex++){
		flag = line->subportid[vindex].value.flag;
		if(flag==0){
			line->subportid[vindex].value.id   = sport->groupid;
			line->subportid[vindex].value.flag = 1;
			sport->linesportid      = vindex;
			return 0;
		}
	}
	return -1;
}

static void virtual_line_delete_groupid(struct sched_port * port,
									         struct sched_subport * sport)
{
	struct sched_virtual_line * line;

	line = &port->virline[sport->lineroadindex];
	line->subportid[sport->linesportid].subportid = 0;
}

static void virtual_line_rate_config(struct sched_virtual_line * line,
	                                 	 uint64_t hz,
	                                 	 int64_t up_cir,
	                                 	 int64_t down_cir)
{
	uint64_t period;
	uint64_t bytes_per_period;
	if(up_cir == 0) return;
	line->bwinfo[UP_LINK].total_ceil -= up_cir;
	get_tb_params(line->bwinfo[UP_LINK].total_ceil,&period,&bytes_per_period,hz);
	line->bwinfo[UP_LINK].period = period;
	line->bwinfo[UP_LINK].bytes_per_period = bytes_per_period;
	
	if(down_cir == 0) return;
	line->bwinfo[DOWN_LINK].total_ceil -= down_cir;
	get_tb_params(line->bwinfo[DOWN_LINK].total_ceil,&period,&bytes_per_period,hz);
	line->bwinfo[DOWN_LINK].period = period;
	line->bwinfo[DOWN_LINK].bytes_per_period = bytes_per_period;	

}

static int virtual_line_config(struct sched_port * port,
								  struct sched_subport * sport,
								  uint32_t lineroadid)
{
	struct sched_virtual_line ** line = virtual_line_lookup(port,lineroadid);
	if(line == NULL){
		return -1;
	}
	struct sched_virtual_line * p = *line;
	
	sport->lineroadid	 = lineroadid;
	sport->lineroadindex = p->lineroadindex;
	
	//check rationality of rate and ceil 
	if(p->bwinfo[UP_LINK].total_bandwidth < sport->tb_pir_sport[UP_LINK] ||
	   p->bwinfo[DOWN_LINK].total_bandwidth < sport->tb_pir_sport[DOWN_LINK])
	{
		return -1;
	}
	if(sport->tb_cir_sport[UP_LINK] != 0 && p->bwinfo[UP_LINK].total_ceil < sport->tb_cir_sport[UP_LINK]){
		return -1;
	}
	if(sport->tb_cir_sport[DOWN_LINK] != 0 && p->bwinfo[DOWN_LINK].total_ceil < sport->tb_cir_sport[DOWN_LINK]){
		return -1;
	}	
	virtual_line_rate_config(p,port->hz,sport->tb_cir_sport[UP_LINK],sport->tb_cir_sport[DOWN_LINK]);

	//add groupid to virtual_line
	int ret = virtual_line_add_groupid(port,sport);
	if(ret < 0){
		printf("%s:Subport of virtual line %u is full!\n",__func__,sport->lineroadid);
		virtual_line_rate_config(p,port->hz,-sport->tb_cir_sport[UP_LINK],-sport->tb_cir_sport[DOWN_LINK]);
		return ret;
	}
	
	return 0;
}

static void virtual_line_config_callback(struct sched_port * port,
								  			  struct sched_subport * sport)
{
	virtual_line_delete_groupid(port,sport);
	virtual_line_rate_config(&port->virline[sport->lineroadindex],
							  port->hz,
							 -sport->tb_cir_sport[UP_LINK],
							 -sport->tb_cir_sport[DOWN_LINK]);
}


/*************************************************************/
static void shared_pipe_install(struct sched_subport * subport)
{
	struct sched_pipe * pipe;
	uint32_t index;
	for (index = 0; index < subport->n_shared_pipes; index++)
	{
		pipe = &subport->pipe[index];
		pipe->pipeid = index;
		pipe->pipeinner[DOWN_LINK].qindex = index;
		pipe->pipeinner[UP_LINK].qindex = index+subport->n_pipes;
		pipe->pipeid = index;
		pipe->traffic_index = -1;
		pipe->ipaddr        = 0;
	}
	
}

static int single_pipe_install(struct sched_port * port,
							      struct sched_subport * subport)
{
	uint32_t index;
	int32_t pos;
	struct sched_pipe * pipe;
	for (index = 0; index < subport->n_single_pipes; index++)
	{
		pipe = &subport->single_pipe[index];
		pipe->pipeid = index + subport->n_shared_pipes;
		pipe->ipaddr = port->ipbuf[index];
		pipe->pipeinner[DOWN_LINK].qindex = index + subport->n_shared_pipes;
		pipe->pipeinner[UP_LINK].qindex   = index + subport->n_pipes + subport->n_shared_pipes;
		pos = sched_port_hashtab_loolup(port,pipe->ipaddr);
		if(pos < 0) return -1;
		pipe->traffic_index = pos;
	}
	return 0;
}


static void single_pipe_uninstall(struct sched_port    * port, 
	                              	  struct sched_subport * sport)
{
	struct sched_pipe    * pipe;
	struct traffic_value * value;
	uint32_t index;
	int cnt = 0;
	for (index = 0; index < sport->n_single_pipes; index++)
	{
		pipe = &sport->single_pipe[index];
		
		if (pipe->traffic_index != -1 && pipe->traffic_index < MAX_HASH_ENTRIES){
			
			value = &port->hvalue[pipe->traffic_index];
			
			if (value->key.ip_addr == pipe->ipaddr){
				cnt += del_hierarchy_map_entry(value,sport->groupid);
			}else{
				printf("%s:Data exception hashvalue(ipaddr:%u) not equal pipe(ipaddr%u)!\n",
					    __func__,value->key.ip_addr,pipe->ipaddr);
				continue;
			}
			
			if(value->nums == 0){
				rte_hash_del_key(port->hkey,(void*)&value->key);
				value->key.ip_addr = 0;
			}
			pipe->traffic_index = -1;
		}
	}
	printf("%s: total users = %u,delete users = %d.\n",__func__,sport->n_single_pipes,cnt);
}

static void single_pipe_tb_cfg(struct sched_port * port,struct sched_subport * subport)
{
	if (subport->type == SINGLE_PIPE){
		uint64_t time = rte_get_tsc_cycles();
		struct sched_pipe * pipe;
		uint32_t index;
		for (index = 0; index < subport->n_single_pipes; index++){
			pipe = &subport->single_pipe[index];
			token_bucket_config(&pipe->pipeinner[DOWN_LINK].pipe_tb,
				                 subport->tb_pir_pipe[DOWN_LINK],
				                 subport->tb_size,
				                 time,
				                 port->hz);
			token_bucket_config(&pipe->pipeinner[UP_LINK].pipe_tb,
				                 subport->tb_pir_pipe[UP_LINK],
				                 subport->tb_size,
				                 time,
				                 port->hz);

		}
	}
}

static void shared_pipe_tb_cfg(struct sched_port * port,struct sched_subport * subport)
{

	uint64_t time = rte_get_tsc_cycles();
	struct sched_pipe * pipe;
	uint32_t index;
	for (index = 0; index < subport->n_shared_pipes; index++){
		pipe = &subport->pipe[index];
		token_bucket_config(&pipe->pipeinner[DOWN_LINK].pipe_tb,
				             subport->tb_pir_pipe[DOWN_LINK],
				             subport->tb_size,
				             time,
				             port->hz);
		token_bucket_config(&pipe->pipeinner[UP_LINK].pipe_tb,
				             subport->tb_pir_pipe[UP_LINK],
				             subport->tb_size,
							 time,
				             port->hz);

	}
}

static int sched_pipe_config(struct sched_port    * port, 
	                              struct sched_subport * sport)
{

	if (sport->type & DEFAULT_PIPE){
		return 0;
	}
	struct sched_pipe          * pipe;
	struct traffic_value       * value;
	//struct hierarchy_map_entry * entry;
	uint32_t index;
	for (index = 0; index < sport->n_single_pipes; index++){
		pipe  = &sport->single_pipe[index];
		if (unlikely(pipe->traffic_index<0 || pipe->traffic_index>=MAX_HASH_ENTRIES)){
			printf("%s:Data Exception traffic_index=%d\n",__func__,pipe->traffic_index);
			return -1;
		}
		value = &port->hvalue[pipe->traffic_index];
		if(unlikely(value->key.ip_addr != pipe->ipaddr)){
			printf("%s:Data exception hashvalue(ipaddr:%u) not equal pipe(ipaddr%u)!\n",
					__func__,value->key.ip_addr,pipe->ipaddr);
			return -1;
		}
		/*
		entry = alloc_hierarchy_map_entry(port);
		if (unlikely(entry == NULL)){
			return -1;
		}
		
		entry->value.hierarchy.subport = sport->groupid;
		entry->value.hierarchy.pipe    = pipe->pipeid;
		entry->next = NULL;
		*/
		union hierarchy_map_entry entry;
		entry.hierarchy.subport = sport->groupid;
		entry.hierarchy.pipe    = pipe->pipeid;	
		if(add_hierarchy_map_entry(port,value,&entry) < 0 ){ 
			return -1;
		}
	}
	return 0;
}

static struct sched_subport * alloc_subport(struct sched_port * port,uint32_t type)
{
	uint32_t index;
	struct sched_subport * sport = NULL;
	uint32_t groupid;
	if(type == DEFAULT_PIPE){
		sport = &port->subport[0];
		if(sport->used == 1){
			return NULL;
		}
		else{
			sport->used    = 1;
			sport->groupid = 0;
			return sport;
		}
	}

	for ( index = 0; index < MAX_SUBPORT_NUMS; index++ )
	{
		sport = &port->subport[port->subport_index];
		groupid = port->subport_index;
		port->subport_index = (port->subport_index+1) % MAX_SUBPORT_NUMS;
		if (sport->used == 0){
			sport->used = 1;
			sport->groupid = groupid;
			return sport;
		}
	}
	return NULL;
}

static void 
free_subport(struct sched_subport * sport)
{
	if (sport != NULL){
		sport->used    =  0;
		sport->groupid =  UINT32_MAX;
	}
}

static int 
sched_subport_config(struct sched_port    * port, 
	                       struct sched_subport * sport,
	                       struct msg_ds        * params)
{
	int ret = 0;

	/* Config User parameters */
	sport->priority = params->priority;
	sport->sportkey = params->subportkey;
	sport->qsize    = params->qsize;
	sport->type     = params->type;
	sport->forbid   = !QOS_SUBPORT_FUN_FORBID;
	sport->users    = params->users;
	memcpy(sport->protomask,params->protomask,sizeof(params->protomask));

	/*config subport tb param, assure channel:ceil >= rate && rate !=0 
	                           ceil   channel:ceil >  rate && rate ==0
	  config pipe tb param, pipe ceil <= subport ceil*/
	sport->tb_size = params->tb_size;
	
	sport->tb_pir_sport[DOWN_LINK] = params->tb_pir_sport[DOWN_LINK];
	sport->tb_cir_sport[DOWN_LINK] = params->tb_cir_sport[DOWN_LINK];
	
	sport->tb_pir_sport[UP_LINK]   = params->tb_pir_sport[UP_LINK];
	sport->tb_cir_sport[UP_LINK]   = params->tb_cir_sport[UP_LINK];
	
	sport->tb_pir_pipe[DOWN_LINK]  = params->tb_pir_pipe[DOWN_LINK];
	sport->tb_pir_pipe[UP_LINK]    = params->tb_pir_pipe[UP_LINK];
	/*inner data: 'used' and 'groupid' are assigned when they are allocated */

	/*list next*/
	sport->next = NULL;
	
	/*pipe index*/
	sport->n_shared_pipes = MAX_SHARED_PIPE_NUMS;
	sport->n_single_pipes = sport->users;
	sport->n_pipes        = sport->n_shared_pipes + sport->n_single_pipes;

	/*memory alloc, memory manage*/
	uint32_t entry_size = 2 * sizeof(struct sched_subport_inner);  //up link and down link
	uint32_t tpipe_size = sport->n_shared_pipes * sizeof(struct sched_pipe);
	uint32_t spipe_size = sport->n_single_pipes * sizeof(struct sched_pipe);
	uint32_t queue_size = 2 * sport->n_pipes * sport->qsize * sizeof(struct rte_mbuf*);

	uint32_t base_entry = 0;
	uint32_t base_tpipe = 0;
	uint32_t base_spipe = 0;
	uint32_t base_queue = 0;
	uint32_t base       = 0;

	base_tpipe += base_entry + RTE_CACHE_LINE_ROUNDUP(entry_size);
	base_spipe += base_tpipe + RTE_CACHE_LINE_ROUNDUP(tpipe_size);
	base_queue += base_spipe + RTE_CACHE_LINE_ROUNDUP(spipe_size);
	base       += base_queue + RTE_CACHE_LINE_ROUNDUP(queue_size);
	
	/* Allocate memory to store the data structures */
	char mem_name[MAX_MEMORY_NAME_SIZE];
	snprintf(mem_name,sizeof(mem_name),"memory_sched_subport:%d",sport->groupid);
	sport->memory = rte_zmalloc(mem_name, base, RTE_CACHE_LINE_SIZE);
	
	if (sport->memory == NULL) {
		printf("%s: subport:alloc big memory fail\n", __func__);
		ret = -1;
		goto err;
	}
	sport->run_entry   = (struct sched_subport_inner *) (sport->memory + base_entry);
	sport->pipe        = (struct sched_pipe *) (sport->memory + base_tpipe);
	sport->single_pipe = (struct sched_pipe *) (sport->memory + base_spipe);
	sport->queue_array = (struct rte_mbuf  **) (sport->memory + base_queue);
	
	/*runtime data config*/
	sport->runtime[DOWN_LINK] = &sport->run_entry[0];
	sport->runtime[UP_LINK]   = &sport->run_entry[1];

	/*down link running-time data*/
	sport->runtime[DOWN_LINK]->next_pipeid     = 0;
	sport->runtime[DOWN_LINK]->exaust          = 0;
	sport->runtime[DOWN_LINK]->activate_queues = 0;
	sport->runtime[DOWN_LINK]->current_pipe    = NULL;
	sport->runtime[DOWN_LINK]->pkt             = NULL;
	sport->runtime[DOWN_LINK]->q_base          = NULL;
	sport->runtime[DOWN_LINK]->state           = e_PREFETCH_PIPE;

	/*up link running-time data*/
	sport->runtime[UP_LINK]->next_pipeid       = 0;
	sport->runtime[UP_LINK]->exaust            = 0;
	sport->runtime[UP_LINK]->activate_queues   = 0;
	sport->runtime[UP_LINK]->current_pipe      = NULL;
	sport->runtime[UP_LINK]->pkt               = NULL;
	sport->runtime[UP_LINK]->q_base            = NULL;
	sport->runtime[UP_LINK]->state             = e_PREFETCH_PIPE;

	uint64_t time = rte_get_tsc_cycles();
	token_bucket_config(&sport->runtime[DOWN_LINK]->subport_tb_pir,
		                 sport->tb_pir_sport[DOWN_LINK],
		                 sport->tb_size,time,port->hz);
	token_bucket_config(&sport->runtime[UP_LINK]->subport_tb_pir,
		                 sport->tb_pir_sport[UP_LINK],
		                 sport->tb_size,time,port->hz);
	if(sport->tb_cir_sport[DOWN_LINK]!=0){
		token_bucket_config(&sport->runtime[DOWN_LINK]->subport_tb_cir,
							 sport->tb_cir_sport[DOWN_LINK],
							 sport->tb_size,time,port->hz);

	}
	if(sport->tb_cir_sport[UP_LINK]!=0){
		token_bucket_config(&sport->runtime[UP_LINK]->subport_tb_cir,
							 sport->tb_cir_sport[UP_LINK],
							 sport->tb_size,time,port->hz);
	}

	/*virtual line config*/
	ret = virtual_line_config(port,sport,params->virlinekey);
	if(ret < 0){
		rte_free(sport->memory);
		goto err;
	}
	sport->runtime[DOWN_LINK]->virline_bw = &port->virline[sport->lineroadindex].bwinfo[DOWN_LINK];
	sport->runtime[UP_LINK]->virline_bw   = &port->virline[sport->lineroadindex].bwinfo[UP_LINK];

	//install shared pipe
	if(sport->type == SINGLE_PIPE){
		sport->n_valid_pipes = sport->n_single_pipes;
	}
	else{
		sport->n_valid_pipes = sport->n_shared_pipes;
	}
	shared_pipe_install(sport);
	//shared_pipe_tb_cfg(port,sport);
	ret = single_pipe_install(port,sport);
	if(ret < 0){
		virtual_line_config_callback(port,sport);
		rte_free(sport->memory);
		goto err;
	}
	
	return 0;
err:
	return ret;
}


struct sched_subport ** 
sched_subport_lookup(struct sched_port * port,uint32_t sportkey)
{
	uint32_t subportkey = sportkey;
	struct sched_subport ** sport;
	for(sport = &port->sport_list; *sport != NULL; sport = &(*sport)->next){
		if((*sport)->sportkey == subportkey){
			return sport;
		}
	}
	return NULL;
}

static int sched_subport_add2list(struct sched_port    * port, 
	                                    struct sched_subport * sport)
{

	//implement dynamic priority    1 <= priority <= UINT32_MAX
	if (sport->type == DEFAULT_PIPE){
		if (*port->sport_default != NULL ){
			printf("%s:default subport have added!\n",__func__);
			return -1;
		}
		*port->sport_default = sport;
		sport->priority = 1;
		return 0;
	}

	if(*port->sport_default == NULL){
		printf("%s:schedport has not added default traffic channel!\n",__func__);
		return -1;
	}
	
	uint32_t priority = 0;
	struct sched_subport **  pnext;
	

	for (pnext = &port->sport_list; 
	    *pnext != *port->sport_default && *pnext != NULL; 
		 pnext = &(*pnext)->next)
	{
		priority = (*pnext)->priority;
		if (sport->priority <= priority){
			sport->next = *pnext;
			*pnext = sport;
			break;
		}
	}

	if(*pnext == *port->sport_default){
		if(sport->priority == UINT32_MAX){
			sport->priority = priority + 1;
		}
		sport->next = *pnext;
		*pnext = sport;
		port->sport_default = &sport->next;
		(*port->sport_default)->priority= sport->priority;
	}
	
	port->subport_nodefault_nums++;
	pnext = &sport->next;
	
	for (; *pnext != NULL; pnext = &(*pnext)->next){
		(*pnext)->priority++;
	}

	return 0;
}

static int sched_subport_delfromlist(struct sched_port    *  port, 
	                                        struct sched_subport ** sport,
	                                        uint32_t sportkey)
{
	int flag = -1;
	struct sched_subport ** pnext;
	
	for (pnext = &port->sport_list; 
	    *pnext != *port->sport_default && *pnext != NULL; 
		 pnext = &(*pnext)->next)
	{
		if((*pnext)->sportkey == sportkey){
			*sport = *pnext;
			*pnext = (*pnext)->next;
			port->subport_nodefault_nums--;
			flag = 0;
			break;
		}
	}

	if(flag != 0) goto ret;
	
	for (; *pnext != NULL; pnext = &(*pnext)->next){
		(*pnext)->priority--;
	}
	
ret:
	return flag;
}

static void free_sched_subport_memory(struct sched_subport * sport)
{
	if (sport->memory != NULL)
	{
		uint32_t groupid = sport->groupid;
		rte_free(sport->memory);
		sport->memory = NULL;
		free_subport(sport);
		printf("sched subport:%u free ok\n",groupid);
	}
}


void uninstall_sched_subport(struct sched_port    * port,
	                         	   struct sched_subport * sport)
{
	/*del pipe config*/
	if (sport->type & DEFAULT_PIPE){
		printf("%s:default traffic channel must be not deleted!\n",__func__);
		return;
	}
	struct sched_subport * tmp = NULL;
	
	single_pipe_uninstall(port,sport);
	sched_subport_delfromlist(port,&tmp,sport->sportkey);
	virtual_line_config_callback(port,sport);
	//queue
	free_sched_subport_memory(tmp);

	return;

}

static int install_sched_subport(struct sched_port   * port,
	                                  struct msg_ds * params)
{

	struct sched_subport **lkport = sched_subport_lookup(port,params->subportkey);
	if(lkport != NULL){
		printf("The traffic channel %u have existed\n",params->subportkey);
		return -1;
	}
	
	struct sched_subport * sport;
	sport = alloc_subport(port,params->type);
	if (sport == NULL){
		printf("%s:alloc traffic channel fail!\n",__func__);
		return -1;
	}

	if(0 != sched_subport_config(port,sport,params)){
		printf("%s:config traffic channel fail!\n",__func__);
		free_subport(sport);
		return -1;
	}
	//add subport to list 
	if(0 != sched_subport_add2list(port,sport)){
		printf("%s:add traffic channel to list fail!\n",__func__);
		virtual_line_config_callback(port,sport);
		free_sched_subport_memory(sport);
		return -1;
	}

	if(0 != sched_pipe_config(port,sport)){
		printf("%s:config user channel fail!\n",__func__);
		uninstall_sched_subport(port,sport);
		return -1;
	}
	single_pipe_tb_cfg(port,sport);
/*
	if(0 != single_pipe_tb_cfg(port,sport)){
		ret = -5;
		uninstall_sched_subport(port,sport);
		goto err;		
	}
*/
	return 0;
}


/*for sched port---------------------------------------------------------*/
static int alloc_sched_port_memory(struct sched_port * port)
{
	char port_name[MAX_MEMORY_NAME_SIZE]; /* static as referenced from global port_params*/
	char hash_name[MAX_MEMORY_NAME_SIZE];

	uint32_t portid    = port->port_id;
	int32_t  socketid  = port->socket_id;
	uint32_t linkspeed = port->linkspeed;
	
	/*check params*/
	if (socketid < 0 || socketid >= RTE_MAX_NUMA_NODES){
		printf("%s:socket id is illegal!\n",__func__);
		return -1;
	}
		
	if (linkspeed == 0){
		printf("%s:get error port link speed!\n",__func__);
		return -2;
	}
	
	/*total bandwidth meter in bytes*/
	port->rate_total[DOWN_LINK] = (linkspeed * 1000 * 1000) / 8;
	port->rate_total[UP_LINK]   = (linkspeed * 1000 * 1000) / 8;
	port->rate_used[DOWN_LINK]  = 0;
	port->rate_used[UP_LINK]    = 0;

	snprintf(hash_name,sizeof(hash_name),"sched_port_hashtab_port:%u",portid);
	
	hash_params.name      = hash_name;
	hash_params.socket_id = port->socket_id;
	
	port->hkey = rte_hash_create(&hash_params);
	
	if (port->hkey == NULL) {
		printf("%s: Table for key creation failed\n", __func__);
		return -3;
	}
	
	/*alloc memory*/
	uint32_t size_value   = MAX_HASH_ENTRIES * sizeof(struct traffic_value);
  //uint32_t size_entry   = MAX_HIERARCHY_MAP_ENTRY * sizeof(struct hierarchy_map_entry);
	uint32_t size_subport = MAX_SUBPORT_NUMS * sizeof(struct sched_subport);
	uint32_t size_virline = MAX_VIRTUAL_LINE * sizeof(struct sched_virtual_line);
	uint32_t size_ipbuf   = MAX_USERS_PER_SUBPORT * sizeof(uint32_t);

	uint32_t base_value   = 0;
  //uint32_t base_entry   = 0;
	uint32_t base_subport = 0;
	uint32_t base_virline = 0;
	uint32_t base_ipbuf   = 0;
	uint32_t base         = 0;

  //base_entry   += base_value   + RTE_CACHE_LINE_ROUNDUP(size_value);
  //base_subport += base_entry   + RTE_CACHE_LINE_ROUNDUP(size_entry);
    base_subport += base_value   + RTE_CACHE_LINE_ROUNDUP(size_value);
	base_virline += base_subport + RTE_CACHE_LINE_ROUNDUP(size_subport);
	base_ipbuf   += base_virline + RTE_CACHE_LINE_ROUNDUP(size_virline);
	base         += base_ipbuf   + RTE_CACHE_LINE_ROUNDUP(size_ipbuf);
	
	/* Allocate memory to store the data structures */
	snprintf(port_name,sizeof(port_name),"sched_port_memory_port:%u",port->port_id);
	port->memory = rte_zmalloc(port_name, base, RTE_CACHE_LINE_SIZE);
	if (port->memory == NULL) {
		printf("%s: alloc big memory fail\n", __func__);
		rte_hash_free(port->hkey);
		port->hkey = NULL;
		return -4;
	}

	port->hvalue  = (struct traffic_value*)      (port->memory + base_value);
  //port->hentry  = (struct hierarchy_map_entry*)(port->memory + base_entry);
	port->subport = (struct sched_subport*)      (port->memory + base_subport);
	port->virline = (struct sched_virtual_line*) (port->memory + base_virline);
	port->ipbuf   = (uint32_t*)                  (port->memory + base_ipbuf);
	
	return 0;
}

static void free_sched_port_memory(struct sched_port * port)
{
	if (port->hkey != NULL)
	{
		rte_hash_free(port->hkey);
		port->hkey = NULL;
		printf("sched port hash table free OK!\n");
	}
	if (port->memory != NULL)
	{
		rte_free(port->memory);
		port->memory = NULL;
		printf("sched port memory free OK!\n");
	}
}

int init_sched_port(struct sched_port * port,uint16_t portid,int socketid)
{
	//init port, set all member equal 0;
	memset(port,0,sizeof(struct sched_port));
	
	port->port_id         = portid;
	port->socket_id       = socketid;
	port->hz              = rte_get_tsc_hz();
	port->time       	  = rte_get_tsc_cycles();
	
	port->sport_list      = NULL;
	port->sport_default   = &port->sport_list;
	port->list_line       = NULL;
	port->list_line_tail  = &port->list_line;

	port->mtu             = DEFAULT_MTU;
	port->frame_overhead  = FRAME_OVERHEAD;
	return 0;
}

/*init memory sched port and install default channel*/
static int init_sched_port2(struct sched_port * port)
{
	int ret;
	//is hash table or memory for port created?
	if(port->hkey == NULL && port->memory == NULL)
	{
		ret = alloc_sched_port_memory(port);
		if (ret < 0){
			return -1;
		}
	}
	else{
		printf("%s:hash table and memory have allocated!\n",__func__);
	}
	
	//if default subport is installed, not execute
	if (*port->sport_default == NULL){
		ret = virtual_line_add(port,&default_params);
		if(ret < 0){
			return -2;
		}
		
		ret=install_sched_subport(port,&default_params);
		if(ret < 0){
			return -1;
		}
	}
	return 0;
}


/*****************************schedule***********************************/
static inline void 
sched_port_stat_statistics_rx(struct sched_stats * stat_virline,
                                    struct sched_stats * stat_subport,
	                                struct sched_stats * stat_pipe,
	                                uint32_t pkt_len)
{
	SCHED_STATS_ADD(stat_virline->n_pkts,1);
	SCHED_STATS_ADD(stat_virline->n_bytes,pkt_len);
	SCHED_STATS_ADD(stat_subport->n_pkts,1);
	SCHED_STATS_ADD(stat_subport->n_bytes,pkt_len);
	SCHED_STATS_ADD(stat_pipe->n_pkts,1);
	SCHED_STATS_ADD(stat_pipe->n_bytes,pkt_len);
}

static inline void 
sched_port_stat_statistics_dropped(struct sched_stats * stat_virline,
	                                       struct sched_stats * stat_subport,
	                                       struct sched_stats * stat_pipe,
	                                       uint32_t pkt_len)
{
	SCHED_STATS_ADD(stat_virline->n_pkts_dropped,1);
	SCHED_STATS_ADD(stat_virline->n_bytes_dropped,pkt_len);
	SCHED_STATS_ADD(stat_subport->n_pkts_dropped,1);
	SCHED_STATS_ADD(stat_subport->n_bytes_dropped,pkt_len);
	SCHED_STATS_ADD(stat_pipe->n_pkts_dropped,1);
	SCHED_STATS_ADD(stat_pipe->n_bytes_dropped,pkt_len);
}

static void sched_port_pkt_read_tree_path(struct sched_port * port,
	                                               struct traffic_value * value,
	                                               uint64_t protoid,
	                                               struct sched_subport ** subport,
	                                               struct sched_pipe    ** pipe)
{

	uint32_t subportid;
	uint32_t pipeid;	

	subportid = (*port->sport_default)->groupid;
	pipeid    = DEFAULT_PIPE_INDEX;
	
	
	if (value==NULL){
		goto default_value;
	}
	uint32_t sportid;
	uint64_t protomask;
	uint32_t proto = protoid - 1;
	uint32_t index;
	struct sched_subport * spt;
	
	for (index = 0; index < value->nums && index < APP_TYPE_NUMS_PER_IP; index++){
		
		sportid   = value->entry[index].hierarchy.subport;
		protomask = port->subport[sportid].protomask[proto/PROTOCOL_BITS];
		if ( protomask & (PROTOCOL_SHIFT << proto%PROTOCOL_BITS)){
			spt = &port->subport[sportid];
			if(spt->forbid == QOS_SUBPORT_FUN_FORBID){
				continue;
			}
			subportid = sportid;
			if(spt->type == SINGLE_PIPE){
				pipeid  = value->entry[index].hierarchy.pipe;
			}
			break;
		}
	}
	
default_value:
	*subport = &port->subport[subportid];
	*pipe    = &(*subport)->pipe[pipeid];
}

#if 0
static void sched_port_pkt_read_tree_path(struct sched_port * port,
	                                               struct traffic_value * value,
	                                               uint64_t protoid,
	                                               struct sched_subport ** subport,
	                                               struct sched_pipe    ** pipe)
{
	if (value==NULL){
		goto default_value;
	}
	
	struct hierarchy_map_entry * p;
	struct sched_subport * spt;
	
	uint32_t sportid;
	uint64_t protomask;
	uint32_t proto = protoid - 1;

	uint32_t minsport = (*port->sport_default)->groupid;
	uint32_t minpipe  = DEFAULT_PIPE_INDEX;
	
	for (p = value->head; p != NULL; p = p->next){
		sportid   = p->value.hierarchy.subport;
		protomask = port->subport[sportid].protomask[proto/PROTOCOL_BITS];
		if ( protomask & (PROTOCOL_SHIFT << proto%PROTOCOL_BITS)){
			spt = &port->subport[sportid];
			if(spt->forbid == QOS_SUBPORT_FUN_FORBID){
				continue;
			}
			if(spt->priority < port->subport[minsport].priority){
				minsport = sportid;
				minpipe  = p->value.hierarchy.pipe;
			}
			
			/*
			*subport = &port->subport[sportid];
			if((*subport)->forbid == QOS_SUBPORT_FUN_FORBID){
				continue;
			}
			if ((*subport)->type & SHARED_PIPE){
		 		*pipe = &(*subport)->pipe[DEFAULT_PIPE_INDEX];
			}
			else {
				*pipe = &(*subport)->pipe[pipeid];
			}
			return;
			*/
		}
		
	}
	*subport = &port->subport[minsport];
	if ((*subport)->type & SINGLE_PIPE){
		*pipe = &(*subport)->pipe[minpipe];
	}
	else {
		*pipe = &(*subport)->pipe[DEFAULT_PIPE_INDEX];
	}
	return;
default_value:
	*subport = *port->sport_default;
	*pipe    = &(*subport)->pipe[DEFAULT_PIPE_INDEX];
	
}
#endif
static int sched_port_enqueue_qwa(struct sched_port       * port,
	     								   struct sched_subport    * sport,
                                           struct sched_pipe       * pipe,
                                           struct rte_mbuf        ** qbase, 
                                           struct rte_mbuf         * pkt,
                                           uint8_t                   flag)
{
	struct sched_queue *q = &pipe->pipeinner[flag].queue;    //queue info of pipe private data 
	uint64_t qsize        = (uint64_t)sport->qsize;    //get group queue size
	uint64_t qlen         = q->qw - q->qr;
	
	/* Drop the packet (and update drop stats) when queue is full */
	if (qlen >= qsize) {
		rte_pktmbuf_free(pkt);
		sched_port_stat_statistics_dropped(&port->virline[sport->lineroadindex].bwinfo[flag].stats,
										   &sport->runtime[flag]->stats,
			                               &pipe->pipeinner[flag].stats,
			                                pkt->pkt_len);
		return 0;
	}

	/* Enqueue packet */
	uint64_t qr = q->qw & (qsize - 1);
	qbase[qr]   = pkt;
	q->qw++;

	/* Activate pipe queue */
	if (pipe->pipeinner[flag].activate == 0){
		pipe->pipeinner[flag].activate = 1;
		sport->runtime[flag]->activate_queues++;
	}
	
	/* Statistics */
	sched_port_stat_statistics_rx(&port->virline[sport->lineroadindex].bwinfo[flag].stats,
	               				  &sport->runtime[flag]->stats,
	               				  &pipe->pipeinner[flag].stats,
	               				   pkt->pkt_len);
	return 1;
}

typedef uint32_t (*__get_addr)(struct rte_mbuf *);
	
static uint32_t get_addr_src(struct rte_mbuf *pkt){
	return pkt->tuple.ipv4.ip_src;
}
static uint32_t get_addr_dst(struct rte_mbuf *pkt){
	return pkt->tuple.ipv4.ip_dst;
}

static __get_addr get_addr[2] = {get_addr_dst,get_addr_src};



int sched_port_enqueue(struct sched_port *port, 
	                          struct rte_mbuf  *pkt,
	                          uint8_t flag)
{
	struct rte_mbuf      **q_base;
	struct sched_subport * sport;
	struct sched_pipe    * pipe;
	struct traffic_value * value;

	struct ip_addr_key key;
	key.ip_addr   = get_addr[flag](pkt);
	uint8_t proto = pkt->pktmark;
	
	int32_t pos = rte_hash_lookup(port->hkey,(void*)&key);
	switch(pos){
		case -EINVAL:
			return -1; //exception deal!!!!!
		case -ENOENT:
			sport = *port->sport_default;
			pipe  = &sport->pipe[DEFAULT_PIPE_INDEX];
			break;
		default:
			value = &port->hvalue[pos];
			sched_port_pkt_read_tree_path(port,value,proto,&sport,&pipe);
			break;
	}
		
	q_base = &sport->queue_array[sport->qsize * pipe->pipeinner[flag].qindex];
	return sched_port_enqueue_qwa(port,sport,pipe,q_base,pkt,flag);
}


int sched_port_bulk_enqueue(struct sched_port *port, 
	                          		struct rte_mbuf  **pkts,
	                          		uint32_t n_pkts,
	                          		uint8_t flag)
{
	uint32_t result, i;
	result = 0;

	for (i = 0; i < n_pkts; i++) {
		struct rte_mbuf      * pkt;
		struct rte_mbuf      **q_base;
		struct sched_subport * sport;
		struct sched_pipe    * pipe;
		struct traffic_value * value;
		
		pkt = pkts[i];

		struct ip_addr_key key;
		key.ip_addr   = get_addr[flag](pkt);
		//uint8_t proto = pkt->tuple.ipv4.proto;
		uint8_t proto = pkt->pktmark;
		
		int32_t pos = rte_hash_lookup(port->hkey,(void*)&key);
		switch(pos){
			case -EINVAL:
				return -1; //exception deal!!!!!
			case -ENOENT:
				sport = *port->sport_default;
				pipe  = &sport->pipe[DEFAULT_PIPE_INDEX];
				break;
			default:
				value = &port->hvalue[pos];
				sched_port_pkt_read_tree_path(port,value,proto,&sport,&pipe);
				break;
		}
		
		q_base = &sport->queue_array[sport->qsize * pipe->pipeinner[flag].qindex];
		//q_base = sport->queue_array + sport->qsize * pipe->qindex;

		result += sched_port_enqueue_qwa(port,sport,pipe,q_base,pkt,flag);
	}
	return result;
}

static inline uint32_t
sched_min_val_2_u32(uint32_t x, uint32_t y)
{
	return (x < y)? x : y;
}

static void update_credits(struct sched_port    * port,
	                           struct sched_subport * subport,
	                           struct sched_pipe    * pipe,
	                           uint8_t flag)
{

	uint64_t n_periods;
	uint64_t time_diff;
	uint64_t current_time = rte_get_tsc_cycles();
	struct token_bucket_data * tb;
	
	struct sched_virtual_line_bwinfo * bwinfo = subport->runtime[flag]->virline_bw;
	time_diff = current_time - port->time;
	n_periods = time_diff / bwinfo->period;
	bwinfo->totaltokens += n_periods * bwinfo->bytes_per_period;
	bwinfo->totaltokens = sched_min_val_2_u32(bwinfo->totaltokens,2048);
	port->time += n_periods * bwinfo->period;
	
	// Subport TB  P
	tb = &subport->runtime[flag]->subport_tb_pir;
	time_diff = current_time - tb->tb_time;
	n_periods = time_diff / tb->tb_period;
	tb->tb_credits += n_periods * tb->tb_bytes_per_period;
	tb->tb_credits  = sched_min_val_2_u32(tb->tb_credits,tb->tb_size);
	//tb->tb_time = current_time;
	tb->tb_time += n_periods * tb->tb_period;
	//Subport  TB  C
	if(subport->tb_cir_sport[flag] != 0){
		tb = &subport->runtime[flag]->subport_tb_cir;
		time_diff = current_time - tb->tb_time;
		n_periods = time_diff / tb->tb_period;
		tb->tb_credits += n_periods * tb->tb_bytes_per_period;
		tb->tb_credits  = sched_min_val_2_u32(tb->tb_credits,tb->tb_size);
		//tb->tb_time = current_time;
		tb->tb_time += n_periods * tb->tb_period;
	}
	// Pipe TB  P
	if(subport->type == SINGLE_PIPE && subport->tb_pir_pipe[flag] != 0){
		tb = &pipe->pipeinner[flag].pipe_tb;
		time_diff  = current_time - tb->tb_time;
		n_periods  = time_diff / tb->tb_period;
		tb->tb_credits += n_periods * tb->tb_bytes_per_period;
		tb->tb_credits  = sched_min_val_2_u32(tb->tb_credits,tb->tb_size);
		//tb->tb_time = current_time;
		tb->tb_time += n_periods * tb->tb_period;
	}
#if 0
	// Pipe TB  C
	tb = &pipe->pipeinner[flag].pipe_tb_cir;
	pipe_time_diff = current_time - tb->tb_time;
	pipe_n_periods = pipe_time_diff / tb->tb_period;
	tb->tb_credits += pipe_n_periods * tb->tb_bytes_per_period;
	tb->tb_credits  = sched_min_val_2_u32(tb->tb_credits,tb->tb_size);
	tb->tb_time += pipe_n_periods * tb->tb_bytes_per_period;
#endif
}

static int credits_check(struct sched_port    * port,
	                        struct sched_subport * sport,
	                        struct sched_pipe    * pipe,
	                        uint8_t flag)
{
	struct rte_mbuf *pkt = sport->runtime[flag]->pkt;
	uint32_t pkt_len = pkt->pkt_len + port->frame_overhead;
	
	struct token_bucket_data * tb_pir = &sport->runtime[flag]->subport_tb_pir;
	struct token_bucket_data * tb_cir = &sport->runtime[flag]->subport_tb_cir;
	struct token_bucket_data * tb_pip = &pipe->pipeinner[flag].pipe_tb;
	struct sched_virtual_line_bwinfo * bwinfo = sport->runtime[flag]->virline_bw;

	uint32_t pip_pkt_len = 0;

	//check pipe pir bucket if it is single pipe;
	if(sport->type == SINGLE_PIPE){
		if(tb_pip->tb_credits < pkt_len){
			return 0;
		}
		else {
			pip_pkt_len = pkt_len;
		}
	}
	
	if(sport->tb_cir_sport[flag]==0) //assure rate is equal 0, limit channel
	{
		if(tb_pir->tb_credits  >= pkt_len &&
		   bwinfo->totaltokens >= pkt_len)
		{
			tb_pir->tb_credits -= pkt_len;
			bwinfo->totaltokens-= pkt_len;
			tb_pip->tb_credits -= pip_pkt_len;
			return 1;
		}
		return 0;
	}
	/*
	if(tb_cir->tb_credits >= pkt_len){
		tb_pir->tb_credits -= pkt_len;
		tb_cir->tb_credits -= pkt_len;
		tb_pip->tb_credits -= pip_pkt_len;
		return 1;
	}
	if(tb_pir->tb_credits >= pkt_len){
		
		if(bwinfo->totaltokens < pkt_len){
			return 0;
		}
		else{
			tb_pir->tb_credits -= pkt_len;
			bwinfo->totaltokens-= pkt_len;
			tb_pip->tb_credits -= pip_pkt_len;
			return 1;
		}
	}
	return 0;
	*/
 
	
	if(tb_pir->tb_credits < pkt_len) return 0;
	
	if(tb_cir->tb_credits < pkt_len){
		
		if(bwinfo->totaltokens >= pkt_len){
			tb_pir->tb_credits -= pkt_len;
			bwinfo->totaltokens-= pkt_len;
			tb_pip->tb_credits -= pip_pkt_len;
			return 1;
		}
		return 0;
	}

	tb_pir->tb_credits -= pkt_len;
	tb_cir->tb_credits -= pkt_len;
	tb_pip->tb_credits -= pip_pkt_len;
	return 1;
	
}

static int do_schedule(struct sched_port    * port,
	                       struct sched_subport * sport,
	                       struct sched_pipe    * pipe,
	                       uint8_t flag)
{
	struct sched_queue *queue = &pipe->pipeinner[flag].queue;
	struct rte_mbuf *pkt = sport->runtime[flag]->pkt;
	//uint32_t pkt_len = pkt->pkt_len + port->frame_overhead;

	if (!credits_check(port,sport,pipe,flag)) {
		return 0;
	}

	/* Send packet */
	port->pkts_out[flag][ port->n_pkts_out[flag]++ ] = pkt;
	queue->qr++;
	
	if (queue->qr == queue->qw) {
		pipe->pipeinner[flag].activate = 0;
		sport->runtime[flag]->activate_queues--;
		
		//--------------------------------------------------red
		//sched_port_set_queue_empty_timestamp(port, qindex);
	}
	
	return 1;
}

static int do_handle(struct sched_port    * port,
	                    struct sched_subport * sport,
	                    uint8_t flag)
{
	struct sched_subport_inner * inner = sport->runtime[flag];                  
	switch (inner->state) {
		
		case e_PREFETCH_PIPE:
		{
			uint32_t index = inner->next_pipeid + (sport->type == SINGLE_PIPE);
			inner->current_pipe= &sport->pipe[index];
			inner->next_pipeid = (inner->next_pipeid + 1) % sport->n_valid_pipes;
			if (inner->current_pipe->pipeinner[flag].activate == 0) {
				if (inner->next_pipeid == 0){
					inner->exaust = 1;
				}
				inner->state = e_PREFETCH_PIPE;
				return 0;
			}
			rte_prefetch0(inner->current_pipe);
			inner->state = e_PREFETCH_QUEUE_ARRAYS;
			return 0;
		}
	
		case e_PREFETCH_QUEUE_ARRAYS:
		{
			struct sched_pipe * pipe = inner->current_pipe;
			inner->q_base = &sport->queue_array[sport->qsize * pipe->pipeinner[flag].qindex];
			rte_prefetch0(inner->q_base);
			update_credits(port,sport,pipe,flag);
			inner->state= e_PREFETCH_MBUF;
			return 0;
		}
	
		case e_PREFETCH_MBUF:
		{
			struct sched_pipe * pipe  = inner->current_pipe; 
			struct rte_mbuf  ** qbase = inner->q_base;
			uint64_t qsize = (uint64_t)sport->qsize;
			uint64_t qr    = pipe->pipeinner[flag].queue.qr & (qsize-1);
			inner->pkt = qbase[qr];
			rte_prefetch0(inner->pkt);
			if (unlikely((qr & 0x7) == 7)) {
				uint16_t qr_next = (pipe->pipeinner[flag].queue.qr + 1) & (qsize - 1);
				rte_prefetch0(qbase + qr_next);
			}
			inner->state = e_READ_MBUF;
			return 0;
		}
	
		case e_READ_MBUF:
		{
			uint32_t result = 0;
			struct sched_pipe * pipe = inner->current_pipe;
			result = do_schedule(port,sport,pipe,flag);
	
			/* Look for next packet within the same TC */
			if (result && pipe->pipeinner[flag].activate==1) {
				inner->state = e_PREFETCH_MBUF;
				return 1;
			}

			/*
			if (result == 0 && pipe->activate==1){
				sport->state = e_PREFETCH_QUEUE_ARRAYS;
				return 0;
			}
			*/
			if (inner->next_pipeid == 0){
				inner->exaust = 1;
			}
			
			inner->state = e_PREFETCH_PIPE;
			return result;

		}
		
		default:
			rte_panic("Algorithmic error (invalid state)\n");
			return 0;
		}
}


static void sched_virtual_line_update_token(struct sched_port *port,uint8_t flag)
{
	uint64_t current_time = rte_get_tsc_cycles();
	uint64_t time_diff    = current_time - port->time;
	uint64_t n_periods;
	struct sched_virtual_line **line;
	struct sched_virtual_line_bwinfo * bwinfo;
	for(line = &port->list_line; *line != NULL; line = &(*line)->next)
	{
		bwinfo = &(*line)->bwinfo[flag];
		n_periods = time_diff / bwinfo->period;
		bwinfo->totaltokens += n_periods * bwinfo->bytes_per_period;
		bwinfo->totaltokens = sched_min_val_2_u32(bwinfo->totaltokens,65536);
	}
	port->time = current_time;
#if 0	
	uint64_t cycles_diff = cycles - port->time_cpu_cycles;
	double   bytes_diff  = ((double) cycles_diff) / port->cycles_per_byte;

	//Advance port time 
	port->time_cpu_cycles = cycles;
	port->time_cpu_bytes += (uint64_t) bytes_diff;
	if (port->time < port->time_cpu_bytes){
		port->time = port->time_cpu_bytes;
	}
#endif	
}


int sched_port_dequeue(struct sched_port * port, 
	                          struct rte_mbuf   **pkts,
	                          uint32_t n_pkts,
	                          uint8_t flag)
{
	uint32_t count=0;

	port->pkts_out[flag]   = pkts;
	port->n_pkts_out[flag] = 0;

	//sched_virtual_line_update_token(port,flag);

	struct sched_subport * p = port->sport_list;
	//use pointer pointer funtion
	struct sched_subport ** prev;
	for(; p != NULL; p = *prev){//
		prev = &p->next;
		
		if (p->runtime[flag]->activate_queues == 0){
			continue;
		}
		p->runtime[flag]->exaust = 0;
		while(1){
			count += do_handle(port,p,flag);
			if (count == n_pkts) return count;

			if (p->runtime[flag]->activate_queues==0 || p->runtime[flag]->exaust == 1){
				break;
			}
		}
	}
	return count;
}


/**************************************************************************/
//for functional function
//enable disable add delete update list
static int 
port_qos_enable(struct sched_port * port)
{
	int ret = 0;
	
	if (port->enable == QOS_UP) {
		printf("traffic control function have been UP!\n");
		return CODE_RE_ENABLE;
	}

	ret = init_sched_port2(port);

	if (ret < 0){
		printf("traffic control function is UP fail!\n");
		return CODE_ENABLE_FAIL;
	}
	
	port->enable = QOS_UP;
	
	return CODE_CALL_OK;
}

static int 
port_qos_disable(struct sched_port * port)
{
	if (port->enable == QOS_DOWN) {
		
		printf("traffic control function have been DOWN!\n");
		return CODE_RE_DISABLE;
	}
	port->enable = QOS_DOWN;

	return CODE_CALL_OK;
}

void 
port_subport_enable(struct sched_subport * sport)
{
	if (sport->type != DEFAULT_PIPE){
		sport->forbid = !QOS_SUBPORT_FUN_FORBID;
	}
}

void 
port_subport_disable(struct sched_subport * sport)
{
	if (sport->type != DEFAULT_PIPE){
		sport->forbid = QOS_SUBPORT_FUN_FORBID;
	}	
}

void 
port_singlepipe_enable(struct sched_subport * sport)
{
	if (sport->type != DEFAULT_PIPE){
		sport->type = SINGLE_PIPE;
	}
}

void 
port_singlepipe_disable(struct sched_subport * sport)
{
	if (sport->type != DEFAULT_PIPE){
		sport->forbid = SHARED_PIPE;
	}	
}


static int 
port_qos_add_subport(struct sched_port * port,struct msg_ds * param)
{
	int ret;
	
	if (port->enable == QOS_DOWN){

		ret = init_sched_port2(port);
		if (ret < 0){
			printf("init_sched_port2:%d add traffic control channel fail!\n",ret);
			return CODE_ADD_SP_FAIL;
		}
	}

	ret = install_sched_subport(port,param);
	
	if(ret < 0){
		return CODE_ADD_SP_FAIL;
	}

	return CODE_CALL_OK;
	
}

static int
port_qos_del_subport(struct sched_port * port,struct msg_ds * params)
{

	struct sched_subport ** sport;
	uint32_t sportkey;
	
	if (port->subport_nodefault_nums == 0) {
		printf("%s:don't have enough user channel for you to delete!\n",__func__);
		return CODE_DEL_SP_FAIL;
	}

 	sportkey = params->subportkey;
	
	sport = sched_subport_lookup(port,sportkey);

	if (sport == NULL || (*sport)->type == DEFAULT_PIPE){
		printf("%s:don't find the traffic channel of %u!\n",__func__,sportkey);
		return CODE_DEL_SP_FAIL;
	}
	
	uninstall_sched_subport(port,*sport);
	
	return CODE_CALL_OK;
}

static int 
port_qos_del_virline(struct sched_port * port,struct msg_ds * params)
{
	int ret = virtual_line_delete(port,params->virlinekey);
	if(ret < 0){
		return CODE_DEL_VL_FAIL;
	}
	
	return CODE_CALL_OK;
}

static int 
port_qos_add_virline(struct sched_port * port,struct msg_ds * params)
{
	int ret;

	if (port->enable == QOS_DOWN){

		ret = init_sched_port2(port);
		if (ret < 0){
			printf("init_sched_port2:%d add virtual line fail!\n",ret);
			return CODE_ADD_VL_FAIL;
		}
	}
	
	ret = virtual_line_add(port,params);

	if(ret < 0){
		return CODE_ADD_VL_FAIL;
	}
	
	return CODE_CALL_OK;
} 

int port_qos_update_groupid(struct sched_port * port,uint32_t sportkey,uint32_t priority)
{

	struct sched_subport ** lksport = sched_subport_lookup(port,sportkey);
	
	if (lksport == NULL || (*lksport)->type == DEFAULT_PIPE){
		printf("Don't find the TC of %u or it is default TC!\n",sportkey);
		return -1;
	}

	uint32_t oldpriority = (*lksport)->priority;
	
	if (priority == 0 || oldpriority == priority) return 0;

	if(port->sport_list == *lksport && port->subport_nodefault_nums == 1){
	   	printf("have one node!\n");
		(*lksport)->priority = priority;
		return 0;
	}
	
	struct sched_subport * p;
	int ret = sched_subport_delfromlist(port,&p,sportkey);
	if(ret < 0){
		return -1;
	}
	
	p->priority = priority;
	sched_subport_add2list(port,p);
	
	uint32_t index;
	struct traffic_value * value;
	for(index = 0; index < p->n_shared_pipes; index++){
		value = &port->hvalue[p->single_pipe[index].traffic_index];
		shift_hierarchy_map_entry(port,value,oldpriority,priority);
	}
	
	return 0;
}

int port_qos_update_sport_pir(struct sched_port    *port,
	                                 struct sched_subport *subport,
	                                 uint64_t rate,
	                                 uint8_t flag)
{
	if(port->hz == 0){
		printf("%s:inner parameter hz exception!\n",__func__);
		return -1;
	}

	struct sched_virtual_line_bwinfo * line   = &port->virline[subport->lineroadindex].bwinfo[flag];
	uint64_t __rate = rate;
	uint64_t period;
	uint64_t bytes_per_period;

	if(line->total_bandwidth < __rate){
		__rate = line->total_bandwidth;
	}
	if(subport->tb_cir_sport[flag] > __rate){
		__rate = subport->tb_cir_sport[flag];
	}

	if(__rate == subport->tb_pir_sport[flag]){
		return 0;
	}


	get_tb_params(__rate, &period, &bytes_per_period,port->hz);

	subport->runtime[flag]->subport_tb_pir.tb_period=period;
	subport->runtime[flag]->subport_tb_pir.tb_bytes_per_period=bytes_per_period;
	subport->tb_pir_sport[flag] = __rate;

	//update shared pipe
	uint32_t index;
	struct token_bucket_data * tb;
	for (index = 0; index < subport->n_shared_pipes; index++){
		tb = &subport->pipe[index].pipeinner[flag].pipe_tb;
		tb->tb_period = period;
		tb->tb_bytes_per_period = bytes_per_period;
	}
	return 0;
}

int port_qos_update_sport_cir(struct sched_port    *port,
	                                 struct sched_subport *subport,
	                                 uint64_t rate,
	                                 uint8_t flag)
{
	if(port->hz == 0){
		printf("%s:inner parameter hz exception!\n",__func__);
		return -1;
	}
	struct sched_virtual_line_bwinfo * line   = &port->virline[subport->lineroadindex].bwinfo[flag];

	uint64_t rate_update = rate;
	uint64_t rate_last   = subport->tb_cir_sport[flag];
	int64_t  rate_vir;

	if(rate_update > subport->tb_pir_sport[flag]){
		rate_update = subport->tb_pir_sport[flag];
	}
	rate_vir  = rate_update - rate_last;
	if((int64_t)line->total_ceil < rate_vir){
		rate_vir    = line->total_ceil;
		rate_update = rate_vir + rate_last;
	}

	if(rate_update == subport->tb_cir_sport[flag]){  //as same as last
		return 0;
	}
	
	uint64_t period;
	uint64_t bytes_per_period;
	//subport
	get_tb_params(rate_update, &period, &bytes_per_period,port->hz);
	subport->runtime[flag]->subport_tb_cir.tb_period=period;
	subport->runtime[flag]->subport_tb_cir.tb_bytes_per_period=bytes_per_period;
	subport->tb_cir_sport[flag] = rate_update;
	//virtual line
	line->total_ceil -= rate_vir;
	get_tb_params(line->total_ceil,&period,&bytes_per_period,port->hz);
	line->period = period;
	line->bytes_per_period = bytes_per_period;
	return 0;
}


int port_qos_update_pipe_rate(struct sched_port * port,
								     struct sched_subport *subport,
									 uint64_t rate,
									 uint8_t flag)
{
	if(port->hz == 0){
		printf("%s:inner parameter hz exception!\n",__func__);
		return -1;
	}
	
	uint64_t __rate = rate;

	if(__rate > subport->tb_pir_pipe[flag]){
		__rate = subport->tb_pir_pipe[flag];
	}
	
	uint64_t rate_bytes_per_period;
	uint64_t rate_period;
	get_tb_params(__rate, &rate_period, &rate_bytes_per_period,port->hz);

	uint32_t index;
	struct token_bucket_data * tb;
	
	for(index = 0; index < subport->n_single_pipes; index++){
		tb = &subport->single_pipe[index].pipeinner[flag].pipe_tb;
		tb->tb_bytes_per_period = rate_bytes_per_period;
		tb->tb_period = rate_period;
	}
	subport->tb_pir_pipe[flag] = __rate;
	return 0;

}

void port_subport_update_bucketsize(struct sched_subport *subport,
									 	     uint32_t bucketsize)
{
	if ( bucketsize < TB_DEFAULT_BUCKETSIZE)
		return;
	subport->tb_size = bucketsize;
	subport->runtime[UP_LINK]->subport_tb_cir.tb_size = bucketsize;
	subport->runtime[UP_LINK]->subport_tb_pir.tb_size = bucketsize;
	subport->runtime[DOWN_LINK]->subport_tb_cir.tb_size = bucketsize;
	subport->runtime[DOWN_LINK]->subport_tb_pir.tb_size = bucketsize;

}

void port_pipe_update_bucketsize(struct sched_subport *subport,
									     uint32_t bucketsize)
{
	if ( bucketsize < TB_DEFAULT_BUCKETSIZE)
		return;
	struct sched_pipe * pipe;
	uint32_t index;
	for(index = 0; index < subport->n_pipes; index++){
		pipe = &subport->pipe[index];
		pipe->pipeinner[UP_LINK].pipe_tb.tb_size = bucketsize;
		pipe->pipeinner[DOWN_LINK].pipe_tb.tb_size = bucketsize;
	}
	subport->tb_size = bucketsize;
}

int port_subport_default_reset(struct sched_port * port)
{
	int ret = 0;
	struct sched_subport * sport = *port->sport_default;
	
	if(sport == NULL){
		printf("default is not found!\n");
		return -1;
	}
	port_subport_update_bucketsize(sport,TB_DEFAULT_BUCKETSIZE);
	port_pipe_update_bucketsize(sport,TB_DEFAULT_BUCKETSIZE);
	port_qos_update_sport_pir(port,sport,TB_DEFAULT_PIR,UP_LINK);
	port_qos_update_sport_pir(port,sport,TB_DEFAULT_PIR,DOWN_LINK);
	return ret;
}

static void print_real_rate(struct sched_stats * upoldstats,
	                   struct sched_stats * upnewstats,
	                   struct sched_stats * downoldstats,
	                   struct sched_stats * downnewstats)
{
	printf("uplink  : recv packets: %10"PRIu64 " recv bytes: %10"PRIu64 "\n"
		   "          drop packets: %10"PRIu64 " drop bytes: %10"PRIu64 "\n"
		   "downlink: recv packets: %10"PRIu64 " recv bytes: %10"PRIu64 "\n"
		   "          drop packets: %10"PRIu64 " drop bytes: %10"PRIu64 "\n",
		    upnewstats->n_pkts            - upoldstats->n_pkts,
		    upnewstats->n_bytes           - upoldstats->n_bytes,
		    upnewstats->n_pkts_dropped    - upoldstats->n_pkts_dropped,
		    upnewstats->n_bytes_dropped   - upoldstats->n_bytes_dropped,
		    downnewstats->n_pkts          - downoldstats->n_pkts,
		    downnewstats->n_bytes         - downoldstats->n_bytes,
		    downnewstats->n_pkts_dropped  - downoldstats->n_pkts_dropped,
		    downnewstats->n_bytes_dropped - downoldstats->n_bytes_dropped);
	memcpy(upoldstats,upnewstats,sizeof(struct sched_stats));
	memcpy(downnewstats,downoldstats,sizeof(struct sched_stats));
}

void print_virline_real_rate(struct sched_virtual_line * line,
								struct sched_stats *upstats,
								struct sched_stats *downstats)

{
	printf("***************************************************************\n");
	printf("virtual line ID: %"PRIu32",virtual line index: %"PRIu32"\n",
		    line->lineroadid,line->lineroadindex);
	print_real_rate(upstats,  &line->bwinfo[UP_LINK].stats,
		            downstats,&line->bwinfo[DOWN_LINK].stats);	
}
void print_subport_real_rate(struct sched_subport * sport,
	                              struct sched_stats *upstats,
	                              struct sched_stats *downstats)
{
	printf("\nvirtual line: %"PRIu32",sched subport: %"PRIu32",priority: %"PRIu32"\n",
		    sport->lineroadid,
		    sport->sportkey,
		    sport->priority);
	print_real_rate(upstats,  &sport->runtime[UP_LINK]->stats,
		            downstats,&sport->runtime[DOWN_LINK]->stats);
}

void print_pipe_real_rate(struct sched_pipe * pipe,
						      struct sched_stats *upstats,
							  struct sched_stats *downstats)

{
	printf("Pipe ID: %"PRIu32"\n",pipe->pipeid);
	print_real_rate(upstats,  &pipe->pipeinner[UP_LINK].stats,
		            downstats,&pipe->pipeinner[DOWN_LINK].stats);	
}


#if 0
void port_qos_manage(void * arg)
{
	struct system_info * sysinfo = (struct system_info *)arg;
	struct portinfo    * pinfo   = &sysinfo->portinfos;
	struct sched_port  * port;
	uint8_t portid=1;
	static int cnt=0;
	cnt++;
	printf("sencond:%d-----cycles:%lu-----tcs_hz%lu\n",cnt,rte_get_tsc_cycles(),rte_get_tsc_hz());
	while(portid <= 1/*RTE_MAX_ETHPORTS*/){
		if(pinfo->status_uk[portid] & USER_STATUS){
			port = &pinfo->schport[portid];
			if (cnt==5)port_qos_enable(port);
			parse_message(port);
		}
		portid++;
	}
}
void port_qos_manage(void * arg)
{
	struct system_info * sysinfo = (struct system_info *)arg;
	struct portinfo    * pinfo   = &sysinfo->portinfos;
	struct sched_port  * port;
	uint8_t portid=0;
	while(portid <= RTE_MAX_ETHPORTS){
		if(pinfo->status_uk[portid] & USER_STATUS){
			port = &pinfo->schport[portid];
			parse_message(port);
		}
		portid++;
	}
}

#endif

int qos_init(__attribute__((unused))void * __sysinfo)
{
	int ret = -1;

  //int ret = msgget((key_t)MSG_KEY_T, 0666 | IPC_CREAT | IPC_EXCL);
	ret = msgget((key_t)MSG_KEY_T, 0666 | IPC_CREAT);

		
	if( ret == -1){
		printf("get message queue id failed with error: %d\n", errno);
	    //rte_exit(EXIT_FAILURE,"get message queue id failed with error: %d\n",errno);
		return -1;
	}
		
	msqid = ret;
	printf("create message queue ok!\n");
	
	struct msqid_ds msg_info;
	
	ret = msgctl(msqid, IPC_STAT, &msg_info);
	if( ret < 0 ){
		printf("get message queue stat failed with error: %d\n", errno);
		return -1;
	}
	
	printf("\ncurrent number of bytes on queue is %d\n"
		   "number of messages in queue is %d\n"
		   "max number of bytes on queue is %d\n"
		   "pid of last msgsnd is %d\n"
		   "pid of last msgrcv is %d\n"
		   "last msgsnd time is %s"
		   "last msgrcv time is %s"
		   "last change time is %s"
		   "msg uid is %d\n"
		   "msg gid is %d\n",
		   (int)msg_info.msg_cbytes,
		   (int)msg_info.msg_qnum,
		   (int)msg_info.msg_qbytes,
		   (int)msg_info.msg_lspid,
		   (int)msg_info.msg_lrpid,
		   ctime(&(msg_info.msg_stime)),
		   ctime(&(msg_info.msg_rtime)),
		   ctime(&(msg_info.msg_ctime)),
		   (int)msg_info.msg_perm.uid,
		   (int)msg_info.msg_perm.gid);

	return 0;
}

int qos_exit(__attribute__((unused))void * __sysinfo)
{
	int ret;
	ret = msgctl(msqid,IPC_RMID,NULL);
	if(ret < 0){
		printf("rm message queue error!\n");
	}
	else {
		printf("rm message queue ok!\n");
	}
	printf("qos exit,end!\n");
	return 0;
}

static int 
parse_message(struct msg_ds * param, struct system_info * sysinfo)
{
	int mark;
	struct portinfo    * pinfo;
	struct sched_port  * schp;

	//port
	uint32_t portid = param->portid;
	
	if(portid >= RTE_MAX_ETHPORTS){
		printf("port id %u of msg error!\n",portid);
		mark = CODE_PORT_NOFD;
		goto retmark;
	}
	
	pinfo = &sysinfo->portinfos;
	if(!(pinfo->status_uk[portid] & USER_STATUS)){
		printf("status of port:%u is not using!\n",portid);
		mark = CODE_PORT_NOFD;
		goto retmark;
	}

	schp = &pinfo->schport[portid];

	uint32_t opcode = param->cmdtype;

	switch(opcode){
		case QOS_OPCODE_ENABLE:
			mark = port_qos_enable(schp);
			break;
		case QOS_OPCODE_DISABLE:
			mark = port_qos_disable(schp);
			break;
		case QOS_OPCODE_ADD_SUBPORT:
			mark = port_qos_add_subport(schp,param);
			break;
		case QOS_OPCODE_DEL_SUBPORT:
			mark = port_qos_del_subport(schp,param);
			break;
		case QOS_OPCODE_ADD_VIRLINE:
			mark = port_qos_add_virline(schp,param);
			break;
		case QOS_OPCODE_DEL_VIRLINE:
			mark = port_qos_del_virline(schp,param);
			break;
		default:
			mark = CODE_UNKNOWN_CMD;
			break;
	}
retmark:
	return mark;
}

int qos_manage(void * arg)
{
	int ret;
	int mark;
	struct msgbuf recvbuf;
	struct msgbuf sendbuf;
	
	size_t recvlength;
	size_t sendlength;
	
	memset(&recvbuf,0,sizeof(struct msgbuf));
	memset(&sendbuf,0,sizeof(struct msgbuf));
	recvlength = sizeof(struct msgbuf) - sizeof(long);
	sendlength = sizeof(struct msgbuf) - sizeof(long);
	/*msgtype = 0 the first msg of "all msg"
	  msgtype > 0 the first msg of "the same msg type"
	  msgtype < 0 the first msg of "type <= |msgtype|"
	*/
	ret = msgrcv(msqid,(void*)&recvbuf,recvlength,1,IPC_NOWAIT);
	
	if(ret < 0) {
		//printf("errno:%d[%d,%d,%d,%d,%d,%d,%d,%d]\n",errno,E2BIG,EACCES,EAGAIN,EFAULT,EIDRM,EINTR,EINVAL,ENOMSG);
		if(errno == ENOMSG) return 0;
		printf("recv message fail with errno=%d\n",errno);
		return -1;
	}
	
	printf("recv tcs message succ!\n");

	
	struct msg_ds param;
	memcpy(&param,recvbuf.mtext,sizeof(struct msg_ds));

	sendbuf.mtype = param.mtype;
	
	mark = parse_message(&param,(struct system_info *)arg);
	
	snprintf(sendbuf.mtext,sizeof(sendbuf.mtext),"%d",mark);
	printf("send reply message %s\n",sendbuf.mtext);
	ret = msgsnd(msqid,(void*)&sendbuf,sendlength,0); /*IPC_NOWAIT*/

	if(ret < 0){
		printf("send back message fail!\n");
		return -1;
	}
	return 0;
}


//MODULE_INIT(qos_init);
//MODULE_EXIT(qos_exit);

