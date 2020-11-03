/***********************************************************************
 *
 *  Copyright (c) 
 *  All Rights Reserved
 *
 *
 ************************************************************************/
#include <sys/socket.h>
#include <errno.h>

#include "cli.h"
#include "cli_log.h"
#ifdef CLI_CMD_EDIT
#include "cmdedit.h"
#endif



/* global */
char menu_path_buf[MAX_MENU_PATH_LENGTH] = "<NGFW> ";
unsigned char cli_keep_looping=TRUE;
unsigned int exit_on_timeout;

static void process_input(void);

void bdcli_print_welcome(void)
{
   	printf("Bluedon NGFW Cli\n");
}

void bdcli_run(unsigned int exit_timeout)
{

   	cli_log_debug("CLI library entered");
   	exit_on_timeout = exit_timeout;

   	while ( cli_keep_looping ) 
	{
      		process_input();
   	}
   	printf("\nBye bye. Have a nice day!!!\n");
	system("exit");
}

/** Reads an input line from user and processes it.
 *
 */
void process_input() 
{
   	char cmd_line[CLI_MAX_BUF_SZ];
   	int found_handler;
  	/*
    	* Read an input line from the user and process it using
    	* menu and/or cmd code.
    	*/
   	bzero(cmd_line,CLI_MAX_BUF_SZ);

#ifdef CLI_CMD_EDIT
	if (cmdedit_read_input(menu_path_buf, cmd_line) < 0)
	{
		cli_keep_looping = FALSE;
		return;
	}
   
	  // remove the trailing return
	int l = strlen(cmd_line);
	if (l > 0 && cmd_line[l-1] == '\n')
		cmd_line[l-1] = 0;
#else
	printf("%s", menu_path_buf);
	fflush(stdout);
	if (cli_read_string(cmd_line, CLI_MAX_BUF_SZ) != 0)
	{
		cli_keep_looping = FALSE;
		return;
	}
#endif

//   	printf("read =>%s<=\n", cmd_line);

   	if ( strlen(cmd_line) == 0 )
      		return;

   	found_handler = FALSE;

   	if ( !found_handler )
   	{
		if ( cli_process_cmd(cmd_line) == TRUE ) 
		{
         	/* input is command line command */
         	/* no need to do anything in here */
      		}
      		else 
		{
         		printf("unrecognized command %s\n", cmd_line);
      		}
   	}
   	return;
}

#define CLI_BACKSPACE        '\x08'

int cli_read_string(char *buf, int size)
{
	int nchars = 0;
	int ch = 0;
	int ret;

   	memset(buf, 0, size);

	if ((ret = cli_wait_for_input_available()) != 0)
	{
		return ret;
	}

   	/* read individual characters until we get a newline or until
    	* we exceed given buffer size.
    	*/
   	for ( ch = fgetc( stdin );
	ch != '\r' && ch != '\n' && ch != EOF && nchars < (size-1) ;
	ch = fgetc( stdin ) ) 
	{
		if ( ch == CLI_BACKSPACE ) 
		{
			if ( nchars > 0 )
				nchars--;
		} 
		else 
		{
			buf[nchars++] = ch;
		}
	}

	if (ch == EOF)
	{
		printf("EOF detected, terminate login session.\n");
		exit(0);
	}

	buf[nchars] = '\0';

	return ret;
}

int cli_wait_for_input_available()
{
	struct timeval timeout;
   	struct timeval *timeout_ptr=NULL;
   	fd_set readfds;
   	int msgfd=0;
   	ssize_t n;

	if (exit_on_timeout > 0)
	{
		timeout.tv_sec = exit_on_timeout;
		timeout.tv_usec = 0;
		timeout_ptr = &timeout;
	}
   	else
	{
	      	/*
	       * If user has set exitOnIdleTimeout to 0, that means no timeout.  Wait indefinately.
	       */
		timeout_ptr = NULL;
	}

	FD_ZERO(&readfds);
	FD_SET(0, &readfds);

	n = select(msgfd+1, &readfds, NULL, NULL, timeout_ptr);
	if (n == 0)
	{
		printf("session terminated due to idle timeout (%d seconds)\n", exit_on_timeout);
		return 9500;
	}
	else if (n < 0)
   	{
		printf("select interrupted");
		return 9400;
	}
	return 0;
}
