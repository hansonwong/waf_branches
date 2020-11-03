#ifndef  __HASH__H
#define  __HASH__H

#include <stdlib.h>
#include<stdint.h>
#include <malloc.h>
#include "link.h"


static inline 
uint32_t default_hash(uint8_t *key,int len)
{
    uint32_t hash = 0;  
    int  i; 
     for (i=0;i<len;i++) 
     {
        hash = hash * 33 + key[i];
     }
    return hash;  
}

typedef void *(*pmalloc)(uint32_t size);
typedef void  (*pfree)(void * );
typedef uint32_t (*phash)(void *key); 
typedef int     (*pcompare)(struct list_head  *link,void *item);
typedef int     (*pupdate)(struct list_head  *link);
typedef int     (*pcallbk)(struct list_head  *link);
struct hashinfo {
	uint32_t bucket;
	pmalloc malloc;
	pfree free;
	phash hash;
	pcompare compare;
	pupdate update;
};


struct hhash {
	uint32_t bucketmark;
	phash hash;
	pcompare compare;
	pupdate update;
	struct list_head  *head;
}__attribute__((aligned(64)));

static inline 
struct hhash *hashcreate(struct hashinfo *info) {
	uint32_t i;
	uint32_t totalsize;
	struct hhash *hash;
	char *addr;
	if(!info->bucket)  {
		printf("error:bucket =0\n");
		return NULL;
	}
	if(info->bucket & (info->bucket-1)) {
		printf("error:bucket should be 2^n,link 126,256,1024..\n");
		return NULL;
	}
	if(info->hash==NULL) {
		printf("error:need hash function\n");
		return NULL;
	}
	if(info->compare==NULL) {
		printf("error:need compare function\n");
		return NULL;
	}

	if(!info->malloc)
		info->malloc=(pmalloc)malloc;
	if(!info->free)
		info->free=(pfree)free;
	totalsize=sizeof(struct hhash )+sizeof(struct list_head)*info->bucket;
	
	addr=(char *)info->malloc(totalsize);
	if(!addr) {
		printf("hashcreate malloc fail!\n");
		return NULL;
	}
	hash=(struct hhash *)addr;
	addr+=sizeof(struct hhash );
	hash->head=(struct list_head  *)addr;
	
	for(i=0;i<info->bucket;i++)
		INIT_LIST_HEAD(&hash->head[i]);
	hash->bucketmark=info->bucket-1;
	hash->hash=info->hash;
	hash->compare=info->compare;
	hash->update=info->update;
	return hash;	
}

static inline struct list_head *
hhash_find(struct hhash *h,void *item)
{	
	struct list_head *pos,*n;
	uint32_t hash=h->hash(item)&h->bucketmark;
	list_for_each_safe(pos,n,&h->head[hash]) {
	 	if(h->compare(pos,item))
	 		return pos;
	 }
	return  NULL;
}

static inline int 
hhash_add(struct hhash *h,void *item,struct list_head *link)
{
    uint32_t hash;
    hash=h->hash(item)&h->bucketmark;
    list_add_tail(link,&h->head[hash]);
    return 0;
}

static inline int 
hhash_add_safe(struct hhash *h,void *item,struct list_head *link)
{
    struct list_head *pos,*n;
   uint32_t hash=h->hash(item)&h->bucketmark;
	list_for_each_safe(pos,n,&h->head[hash]) {
	 	if(h->compare(pos,item)) {
			//printf("item has already in hashtalbe!\n");
			if(h->update)
				h->update(pos);
			return -1;
	 	}
	 }
    list_add_tail(link,&h->head[hash]);
    return 0;
}


static inline int 
hhash_del(struct list_head *link)
{
    list_del(link);
    return 0;
}


static inline struct list_head *
hhash_iterator(struct hhash *h,pcallbk  callbk)
{	
	uint32_t i;
	struct list_head *pos,*n,*head;
	for(i=0;i<=h->bucketmark;i++) {
		head=&h->head[i];
		list_for_each_safe(pos,n,head) {
	 		if(callbk(pos))
	 			return pos;
	 	}
	 }
	 return  NULL;
}

static inline 
void hashdestroy(struct hhash *h,struct hashinfo *info) 
{
	if(!info->free)
		info->free=(pfree)free;
	info->free(h);
}


/*****************************************************
struct  port_mac {
	union {
		struct {
		uint8_t portid;
		uint8_t mac[6];
		};
		uint8_t key[7];
	};
	struct list_head hl;
};

static uint32_t port_mac_hash(struct  port_mac  *pmac) {
	return default_hash(pmac->key,sizeof(pmac->key));
}

static  int    port_mac_same(struct list_head  *link,struct  port_mac *pmac) {
	struct  port_mac *tmp=(struct  port_mac *)list_entry(link,struct  port_mac,hl);
	if(0==memcmp(tmp->key,pmac->key,sizeof(pmac->key)))
		return 1;
	return 0;
 }

static int  print(struct list_head  *link){
 	int i;
	struct  port_mac *tmp=(struct  port_mac *)list_entry(link,struct  port_mac,hl);
	printf("port %d,mac:",tmp->portid);
	for(i=0;i<6;i++)
		printf("0x%x ",tmp->mac[i]);
	printf("\n");
	return 0;
 }
 
static struct hashinfo  hinfo={
	.bucket=256,
	.hash=(phash)port_mac_hash,
	.compare=(pcompare)port_mac_same,
};

static struct hhash *h;
int main(void ) {
	struct  port_mac  p1={
		.key={1,2,3,4,5,6,7},
	};
	struct  port_mac  p2={
		.key={2,2,3,4,5,6,7},
	};
	struct  port_mac  p3={
		.key={3,2,3,4,5,6,7},
	};
	struct  port_mac  p4={
		.key={4,2,3,4,5,6,7},
	};
	
	h=hashcreate(&hinfo);
	if(!h) {
		printf("hashcreate fail!\n");
		return -1;
	}

	if(hhash_find(h,&p1))
		printf("p1 found\n");
	else 
		printf("p1 not found!\n");
	hhash_add(h,&p1,&p1.hl);
	if(hhash_find(h,&p1))
		printf("p1 found\n");
	else 
		printf("p1 not found!\n");

	hhash_add_safe(h,&p2,&p2.hl);
	hhash_add_safe(h,&p2,&p2.hl);
	hhash_del(&p2.hl);
	hhash_add_safe(h,&p2,&p2.hl);
	hhash_add_safe(h,&p3,&p3.hl);
	hhash_add_safe(h,&p4,&p4.hl);
	
	hhash_iterator(h,print);
	
	return 1;
}

**********************************************************/


#endif

