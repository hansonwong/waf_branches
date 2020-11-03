#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "dpdk_frame.h"
#include "flow.h"
#include "dpi.h"


#define FLOW_LOG DPDK_LOG
//define FLOW_LOG(x,l,fmt,arg...) printf(fmt, ##arg)

static struct Flow_table * pftab;
static int flow_entry_size = 0;

void Flow_table_status_dump(struct Flow_table * ftab)
{
    unsigned i,index[FLOW_MAX_TYPE];
    struct Flow_table_core * ftabcore;
    int tabts[FLOW_MAX_TYPE][25];

    ftabcore = ftab->ftabcorebuf;
    printf("Traffic Statistics : %s\n",ftab->ts_flag ? "ON" : "OFF");
    printf("Flow entry timeout : %lus\n",ftab->flowtimeout/ftab->hz);  
    printf("TS time:           : %lus\n",ftab->tstime/ftab->hz);
    if(ftab->flowalloc != NULL){
        printf("Flow Table memory queue stat:\n");
        rte_ring_dump(stdout,ftab->flowalloc);      
    }
    printf("Flow Entry info:\n");
    printf("Total Free Flow:%u\n",ftab->totalflow);
    printf("Total Used Flow:%u\n",(ftab->totalflow-rte_ring_count(ftab->flowalloc)));
    printf("Flow Table flownums: %d\nOrigin Flow Buckets:",ftabcore->flownums);
    memset(tabts,0,sizeof(tabts));
    for(i = 0; i < MAX_FLOW_BUCKET; i++){
        index[0] = ftabcore->bucket[0][i].nums;
        index[1] = ftabcore->bucket[1][i].nums;
        index[0] = index[0] >= 24 ? 24 : index[0];
        index[1] = index[1] >= 24 ? 24 : index[1];
        tabts[0][index[0]]++;
        tabts[1][index[1]]++;
    }
    for(i = 0; i < 25; i++){
        if(i % 5 == 0) printf("\n");
        printf("%2d CTs:%5d Buckets;\t",i,tabts[0][i]);
    }
    printf("\n\nNat Flow Buckets:");
    for(i = 0; i < 25; i++){
        if(i % 5 == 0) printf("\n");
        printf("%2d CTs:%5d Buckets;\t",i,tabts[1][i]);
    }
    printf("\n");
}

static int Flow_table_init(__attribute__((unused))void * __sysinfo)
{
    uint32_t i,coreidx;
    uint32_t size,root_size;
    uint32_t entries;
    struct system_info * sysinfo;
    struct Flow_table  * flowtab;
    struct Flow_table_core * ftabcore;
    
    sysinfo = (struct system_info *)__sysinfo;
    flowtab = &sysinfo->ftab;
    memset(flowtab, 0, sizeof(struct Flow_table));
    snprintf(flowtab->name,sizeof(flowtab->name),FLOW_TABLE_NAME);
    flowtab->hz = sysinfo->hz;
    entries = MAX_FLOW_BUCKET * MAX_BUCKET_ENTRY;
    
    flow_entry_size = sizeof(struct Flow_entry);
    size =  flow_entry_size * entries;
    size =  RTE_CACHE_LINE_ROUNDUP(size);

    root_size = sizeof(struct Flow_table_core);
    //root_size = root_size * MAX_LCORE_NUM;
    //root_size = RTE_CACHE_LINE_ROUNDUP(root_size);
    
    flowtab->tabbuf = (struct Flow_entry *)rte_zmalloc(flowtab->name,(size+root_size), RTE_CACHE_LINE_SIZE);
    if(flowtab->tabbuf == NULL){
        rte_exit(EXIT_FAILURE, "alloc flow table memory fail\n");
    }
    flowtab->ftabcorebuf = (struct Flow_table_core *)((uint8_t *)flowtab->tabbuf + size);

    //init alloc queue
    flowtab->flowalloc = rte_ring_create(FLOW_ALLOC_QUEUE,entries,rte_socket_id(),0);
    if(flowtab->flowalloc == NULL){
        rte_free(flowtab->tabbuf);
        flowtab->tabbuf= NULL;
        rte_exit(EXIT_FAILURE, "create flow alloc queue failed\n");
    }
    for(i = 1; i < entries; i++){
        flowtab->tabbuf[i].ctid = i;
        INIT_HLIST_NODE(&flowtab->tabbuf[i].hchain[FLOW_NOT_NAT]);
        INIT_HLIST_NODE(&flowtab->tabbuf[i].hchain[FLOW_NAT_DIR]);
        if(rte_ring_mp_enqueue(flowtab->flowalloc,(void*)&flowtab->tabbuf[i])){
            printf("Init Flow Alloc Queue Failed,enqueue %d total %d\n",i-1,entries-1);
            break;
        }
    }
    flowtab->totalflow = i-1;
    ftabcore = flowtab->ftabcorebuf;
    TAILQ_INIT(&ftabcore->lrulist);
    for(i = 0; i < MAX_FLOW_BUCKET; i++){
        //rte_spinlock_init(&ftabcore->bucket[i].bucketlock);
        INIT_HLIST_HEAD(&ftabcore->bucket[FLOW_NOT_NAT][i].root);
        INIT_HLIST_HEAD(&ftabcore->bucket[FLOW_NAT_DIR][i].root);
    }
    
    flowtab->flowtimeout = rte_get_tsc_hz() * MAX_FLOW_TIMEOUT;
    flowtab->tstime      = rte_get_tsc_hz() * MAX_TS_TIMEOUT;

    flowtab->ts = rte_ring_create(TRAFFIC_STATISTICS,MAX_TS_QUEUE_NUM,rte_socket_id(),RING_F_SC_DEQ);
    if(flowtab->ts == NULL){
        printf("create ts queue failed\n");
    }
    flowtab->ftab_flag = 1;
    flowtab->ts_flag   = 0;

    pftab = flowtab;
    
    int sizeMb = size / (1024 * 1024);
    printf("FLOW:Flowentry:%d Flowentries:%u Flowkey:%lu The sizeof %s is %uMB,The sizeof Bucket is %uB\n",
            flow_entry_size,entries,sizeof(struct Flow_key),flowtab->name,sizeMb,root_size);
    return 0;
}

