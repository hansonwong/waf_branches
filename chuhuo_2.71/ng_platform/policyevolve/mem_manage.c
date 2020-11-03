#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdint.h>
#include <time.h>

#include "mem_manage.h"


//calc level base on size
static int level_nums(uint32_t entries,uint32_t *lev,uint32_t * levelnums)
{
    uint32_t cnums = entries;
    int level      = 0;
	int totalbytes = 0;
    while(cnums >= BITMAP_PER_SIZE){
        cnums = cnums / BITMAP_PER_SIZE;
		totalbytes += cnums * sizeof(bitmap_set);
		level++;
    }
	if(level > MAX_LEVEL_MAP){
		return -1;
	}
	int index = level - 1;
    while(entries >= BITMAP_PER_SIZE && index >= 0){
        entries = entries / BITMAP_PER_SIZE;
		levelnums[index--] = entries;
    }
	*lev = level;
    return totalbytes;
}


static int get_bitmap_bytes(uint32_t entries)
{
    int level = 0;
	int bytes = 0;
	
    while(entries >= BITMAP_PER_SIZE){
        entries = entries / BITMAP_PER_SIZE;
		bytes  += entries * sizeof(bitmap_set);
		level++;
    }
	if(level > MAX_LEVEL_MAP){
		return -1;
	}
	return bytes;
}

static int lookup_unused_bit(bitmap_set * bitmap)
{
	uint32_t index;
	for(index = 0; index < BITMAP_PER_SIZE; index++){
		if((*bitmap & (SHIFT_BIT<<index)) == 0) break;
	}
	return index;
}

static int lookup_unused_level(bitmap_set * map,int max)
{
	int index;
	uint32_t ret;

	
	for(index = 0; index < max; index++){
		if(map[index] != MAX_BITMAP_UNIT){
			ret = lookup_unused_bit(map+index);
			return  index * BITMAP_PER_SIZE + ret;
		}
	}
	return -1;
}

void * alloc_mem_by_pos(MemManage * m,uint32_t pos)
{
	if(pos >= m->entries){
		return NULL;
	}
	
	int level = m->level - 1;
	uint32_t bitpos = pos;

	if(BITMAP_TEST(m->bitmap[level],bitpos)) return NULL;

	BITMAP_SET(m->bitmap[level],bitpos);
	level--;
	for( ; level >= 0; level--)
	{
		bitpos = bitpos / BITMAP_PER_SIZE;
		if(m->bitmap[level+1][bitpos] == MAX_BITMAP_UNIT){
			BITMAP_SET(m->bitmap[level],bitpos);
		}
	}
	
	void * data = (void*)(m->data + pos * m->entry_size_algin);
	m->entries_used++;
	return data;
}

void * alloc_mem(MemManage * m)
{
	int index;
	int levelret;
	int pos[MAX_LEVEL_MAP] = {0};

	levelret = lookup_unused_level(m->bitmap[0],m->levelnums[0]);
	if(levelret < 0) return NULL;
	pos[0] = levelret;
	int maxlevel = (int)m->level;
	for(index = 1; index < maxlevel; index++){
		uint32_t bit = lookup_unused_bit(m->bitmap[index]+levelret);
		pos[index] = levelret * BITMAP_PER_SIZE + bit;
		levelret   = pos[index];
	}
	
	uint32_t cnum = levelret;
	//Light up the level of bottom
	index = m->level - 1;
	BITMAP_SET(m->bitmap[index],pos[index]);
	index--;
	for(; index >= 0; index--){
		cnum = cnum / BITMAP_PER_SIZE;
		if(m->bitmap[index+1][cnum] == MAX_BITMAP_UNIT){
			BITMAP_SET(m->bitmap[index],pos[index]);
		}
	}
	void * ret_mem = (void *)(m->data + levelret * m->entry_size_algin);
	m->entries_used++;
	return ret_mem;
	
}

int get_mem_pos(MemManage * m,void * memstruct)
{
	uint8_t * data = (uint8_t*)memstruct;
	uint32_t data_offset = data - m->data;
	uint32_t  pos  = data_offset / m->entry_size_algin;
	if(data_offset % m->entry_size_algin != 0) return -1;
	return pos;
}

int free_mem_by_pos(MemManage * m,uint32_t pos)
{
	if(pos >= m->entries) return -1;
	
	int level = m->level - 1;
	uint32_t bitpos = pos;
	for( ; level >= 0; level--){
		BITMAP_CLEAR(m->bitmap[level],bitpos);
		bitpos = bitpos / BITMAP_PER_SIZE;
	}
	uint8_t * data = m->data + pos * m->entry_size_algin;
	memset(data,0,m->entry_size_algin);
	m->entries_used--;
	return 0;
}

int free_mem(MemManage * m,void * memstruct)
{
	uint8_t * data = (uint8_t*)memstruct;
	uint32_t data_offset = data - m->data;
	uint32_t  pos  = data_offset / m->entry_size_algin;
	if(data_offset % m->entry_size_algin != 0) return -1;
	return free_mem_by_pos(m,pos);
	
}

