#ifndef __DPDK_WARP_H
#define __DPDK_WARP_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <stdarg.h>
#include <inttypes.h>
#include <inttypes.h>
#include <sys/queue.h>
#include <errno.h>
#include <netinet/ip.h>

#include <rte_config.h>
#include <rte_common.h>
#include <rte_memory.h>
#include <rte_memzone.h>
#include <rte_tailq.h>
#include <rte_eal.h>
#include <rte_byteorder.h>
#include <rte_launch.h>
#include <rte_per_lcore.h>
#include <rte_lcore.h>
#include <rte_branch_prediction.h>
#include <rte_atomic.h>
#include <rte_ring.h>
#include <rte_log.h>
#include <rte_debug.h>
#include <rte_mempool.h>
#include <rte_memcpy.h>
#include <rte_mbuf.h>
#include <rte_interrupts.h>
#include <rte_pci.h>
#include <rte_ethdev.h>
#include <rte_byteorder.h>
#include <rte_malloc.h>
#include <rte_fbk_hash.h>
#include <rte_string_fns.h>

#include <rte_spinlock.h>
#include <rte_rwlock.h>
#include <rte_errno.h>
#ifdef RTE_MACHINE_CPUFLAG_SSE4_2
#include <rte_hash_crc.h>
#define RTE_JHASH     		rte_hash_crc
#define RTE_JHASH_4BYTE	rte_hash_crc_4byte
#else
#include <rte_jhash.h>
#define RTE_JHASH      		rte_jhash
#define	RTE_JHASH_4BYTE	rte_jhash_1word
#endif

#include <rte_cycles.h>
#include <rte_ether.h>
#include <rte_ip.h>
#include <rte_udp.h>
#include <rte_tcp.h>
#include <rte_icmp.h>

//#define ntohs(x) rte_be_to_cpu_16(x)
//#define ntohl(x) rte_be_to_cpu_32(x) 

#endif
