
#ifndef __POLICYRUN_H__
#define __POLICYRUN_H__

#include "tse.h"

extern volatile uint8_t tce_ctl_flags;

#define TCE_STOP 1
#define TCE_KILL 2
#define TCE_DONE 4

#define IPTABLES_CMD "/usr/sbin/iptables"
#define TABLES "mangle"
#define NFQUEUE_CHAIN "NF_QUEUE_CHAIN"
#define RULE_CHAIN_NAME "TSE_CHAIN"

void TseCfgPrint(struct Tacticsevolve * te);

int PolicyConfigfileInit(struct Tacticsevolve * te);


#endif /*__POLICYRUN_H__*/



