FPDEBUG=fp-debug
STRINGTOKENIZER=StringTokenizer
all:$(FPDEBUG) clean0

HERE=$(shell pwd)
DPDK_WARPER?=$(HERE)/../..
INC1=$(DPDK_WARPER)/include
INC2=$(DPDK_WARPER)/include2
INC_NDPI=$(DPDK_WARPER)/include2/ndpi
LIB1=$(DPDK_WARPER)/lib
LIB2=$(DPDK_WARPER)/lib2

FPDEBUG_OBJ=$(HERE)/fp-debug.o $(HERE)/StringTokenizer.o

CFLAGS:=-O2  -Wall -W -Wno-unused-parameter \
	-I$(INC1) \
	-I$(INC2) \
	-I$(INC_NDPI) \
	-I. -DHAVE_LIBEDIT

LDFLAGS=-L$(LIB2) -ldpdk_bd \
	-L$(LIB1) -ldpdk  \
	-lpthread -ldl -lrt \
	-lbdpi -lext -lcrypto -lz -lzlog\
	-Lreadline/lib -lreadline -lncurses


$(FPDEBUG):$(FPDEBUG_OBJ)
	@echo "$@-------------------->"
	g++ -o  $@   $^  $(LDFLAGS)

%.o:%.cpp
	g++ -c $(CFLAGS) $< -o $@


.PHONY:clean
clean0: 
	rm -fr $(HERE)/*.o 

.PHONY:clean
clean:
	rm -fr $(FPDEBUG) 
	rm -fr $(HERE)/*.o 

