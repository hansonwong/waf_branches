TSEPOLICY=nftse
POLICY_CTL=policy-ctl

all:$(TSEPOLICY) $(POLICY_CTL) clean0

HERE=$(shell pwd)

INC=$(HERE)/
LIB=$(HERE)/

TSEPOLICY_OBJ=$(HERE)/thread.o \
	          $(HERE)/mem_manage.o \
	          $(HERE)/nfq.o \
	          $(HERE)/tse.o \
              $(HERE)/connt.o\
              $(HERE)/util.o\
              $(HERE)/admin.o\
              $(HERE)/monitor.o\
              $(HERE)/rwini.o\
              $(HERE)/log.o\
              $(HERE)/policyrun.o

POLICY_CTL_OBJ=$(HERE)/policy-ctl.o

#Compiler Options
CFLAGS:= -g -Wall -W \
         -Wno-unused-parameter \
	     -Wno-unused-function \
         -Wno-unused-variable \
	     -Wno-unused-but-set-parameter \
         -Wpointer-arith \
	     -Waggregate-return \
	     -Wunreachable-code \
	     -Wcast-align \
	     -I$(INC) 
#-Wcast-qual -Wunused-variable
LDFLAGS=-lpthread -ldl -lrt -lm -lnetfilter_queue -lnfnetlink -L/usr/lib64/mysql -lmysqlclient

$(POLICY_CTL):$(POLICY_CTL_OBJ)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

$(TSEPOLICY):$(TSEPOLICY_OBJ)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

#$(TSEPOLICY_OBJ):%.o:%.c
#	$(CC) -c $(CFLAGS) $< -o $@

%.o:%.c
	$(CC) -c $(CFLAGS) $< -o $@

.PHONY:clean0
clean0:
	rm -fr $(HERE)/*.o

.PHONY:clean
clean:
	rm -fr $(HERE)/$(TSEPOLICY) $(HERE)/$(POLICY_CTL)
	rm -fr $(HERE)/*.a
	rm -fr $(HERE)/*.o
