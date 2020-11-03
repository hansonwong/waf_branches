#include "clientext_queue.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <memory.h>
#include <sys/ipc.h>
#include <sys/shm.h>

/**
 *  buff�ڴ�ʹ�����
 *  ringͷ    flags_array_              datasize_array_   element_0  element_1  .................     element_n  ����
 * |---------|-------------------------|-----------------|----------|----------|----------|----------|----------|---------
 *
 */

struct ring_queue* ring_queue_create(char *buff, int buffsize, int nodesize)
{
	if (buff == 0) return 0;
	
	if (buffsize < (int)sizeof(struct ring_queue)) return 0;											// ����ռ䲻������ring_bufͷ�Ŀռ�
	
	struct ring_queue* ring = (struct ring_queue*)buff;
	
	ring->size_ = (buffsize - sizeof(struct ring_queue)) / (nodesize + sizeof(unsigned char) + sizeof(int));	// ����buff�����Դ�ŵ�Ԫ�صĸ���
	
	
	ring->flags_array_offset_ = sizeof(struct ring_queue);
	ring->datalen_array_offset_ = sizeof(struct ring_queue) + ring->size_ * sizeof(unsigned char);
	ring->data_array_offset_ = sizeof(struct ring_queue) + ring->size_ * sizeof(unsigned char) + ring->size_ * sizeof(int);
	
	
	memset(buff + ring->flags_array_offset_, 0, sizeof(unsigned char) * ring->size_);							// ��ʼ����־���������
	memset(buff + ring->datalen_array_offset_, 0, sizeof(int) * ring->size_);									// ��ʼ�洢Ԫ�����ݴ�С�����������
	
	ring->element_size_ = nodesize;
    ring->head_index_ = 0;
    ring->tail_index_ = 0;
    ring->element_num_ = 0;
	return ring;
}

int ring_queue_add(struct ring_queue* ring, void* data, int datasize)
{
	if (!(ring->element_num_ < ring->size_))
        return 1;

    int cur_tail_index = ring->tail_index_;

	unsigned char *cur_tail_flag_index = (unsigned char*)((char*)ring + ring->flags_array_offset_) + cur_tail_index;
	
	// æʽ�ȴ�
	// while�е�ԭ�Ӳ����������ǰtail�ı��Ϊ������ռ��(1)���������cur_tail_flag_index,
	// ����ѭ�������򣬽�tail�����Ϊ�Ѿ�ռ��
	
	while (!__sync_bool_compare_and_swap(cur_tail_flag_index, 0, 1)) {
	
		cur_tail_index = ring->tail_index_;
		
		cur_tail_flag_index = (unsigned char*)((char*)ring + ring->flags_array_offset_) + cur_tail_index;
	
	}
	
	// ��������߳�֮���ͬ��
	// ȡģ���������Ż�
	
	int update_tail_index = (cur_tail_index + 1) % ring->size_;
	
	// ����Ѿ����������̸߳��¹�������Ҫ���£�
	// ���򣬸���Ϊ (cur_tail_index+1) % size_;
	
	__sync_bool_compare_and_swap(&(ring->tail_index_), cur_tail_index, update_tail_index);
	
	// ���뵽���õĴ洢�ռ�
	memcpy((int*)((char*)ring + ring->datalen_array_offset_) + cur_tail_index, &datasize, sizeof(int));
	memcpy((char*)((char*)ring + ring->data_array_offset_) + cur_tail_index * ring->element_size_, data, datasize);
	
	// д�����
	__sync_fetch_and_add(cur_tail_flag_index, 1);
	
	// ����size;����߳�������߳�֮���Э��
	__sync_fetch_and_add(&(ring->element_num_), 1);

    return 0;


}

int ring_queue_get(struct ring_queue* ring, void* data, int* datasize)
{
	if (!(ring->element_num_ > 0))

        return 1;
	int flag = 0;
	
    int cur_head_index = ring->head_index_;

    unsigned char * cur_head_flag_index = (unsigned char*)((char*)ring + ring->flags_array_offset_) + cur_head_index;

    while (!__sync_bool_compare_and_swap(cur_head_flag_index, 2, 3)) {

        cur_head_index = ring->head_index_;

        cur_head_flag_index = (unsigned char*)((char*)ring + ring->flags_array_offset_) + cur_head_index;

    }

    // ȡģ���������Ż�
    int update_head_index = (cur_head_index + 1) % ring->size_;

    __sync_bool_compare_and_swap(&(ring->head_index_), cur_head_index, update_head_index);

    memcpy(datasize, (int*)((char*)ring + ring->datalen_array_offset_) + cur_head_index, sizeof(int));
    if (*datasize <= ring->element_size_)
    {
    	memcpy(data, (char*)((char*)ring + ring->data_array_offset_) + cur_head_index * ring->element_size_, *datasize);
	}
	else
	{
		flag = 1;	
	}
    // �������
    __sync_fetch_and_sub(cur_head_flag_index, 3);

    // ����size
    __sync_fetch_and_sub(&(ring->element_num_), 1);
    
    return flag;


}

struct ring_queue* ring_queue_shared_create(int queueid, int buffsize, int nodesize)
{
	int shmid, ret;
	
	{
		struct shmid_ds shmds;
		shmid = shmget( queueid,0,0 );//ʾ���������һ�������ڴ�ı�ʶ��
		ret = shmctl(shmid, IPC_STAT, &shmds );
		if( ret == 0 )
		{
			printf( "Size of memory segment is %lu\n",shmds.shm_segsz );
			printf( "Numbre of attaches %d\n",( int )shmds.shm_nattch );
			
			//ɾ���ù����ڴ���
			ret = shmctl(shmid, IPC_RMID, 0);
			if( ret==0 )
				printf( "Shared memory removed \n" );
			else
				printf( "Shared memory remove failed \n" );
		}
		else
		{
			printf( "shmctl(  ) call failed \n" );
		}
		
	}
		
    shmid = shmget(queueid, buffsize, IPC_CREAT );
	char* mem = shmat( shmid,( const void* )0,0 );
	if (mem)
	{
		printf("mem = %p\n", mem);
	}
	
	return ring_queue_create(mem, buffsize, nodesize);
}

struct ring_queue* ring_queue_shared(int queueid)
{
	int shmid;
	//shmid = shmget(MY_SHM_ID, 0, 0);
	shmid = shmget(queueid, 0, 0);
	char* mem = shmat( shmid,( const void* )0,0 );
	return (struct ring_queue*)mem;
}
