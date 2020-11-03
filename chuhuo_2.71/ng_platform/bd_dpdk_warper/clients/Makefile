BRIDGE=bridge
EXTCLIENT=extclient
EXTCLIENT_TEST=extclient_test
KNI=kni
DAQ=daq
DAQ2=daq2
MULTIPLIER=multiplier
MIRROR_DPDK=mirror
USE_KERNEL=use_kernel
DETECT_VIRUS=virus
DETECT_VIRUS_FAST=virus_fast
KEY_WORD_FILTER=key_word_filter
DETECT_PORTSCAN=portscan
FWAUDIT=fwaudit
VIR_LINE=vir_line
PORT_CONFIG=port_config
SET_MIRROR=set_mirror
TCPDUMP=tcpdump
TCS=tcs
#DDOS=ddos
REASS=reass
DDOS_FLAG=ddos_flag
DDOS_CTL=ddos-ctl
DPI=dpi_mgr
TCF=traffic_count_flag
GSD=get_statistics_data
GIT=get_interface_type
TS=ts
DPDKDEBUG=dpdkdebug
all:$(EXTCLIENT) $(EXTCLIENT_TEST) $(KNI) $(DAQ) $(DAQ2) $(MULTIPLIER) $(MIRROR_DPDK) $(USE_KERNEL) $(DETECT_VIRUS_FAST) $(DETECT_VIRUS) $(KEY_WORD_FILTER) $(DETECT_PORTSCAN) $(FWAUDIT)  $(VIR_LINE) $(PORT_CONFIG) $(SET_MIRROR) $(TCPDUMP) $(TCS) $(REASS) $(DDOS_FLAG) $(DDOS_CTL) $(DPI) $(TCF) $(GSD) $(GIT) $(TS) $(DPDKDEBUG) clean0

HERE=$(shell pwd)
DPDK_WARPER?=$(HERE)/..
INC1=$(DPDK_WARPER)/include
INC2=$(DPDK_WARPER)/include2
INC_NDPI=$(DPDK_WARPER)/include2/ndpi
LIB1=$(DPDK_WARPER)/lib
LIB2=$(DPDK_WARPER)/lib2

BRIDGE_OBJ=$(HERE)/bridge.o
EXTCLIENT_OBJ=$(HERE)/extclient.o
EXTCLIENT_TEST_OBJ=$(HERE)/extclient_test.o
KNI_OBJ=$(HERE)/kni.o
DAQ_OBJ=$(HERE)/daq_dpdk.o
DAQ2_OBJ=$(HERE)/daq_dpdk2.o
MULTIPLIER_OBJ=$(HERE)/multiplier.o
MIRROR_DPDK_OBJ=$(HERE)/mirror_dpdk.o
USE_KERNEL_OBJ=$(HERE)/use_kernel.o
DETECT_VIRUS_OBJ=$(HERE)/virus.o
DETECT_VIRUS_FAST_OBJ=$(HERE)/virus_fast.o
KEY_WORD_FILTER_OBJ=$(HERE)/key_word_filter.o
DETECT_PORTSCAN_OBJ=$(HERE)/portscan.o
FWAUDIT_OBJ=$(HERE)/fwaudit.o
VIR_LINE_OBJ=$(HERE)/vir_line.o
PORT_CONFIG_OBJ=$(HERE)/port_config.o
SET_MIRROR_OBJ=$(HERE)/set_mirror.o
TCPDUMP_OBJ=$(HERE)/tcpdump.o
TCS_OBJ=$(HERE)/tcs.o
#DDOS_OBJ=$(HERE)/ddos_app.o
REASS_OBJ=$(HERE)/reass.o
DDOS_FLAG_OBJ=$(HERE)/ddos_flag.o
DDOS_CTL_OBJ=$(HERE)/ddosctl.o
DPI_OBJ=$(HERE)/dpi_mgr.o
TCF_OBJ=traffic_count_flag.o
GSD_OBJ=get_statistics_data.o
GIT_OBJ=get_interface_type.o
TS_OBJ=ts.o
DPDKDEBUG_OBJ=dpdkdebug.o

CFLAGS:=-O2 -g -Wall -W -Wno-unused-parameter -Wno-unused-variable -Wno-unused-function\
	-I$(INC1) \
	-I$(INC2) \
	-I$(INC_NDPI)

LDFLAGS=-L$(LIB2) -ldpdk_bd \
	-L$(LIB1) -ldpdk  \
	-lpthread -ldl -lrt -lm -lbdpi -lext -lcrypto -lz -lzlog

LDFLAGS2=-L$(LIB2) -ldpdk_bd_ext


$(BRIDGE):$(BRIDGE_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^  $(LDFLAGS)

$(EXTCLIENT):$(EXTCLIENT_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^  $(LDFLAGS) $(LDFLAGS2)

$(EXTCLIENT_TEST):$(EXTCLIENT_TEST_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS2)

$(KNI):$(KNI_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(DAQ):$(DAQ_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)


$(DAQ2):$(DAQ2_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)
	
$(MULTIPLIER):$(MULTIPLIER_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(MIRROR_DPDK):$(MIRROR_DPDK_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)
	
$(USE_KERNEL):$(USE_KERNEL_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(DETECT_VIRUS):$(DETECT_VIRUS_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(KEY_WORD_FILTER):$(KEY_WORD_FILTER_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(DETECT_PORTSCAN):$(DETECT_PORTSCAN_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)
$(DETECT_VIRUS_FAST):$(DETECT_VIRUS_FAST_OBJ)
	@echo "$@-------------------->"
	 $(CC)   -o  $@   $^   $(LDFLAGS)
$(FWAUDIT):$(FWAUDIT_OBJ)
	@echo "$@-------------------->"
	 $(CC)   -o  $@   $^   $(LDFLAGS)

$(VIR_LINE):$(VIR_LINE_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(PORT_CONFIG):$(PORT_CONFIG_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(SET_MIRROR):$(SET_MIRROR_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(TCPDUMP):$(TCPDUMP_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(TCS):$(TCS_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

#$(DDOS):$(DDOS_OBJ)
#	@echo "$@-------------------->"
#	$(CC)   -o  $@   $^   $(LDFLAGS)

$(DDOS_FLAG):$(DDOS_FLAG_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(DDOS_CTL):$(DDOS_CTL_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(DPI):$(DPI_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(TCF):$(TCF_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(GSD):$(GSD_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(GIT):$(GIT_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)
	
$(REASS):$(REASS_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)
		
$(TS):$(TS_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)

$(DPDKDEBUG):$(DPDKDEBUG_OBJ)
	@echo "$@-------------------->"
	$(CC)   -o  $@   $^   $(LDFLAGS)  
   
%.o:%.c
	$(CC) -c $(CFLAGS) $< -o $@


.PHONY:clean
clean0: 
	rm -fr $(HERE)/*.o 

.PHONY:clean
clean:
	rm -fr $(EXTCLIENT) $(EXTCLIENT_TEST)  $(KNI) $(DAQ) $(DAQ2) $(MULTIPLIER) $(MIRROR_DPDK) $(USE_KERNEL) $(DETECT_VIRUS_FAST) $(DETECT_VIRUS) $(FWAUDIT) $(KEY_WORD_FILTER) $(DETECT_PORTSCAN) $(VIR_LINE) $(PORT_CONFIG) $(SET_MIRROR) $(TCPDUMP) $(TCS) $(REASS) $(DDOS_FLAG) $(DDOS_CTL) $(DPI) $(TCF) $(GSD) $(GIT) $(TS) $(DPDKDEBUG)
	rm -fr $(HERE)/*.o 
