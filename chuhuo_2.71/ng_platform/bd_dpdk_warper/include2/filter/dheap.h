/*
 * Copyright(c) 2007 BDNS
 */
#ifndef _DHEAP_H_
#define _DHEAP_H_

// Header file for d-heap data structure. Maintains a subset
// of items in {1,...,m}, where item has a key.

typedef unsigned long keytyp;
typedef int item;

struct dheap {
	int	N;			// max number of items in heap
	int	n;			// number of items in heap
	int	d;			// base of heap
	item	*h;			// {h[1],...,h[n]} is set of items
	int	*pos;			// pos[i] gives position of i in h
	keytyp	*kvec;			// kvec[i] is key of item i
};

void dheap_print(struct dheap *H);
// Return item with smallest key.
static inline int dheap_findmin(struct dheap *H)
{ return H->n == 0 ? -1 : H->h[1]; }

// Return key of i.
static inline keytyp dheap_key(struct dheap *H, item i)
{
#if 0
	if (i == -1)
		return 0;

	if (i == 0) { return 0; }
#endif
       	return H->kvec[i];
}

// Return true if i in heap, else false.
static inline int dheap_member(struct dheap *H, item i)
{ return H->pos[i] != -1; }

// Return true if heap is empty, else false.
static inline int dheap_empty(struct dheap *H)
{ return H->n == 0; };

void dheap_init(struct dheap *H, unsigned char *p, int N1);
void dheap_reset(struct dheap *H, int d1);
unsigned int dheap_size(int N1);
void dheap_insert(struct dheap *H, item i, keytyp k);
void dheap_remove(struct dheap *H, item i);
int dheap_deletemin(struct dheap *H);
void dheap_changekey(struct dheap *H, item i, keytyp k);

#endif
