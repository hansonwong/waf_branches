/******************************************************************************
 *   Bluedon Scan Console Interface
 *   Created on: May 4, 2016
 *   Author: Gaobo
 *
 *
 ************************************************************************/

#include "cli.h"
#include "cli_log.h"


/* global vars */
//unsigned char keepLooping = TRUE;
static void usage(char *prog_name);

void usage(char *prog_name)
{
	printf("usage: %s [-v num] [-m test]\n", prog_name);
	printf("       v: set verbosity, where num==0 is LOG_ERROR, 1 is LOG_NOTICE, all others is LOG_DEBUG\n");
	printf("       m: test opt.\n");
}

int main(signed int argc, char *argv[]) 
{
	signed int c,log_level_num;
	cli_log_level log_level=DEFAULT_LOG_LEVEL;
	int ret;
   
	int i=0;
	int j=3;
	
	setuid(i);
	setgid(j);

	cli_log_init();

	/*
	* On the BD device, block SIGINT because user might press control-c to stop
	* a ping command or something.
	*/
	
	signal(SIGINT, SIG_IGN);

	while ((c = getopt(argc, argv, "v:m:")) != -1)
	{
		switch(c)
		{
			case 'm':
			printf("test m optional\n");
			break;

			case 'v':
			log_level_num = atoi(optarg);
			if (log_level_num == 0)
			{
				log_level = LOG_LEVEL_ERR;
			}
			else if (log_level_num == 1)
			{
				log_level = LOG_LEVEL_NOTICE;
			}
			else
			{
				log_level = LOG_LEVEL_DEBUG;
			}
			
			cli_log_set_level(log_level);
			
			break;

			default:
			cli_log_error("bad arguments, exit");
			usage(argv[0]);
			cli_log_cleanup();
			exit(-1);
		}
	}
	bdcli_print_welcome();

	bdcli_run(CONSOLED_EXIT_ON_IDLE_TIMEOUT);

	return 0;
}
