
#ifndef __DPDK_CONFIG_H__
#define __DPDK_CONFIG_H__

#define RTE_LOGTYPE_PLATFORM RTE_LOGTYPE_USER1
#define RTE_LOGTYPE_FLOW     RTE_LOGTYPE_USER2
#define RTE_LOGTYPE_TS       RTE_LOGTYPE_USER3
#define RTE_LOGTYPE_DPI      RTE_LOGTYPE_USER4

/***************************************************/
/*dpdk frame*/
#define DPDK_LOG_DEBUG 0  // 1

/***************************************************/
/*flow table*/

#define FLOW_TABLE_MCORE 1    

#define FLOW_LOG_DEBUG 0  // 1

#define MAX_FLOW_BUCKET  131072  //must be 2^n
#define MAX_BUCKET_ENTRY 4       //
#define MAX_FLOW_ENTRY   524288  //MAX_FLOW_BUCKET *  MAX_BUCKET_ENTRY

#define MAX_LCORE_NUM   32

#define MAX_FLOW_TIMEOUT 30    //flow timeout

#define MAX_TIMEOUT_NUMS 16    //max processing timeout entries

/***************************************************/
/* TS */
#define TS_MCORE 1

#define TS_LOG_DEBUG 0     // 1

#define MAX_TS_TIMEOUT   3     //ts timeout
#define MAX_TS_QUEUE_NUM 1024  //ts queue size


/***************************************************/
/*NDPI*/
#define NDPI_MCORE 1

#define DPI_LOG_DEBUG 0  // 1
#define MAX_NDPI_FLOW 65535    //65535 dpiflow is about 172M


/***************************************************/
/*ping agent*/
//#define PING_MCORE 0

#define PING_LOG_DEBUG 0 // 1

#endif

