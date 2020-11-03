/*
 * Copyright(c) 2007 BDNS
 */
#ifndef __RFC_H__
#define __RFC_H__

#define MAXRULES 1000 //10000
#define MAXDIMENSIONS 6
#define MAXCHUNKS 8
#define FILTERSIZE 18

#ifndef RFC_PHASE
#define RFC_PHASE  4
#endif

#if (RFC_PHASE != 4) && (RFC_PHASE != 3)
#error RFC_PHASE is 3 or 4
#endif

#include "filter/dheap.h"
#include "filter/fblock.h"
#include "filter/filter.h"

//#define PRINT_MATCH 0
#ifdef PRINT_MATCH
#include <stdio.h>
#endif

#ifndef NIPQUAD
#define NIPQUAD(addr) \
((unsigned char *)&addr)[3], \
	((unsigned char *)&addr)[2], \
	((unsigned char *)&addr)[1], \
	((unsigned char *)&addr)[0]
#endif

struct eq {
  int numrules;
  int first_rule_id;
  int *rulelist;
};

struct range{
  uint32_t low;
  uint32_t high;
};

struct pc_rule{
  uint32_t filtId;
  uint32_t cost;
  struct range field[MAXDIMENSIONS];
};

struct trie_rfc {
	int p0_table[8][65536];                  //phase 0 chunk tables
	int *p1_table[4];               //phase 1 chunk tables
	int *p2_table[2];               //phase 2 chunk tables
	int *p3_table;                  //phase 3 chunk tables
	struct eq p0_eq[8][2*MAXRULES];          //phase 0 chunk equivalence class
	struct eq p1_eq[4][2*MAXRULES];          //phase 1 chunk equivalence class
	struct eq p2_eq[2][2*MAXRULES];          //phase 2 chunk equivalence class
	struct eq p3_eq[2*MAXRULES];             //phase 3 chunk equivalence class
	int p0_neq[8];                           //phase 0 number of chunk equivalence classes
	int p1_neq[4];                           //phase 1 number of chunk equivalence classes
	int p2_neq[2];                           //phase 2 number of chunk equivalence classes
	int p3_neq;                              //phase 3 number of chunk equivalence classes
	struct pc_rule rule[MAXRULES];
	int numrules;
	struct fblock fb;
	struct dheap dheap;
} __rte_cache_aligned;

#define RFC_5BIT_PROTO_INVALID 31
#define RFC_5BIT_PROTO_UNKNOWN 30
#define RFC_5BIT_PROTO_MAX RFC_5BIT_PROTO_UNKNOWN


extern uint8_t rfc_protocomptab[256];
extern volatile int rfc_protocomptab_built;
/* build the protocol 8-to-5-bit compression table */
static inline void rfc_protocomptab_build(void)
{
	/* protocol numbers for ICMP, IGMP, IPV4, TCP, UDP, IPV6, RSVP, GRE,
	 * ESP, AH, OSPF, PIM, VRRP, ISIS, SCTP, UDPLITE */
	static uint8_t proto[]={1,2,4,6,17,41,46,47,50,51,89,103,112,124,132,136};
	uint8_t i;

	memset(rfc_protocomptab, RFC_5BIT_PROTO_UNKNOWN, sizeof(rfc_protocomptab));
	for (i=0; i<ARRAY_SIZE(proto); i++)
		rfc_protocomptab[proto[i]] = i;
	
	rfc_protocomptab_built = 1;
}

/* return a unique value between 0 and RFC_5BIT_PROTO_UNKNOWN-1 for known
   protocols, RFC_5BIT_PROTO_UNKNOWN otherwise */
static inline uint8_t rfc_proto_compress(uint8_t proto)
{
	return rfc_protocomptab[proto];
}

/* build the VR+proto (network order) field based on:
 * inport  and compressed protocol */
static inline uint16_t rfc_make_vrproto(uint16_t vrfid, uint8_t proto)
{
	return ((vrfid<<5)|proto);
}

static inline int rfc_rule_isempty(void *ctx){
	struct trie_rfc *t=(struct trie_rfc *)ctx;
	return !(t->numrules);
}

extern void *rfc_init(void *memstart, uint32_t memsize);
extern void rfc_update(struct FILTER *f, void *user_ctx);
extern void rfc_final(void *user_ctx);
extern int rfc_lookup(void *ctx,
		      uint32_t src,
		      uint32_t dst,
		      uint8_t proto,
		      uint16_t sport,
		      uint16_t dport,
		      uint16_t vrfid,
		      uint16_t inport,
		       void **filterlist,
		      uint32_t *index);
extern void rfc_print_rules(struct trie_rfc *t);
#endif
