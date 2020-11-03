CC      := gcc
LD      := ld
LDFLAGS := -shared -fpic
SOURCE 	:= $(wildcard *.c ./protocols/*.c ./third_party/src/*.c)
#SOURCE 	:= $(wildcard *.c ./protocols/*.c)
OBJS	:= $(patsubst %.c,%.o,$(SOURCE))
LIB_OBJS:= libndpi.so

HERE := $(shell pwd)
NDPI_PRO := ${HERE}/protocols
NDPI_3RDPARTY := ${HERE}/third_party

CFLAGS := -fPIC -I${HERE}/include -I${HERE}/lib -I../src -O2 -Wall -w -Wunused-but-set-variable -Wunused-variable
CFLAGS += -I${NDPI_3RDPARTY}/include 
CFLAGS += -I${HERE}/../../include2/ndpi
#CFLAGS += -DOPENDPI_NETFILTER_MODULE 

all:$(OBJS)
	echo $(OBJS)
	$(LD) $(LDFLAGS) -o $(LIB_OBJS) $(OBJS) 
	@echo "Install the ndpi lib"	
	cp -f libndpi.so /lib/
	ln -sf /lib/libndpi.so /lib/libndpi.so.1
	ldconfig
	
%.o:%.c
	@echo Compiling $< ...
	$(CC) -c $(CFLAGS) $< -o $*.o
	



.PHONY: clean

clean:
	rm -rf *.o *.so
	rm -rf $(NDPI_PRO)/*.o $(NDPI_PRO)/*.so
	rm -rf $(NDPI_3RDPARTY)/src/*.o $(NDPI_PRO)/src/*.so
