/*
 * Copyright(c) 2007 BDNS
 */
#ifndef _FILTER_H_
#define _FILTER_H_

#include<stdio.h>
#include<stdlib.h>
#include<stdint.h>
#include<string.h>

#define ADRLEN          32
#define SRCADRLEN       ADRLEN/8

#define MAX_STRIDE		8

struct FILTER {
	uint32_t filtId;
	uint32_t cost;           /* host order */

	uint32_t dst;            /* network order */
	uint32_t dst_mask;       /* network order */

	uint32_t src;            /* network order */
	uint32_t src_mask;       /* network order */

	uint8_t  dst_plen;
	uint8_t  src_plen;
	uint8_t  ul_proto;
#define FILTER_ULPROTO_ANY    255
	
	uint16_t vrfid;          /* host order */

	uint16_t srcport_min;    /* network order */
	uint16_t srcport_max;    /* network order */
	uint16_t dstport_min;    /* network order */
	uint16_t dstport_max;    /* network order */

	uint16_t inport_min;
	uint16_t inport_max;
};

#ifndef ARRAY_SIZE
#define ARRAY_SIZE(x) (sizeof(x) / sizeof((x)[0]))
#endif

#ifndef likely
#define likely(x)       __builtin_expect(!!(x), 1)
#endif

#ifndef unlikely
#define unlikely(x)     __builtin_expect(!!(x), 0)
#endif

#ifndef ntohs
#define ntohs(x)    ((x) >> 8) | ((x) << 8) 
#endif
#ifndef htons
#define htons(x)    ((x) >> 8) | ((x) << 8) 
#endif
#ifndef ntohl
#define ntohl(x)   ( ( \
	(((uint32_t)(x) & (uint32_t)0x000000ffUL) << 24) |		\
	(((uint32_t)(x) & (uint32_t)0x0000ff00UL) <<  8) |		\
	(((uint32_t)(x) & (uint32_t)0x00ff0000UL) >>  8) |		\
	(((uint32_t)(x) & (uint32_t)0xff000000UL) >> 24)))
#endif
#endif
