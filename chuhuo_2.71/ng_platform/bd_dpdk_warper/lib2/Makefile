DPDK_BD=libdpdk_bd.a
DPDK_BD_EXT=libdpdk_bd_ext.a
all:$(DPDK_BD) $(DPDK_BD_EXT) clean0

HERE=$(shell pwd)
DPDK_WARPER?=$(HERE)/..
INC1=$(DPDK_WARPER)/include
INC2=$(DPDK_WARPER)/include2
INC_NDPI=$(DPDK_WARPER)/include2/ndpi
LIB1=$(DPDK_WARPER)/lib

DPDK_BD_OBJ=$(HERE)/dpdk_frame.o \
		$(HERE)/filter/rfc/dheap.o \
		$(HERE)/filter/rfc/rfc.o \
		$(HERE)/bridge_simple.o \
		$(HERE)/qos_sched.o \
		$(HERE)/dpdk_reass.o \
		$(HERE)/ddos.o \
		$(HERE)/pingagent.o \
		$(HERE)/flow.o \
		$(HERE)/dpi.o
DPDK_BD_EXT_OBJ=$(HERE)/clientext_queue.o


CFLAGS:= -O2  -Wall -W -Wno-unused-parameter -Wno-unused-variable -Wno-unused-function\
	-I$(INC1) \
	-I$(INC2) \
	-I$(INC_NDPI)


LDFLAGS=-L$(LIB1) -ldpdk  \
	-lpthread -ldl -lrt


$(DPDK_BD):$(DPDK_BD_OBJ)
	$(AR) -cr  $@ $^

$(DPDK_BD_EXT):$(DPDK_BD_EXT_OBJ)
	$(AR) -cr  $@ $^

$(DPDK_BD_EXT_OBJ):%.o:%.c
	$(CC) -c $(CFLAGS) $< -o $@

%.o:%.c
	$(CC) -c $(CFLAGS) $< -o $@

.PHONY:clean0
clean0:
	rm -fr $(HERE)/*.o

.PHONY:clean
clean:
	rm -fr $(HERE)/*.a
	rm -fr $(HERE)/*.o
	rm -fr $(HERE)/filter/rfc/*.o
