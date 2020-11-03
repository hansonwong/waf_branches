
#ifndef __LOG_H__
#define __LOG_H__

#include <stdint.h>
#include <stdio.h>
#include <stdarg.h>

/* Can't use 0, as it gives compiler warnings */
#define TSE_LOG_EMERG     1U  /**< System is unusable.               */
#define TSE_LOG_ALERT     2U  /**< Action must be taken immediately. */
#define TSE_LOG_CRIT      3U  /**< Critical conditions.              */
#define TSE_LOG_ERR       4U  /**< Error conditions.                 */
#define TSE_LOG_WARNING   5U  /**< Warning conditions.               */
#define TSE_LOG_NOTICE    6U  /**< Normal but significant condition. */
#define TSE_LOG_INFO      7U  /**< Informational.                    */
#define TSE_LOG_DEBUG     8U  /**< Debug-level messages.             */

#define TSE_LOG_DEFAULT TSE_LOG_WARNING

#define TSE_LOGTYPE_ADMIN     0x00000001
#define TSE_LOGTYPE_MONITOR   0x00000002
#define TSE_LOGTYPE_PACKET    0x00000004
#define TSE_LOGTYPE_CONNECT   0x00000008
#define TSE_LOGTYPE_NFQ       0x00000010
#define TSE_LOGTYPE_MAIN      0x00000020
#define TSE_LOGTYPE_EXCE      0x00000040


#define TSE_LOGMODE_CONSOLE   0
#define TSE_LOGMODE_SYSLOG    1

/** The rte_log structure. */
struct Tse_logs {
	uint32_t type;  /**< Bitfield with enabled logs. */
	uint32_t level; /**< Log level. */
	uint32_t mode;  /**< output mode,file or console*/
	FILE *file;     /**< Pointer to current FILE* for logs. */
};

/** Global log informations */
extern struct Tse_logs tselogs;

void Tse_syslog(const char *fmt, ...);


#define TSE_LOG(l, t, fmt, args...)                                       \
    do {                                                                  \
        if (l <= tselogs.level && (TSE_LOGTYPE_##t) & tselogs.type) {     \
            if (tselogs.mode == TSE_LOGMODE_CONSOLE)                      \
                printf(#t "-" #l ": " fmt, ## args);                      \
            else                                                          \
                Tse_syslog(#t "-" #l ": " fmt, ## args);                  \
        }                                                                 \
    } while(0)


void TseSetLogLevel(unsigned lev);
void TseSetLogMode(int mode);
void TseSetLogFile(const char * file);
void TseSetLogType(int type);
void TseUnLogType(int type);
void TseSetLogAllType();


#endif /*__LOG_H__*/