static void Flow_table_deinit(struct Flow_table * tab)
{
    if(tab->tabbuf != NULL){
        rte_free(tab->tabbuf);
        tab->tabbuf= NULL;
    }
#if 0
    if(tab->ts != NULL){
        rte_ring_free(tab->ts);
        tab->ts = NULL;
    }
    if(tab->flowalloc != NULL){
        rte_ring_free(tab->flowalloc);
        tab->flowalloc = NULL;
    }
#endif

}

static int Flow_table_exit(__attribute__((unused))void * __sysinfo)
{
    struct system_info * sysinfo;
    
    sysinfo = (struct system_info *)__sysinfo;
    Flow_table_deinit(&sysinfo->ftab);
    return 0;
}

static struct Flow_table_core * Flow_table_get(void)
{
    //return &pftab->ftabcorebuf[rte_lcore_id()];
    return pftab->ftabcorebuf;
}

static void get_key_isswap(struct Flow_key * key,uint8_t * isswap)
{
    uint32_t tmp;
    if(key->ip_src > key->ip_dst)
        *isswap = 0;
    else {
        tmp = key->ip_src;
        key->ip_src = key->ip_dst;
        key->ip_dst = tmp;
        tmp = key->port_src;
        key->port_src = key->port_dst;
        key->port_dst = tmp;
        *isswap = 1;
    }
}

static void get_key_from_packet(struct rte_mbuf *  mbuf,struct Flow_key * key)
{
    uint16_t network_header;
    uint16_t eth_type;
    uint16_t *eth_vlan_hdr;
    struct ether_hdr      *eth_hdr;
    struct ipv4_hdr       *ipv4hdr; 
    struct udp_hdr        *udphdr;
    struct tcp_hdr        *tcphdr;
    struct icmp_hdr       *icmphdr;
    
    mbuf->mac_header = mbuf->data_off;
    mbuf->network_header = mbuf->mac_header + sizeof(struct ether_hdr);
    eth_hdr  = rte_pktmbuf_mtod_mac(mbuf, struct ether_hdr *);
    eth_type = rte_be_to_cpu_16(eth_hdr->ether_type);
    if(unlikely(eth_type == 0x8100 || eth_type == 0x9100)){
        eth_vlan_hdr = (uint16_t*)(eth_hdr + 1);
        mbuf->network_header += 4;
        eth_type=rte_be_to_cpu_16(eth_vlan_hdr[1]);
        if(unlikely(eth_type == 0x8100 || eth_type == 0x9100)){
            mbuf->network_header += 4;
            eth_type=rte_be_to_cpu_16(eth_vlan_hdr[3]);
        }
    }

    if(eth_type != 0x0800){
        mbuf->ifnfct = 0;
        return;
    }
    
    ipv4hdr = rte_pktmbuf_mtod_network(mbuf,struct ipv4_hdr *);
    key->proto = ipv4hdr->next_proto_id;
    key->ip_src = rte_be_to_cpu_32(ipv4hdr->src_addr);
    key->ip_dst = rte_be_to_cpu_32(ipv4hdr->dst_addr);
    
    mbuf->transport_header=mbuf->network_header+((ipv4hdr->version_ihl & 0xf)<<2);
    switch (key->proto) {
        case IPPROTO_TCP:
            tcphdr = rte_pktmbuf_mtod_transport(mbuf,struct tcp_hdr *);
            key->port_src = rte_be_to_cpu_16(tcphdr->src_port);
            key->port_dst = rte_be_to_cpu_16(tcphdr->dst_port);
            mbuf->ifnfct = 1;
            break;
        case IPPROTO_UDP:
            udphdr = rte_pktmbuf_mtod_transport(mbuf,struct udp_hdr *);
            key->port_src = rte_be_to_cpu_16(udphdr->src_port);
            key->port_dst = rte_be_to_cpu_16(udphdr->dst_port);
            mbuf->ifnfct = 1;
            break;
        case IPPROTO_ICMP:
            icmphdr = rte_pktmbuf_mtod_transport(mbuf,struct icmp_hdr *);
            key->port_src = rte_be_to_cpu_16(icmphdr->icmp_ident);
            key->port_dst = key->port_src;//(icmphdr->icmp_code << 8 | icmphdr->icmp_type);
            mbuf->ifnfct = 1;
            break;
        default:
            key->port_src = 0;
            key->port_dst = 0;
            mbuf->ifnfct = 0;
    }
    return;
}


static int Flow_entry_cmp(const struct Flow_key * src,const struct Flow_key * dst)
{

    if(src->ip_src   == dst->ip_src &&
       src->ip_dst   == dst->ip_dst &&
       src->port_src == dst->port_src &&
       src->port_dst == dst->port_dst &&
       src->proto    == dst->proto){
       return 0;
    }
    return -1;
}

