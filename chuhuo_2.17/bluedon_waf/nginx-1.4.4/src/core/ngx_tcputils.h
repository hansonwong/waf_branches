#ifndef _NGX_TCPUTILS_H_INCLUDED_
#define _NGX_TCPUTILS_H_INCLUDED_

#include <ngx_config.h>
#include <ngx_core.h>

typedef struct
{
    struct rte_mbuf *m;
    u_char *pdata;
    struct ether_hdr *ethp;
    struct iphdr *ipp;
    struct tcphdr *tcpp;
} ngx_tcputils_packet_t;


// 初始化内部数据包，会过滤掉非tcp包
ngx_tcputils_packet_t *ngx_tcputils_packet_init(ngx_cycle_t *cycle, struct rte_mbuf *m);



// 过滤掉非指定端口的数据包
ngx_int_t ngx_tcputils_filter_ports(ngx_cycle_t *cycle, u_char *raw_packet);





// test regex
void ngx_tcputils_test_regex(void);




#endif