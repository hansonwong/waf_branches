
#ifndef _ADMIN_H_
#define _ADMIN_H_

#include "thread.h"

#define POLICY_MSG_KEY_T 1682493570
#define MSG_MAX_SIZE     640

#define POLICY_UP   2
#define POLICY_DOWN 1

#define CMD_NONE			    0x00000000U
#define CMD_SYSTEM_OPERATOR     0x00000001U
#define CMD_TYPE_OPERATOR       0x00000002U
#define CMD_PORT_ADD            0x00000004U
#define CMD_PORT_DEL            0x00000008U

#define POLICY_VALUE_INTERVAL   0x0001
#define POLICY_VALUE_THRESHOLD  0x0002
#define POLICY_VALUE_MAXTIMES   0x0004
#define POLICY_VALUE_REJECTIME  0x0008
#define POLICY_VALUE_PORT       0x0010

#define MSG_TSE_MAX 4

struct policy_ctl_msgbuf
{
	long mtype;
	char mtext[MSG_MAX_SIZE];
};

struct policy_ctl_msg_ds {
	long mtype;
	int cmd;
	int sys_operid;
	//int isauto;
	int type_operid;
	int isup;
	/*
	unsigned short minport;
	unsigned short maxport;
	*/
	unsigned interval;
	unsigned threshold;
	unsigned max_times;
	unsigned rejectime;
	unsigned cmdvalue;
	char portstr[512];
}__attribute__((__packed__));


void AdminModuleRegister(void);
int RunAdminDoMsg(ThreadPool * tpool);



#endif /*_ADMIN_H_*/