static int Flow_entry_src_cmp(const struct Flow_key * src,const struct Flow_key * dst,
                                    const uint8_t srcswap,const uint8_t dstswap)
{
    int ret = 0;
    uint8_t type;
    
    if(src->proto != dst->proto)
        return 3;
    
    type = (dstswap << 1 | srcswap);
    switch(type){
        case 0:
            ret  = (src->ip_dst != dst->ip_dst || src->port_src != dst->port_src || src->port_dst != dst->port_dst);
            ret |= (src->ip_src != dst->ip_src) << 1;
            break;
        case 1:
            ret  = (src->ip_src != dst->ip_dst || src->port_dst != dst->port_src || src->port_src != dst->port_dst);
            ret |= (src->ip_dst != dst->ip_src) << 1;
            break;
        case 2:
            ret  = (src->ip_dst != dst->ip_src || src->port_src != dst->port_dst || src->port_dst != dst->port_src);
            ret |= (src->ip_src != dst->ip_dst) << 1;
            break;
        case 3:
            ret  = (src->ip_src != dst->ip_src || src->port_src != dst->port_src || src->port_dst != dst->port_dst);
            ret |= (src->ip_dst != dst->ip_dst) << 1;
            break;
    }
    return ret;
}

static int Flow_entry_dst_cmp(const struct Flow_key * src,const struct Flow_key * dst,
                              const uint8_t srcswap,const uint8_t dstswap)
{
    int ret = 0;
    uint8_t type;
    
    if(src->proto != dst->proto)
        return 3;
    
    type = (dstswap << 1 | srcswap);
    switch(type){
        case 0:
            ret  = (src->ip_src != dst->ip_src || src->port_src != dst->port_src || src->port_dst != dst->port_dst);
            ret |= (src->ip_dst != dst->ip_dst) << 1;
            break;
        case 1:
            ret  = (src->ip_dst != dst->ip_src || src->port_dst != dst->port_src || src->port_src != dst->port_dst);
            ret |= (src->ip_src != dst->ip_dst) << 1;
            break;
        case 2:
            ret  = (src->ip_src != dst->ip_dst || src->port_src != dst->port_dst || src->port_dst != dst->port_src);
            ret |= (src->ip_dst != dst->ip_src) << 1;
            break;
        case 3:
            ret  = (src->ip_dst != dst->ip_dst || src->port_src != dst->port_src || src->port_dst != dst->port_dst);
            ret |= (src->ip_src != dst->ip_src) << 1;
            break;
    }
    return ret;
}

static struct Flow_entry * Flow_entry_get_byctid(uint32_t ctid)
{
    return &pftab->tabbuf[(ctid & (MAX_FLOW_ENTRY - 1))];
}

static void Flow_stats_init(struct Flow_stats * stats,uint64_t time)
{
    stats->lastbytes[FLOW_ORIG]     = 0;
    stats->lastbytes[FLOW_REPLY]    = 0; 
    stats->totalpackets             = 0; 
    stats->totalbytes[FLOW_ORIG]    = 0;
    stats->totalbytes[FLOW_REPLY]   = 0;
    stats->last_count               = time;
    stats->curr_count               = time;
    stats->last_seen                = time;
}

static void Flow_key_init(struct Flow_key * src,const struct Flow_key * dst)
{
    src->ip_src   = dst->ip_src;
    src->ip_dst   = dst->ip_dst;
    src->port_src = dst->port_src;
    src->port_dst = dst->port_dst;
    src->proto    = dst->proto;
}

#if 0
static void Flow_entry_origin_init(struct rte_mbuf * mbuf,
                                       struct Flow_entry * entry,
                                       struct Flow_key * key, 
                                       uint64_t curtime,
                                       uint32_t hash)
{
    /*key init*/
    Flow_key_init(&entry->key[FLOW_ORIG],key);
    Flow_key_sdswap(&entry->key[FLOW_REPLY],key);

    /*stat init,for ts using*/
    Flow_stats_init(&entry->stats,curtime);

    /*flow current time init*/
    entry->last_seen = curtime;

    /*for dpi using*/
    entry->ifmark     = 0;
    entry->protoapp   = 0;
    entry->ext        = NULL;

    entry->hash[FLOW_ORIG]  = hash;
    entry->hash[FLOW_REPLY] = 0;//rte_jhash((void *)(&entry->key[FLOW_REPLY]),sizeof(struct Flow_key),0);   

    /*port init*/
    entry->port[FLOW_ORIG].inport   = mbuf->inport;
    entry->port[FLOW_ORIG].outport  = 0xff;
    entry->port[FLOW_REPLY].inport  = 0xff;
    entry->port[FLOW_REPLY].outport = mbuf->inport;

    /*flow status*/
    entry->status = FIRST_NEW_FLOW;

    /*init hash list*/
    INIT_HLIST_NODE(&entry->hchain[FLOW_ORIG]);
    INIT_HLIST_NODE(&entry->hchain[FLOW_REPLY]);

    /*init flow,dir is FLOW_ORIG*/
    mbuf->flow_dir = FLOW_ORIG;
}
#endif
static uint32_t Flow_dir_get(struct Flow_entry * entry,int dir)
{
    uint32_t status;
    switch(entry->status){
        case EXCEPTION_FLOW:
            status = EXCEPTION_FLOW;
            break;
        case FIRST_NEW_FLOW:
            if(dir == FLOW_REPLY)
                status = FIRST_REPLY_FLOW;
            else status = EXCEPTION_FLOW;
            break;
        case FIRST_REPLY_FLOW:
            status = ESTABLISH_FLOW;
            break;
        case ESTABLISH_FLOW:
            status = ESTABLISH_FLOW;
            break;
        default:
            status = EXCEPTION_FLOW;
            break;
    }
    return status;
}

