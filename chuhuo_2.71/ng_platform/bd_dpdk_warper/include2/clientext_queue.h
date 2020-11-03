#ifndef _BDDPDK_RING_QUEUE_H
#define _BDDPDK_RING_QUEUE_H



#define RING_HEAD_OFFSET 0
#define RING_TAIL_OFFSET sizeof(int)

struct ring_queue
{
	int data_array_offset_;
	int flags_array_offset_;
	int datalen_array_offset_;
	
	
	/*
	char *data_array_;
	unsigned char *flags_array_;	// ���λ�����ĳ��λ�õ�Ԫ���Ƿ�ռ��
									// flags: 0���սڵ㣻1���ѱ����룬����д��
									// 2���Ѿ�д�룬���Ե���;3,���ڵ�������;
	int *datalen_array_;
	*/
	int element_size_;
	int size_;						// ��������Ĵ�С
	int element_num_;				//������Ԫ�صĸ���
	int head_index_;
	int tail_index_;
};

/**
 *
 * ��� ring_queue ״̬��Ϣ
 */
#define ring_queue_dump(ring) printf("ring: %u\nflags_array_: %u\ndatalen_array_: %u\ndata_array_: %u\nelement_size_: %d\nsize_: %d\nelement_num_: %d\nhead_index_: %d\ntail_index_: %d\n", \
	ring, \
	ring->flags_array_offset_, \
	ring->datalen_array_offset_, \
	ring->data_array_offset_, \
	ring->element_size_, \
	ring->size_, \
	ring->element_num_, \
	ring->head_index_, \
	ring->tail_index_);


struct ring_queue* ring_queue_create(char *buff, int buffsize, int nodesize);

int ring_queue_add(struct ring_queue* ring, void* data, int datasize);

int ring_queue_get(struct ring_queue* ring, void* data, int* datasize);

struct ring_queue* ring_queue_shared_create(int queueid, int buffsize, int nodesize);

struct ring_queue* ring_queue_shared(int queueid);

#endif
