#ifndef __DPI_H__
#define __DPI_H__

#include "dpdk_warp.h"
#include "flow.h"
#include "dpdk_config.h"

#define NDPI_STRUCT_NAME "SERVER_NDPI_STRUCT"

#define NDPI_DEFAULT_MARK 0x000fffff

#define NDPI_UDP_PKTS   8
#define NDPI_TCP_PKTS   10
#define NDPI_OTHER_PKTS 5
#define NDPI_ICMP_PKTS  1


#define NDPI_SWITCH      0
#define NDPI_GUESS_PROTO 1
struct ndpi_struct_t {
    char name[32];
    uint16_t  ndpi_flag[2];
    rte_spinlock_t ndpilock;
    struct rte_ring * allocq;
    uint8_t * dpibuf;
}__rte_cache_aligned;


int dpi_flow_node_free(void * dpinode);
int packet_dpi_analyzer(struct rte_mbuf *mbuf);
uint8_t packet_dpi_default_cnt(uint8_t protocol);
uint32_t packet_dpi_mark_get(struct Flow_entry * entry);

#endif