static void Flow_free_entry(struct Flow_table_core * ftabcore,struct Flow_entry * entry)
{  
    if(entry->hchain[FLOW_NOT_NAT].pprev)
        ftabcore->bucket[FLOW_NOT_NAT][entry->hash[FLOW_NOT_NAT] & (MAX_FLOW_BUCKET-1)].nums--;
    if(entry->hchain[FLOW_NAT_DIR].pprev)
        ftabcore->bucket[FLOW_NAT_DIR][entry->hash[FLOW_NAT_DIR] & (MAX_FLOW_BUCKET-1)].nums--;

    TAILQ_REMOVE(&ftabcore->lrulist,entry,tchain);
    hlist_del_init(&entry->hchain[FLOW_NOT_NAT]);
    hlist_del_init(&entry->hchain[FLOW_NAT_DIR]);
    ftabcore->flownums--;

    if(entry->ext){
        dpi_flow_node_free(entry->ext);
        entry->ext = NULL;
    }
    entry->status = EXCEPTION_FLOW;
    entry->used = 0;
    if(rte_ring_mp_enqueue(pftab->flowalloc,entry)){
        FLOW_LOG(ERR,FLOW,"%s():free flow entry failed!\n",__func__);
    }       
}

static void Flow_Timeout(uint64_t curtime)
{
    int idx;
    struct Flow_entry      * entry;
    struct Flow_table_core * ftabcore;

    ftabcore = Flow_table_get();
    
    for (idx = 0; idx < MAX_TIMEOUT_NUMS; idx++) {
        if (TAILQ_EMPTY(&ftabcore->lrulist))
            break;
        entry = TAILQ_FIRST(&ftabcore->lrulist);
        if ((curtime - entry->stats.last_seen) > pftab->flowtimeout){
            FLOW_LOG(INFO,FLOW,"Timeout Delete Flow(%p) Sucess; "
                               "Ogn Packet: src %u.%u.%u.%u; dst %u.%u.%u.%u; proto %d; srcport %u; dstport %u isswap %u "
                               "Nat Packet: src %u.%u.%u.%u; dst %u.%u.%u.%u; proto %d; srcport %u; dstport %u isswap %u "
                               "status %u, ctid %u; appmark %u;\n", 
                               entry,
                               NIPQUAD(entry->key[FLOW_NOT_NAT].ip_src),
                               NIPQUAD(entry->key[FLOW_NOT_NAT].ip_dst),
                               entry->key[FLOW_NOT_NAT].proto,
                               entry->key[FLOW_NOT_NAT].port_src,
                               entry->key[FLOW_NOT_NAT].port_dst,
                               entry->isswap[FLOW_NOT_NAT],
                               NIPQUAD(entry->key[FLOW_NAT_DIR].ip_src),
                               NIPQUAD(entry->key[FLOW_NAT_DIR].ip_dst),
                               entry->key[FLOW_NAT_DIR].proto,
                               entry->key[FLOW_NAT_DIR].port_src,
                               entry->key[FLOW_NAT_DIR].port_dst,
                               entry->isswap[FLOW_NAT_DIR],
                               entry->status,
                               entry->ctid,
                               entry->protoapp);
            Flow_free_entry(ftabcore,entry);
        }
        else break;
    }
}


static void Flow_entry_key(struct Flow_key * key,
                                struct rte_mbuf * mbuf,
                                uint8_t * isswap)
{
    struct ipv4_tuple5 * pkey = &mbuf->tuple.ipv4;
    
    //note if srcip == dstip
    if(pkey->ip_src > pkey->ip_dst) { //key  src ip > dst ip 
        key->ip_src    = pkey->ip_src;
        key->ip_dst    = pkey->ip_dst;
        key->port_src  = pkey->port_src;
        key->port_dst  = pkey->port_dst;
        *isswap = 0;          //not swap is orig
    } else {
        key->ip_src    = pkey->ip_dst;
        key->ip_dst    = pkey->ip_src;
        key->port_src  = pkey->port_dst;
        key->port_dst  = pkey->port_src;
        *isswap = 1;
    }
    key->proto = pkey->proto;
}

static uint32_t Flow_entry_hash(struct Flow_key * key,
                                     struct rte_mbuf * mbuf,
                                     uint8_t * isswap)
{
    uint32_t hash;
    Flow_entry_key(key,mbuf,isswap);
    //get hash value
    hash = rte_jhash((void *)key,sizeof(struct Flow_key),0);
    return hash;
}

static struct Flow_entry * Flow_tfind(struct Flow_root * bucket,
                                        const struct Flow_key * key,
                                        uint32_t flowtype)
{
    struct Flow_entry * entry;
    struct hlist_node * node;
    hlist_for_each_entry(entry,node,&bucket->root,hchain[flowtype]){
        if (Flow_entry_cmp(key,&entry->key[flowtype]) == 0 ){
            return entry;
        }
    }
    return NULL;
}

