/***********************************************************************
 *
 *  Copyright (c) 
 *  All Rights Reserved
 *
 ************************************************************************/

/*!\file cli.h
 * \brief internal header file for CLI library.
 */
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <stdlib.h>
//add for md5 encrypt
#include<openssl/md5.h>
//add for mysql
#include "mysql.h"


#ifndef TRUE
#define TRUE  1
#endif

#ifndef FALSE
#define FALSE 0
#endif


#ifndef NULL
#define	NULL 0
#endif


/** The amount of idle time, in seconds, before consoled exits.
 * If 0, then no timeout.
 */
#define CONSOLED_EXIT_ON_IDLE_TIMEOUT  600


/** Max length of a single line of input */
#define CLI_MAX_BUF_SZ   256

#define BUFLEN_32       32    //!< buffer length 32
#define BUFLEN_64       64    //!< buffer length 64
#define BUFLEN_256      256   //!< buffer length 256


/** The amount of time, in seconds, of idle-ness before timing out the CLI session. */
extern unsigned int exit_on_timeout;

/** Max length of menuPathBuf */
#define MAX_MENU_PATH_LENGTH   1024

/** Global string buffer that displays where we are in the menu hierarchy. */
extern char menu_path_buf[MAX_MENU_PATH_LENGTH];

/** Global boolean to decide whether CLI should keep running. */
extern unsigned char cli_keep_looping;

/** Print a message identifying the modem.
 */
void bdcli_print_welcome(void);


/** Main entry point into the CLI library.
 *
 * @param exitOnIdleTimeout (IN) The amount of time, in seconds, of idle-ness before
 *                               timing out.
 */
void bdcli_run(unsigned int exit_on_timeout);

/** Check cmdLine against the CLI cmd table.
 *
 * @param cmdLine (IN) command line from user.
 *
 * @return TRUE if cmdLine was a CLI command that was processed by
 * this function.
 */
unsigned char cli_process_cmd(const char *cmd_line);

/** Wait for the specified amount of time for input to be available on stdin.
 *  This function will also return if a signal was received.
 *
 *
 * @return 0 if input becomes available.
 *         CMSRET_TIMED_OUT if user stops typing for the exit-on-idle number of seconds.
 *         CMSRET_OP_INTR if input was interrupted by a signal.
 */
int cli_wait_for_input_available(void);

/** Read a line from standard input.
 *
 * @param buf (OUT) buffer to hold the text read.
 * @param size (IN) Size of the buffer.
 *
 * @return 0 if input was read.
 *         9500 if user stops typing for the exit-on-idle number of seconds.
 *         9400 if input was interrupted by a signal.
 */
int cli_read_string(char *buf, int size);

/* functions defined in cli_util.c */
unsigned char cli_isMacAddress(char *addr);
unsigned char cli_isIpAddress(const char *addr);
unsigned char cli_isNumber(const char *buf);
unsigned char cli_isValidIdleTimeout(const char *timeout);
