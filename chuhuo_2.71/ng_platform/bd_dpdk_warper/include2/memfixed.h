#ifndef __MEMPOOL_H
#define __MEMPOOL_H

#include <stdlib.h>
#include<stdint.h>
#include<malloc.h>

typedef void *(*mmalloc)(uint32_t size);
typedef void  (*mfree)(void * );

struct meminfo {
	uint32_t totalunit;
    	uint32_t unitsize;
	mmalloc malloc;
	mfree free;
};
struct memfixed {
    char * obase;
    volatile uint32_t head; 
    volatile uint32_t tail; 
    volatile uint32_t leftunit;
    uint32_t totalunit;
    uint32_t unitsize;
}__attribute__((aligned(64)));

struct list32{
   uint32_t next;
};


static inline struct memfixed *
mempool_init(struct meminfo  *minfo)
{
	uint32_t i;
	uint32_t totalsize;
	char *addr;
	struct memfixed *handle;
	struct list32 *list=NULL;
	
	if(minfo->malloc==NULL)
		minfo->malloc=(mmalloc)malloc;
	if(minfo->free==NULL)
		minfo->free=(mfree)free;
    	
	if(minfo->unitsize<4) {
		printf("error:unitsize=%d < 4",minfo->unitsize);
		return NULL;
	}
	totalsize=sizeof(struct memfixed )+minfo->totalunit*minfo->unitsize;
	addr=(char *)minfo->malloc(totalsize);
	if(!addr) {
		printf("error:mempool_init malloc  fail\n");
		return NULL;
	}
	handle=(struct memfixed *)addr;
	addr=addr+sizeof(struct memfixed );
	
	handle->obase=addr;
    	handle->unitsize=minfo->unitsize;
	handle->totalunit=minfo->totalunit;
	handle->leftunit=minfo->totalunit;

	handle->head=0;
        
        for(i=0;i<handle->totalunit;i++)
        {
            list=(struct list32 *)((char *)addr+i*minfo->unitsize);
            list->next=i+1;        
        }
        list->next=(uint32_t)-1;
        handle->tail=handle->totalunit-1;

	 return handle;
}


static inline void *
mempool_malloc(struct memfixed *handle)
{
    struct list32 *list;
    if(handle->leftunit<=0){
        return NULL;
    }   
    list=(struct list32 *)((char *)(handle->obase)+handle->head*handle->unitsize);
    handle->head=list->next;  
    if(handle->head==(uint32_t)-1)
        handle->tail=(uint32_t)-1;
    handle->leftunit--; 
    
    return list;  
}


static inline void 
mempool_free(struct memfixed *handle,void *addr)
{
    struct list32 *list;
    uint32_t pindex=((char *)addr-handle->obase)/handle->unitsize;
    if(pindex >= handle->totalunit){
        printf("error:free addr %d  out of range (max %d)..\n",pindex,handle->totalunit);
        return ; 
    }
    list=(struct list32 *)((char *)(handle->obase)+pindex*handle->unitsize);
    list->next=(uint32_t)-1;
    if(handle->tail==(uint32_t)-1){
        handle->head=handle->tail=pindex;
    }   else   {   
        list=(struct list32 *)((char *)(handle->obase)+handle->tail*handle->unitsize);
        list->next=pindex;
        handle->tail=pindex;
    }
    handle->leftunit++; 
}

static inline void 
mempool_exit(struct memfixed *m,struct meminfo  *minfo) {
	if(minfo->free==NULL)
		minfo->free=(mfree)free;
	minfo->free(m);
}
#endif


/**********************************************************
static struct meminfo  minfo={
	.totalunit=16,
    	.unitsize=sizeof(uint64_t),
};
static  struct memfixed *m;
int main(void)
{
	uint64_t i;
	uint64_t *p;
	char *addr;

	printf("sizeof(memfixed)=%lu\n",sizeof(struct memfixed));
	m=mempool_init(&minfo);
	if(m==NULL) {
		printf("mempool_init fail!\n");
		return -1;
	}

	for(i=0;i<17;i++) {
		p=mempool_malloc(m);
		if(!p)
			printf("malloc error!\n");
		else {
			*p=0x12345678abcdef00+i;
			printf("p=%p\n",p);
		}
		if(i%2) mempool_free(m,p);
			
	}
	

	addr=m->obase;
	for(i=0;i<m->totalunit*m->unitsize;i++) {
		if(i&&i%m->unitsize==0) 
			printf("\n");
		printf("%x ",addr[i]&0xff);

	}
	return 1;
}
************************************************************************/