static void Flow_tcp_is_finish(struct Flow_entry * entry,struct rte_mbuf * mbuf)
{
    struct tcp_hdr * tcphdr;
    tcphdr = rte_pktmbuf_mtod_transport(mbuf,struct tcp_hdr *);
    /*0(0000)*/
    if(entry->tcpfin == 0 && ((tcphdr->tcp_flags & 0x11) == 0x11)){
        entry->tcpfin |= TCP_FIN_ACK_ORIGIN;
        //printf("FLOW:src %u.%u.%u.%u; dst %u.%u.%u.%u; srcport %u; dstport %u; tcp flags%u\n",
        //NIPQUAD(entry->key[0].ip_src),NIPQUAD(entry->key[0].ip_dst),entry->key[0].port_src,entry->key[0].port_dst,tcphdr->tcp_flags);
    }
    /*1(0001) = TCP_FIN_ACK_ORIGIN*/
    else if(entry->tcpfin == 1 && ((tcphdr->tcp_flags & 0x11) == 0x10)){
        entry->tcpfin |= TCP_ACK_REPLY;
        //printf("FLOW:src %u.%u.%u.%u; dst %u.%u.%u.%u; srcport %u; dstport %u; tcp flags%u\n",
        //NIPQUAD(entry->key[0].ip_src),NIPQUAD(entry->key[0].ip_dst),entry->key[0].port_src,entry->key[0].port_dst,tcphdr->tcp_flags);
    }
    /*3(0011) = TCP_ACK_REPLY|TCP_FIN_ACK_ORIGIN*/
    else if(entry->tcpfin == 3 && ((tcphdr->tcp_flags & 0x11) == 0x11)){
        entry->tcpfin |= TCP_FIN_ACK_REPLY;
        //printf("FLOW:src %u.%u.%u.%u; dst %u.%u.%u.%u; srcport %u; dstport %u; tcp flags%u\n",
        //NIPQUAD(entry->key[0].ip_src),NIPQUAD(entry->key[0].ip_dst),entry->key[0].port_src,entry->key[0].port_dst,tcphdr->tcp_flags);
    }
    /*7(0111) = TCP_FIN_ACK_REPLY|TCP_ACK_REPLY|TCP_FIN_ACK_ORIGIN*/
    else if(entry->tcpfin == 7 && ((tcphdr->tcp_flags & 0x11) == 0x10)){
        entry->tcpfin |= TCP_ACK_ORIGIN;
        //printf("FLOW:src %u.%u.%u.%u; dst %u.%u.%u.%u; srcport %u; dstport %u; tcp flags%u\n",
        //NIPQUAD(entry->key[0].ip_src),NIPQUAD(entry->key[0].ip_dst),entry->key[0].port_src,entry->key[0].port_dst,tcphdr->tcp_flags);
    }
}

static struct Flow_entry * Flow_entry_get(struct rte_mbuf *mbuf,uint64_t curtime)
{
    int ret;
    uint8_t isswap;
    uint32_t hash;
    struct Flow_entry      * entry;
    struct Flow_root       * bucket;
    struct Flow_table_core * ftabcore;
    
    struct Flow_key key = {0};
    /*get key info*/
    Flow_entry_key(&key,mbuf,&isswap);
    ftabcore = Flow_table_get();
    entry = Flow_entry_get_byctid(mbuf->ctid);
    if(mbuf->userdef == NAT_PORT && entry->used == 1){
        if(Flow_entry_cmp(&key,&entry->key[FLOW_NOT_NAT]) == 0){
            mbuf->flow_dir = (isswap != entry->isswap[FLOW_NOT_NAT]);
            FLOW_LOG(DEBUG,FLOW,"PRE FLOW:Lookup Cmp Flow src %u.%u.%u.%u; dst %u.%u.%u.%u; proto %u; srcport %u; dstport %u; hash %u; ctid %u; entry %p; dir %u; isswap %u; mark %u\n",
                                 NIPQUAD(key.ip_src),NIPQUAD(key.ip_dst),key.proto,key.port_src,key.port_dst,entry->hash[0],entry->ctid,entry,mbuf->flow_dir,isswap,entry->protoapp);
            goto findit;
        }
        ret = Flow_entry_dst_cmp(&key,&entry->key[FLOW_NAT_DIR],isswap,entry->isswap[FLOW_NAT_DIR]);
        if(ret == 0 || ret == 2){
            if(hlist_unhashed(&entry->hchain[FLOW_NOT_NAT])){
                Flow_key_init(&entry->key[FLOW_NOT_NAT],&key);
                entry->isswap[FLOW_NOT_NAT] = isswap;
                entry->hash[FLOW_NOT_NAT] = rte_jhash((void *)&key,sizeof(struct Flow_key),0);
                bucket = &ftabcore->bucket[FLOW_NOT_NAT][entry->hash[FLOW_NOT_NAT] & (MAX_FLOW_BUCKET-1)];
                hlist_add_head(&entry->hchain[FLOW_NOT_NAT],&bucket->root);
                bucket->nums++;
                FLOW_LOG(DEBUG,FLOW,"PRE FLOW:Create NAT Flow src %u.%u.%u.%u; dst %u.%u.%u.%u; proto %u; srcport %u; dstport %u; hash %u; ctid %u; entry %p; dir 0; isswap %u; mark %u; ret %u;\n",
                                     NIPQUAD(key.ip_src),NIPQUAD(key.ip_dst),key.proto,key.port_src,key.port_dst,entry->hash[0],entry->ctid,entry,isswap,entry->protoapp,ret);
            }
            mbuf->flow_dir = FLOW_ORIG; //(isswap != entry->isswap[FLOW_NAT_DIR]);
            FLOW_LOG(DEBUG,FLOW,"PRE FLOW:Lookup Dmp Flow src %u.%u.%u.%u; dst %u.%u.%u.%u; proto %u; srcport %u; dstport %u; hash %u; ctid %u; entry %p; dir %u; isswap %u; mark %u; ret %u\n",
                                 NIPQUAD(key.ip_src),NIPQUAD(key.ip_dst),key.proto,key.port_src,key.port_dst,entry->hash[1],entry->ctid,entry,mbuf->flow_dir,isswap,entry->protoapp,ret);
            goto findit;
        }
        else 
            return NULL;
    }
    
    ftabcore = Flow_table_get();
    hash     = rte_jhash((void *)&key,sizeof(struct Flow_key),0);
    bucket   = &ftabcore->bucket[FLOW_NOT_NAT][hash & (MAX_FLOW_BUCKET-1)];
    entry    = Flow_tfind(bucket,&key,FLOW_NOT_NAT);
    
