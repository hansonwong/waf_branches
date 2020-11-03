#ifndef FPLOG_H_INCLUDED
#define FPLOG_H_INCLUDED

#include <sys/time.h>
#include <string.h>
#include <stdarg.h>
#include <stdio.h>
#include <syslog.h>
#include <stdint.h>

typedef struct {
#define FP_LOGTYPE_MAIN_PROC  0x00000001
#define FP_LOGTYPE_EXC        0x00000002
#define FP_LOGTYPE_IP         0x00000004
#define FP_LOGTYPE_FRAG       0x00000008
#define FP_LOGTYPE_IPSEC_IN   0x00000010
#define FP_LOGTYPE_IPSEC_OUT  0x00000020
#define FP_LOGTYPE_IPSEC_REPL 0x00000040
#define FP_LOGTYPE_NF         0x00000080
#define FP_LOGTYPE_REASS      0x00000100
#define FP_LOGTYPE_TUNNEL     0x00000200
#define FP_LOGTYPE_NETFPC     0x00000400
#define FP_LOGTYPE_CRYPTO     0x00000800
#define FP_LOGTYPE_VNB        0x00001000
#define FP_LOGTYPE_TAP        0x00002000
#define FP_LOGTYPE_DDOS       0x00004000
#define FP_LOGTYPE_MEM_POOL   0x00008000
#define FP_LOGTYPE_PSD        0x00010000
#define FP_LOGTYPE_DPDKS      0x00020000


	uint32_t type;

#define FP_LOG_EMERG    0  /* system is unusable               */
#define FP_LOG_ALERT    1  /* action must be taken immediately */
#define FP_LOG_CRIT     2  /* critical conditions              */
#define FP_LOG_ERR      3  /* error conditions                 */
#define FP_LOG_WARNING  4  /* warning conditions               */
#define FP_LOG_NOTICE   5  /* normal but significant condition */
#define FP_LOG_INFO     6  /* informational                    */
#define FP_LOG_DEBUG    7  /* debug-level messages             */
	uint8_t level;
	uint8_t mode;
#define FP_LOG_MODE_CONSOLE 0
#define FP_LOG_MODE_SYSLOG  1
#define FP_LOG_MODE_FILE 2
	uint16_t reserved;
	uint32_t ratelimit;
} fp_debug_t;

#define MCORE_DEBUG
#define FP_LOG_DEFAULT FP_LOG_WARNING
#define FP_LOGTYPE_DEFAULT (~0U)
#define LOG_FILE_NAME "log.txt"


#endif // FPLOG_H_INCLUDED
