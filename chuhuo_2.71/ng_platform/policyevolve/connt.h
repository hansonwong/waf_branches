#ifndef __CONNT_H__

#define __CONNT_H__

#include "thread.h"
#include "tse.h"

#define MAX_RECV_MSG_BUF 8192

#define MAX_CT_HASH_BUCKET  65536
#define MAX_CT_HASH_NODE    524288

enum TseNFIpConntrackDir
{
	TSE_IP_CT_DIR_ORIGINAL,
	TSE_IP_CT_DIR_REPLY,
	TSE_IP_CT_DIR_MAX
};

typedef struct TseNFct_ {
	PacketTuple orig;
	PacketTuple reply;
	struct hlist_node origchain;
	struct hlist_node replychain;
}TseNFct;

typedef struct TseNFctTable_ {
	uint32_t entries;
	uint32_t entries_used;
	uint32_t buckets;
	uint32_t newct;
	uint32_t delct;
	uint32_t errct;
	struct hlist_head cthlist[TSE_IP_CT_DIR_MAX][MAX_CT_HASH_BUCKET];
	MemManage * ctbuff;
}TseNFctTable;

void NFctModuleRegister(void);
TseNFctTable * CreateCtTable();
void FreeCtTable(TseNFctTable * nfct);
int RunNFctDoCT(ThreadPool * tpool);


#endif /*__CONNT_H__*/