    if(entry != NULL){
        entry->stats.totalpackets++;
        mbuf->ctid = entry->ctid;
        mbuf->flow_dir = (isswap != entry->isswap[FLOW_NOT_NAT]);
        FLOW_LOG(DEBUG,FLOW,"PRE FLOW:Lookup Pre Flow src %u.%u.%u.%u; dst %u.%u.%u.%u; proto %u; srcport %u; dstport %u; hash %u; ctid %u; entry %p; dir %u; isswap %u; mark %u;  \n",
                             NIPQUAD(key.ip_src),NIPQUAD(key.ip_dst),key.proto,key.port_src,key.port_dst,entry->hash[0],entry->ctid,entry,mbuf->flow_dir,isswap,entry->protoapp);
findit:
        entry->stats.lastbytes[isswap] += mbuf->data_len;
        mbuf->pktmark = packet_dpi_mark_get(entry);
        entry->stats.last_seen = curtime;
        if(key.proto == IPPROTO_TCP)
            Flow_tcp_is_finish(entry,mbuf);
        TAILQ_REMOVE(&ftabcore->lrulist, entry, tchain);
        TAILQ_INSERT_TAIL(&ftabcore->lrulist,entry,tchain);
        return entry;
    }
    
    if(rte_ring_mc_dequeue(pftab->flowalloc,(void**)&entry)){
        FLOW_LOG(ERR,FLOW,"%s():cannot allocate flow entry!\n",__func__);
        return NULL;
    }
    /*key init*/
    Flow_key_init(&entry->key[FLOW_NOT_NAT],&key);
    memset(&entry->key[FLOW_NAT_DIR],0,sizeof(struct Flow_key));
    
    /*stat init,for ts using*/
    Flow_stats_init(&entry->stats,curtime);
    entry->stats.lastbytes[isswap] += mbuf->data_len;

    /*for dpi using*/
    entry->ifmark   = 0;
    entry->protoapp = 0;
    entry->ext      = NULL;
    entry->dpicnt   = packet_dpi_default_cnt(key.proto);
    
    entry->inport   = mbuf->inport;
    entry->outport  = 0xff;

    /*flow status*/
    entry->status = FIRST_NEW_FLOW;
    /*flow origin is swap or not*/
    entry->isswap[FLOW_NOT_NAT] = isswap;
    entry->hash[FLOW_NOT_NAT] = hash;
    entry->tcpfin = 0;
    entry->used = 1;
    
    mbuf->flow_dir = FLOW_ORIG;
    mbuf->flow_entry = entry;
    mbuf->ctid = entry->ctid;
    mbuf->pktmark = NDPI_DEFAULT_MARK;//packet_dpi_mark_get(entry);

    TAILQ_INSERT_TAIL(&ftabcore->lrulist,entry,tchain);
    
    hlist_add_head(&entry->hchain[FLOW_NOT_NAT],&bucket->root);
    bucket->nums++;
    ftabcore->flownums++;
    FLOW_LOG(DEBUG,FLOW,"PRE FLOW:Create Pre Flow src %u.%u.%u.%u; dst %u.%u.%u.%u; proto %u; srcport %u; dstport %u; hash %u; ctid %u; entry %p; dir %u; isswap %u\n",
                         NIPQUAD(key.ip_src),NIPQUAD(key.ip_dst),key.proto,key.port_src,key.port_dst,hash,entry->ctid,entry,mbuf->flow_dir,isswap);
    return entry;
}

struct Flow_entry * Flow_table_natlookup(struct rte_mbuf *mbuf)
{
#ifdef FLOW_TABLE_MCORE

    uint32_t hash;
    uint8_t  isswap;
    struct Flow_entry      * entry;
    struct Flow_root       * bucket;
    struct Flow_table_core * ftabcore;
    
    if(mbuf->ifnfct != 1){
        mbuf->ctid = 0;
        mbuf->pktmark = 0;
        mbuf->flow_entry = NULL;
        goto ret;
    }

    struct Flow_key key = {0};
    
    ftabcore = Flow_table_get();
    hash     = Flow_entry_hash(&key,mbuf,&isswap);
    bucket   = &ftabcore->bucket[FLOW_NAT_DIR][hash & (MAX_FLOW_BUCKET-1)];
    entry    = Flow_tfind(bucket,&key,FLOW_NAT_DIR);
    
    if(entry != NULL){
        entry->stats.totalpackets++;
        mbuf->flow_entry = entry;
        mbuf->ctid = entry->ctid;
        mbuf->flow_dir = (isswap != entry->isswap[FLOW_NAT_DIR]);
        mbuf->pktmark  = packet_dpi_mark_get(entry);
        FLOW_LOG(DEBUG,FLOW,"NAT FLOW:Lookup Nat Flow src %u.%u.%u.%u; dst %u.%u.%u.%u; proto %u; srcport %u; dstport %u; hash %u; ctid %u; entry %p; dir %u; isswap %u; mark %u\n",
                             NIPQUAD(key.ip_src),NIPQUAD(key.ip_dst),key.proto,key.port_src,key.port_dst,hash,entry->ctid,entry,mbuf->flow_dir,isswap,mbuf->pktmark);
        return entry;
    }
    
    if(rte_ring_mc_dequeue(pftab->flowalloc,(void**)&entry)){
        FLOW_LOG(ERR,FLOW,"%s():cannot allocate flow nat entry!\n",__func__);
        mbuf->ctid = 0;
        mbuf->pktmark = 0;
        mbuf->flow_entry = NULL;
        goto ret;
    }
    /*key init*/
    Flow_key_init(&entry->key[FLOW_NAT_DIR],&key);
    memset(&entry->key[FLOW_NOT_NAT],0,sizeof(struct Flow_key));
    
