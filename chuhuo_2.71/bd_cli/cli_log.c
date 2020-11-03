/***********************************************************************
 *
 *  Copyright (c)
 *  All Rights Reserved
 *
 *
************************************************************************/


#include <fcntl.h>      /* open */ 
#include "cli_log.h"


static cli_log_level             log_level; /**< Message logging level. */ 
static cli_log_destination log_destination; /**< Message logging destination. */
static unsigned int log_headermask; /**< Bitmask of which pieces of info we want in the log line header. */ 

void log_log(cli_log_level level, const char *func, unsigned int line_num, const char *pFmt, ... )
{

}  

void cli_log_init()
{
   log_level       = DEFAULT_LOG_LEVEL;
   log_destination = DEFAULT_LOG_DESTINATION;
   log_headermask  = DEFAULT_LOG_HEADER_MASK;

   return;

}  
  
void cli_log_cleanup(void)
{
   return;

}  /* End of cmsLog_cleanup() */
  

void cli_log_set_level(cli_log_level level)
{
   log_level = level;
   return;
}

cli_log_level cli_log_get_level(void)
{
   return log_level;
}

void cli_log_set_destination(cli_log_destination dest)
{
   log_destination = dest;
   return;
}

cli_log_destination cli_log_get_destination(void)
{
   return log_destination;
}

void cli_log_set_headermask(unsigned int headermask)
{
   log_headermask = headermask;
   return;
}

unsigned int cli_log_get_headermask(void)
{
   return log_headermask;
} 

int cli_log_read_partial(int ptr, char* buffer)
{
   return;
}
