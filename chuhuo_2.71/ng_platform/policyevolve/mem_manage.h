#ifndef _MEM_MANAGE_H_
#define _MEM_MANAGE_H_

#define MEM_CHAR_BIT 8

#ifdef __BIT32__

#define BITMAP_PER_SIZE 32
#define MAX_LEVEL_MAP   5
#define MAX_BITMAP_UNIT UINT32_MAX
#define SHIFT_BIT       1U

typedef uint32_t bitmap_set;

#else

#define BITMAP_PER_SIZE 64
#define MAX_LEVEL_MAP   4
#define MAX_BITMAP_UNIT UINT64_MAX
#define SHIFT_BIT       1UL

typedef uint64_t bitmap_set;

#endif

#define BITMAP_SET(map,p)  ((void)(((bitmap_set*)(map))[(p)/BITMAP_PER_SIZE] |= SHIFT_BIT<<(p)%BITMAP_PER_SIZE))
#define BITMAP_CLEAR(map,p)((void)(((bitmap_set*)(map))[(p)/BITMAP_PER_SIZE]&= ~(SHIFT_BIT<<(p)%BITMAP_PER_SIZE)))
#define BITMAP_FLIP(map,p) ((void)(((bitmap_set*)(map))[(p)/BITMAP_PER_SIZE] ^= SHIFT_BIT<<(p)%BITMAP_PER_SIZE))
#define BITMAP_TEST(map,p) (((bitmap_set*)(map))[(p)/BITMAP_PER_SIZE] & (SHIFT_BIT<<(p)%BITMAP_PER_SIZE))

#define ALIGN_SIZE 64

#define ALGIN_DATA(size,alignment)\
	(alignment * ((size + alignment - 1) / alignment))
	

typedef struct MemManage_{
	uint32_t    entries_used;
	uint32_t    entries;
	uint32_t    entry_size;
	uint32_t    entry_size_algin;
	uint32_t    level;
	uint32_t    levelnums[MAX_LEVEL_MAP];
	bitmap_set* bitmap[MAX_LEVEL_MAP];
	uint8_t*    data;
}MemManage;

void * alloc_mem_by_pos(MemManage * m,uint32_t pos);
void * alloc_mem(MemManage * m);
int get_mem_pos(MemManage * m,void * memstruct);
int free_mem_by_pos(MemManage * m,uint32_t pos);
int free_mem(MemManage * m,void * memstruct);
int mem_manage_memory_bytes(uint32_t entries,uint32_t entry_size);
MemManage * mem_manage_init(uint32_t entries,uint32_t entry_size,
	                                      uint8_t * data,uint32_t data_len);


#endif //_MEM_MANAGE_H_