    /*stat init,for ts using*/
    Flow_stats_init(&entry->stats,rte_get_tsc_cycles());

    /*for dpi using*/
    entry->ifmark   = 0;
    entry->protoapp = 0;
    entry->ext      = NULL;
    entry->dpicnt   = packet_dpi_default_cnt(key.proto);
    
    entry->inport   = mbuf->inport;
    entry->outport  = 0xff;

    /*flow status*/
    entry->status = FIRST_NEW_FLOW;
    /*flow origin is swap or not*/
    entry->isswap[FLOW_NAT_DIR] = isswap;
    entry->hash[FLOW_NAT_DIR] = hash;
    entry->tcpfin = 0;
    entry->used = 1;
    
    mbuf->flow_dir = FLOW_ORIG;
    mbuf->flow_entry = entry;
    mbuf->ctid = entry->ctid;
    mbuf->pktmark = NDPI_DEFAULT_MARK;//packet_dpi_mark_get(entry);

    TAILQ_INSERT_TAIL(&ftabcore->lrulist,entry,tchain);
    
    hlist_add_head(&entry->hchain[FLOW_NAT_DIR],&bucket->root);
    bucket->nums++;
    ftabcore->flownums++;
    FLOW_LOG(DEBUG,FLOW,"NAT FLOW:Create Nat Flow src %u.%u.%u.%u; dst %u.%u.%u.%u; proto %u; srcport %u; dstport %u; hash %u; ctid %u; dir %u; isswap %u; entry %p\n",
                         NIPQUAD(key.ip_src),NIPQUAD(key.ip_dst),key.proto,key.port_src,key.port_dst,hash,entry->ctid,mbuf->flow_dir,isswap,entry);
ret:
    return mbuf->flow_entry;
#else
    mbuf->flow_entry = NULL;
    return mbuf->flow_entry;
#endif
}

struct Flow_entry * Flow_table_lookup(struct rte_mbuf * mbuf)
{
#ifdef FLOW_TABLE_MCORE
    struct Flow_entry * entry;
    uint64_t curtime;
    
    curtime = rte_get_tsc_cycles();

    mbuf->flow_entry = Flow_entry_get(mbuf,curtime);
    
    Flow_Timeout(curtime);
    
#else
    mbuf->flow_entry = NULL;
#endif

    return mbuf->flow_entry;
}

struct Flow_entry * Flow_table_postlookup(struct rte_mbuf *mbuf)
{
#ifdef FLOW_TABLE_MCORE
    int ret = 0;
    uint8_t isswap=0;
    struct Flow_key key = {0};
    struct Flow_entry * entry;
    struct Flow_root  * bucket;
    struct Flow_table_core * ftabcore = Flow_table_get();  

    mbuf->flow_entry = NULL;
    entry = Flow_entry_get_byctid(mbuf->ctid);
    if(mbuf->userdef != NAT_PORT && entry->used == 1){
        get_key_from_packet(mbuf,&key);
        if(unlikely(mbuf->ifnfct != 1)){
            return mbuf->flow_entry;
        }
        get_key_isswap(&key,&isswap);
        if(Flow_entry_cmp(&key,&entry->key[FLOW_NAT_DIR]) == 0){
            mbuf->flow_dir = (isswap != entry->isswap[FLOW_NAT_DIR]);
            mbuf->flow_entry = entry;
            FLOW_LOG(DEBUG,FLOW,"POS FLOW:Lookup Cmp Flow src %u.%u.%u.%u; dst %u.%u.%u.%u; proto %u; srcport %u; dstport %u; hash %u; ctid %u; entry %p; dir %u; isswap %u; mark %u\n",
                                 NIPQUAD(key.ip_src),NIPQUAD(key.ip_dst),key.proto,key.port_src,key.port_dst,entry->hash[0],entry->ctid,entry,mbuf->flow_dir,isswap,entry->protoapp);
            goto ret;
        }        
        ret = Flow_entry_src_cmp(&key,&entry->key[FLOW_NOT_NAT],isswap,entry->isswap[FLOW_NOT_NAT]);
        if(ret == 0 || ret == 2){
            if(hlist_unhashed(&entry->hchain[FLOW_NAT_DIR])){
                Flow_key_init(&entry->key[FLOW_NAT_DIR],&key);
                entry->isswap[FLOW_NAT_DIR]= isswap;
                entry->hash[FLOW_NAT_DIR] = rte_jhash((void *)&key,sizeof(struct Flow_key),0);
                bucket = &ftabcore->bucket[FLOW_NAT_DIR][entry->hash[FLOW_NAT_DIR] & (MAX_FLOW_BUCKET-1)];
                hlist_add_head(&entry->hchain[FLOW_NAT_DIR],&bucket->root);
                bucket->nums++;
                FLOW_LOG(DEBUG,FLOW,"POS FLOW:Create NAT Flow src %u.%u.%u.%u; dst %u.%u.%u.%u; proto %u; srcport %u; dstport %u; hash %u; ctid %u; entry %p; dir 0; isswap %u; mark %u; ret %u\n",
                                     NIPQUAD(key.ip_src),NIPQUAD(key.ip_dst),key.proto,key.port_src,key.port_dst,entry->hash[1],entry->ctid,entry,isswap,entry->protoapp,ret);
            }
            mbuf->flow_dir = FLOW_ORIG; //(isswap != entry->isswap[FLOW_NOT_NAT]);
            FLOW_LOG(DEBUG,FLOW,"POS FLOW:Lookup Smp Flow src %u.%u.%u.%u; dst %u.%u.%u.%u; proto %u; srcport %u; dstport %u; hash %u; ctid %u; entry %p; dir %u; isswap %u; mark %u; ret %u\n",
                                 NIPQUAD(key.ip_src),NIPQUAD(key.ip_dst),key.proto,key.port_src,key.port_dst,entry->hash[1],entry->ctid,entry,mbuf->flow_dir,isswap,entry->protoapp,ret);
            goto ret;
        }
    }
    else if(mbuf->userdef == NAT_PORT && entry->used == 1){
        goto ret;
    }
    
