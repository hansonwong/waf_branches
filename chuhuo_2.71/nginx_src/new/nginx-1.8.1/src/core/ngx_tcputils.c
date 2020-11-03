#include <ngx_config.h>
#include <ngx_core.h>

struct ipaddr {
    union {
        uint64_t addr64[2];
        uint32_t addr32[4];
        uint16_t addr16[8];
        uint8_t  addr8[16];
    } __ipa_u_;
#define addr64 __ipa_u_.addr64
#define addr32 __ipa_u_.addr32
#define addr16 __ipa_u_.addr16
#define addr8  __ipa_u_.addr8
};

typedef enum {
    IP_LESSER = -1,
    IP_EQUAL,
    IP_GREATER,
} IP_CODE;

/*
 * Compare 2 ip address structures, return whether ip_1
 * is greater than, less than or equal too ip_2.
 */
static inline int
ip_compare(struct ipaddr *ip_1, struct ipaddr *ip_2)
{
    /* Profiling tests show that 32 bit comparisons are
     * wayyy faster on 32 bit platforms than the 64 bit
     * variants.  */
#ifndef __x86_64__
    if (ip_1->addr32[0] < ip_2->addr32[0])
        return IP_LESSER;
    if (ip_1->addr32[0] > ip_2->addr32[0])
        return IP_GREATER;
    if (ip_1->addr32[1] < ip_2->addr32[1])
        return IP_LESSER;
    if (ip_1->addr32[1] > ip_2->addr32[1])
        return IP_GREATER;
    if (ip_1->addr32[2] < ip_2->addr32[2])
        return IP_LESSER;
    if (ip_1->addr32[2] > ip_2->addr32[2])
        return IP_GREATER;
    if (ip_1->addr32[3] < ip_2->addr32[3])
        return IP_LESSER;
    if (ip_1->addr32[3] > ip_2->addr32[3])
        return IP_GREATER;
#else
    if (ip_1->addr64[0] < ip_2->addr64[0])
        return IP_LESSER;
    if (ip_1->addr64[0] > ip_2->addr64[0])
        return IP_GREATER;
    if (ip_1->addr64[1] < ip_2->addr64[1])
        return IP_LESSER;
    if (ip_1->addr64[1] > ip_2->addr64[1])
        return IP_GREATER;
#endif

    return IP_EQUAL;
}
struct pseudo_hdr
{
    struct ipaddr srcaddr;
    struct ipaddr dstaddr;
    uint8_t zero;
    uint8_t protocol;
    uint16_t len;
};

// static uint16_t
// checksum(uint16_t *addr, struct pseudo_hdr *pseudo, unsigned len)
// {
//     uint32_t sum = 0;

//     if (pseudo != NULL)
//     {
//         uint16_t *p16 = (uint16_t *)pseudo;

//         sum += p16[0];
//         sum += p16[1];
//         sum += p16[2];
//         sum += p16[3];
//         sum += p16[4];
//         sum += p16[5];
//         sum += p16[6];
//         sum += p16[7];
//         sum += p16[8];
//         sum += p16[9];
//         sum += p16[10];
//         sum += p16[11];
//         sum += p16[12];
//         sum += p16[13];
//         sum += p16[14];
//         sum += p16[15];
//         sum += p16[16];
//         sum += p16[17];
//     }

//     while (len > 1)
//     {
//         sum += *addr++;
//         len -= 2;
//     }

//     if (len == 1)
//         sum += *(unsigned char *) addr;

//     sum = (sum >> 16) + (sum & 0xffff);
//     sum += (sum >> 16);

//     return ~sum;
// }



char *
sub_string(char *str, int start, int end) {
    static char * st = NULL;
    int i = start, j = 0;
    st ? free(st) : 0;
    st = (char *) malloc(sizeof(char) * (end - start + 1));
    while (i < end) {
        st[j++] = str[i++];
    }
    st[j] = '\0';
    return st;
}




// // 过滤掉非tcp的数据包
// static ngx_int_t
// ngx_tcputils_filter_tcp(u_char *raw_packet)
// {
//     return -1;
// }

// 初始化内部数据包，会过滤掉非tcp包
ngx_tcputils_packet_t *
ngx_tcputils_packet_init(ngx_cycle_t *cycle, struct rte_mbuf *m)
{
    ngx_tcputils_packet_t *ret_packet;
    u_char *pdata;
    struct ether_hdr *ethp;
    struct iphdr *ipp;
    struct tcphdr *tcpp;

    ret_packet = NULL;
    pdata = rte_pktmbuf_mtod(m, u_char *);
    ethp = (struct ether_hdr *)pdata;

    // 非ip包
    if (ethp->ether_type != 8)
    {
        dpdk_enqueue(ngx_client_waf, m);
        return NULL;
    }

    ipp = (struct iphdr *)(pdata + sizeof(struct ether_hdr));
    // not tcp packet
    if (ipp->protocol != 0x06)
    {
        dpdk_enqueue(ngx_client_waf, m);
        return NULL;
    }

    tcpp = (struct tcphdr *)(pdata + sizeof(struct ether_hdr) + sizeof(struct iphdr));

    ret_packet = ngx_calloc(sizeof(ngx_tcputils_packet_t), cycle->log);
    ret_packet->m = m;
    ret_packet->pdata = pdata;
    ret_packet->ethp = ethp;
    ret_packet->ipp = ipp;
    ret_packet->tcpp = tcpp;

    return ret_packet;

}


void
ngx_tcputils_test_regex(void)
{
    // ngx_regex_compile_t rc;
    // ngx_int_t n;

    // ngx_memzero(&rc, sizeof(ngx_regex_compile_t));


    // n = ngx_regex_compile(&rc);
    regmatch_t pm[4];
    regex_t preg;
    char *pattern = "(href\\ *=\\ *\\\")([^\\\"]*)(\\\")"; //匹配串
    char
    *file =
        "<a href=\"http://www.awaysoft.com\">Awaysoft.com</a><a href=\"http://www.awaysoft2.com\">Awaysoft2.com</a><a href=\"http://www.awaysoft3.com\">Awaysoft.com3</a>",
        *st; //被匹配串

    if (regcomp(&preg, pattern, REG_EXTENDED | REG_NEWLINE) != 0) { //编译正则表达式
        fprintf(stderr, "Cannot regex compile!");
        exit(-1);
    }
    st = file;

    regexec(&preg, st, 4, pm, REG_NOTEOL);
    fprintf(stderr, "%s\n", sub_string(st, pm[0].rm_so, pm[0].rm_eo));
    fprintf(stderr, "%s\n", sub_string(st, pm[1].rm_so, pm[1].rm_eo));
    fprintf(stderr, "%s\n", sub_string(st, pm[2].rm_so, pm[2].rm_eo));

//  while (st && regexec(&preg, st, 4, pm, REG_NOTEOL) != REG_NOMATCH) { //开始匹配
//      printf("%s\n", sub_string(st, pm[2].rm_so, pm[2].rm_eo));
//      st = &st[pm[3].rm_eo]; //转到下一个匹配的初始位置
//  }

}