int mem_manage_memory_bytes(uint32_t entries,uint32_t entry_size)
{
	//entry need bits
	uint32_t mem_manage_bytes;
	uint32_t bytes_size_algin;
	uint32_t total_bytes;
	
    if((entries & (entries-1)) != 0) {
        printf("entries %u is not pow of 2\n",entries);
        return -1;
    }
	if(entries < BITMAP_PER_SIZE){
		printf("entries nums %u is too small[<%d]!\n",entries,BITMAP_PER_SIZE);
		return -1;
	}
	
	uint32_t alignment = sizeof(bitmap_set);
	
    bytes_size_algin = ALGIN_DATA(entry_size,alignment);

	int ret = get_bitmap_bytes(entries);
	if( ret < 0){
		printf("entries nums %u is too big or too small[<%d]!\n",entries,BITMAP_PER_SIZE);
		return -1;
	}
	total_bytes      = ALGIN_DATA((ret + bytes_size_algin * entries),alignment);
	mem_manage_bytes = ALGIN_DATA(sizeof(MemManage),alignment);
	
	return (total_bytes + mem_manage_bytes);
	
}

MemManage * mem_manage_init(uint32_t entries,uint32_t entry_size,
	                                      uint8_t * data,uint32_t data_len)
{
	uint32_t data_offset = 0;
	uint32_t alignment   = sizeof(bitmap_set);

	if(data_len <= entry_size * entries) return NULL;
	if((entries & (entries-1)) != 0 || entries < BITMAP_PER_SIZE) return NULL;
	
	MemManage * mem = (MemManage *)(data + data_offset);
	data_offset += ALGIN_DATA(sizeof(MemManage),alignment);

	mem->entries_used     = 0;
	mem->entries          = entries;
	mem->entry_size       = entry_size;
	mem->entry_size_algin = ALGIN_DATA(entry_size,alignment);
	
	int ret = level_nums(entries,&mem->level,mem->levelnums);
	if(ret < 0) return NULL;
	
	uint32_t index;
	uint32_t init_offset = data_offset;
	for(index = 0; index < mem->level; index++){
		mem->bitmap[index] = (bitmap_set *)(data + data_offset);
		data_offset += mem->levelnums[index] * sizeof(bitmap_set);
	}
	memset(mem->bitmap[0],0,(data_offset-init_offset));
	mem->data    = (uint8_t *)(data + data_offset);
	data_offset += mem->entry_size_algin * mem->entries;
	if(data_offset > data_len) return NULL;
	return mem;
	
}

#if 0
struct test{
	char a;
	char b;
	int c;
};

int main()
{
	struct test * a;//[268435456];
	
	MemManage * mem;
	uint32_t mem_size = mem_manage_memory_bytes(268435456,sizeof(struct test));
	printf("%u\n",mem_size);
	uint8_t * memory = (uint8_t *)malloc(mem_size);
	if(memory==NULL) {
		printf("malloc mem fail!\n");
		return -1;
	}
	mem = mem_manage_init(268435456,sizeof(struct test),memory,mem_size);
	if(mem == NULL) {
		printf("mem init fail\n");
		return 0;
	}
	int i = 0;
	uint64_t time_s = 0;
	struct timespec start={0,0};
	struct timespec end={0,0};
	clock_gettime(CLOCK_REALTIME,&start);
	a = (struct test *)malloc(sizeof(struct test));
	clock_gettime(CLOCK_REALTIME,&end);
	free(a);
	printf("%lu\n",end.tv_nsec-start.tv_nsec);
	
	start.tv_nsec = 0;
	start.tv_sec  = 0;
	end.tv_nsec   = 0;
	end.tv_sec    = 0;
	clock_gettime(CLOCK_REALTIME,&start);
	for(;i < 268435456; i++){
		a = (struct test *)alloc_mem(mem);
		
		//time_s += end.tv_nsec-start.tv_nsec;
		//if(a == NULL) {
		//	printf("%d fail!\n",i);
		//	break;
		//}
	}
	clock_gettime(CLOCK_REALTIME,&end);
	printf("%lus:%luns\n",end.tv_sec-start.tv_sec,end.tv_nsec-start.tv_nsec);
	int s;
	int m;
	struct test * x;
	while(1){
		printf("-------input free id\n");
		scanf("%d",&s);
		if(s == -1) break;
		if(s>=0 && s <268435456){
			if(free_mem_by_pos(mem,s)< 0)
				printf("free fail\n");
			else
				printf("free succ\n");
		}
		printf("-------input alloc id\n");
		scanf("%d",&m);
		if(m == -1){
			x = (struct test *)alloc_mem(mem);
			if(x == NULL){
				printf("No Pos:alloc fail\n");
			}
			else printf("alloc succ%d\n",((uint8_t*)x - mem->data)/mem->entry_size_algin);
		}
		if(m >= 0){
			x = (struct test *)alloc_mem_by_pos(mem,m);
			if(x == NULL){
				printf("Pos: alloc fail\n");
			}
			else printf("alloc succ%d\n",((uint8_t*)x - mem->data)/mem->entry_size_algin);
		}

	}
	free(memory);
	return 0;
		
}
#endif


