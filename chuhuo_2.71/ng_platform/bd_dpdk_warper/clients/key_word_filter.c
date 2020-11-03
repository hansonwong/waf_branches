#include <dpdk_warp.h>
#include "dpdk_frame.h"

struct system_info  *sysinfo;

int main(int argc, char *argv[])
{
	if(argc != 2) {
		printf("usage:./key_word_filter on or ./key_word_filter off or ./key_word_filter off status\n");
		return -1;
	}	
	
	sysinfo=get_dpdkshm((char*)"key_word_filter", (char*)"program1");
	if(!sysinfo) {
		printf("get sharemeory fail\n");
		exit(-1);
	}

	if(!strcmp(argv[1], "on")) {
		printf("key_word_filter on\n");
		sysinfo->key_word_filter = 1;	
	}
	else if(!strcmp(argv[1], "off")) {
		printf("key_word_filter off\n");
		sysinfo->key_word_filter = 0;
	}if(!strcmp(argv[1], "status")){
		printf("key_word_filter = %d\n", sysinfo->key_word_filter);	
	}
	else
		printf("usage:./key_word_filter on or ./key_word_filter off or ./key_word_filter off status\n");

	

	return 0;
}

