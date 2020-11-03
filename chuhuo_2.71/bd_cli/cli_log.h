/***********************************************************************
 *
 *  Copyright (c) 
 *  All Rights Reserved
 *
 *
 ************************************************************************/

#ifndef __BD_LOG_H__
#define __BD_LOG_H__

/*!\enumcliLogLevel
 * \brief Logging levels.
 * These correspond to LINUX log levels for convenience. 
 */

#ifndef LOG_ALERT
#define LOG_ALERT       1       /* action must be taken immediately */
#endif

#ifndef LOG_CRIT
#define LOG_CRIT        2       /* critical conditions */
#endif

#ifndef LOG_ERR
#define LOG_ERR         3       /* error conditions */
#endif

#ifndef LOG_WARNING
#define LOG_WARNING     4       /* warning conditions */
#endif

#ifndef LOG_NOTICE
#define LOG_NOTICE      5       /* normal but significant condition */
#endif

#ifndef LOG_INFO
#define LOG_INFO        6       /* informational */
#endif

#ifndef LOG_DEBUG
#define LOG_DEBUG       7       /* debug-level messages */
#endif

typedef enum
{
   LOG_LEVEL_ERR    = 3, /**< Message at error level. */
   LOG_LEVEL_NOTICE = 5, /**< Message at notice level. */
   LOG_LEVEL_DEBUG  = 7  /**< Message at debug level. */
} cli_log_level;


/*!\enum BdLogDestination
 * \brief identifiers for message logging destinations.
 */
typedef enum
{
   LOG_DEST_STDERR  = 1,  /**< Message output to stderr. */
   LOG_DEST_SYSLOG  = 2,  /**< Message output to syslog. */
   LOG_DEST_TELNET  = 3   /**< Message output to telnet clients. */
} cli_log_destination;


/** Show application name in the log line. */
#define BDLOG_HDRMASK_APPNAME    0x0001 

/** Show log level in the log line. */
#define BDLOG_HDRMASK_LEVEL      0x0002 

/** Show timestamp in the log line. */
#define BDLOG_HDRMASK_TIMESTAMP  0x0004

/** Show location (function name and line number) level in the log line. */
#define BDLOG_HDRMASK_LOCATION   0x0008 
 

/** Default log level is error messages only. */
#define DEFAULT_LOG_LEVEL        LOG_LEVEL_ERR

/** Default log destination is standard error */
#define DEFAULT_LOG_DESTINATION  LOG_DEST_STDERR

/** Default log header mask */
#define DEFAULT_LOG_HEADER_MASK (BDLOG_HDRMASK_APPNAME|BDLOG_HDRMASK_LEVEL|BDLOG_HDRMASK_TIMESTAMP|BDLOG_HDRMASK_LOCATION)


/** Maxmimu length of a single log line; messages longer than this are truncated. */
#define MAX_LOG_LINE_LENGTH      512


#define cli_log_error(args...)  log_log(LOG_ERR, __FUNCTION__, __LINE__, args)
#define cli_log_notice(args...) log_log(LOG_NOTICE, __FUNCTION__, __LINE__, args)
#define cli_log_debug(args...)  log_log(LOG_DEBUG, __FUNCTION__, __LINE__, args)



/** Internal message log function; do not call this function directly.*/
void log_log(cli_log_level level, const char *func, unsigned int line_num, const char *pFmt, ... );

/*Message log initialization.*/
void cli_log_init();
  
/*Message log cleanup.*/
void cli_log_cleanup(void);
  
/* Set process message logging level.*/
void cli_log_set_level(cli_log_level level);

/*Get process message logging level.*/
cli_log_level cli_log_get_level(void);

/* Set process message logging destination.*/
void cli_log_set_destination(cli_log_destination dest);

/** Get process message logging destination.
 * This function gets the logging destination of a process.
 *
 * @return The process message logging destination.
 */
cli_log_destination cli_log_get_destination(void);

/** Set process message log header mask which determines which pieces of
 * info are included in each log line.
 *
 * @param mask (IN) Bitmask of BDLOG_HDRMASK_xxx
 */
void cli_log_set_headermask(unsigned int headerMask);

/** Get process message log header mask.
 *
 * @return The process message log header mask.
 */
unsigned int cli_log_get_headermask(void);


/** indicate first read */
#define BD_SYSLOG_FIRST_READ           -2

/** indicates error */
#define BD_SYSLOG_READ_BUFFER_ERROR    -1

/** indicates last line was read */
#define BD_SYSLOG_READ_BUFFER_END      -3

/** max log buffer length */
#define BD_SYSLOG_MAX_LINE_SIZE        255


/** Legacy method for reading the system log line by line.
 *
 * @param ptr     (IN) Current line to read.
 * @param buffer (OUT) Line that was read.
 * @return new ptr value for next read.
 */
signed int cli_log_read_partial(signed int ptr, char* buffer);

#endif /* __BD_LOG_H__ */
