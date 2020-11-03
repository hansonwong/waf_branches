#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "dpdk_warp.h"
#include "dpdk_frame.h"
#include "bdpi.h"
#include "dpi.h"

#define DPI_LOG DPDK_LOG

struct ndpi_struct_t * ndpi_st;
static struct rte_ring * flowalloc; 

static unsigned int flow_size;

#define NDPI_SYSTEM_MALLOC 1

#ifdef NDPI_SYSTEM_MALLOC

static void * dpi_malloc_wrapper(size_t size)
{
    return malloc(size);
}
static void dpi_free_wrapper(void * ptr)
{
    free(ptr);
}
#else

static void * dpi_malloc_wrapper(size_t size)
{
    return rte_malloc(NULL,size,RTE_CACHE_LINE_SIZE);
}

static void  dpi_free_wrapper(void * ptr)
{
    rte_free(ptr);
}

#endif

int dpi_flow_node_free(void * dpinode)
{
    return bdpi_flow_free(&dpinode);
}

static void * dpi_flow_alloc(void)
{
    void * flow = NULL;
    if(rte_ring_mc_dequeue(flowalloc,&flow))
        return NULL;
    return flow;
}

static int dpi_flow_free(void * flow)
{
    return rte_ring_mp_enqueue(flowalloc,flow);
}

uint32_t packet_dpi_mark_get(struct Flow_entry * entry)
{
    if(entry->ifmark == 0){
        if(entry->stats.totalpackets <= entry->dpicnt)
            return NDPI_DEFAULT_MARK;
        else {
            return 0;
        }
    }
    else 
        return entry->protoapp;  
}

uint8_t packet_dpi_default_cnt(uint8_t proto)
{
    switch(proto){
        case 6:
            return NDPI_TCP_PKTS;
        case 17:
            return NDPI_UDP_PKTS;
        case 1:
            return NDPI_ICMP_PKTS;
        default:
            return 0;
            
    }
}

static int none_packet_analyzer(__attribute__((unused)) struct rte_mbuf * mbuf)
{
    return 0;
}

static int dpi_packet_analyzer(struct rte_mbuf *mbuf)
{
    int ret;
    uint32_t  appid;
    uint16_t packetlen;
    void * flow;
    struct ipv4_hdr * payload;
    struct Flow_entry * entry;
    char appname[64];

    if(mbuf->flow_entry == NULL){
        return 0;
    }
    entry = (struct Flow_entry *)mbuf->flow_entry;
    if(entry->ifmark || !entry->used)
        return 0;

    payload = rte_pktmbuf_mtod_network(mbuf,struct ipv4_hdr *);
    packetlen = rte_be_to_cpu_16(payload->total_length);
    if(packetlen > (mbuf->pkt_len + mbuf->mac_header - mbuf->network_header)){
        DPI_LOG(WARNING,DPI,"Packet src %u.%u.%u.%u; dst %u.%u.%u.%u; port_src %u; port_dst %u; proto %u; exception packetlen %u, mbuf len %u, nethdrlen %u\n",
                         NIPQUAD(mbuf->tuple.ipv4.ip_src),
                         NIPQUAD(mbuf->tuple.ipv4.ip_dst),
                         mbuf->tuple.ipv4.port_src,
                         mbuf->tuple.ipv4.port_dst,
                         mbuf->tuple.ipv4.proto,packetlen,mbuf->pkt_len,mbuf->network_header-mbuf->mac_header);
        return 0;
    }
    if(entry->ext == NULL){

        if(bdpi_flow_alloc(&entry->ext) < 0){
            DPI_LOG(ERR,DPI,"alloc ndpi flow struct fail\n");
            return -1;
        }
    }
    ret = bdpi_packet_analyzer(entry->ext,
                               (const uint8_t *)payload,
                                packetlen,
                                rte_lcore_id(),
                                &appid);

    if((appid != 0) ||
       (appid == 0 && ret != 0)){
        // mark the flow
        entry->ifmark = 1;
        entry->protoapp = appid;
        // mbuf->pktmark   = entry->protoapp;
        bdpi_flow_free(&entry->ext);
        bdpi_getappname_by_appid(appid,appname,64);
        DPI_LOG(DEBUG,DPI,"Detect src %u.%u.%u.%u; dst %u.%u.%u.%u; port_src %u; port_dst %u; proto %u; AppProtocol = %d AppName = %s\n",
                         NIPQUAD(mbuf->tuple.ipv4.ip_src),
                         NIPQUAD(mbuf->tuple.ipv4.ip_dst),
                         mbuf->tuple.ipv4.port_src,
                         mbuf->tuple.ipv4.port_dst,
                         mbuf->tuple.ipv4.proto,
                         appid,appname);
        return 0;
    }
    DPI_LOG(DEBUG,DPI,"Not Detect src %u.%u.%u.%u; dst %u.%u.%u.%u; port_src %u; port_dst %u; proto %u; AppProtocol %d; AppName = NULL; Packet mark %u\n",
                         NIPQUAD(mbuf->tuple.ipv4.ip_src),
                         NIPQUAD(mbuf->tuple.ipv4.ip_dst),
                         mbuf->tuple.ipv4.port_src,
                         mbuf->tuple.ipv4.port_dst,
                         mbuf->tuple.ipv4.proto,
                         appid,
                         mbuf->pktmark);
    return 0;
}

