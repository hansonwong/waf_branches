#CC= mips64-octeon-linux-gnu-gcc
#CFLAGS+= -mabi=n32
#LDFLAGS+= -static

CC = gcc

CFLAGS+= -O2 -g -W -Wall 
CFLAGS+= -I. -I.. -I../..
CFLAGS+= -I../../../../include2/
# phase 3 or 4
CFLAGS+= -DRFC_PHASE=4
#CFLAGS+= -DRFC_PHASE=3

# for PRINT_STAT
CFLAGS+= -DPRINT_STAT 
LDFLAGS+= -lm

CFLAGS+= -DDEBUG_RULES 

#LDFLAGS+= ElectricFence/libefence.a

rfc: rfctest.c ../rfc.c ../dheap.c   Makefile
	${CC} ${CFLAGS} -o rfc rfctest.c ../rfc.c ../dheap.c  ${LDFLAGS}
#-lm

all: rfc 

clean:
	rm -f rfc
	rm -fr ../rfc.o ../dheap.o

.PHONY: acl fw1 r1
acl: rfc
	./rfc -r acl1_1K -t acl1_1K_trace


fw1: rfc
	./rfc -r fw1 -t fw1_trace

r1: 
	./rfc -r r1 -t t1

