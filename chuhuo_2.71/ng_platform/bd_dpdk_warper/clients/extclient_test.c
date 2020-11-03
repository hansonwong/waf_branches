#include<stdio.h>
#include<stdlib.h>
#include<stdint.h>
#include "clientext_queue.h"

static struct ring_queue  *extqueue;
int main(void) {
	#define  EXT_CLIENT_SHM_ID  0xa769
	#define  EXT_CLIENT_BUFFSIEZ  1600*1024
	#define  EXT_CLIENT_NODESIZE 1600
	int ret;
	char data[EXT_CLIENT_NODESIZE];
	int datasize;
	int count=0;
	extqueue=ring_queue_shared(EXT_CLIENT_SHM_ID);
	if(NULL==extqueue) {
		printf("ring_queue_shared failure!\n");
		return -1;
	}else 
		printf("extqueue=%p\n",extqueue);

	while(1) {
		datasize=EXT_CLIENT_NODESIZE;
		ret=ring_queue_get(extqueue,data,&datasize);
		if(ret)
			continue;
		count++;
		if(count%1000000==0)
			printf("size=%d......conut=%u\n",datasize,count);


	}
	return 0;
}
	