    return mbuf->flow_entry;
    
ret:
    if(entry->tcpfin == 15){
        FLOW_LOG(INFO,FLOW,"TCP DisConnect Delete Flow(%p) Sucess; "
                            "Ogn Packet: src %u.%u.%u.%u; dst %u.%u.%u.%u; proto %d; srcport %u; dstport %u isswap %u "
                            "Nat Packet: src %u.%u.%u.%u; dst %u.%u.%u.%u; proto %d; srcport %u; dstport %u isswap %u "
                            "status %u, ctid %u; appmark %u; dir %u; port mode %u\n", 
                             entry,
                             NIPQUAD(entry->key[FLOW_NOT_NAT].ip_src),
                             NIPQUAD(entry->key[FLOW_NOT_NAT].ip_dst),
                             entry->key[FLOW_NOT_NAT].proto,
                             entry->key[FLOW_NOT_NAT].port_src,
                             entry->key[FLOW_NOT_NAT].port_dst,
                             entry->isswap[FLOW_NOT_NAT],
                             NIPQUAD(entry->key[FLOW_NAT_DIR].ip_src),
                             NIPQUAD(entry->key[FLOW_NAT_DIR].ip_dst),
                             entry->key[FLOW_NAT_DIR].proto,
                             entry->key[FLOW_NAT_DIR].port_src,
                             entry->key[FLOW_NAT_DIR].port_dst,
                             entry->isswap[FLOW_NAT_DIR],
                             entry->status,
                             entry->ctid,
                             entry->protoapp,
                             mbuf->flow_dir,
                             mbuf->userdef);
        Flow_free_entry(ftabcore,entry);
        mbuf->flow_entry = NULL;
    }
    else mbuf->flow_entry = entry;
    
    return mbuf->flow_entry;

#else
    mbuf->flow_entry = NULL;
    return mbuf->flow_entry;
#endif 
}


#if TS_LOG_DEBUG
#define TS_LOG RTE_LOG
#else
#define TS_LOG(l,t,...) do{}while(0)
#endif

static void __Flow_TS(struct rte_mbuf * mbuf)
{
    struct Flow_entry * entry;
    uint64_t curtime,lastime;
    
    if(mbuf->flow_entry == NULL) return;

    curtime    = rte_get_tsc_cycles();
    entry      = (struct Flow_entry *)mbuf->flow_entry;

    //save last time
    lastime = entry->stats.last_count;
    //ts
    //entry->stats.lastbytes[mbuf->flow_dir] += mbuf->data_len;
    if((curtime - entry->stats.curr_count) > pftab->tstime){
        entry->stats.last_count = entry->stats.curr_count;
        entry->stats.curr_count = curtime;
        entry->stats.TS_bytes[0] = entry->stats.lastbytes[0];
        entry->stats.TS_bytes[1] = entry->stats.lastbytes[1];
        if(rte_ring_mp_enqueue(pftab->ts,entry) != 0){
            //enqueue failed recover time
            entry->stats.curr_count = entry->stats.last_count;
            entry->stats.last_count = lastime;
        }
        else{
            entry->stats.totalbytes[FLOW_ORIG]  += entry->stats.lastbytes[FLOW_ORIG];
            entry->stats.totalbytes[FLOW_REPLY] += entry->stats.lastbytes[FLOW_REPLY];
            TS_LOG(DEBUG,TS,"Flow src %u.%u.%u.%u; dst %u.%u.%u.%u; port_src %u; port_dst %u; proto %u; appId = %u; allbytes:%lu, bytes:%u, Rallbytes:%lu, Rbytes:%u\n",
                             NIPQUAD(entry->key[0].ip_src),
                             NIPQUAD(entry->key[0].ip_dst),
                             entry->key[0].port_src,
                             entry->key[0].port_dst,
                             entry->key[0].proto,
                             entry->protoapp,
                             entry->stats.totalbytes[0],
                             entry->stats.lastbytes[0],
                             entry->stats.totalbytes[1],
                             entry->stats.lastbytes[1]);
            //clear zero
            entry->stats.lastbytes[FLOW_ORIG] = 0;
            entry->stats.lastbytes[FLOW_REPLY] = 0;
        }
    }
}

void Flow_TS_bulk(struct rte_mbuf ** mbuf, uint16_t nb_pkts)
{
#ifdef FLOW_TABLE_MCORE
    #ifdef TS_MCORE
    int i;
    if(pftab->ts_flag){
        for(i = 0; i < nb_pkts; i++){
            __Flow_TS(mbuf[i]);
        }
    }
    #endif
#endif
}

void Flow_TS(struct rte_mbuf * mbuf)
{
#ifdef FLOW_TABLE_MCORE
    #ifdef TS_MCORE
    if(pftab->ts_flag){
        __Flow_TS(mbuf);
    }
    #endif
#endif
}

#ifdef FLOW_TABLE_MCORE

MODULE_INIT(Flow_table_init);
MODULE_EXIT(Flow_table_exit);

#endif