typedef int (*DpiAnalyzer)(struct rte_mbuf *);

DpiAnalyzer func[2] = {none_packet_analyzer,dpi_packet_analyzer};

int packet_dpi_analyzer(struct rte_mbuf *mbuf)
{
#ifdef NDPI_MCORE
    return func[ndpi_st->ndpi_flag[NDPI_SWITCH]](mbuf);
#else
    return 0;
#endif
}


static int dpi_init(__attribute__((unused))void * __sysinfo)
{
    int ret, i, size,allocqsize;
    uint8_t * flow;
    uint32_t lcoreid;
    struct ndpi_struct_t * ndpist;
    struct system_info   * sysinfo;

    
    static struct bdpi_init_params initbdpi;

    initbdpi.is_ext_open = 1;
    initbdpi.flowalloctype = 1;
    initbdpi.extlibpath = "/home/ng_platform/bd_dpdk_warper/config/bdapp";
    initbdpi.logconf    = "/home/ng_platform/bd_dpdk_warper/config/bdpi.conf";
    initbdpi.logtype    = "bdpilog";
    initbdpi._malloc = dpi_malloc_wrapper;
    initbdpi._free = dpi_free_wrapper;
    initbdpi.flowalloc = dpi_flow_alloc;
    initbdpi.flowfree = dpi_flow_free;
    initbdpi.tcpcount = NDPI_TCP_PKTS;
    initbdpi.udpcount = NDPI_UDP_PKTS;
    initbdpi.othercount = NDPI_OTHER_PKTS;
    initbdpi.core_mask = 0;
    
    RTE_LCORE_FOREACH_SLAVE(lcoreid){
        initbdpi.core_mask |= (1 << lcoreid);
    }

    if(bdpi_init(&initbdpi)){
        rte_exit(EXIT_FAILURE,"NDPI:Data Plane ndpi 0.1: global structure initialization failed.\n");
    }
    flow_size = RTE_CACHE_LINE_ROUNDUP((initbdpi.flowsize));
    //ndpi_dump_protocols(ndpi_struct);
    
    size =  flow_size * MAX_NDPI_FLOW + sizeof(struct ndpi_struct_t);
    ndpist = (struct ndpi_struct_t *)rte_zmalloc(NDPI_STRUCT_NAME, size, RTE_CACHE_LINE_SIZE);
    if(ndpist == NULL){
        bdpi_exit();
        rte_exit(EXIT_FAILURE, "alloc ndpi memory fail\n");
    }
    
    snprintf(ndpist->name,sizeof(ndpist->name),NDPI_STRUCT_NAME);

    ndpist->dpibuf = (uint8_t *)(ndpist + 1);
    
    ndpist->allocq = rte_ring_create("NDPI_ALLOC_QUEUE",MAX_NDPI_FLOW+1,SOCKET_ID_ANY,0);
    if(ndpist->allocq == NULL){
        rte_free(ndpist);
        bdpi_exit();
        rte_exit(EXIT_FAILURE,"create ndpi mem alloc queue failed\n");
    }
    flowalloc = ndpist->allocq;
    allocqsize = rte_ring_get_memsize(MAX_NDPI_FLOW+1);
    printf("%u   %u\n",allocqsize,flow_size);
    flow = ndpist->dpibuf;
    for(i = 0; i < MAX_NDPI_FLOW; i++){
        if(dpi_flow_free((void *)flow)){
            printf("dpi init alloc queue failed[%d]\n",i);
            break;
        }
        flow = flow + flow_size;
    }
    rte_spinlock_init(&ndpist->ndpilock);
    
    sysinfo = (struct system_info *)__sysinfo;
    sysinfo->ndpist = ndpist;
    ndpi_st = ndpist;

    printf("DPI:The sizeof %s is %dM,alloc queue is %dB,flow size %uB\n",
        ndpist->name, size / (1024 * 1024), allocqsize,flow_size);

    return 0;
}

static int dpi_exit(__attribute__((unused))void * __sysinfo)
{
    struct system_info * sysinfo = (struct system_info *)__sysinfo;
    bdpi_exit();
#if 0
    if(sysinfo->ndpist->allocq != NULL){
        rte_ring_free(sysinfo->ndpist->allocq);
        sysinfo->ndpist->allocq = NULL;
    }
#endif
    if(sysinfo->ndpist != NULL){
        rte_free(sysinfo->ndpist);
        sysinfo->ndpist = NULL;
    }
    return 0;
}
#ifdef NDPI_MCORE
MODULE_INIT(dpi_init);
MODULE_EXIT(dpi_exit);
#endif

