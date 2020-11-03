#include <stdio.h>
#include <sys/msg.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <signal.h>
#include <errno.h>

#include "thread.h"
#include "mem_manage.h"
#include "tse.h"
#include "policyrun.h"
#include "admin.h"
#include "log.h"

#define TRACE_ADMIN(level, fmt, args...) do {              \
	TSE_LOG(TSE_LOG_##level, ADMIN, fmt "\n", ## args);     \
} while(0)


typedef struct AdminThreadVars_
{
    ThreadVars *tv;
	void * exdata;   /*public data*/
	int policy_ctl_msgid;
} AdminThreadVars;

AdminThreadVars AdminThread = {NULL,NULL,-1};

static int AdminThreadInit(ThreadVars *tv, void *data);

static int AdminThreadDeinit(ThreadVars *t, void *data);

static int AdminLoop(ThreadVars *tv, void *data);

static void AdminThreadExit(ThreadVars *tv, void *data);


void AdminModuleRegister(void) 
{
	/*Global Vars init*/
	/*module*/
	module[ADMIN_MODULE].ThreadInit   = AdminThreadInit;
	module[ADMIN_MODULE].ThreadDeinit = AdminThreadDeinit;
	module[ADMIN_MODULE].ThreadLoop   = AdminLoop;
	module[ADMIN_MODULE].ThreadExit   = AdminThreadExit;
}

static int AdminMsgQueueInit()
{
	int ret = -1;
	int policy_ctl_msgid;
  //int ret = msgget((key_t)MSG_KEY_T, 0666 | IPC_CREAT | IPC_EXCL);
	ret = msgget((key_t)POLICY_MSG_KEY_T, 0666 | IPC_CREAT);

		
	if( ret == -1){
		TRACE_ADMIN(ERR,"get message queue id failed with error: %d", errno);
	    //rte_exit(EXIT_FAILURE,"get message queue id failed with error: %d\n",errno);
		return -1;
	}
	policy_ctl_msgid = ret;
	TRACE_ADMIN(INFO,"%s():create message queue ok!", __func__);
	
	struct msqid_ds msg_info;
	
	ret = msgctl(policy_ctl_msgid, IPC_STAT, &msg_info);
	if( ret < 0 ){
		TRACE_ADMIN(ERR,"get message queue stat failed with error: %d", errno);
		return policy_ctl_msgid;
	}
	
	TRACE_ADMIN(INFO,"current number of bytes on queue is %d",(int)msg_info.msg_cbytes);
	TRACE_ADMIN(INFO,"number of messages in queue is %d",(int)msg_info.msg_qnum);
	TRACE_ADMIN(INFO,"max number of bytes on queue is %lu",(uint64_t)(msg_info.msg_qbytes));
	TRACE_ADMIN(INFO,"pid of last msgsnd is %d",(int)(msg_info.msg_lspid));
	TRACE_ADMIN(INFO,"pid of last msgrcv is %d",(int)(msg_info.msg_lrpid));
	TRACE_ADMIN(INFO,"last msgsnd time is %s", ctime(&(msg_info.msg_stime)));
	TRACE_ADMIN(INFO,"last msgrcv time is %s", ctime(&(msg_info.msg_rtime)));
	TRACE_ADMIN(INFO,"last change time is %s", ctime(&(msg_info.msg_ctime)));
	TRACE_ADMIN(INFO,"msg uid is %d",msg_info.msg_perm.uid);
	TRACE_ADMIN(INFO,"msg gid is %d",msg_info.msg_perm.gid);

	return policy_ctl_msgid;
}


typedef void (*BMPort)(bitmap_set * map, int idx);
	
static void BMPortAdd(bitmap_set * map, int idx)
{
	BITMAP_SET(map,idx);
}

static void BMPortDel(bitmap_set * map, int idx)
{
	BITMAP_CLEAR(map,idx);
}

static int AdminPortParse(struct Tacticsevolve * te,char * portstr,BMPort bmport)
{
	int ret;
	
	char * eport = NULL;
	char * pport = portstr;
	char buf[2][16];
	unsigned short minport;
	unsigned short maxport;

	if(portstr == NULL) return 0;

	while((eport=strsep(&pport,","))!=NULL){
		if(strlen(eport)>=12){
			TRACE_ADMIN(WARNING,"port %s error",eport);
			continue;
		}
		ret = sscanf(eport,"%[0-9]-%[0-9]",buf[0],buf[1]);
		if(ret == 1){
			minport = atoi(buf[0]);
			bmport(te->porttable,minport);
		}
		else if(ret == 2){
			minport = atoi(buf[0]);
			maxport = atoi(buf[1]);
			if(minport > maxport){
				minport = minport ^ maxport;
				maxport = minport ^ maxport;
				minport = minport ^ maxport;
			}
			int index;
			for(index = minport; index <=  maxport; index++){
				bmport(te->porttable,index);
			}
		}
		else {
			TRACE_ADMIN(WARNING,"port %s error",eport);
			continue;
		}
	}
	return 0;
}

static int AdminPortConfig(struct policy_ctl_msg_ds * param, struct Tacticsevolve * te)
{	
	if((param->cmdvalue & POLICY_VALUE_PORT) == 0) return 0;
	
	memset(te->porttable,0,((MAX_PORT_NUMS / BITMAP_PER_SIZE) * sizeof(bitmap_set)));

	AdminPortParse(te,param->portstr,BMPortAdd);
	
	return 0;
}

static int AdminPortAdd(struct policy_ctl_msg_ds * param, struct Tacticsevolve * te)
{	
	if((param->cmdvalue & POLICY_VALUE_PORT) == 0) return 0;

	AdminPortParse(te,param->portstr,BMPortAdd);
	
	return 0;
}

static int AdminPortDel(struct policy_ctl_msg_ds * param, struct Tacticsevolve * te)
{	
	if((param->cmdvalue & POLICY_VALUE_PORT) == 0) return 0;
	
	AdminPortParse(te,param->portstr,BMPortDel);
	
	return 0;
}


static int AdminParamConfig(struct policy_ctl_msg_ds * param,
	                               struct TeParam *tp)
{
	if(param->cmdvalue & POLICY_VALUE_INTERVAL){
		tp->interval = param->interval;
	}
	if(param->cmdvalue & POLICY_VALUE_THRESHOLD){
		uint32_t threshold = param->threshold;
		if(param->type_operid == TSE_TRAFFIC){
			threshold = (threshold > TSE_TRAFFIC_MAX_VALUE) ? TSE_TRAFFIC_MAX_VALUE : threshold;
			threshold *= TSE_TRAFFIC_UNIT;
		}
		tp->threshold= threshold;
	}
	if(param->cmdvalue & POLICY_VALUE_MAXTIMES){
		tp->max_times= param->max_times;
	}
	return 0;
}
	
static int AdminSysOper(struct policy_ctl_msg_ds * param,
	                          AdminThreadVars *atv)
{
	ThreadPool * pool = atv->tv->threadpool;
	struct Tacticsevolve * te = (struct Tacticsevolve *)atv->exdata;

	if(param->sys_operid == 0){//start
		PolicyConfigfileInit(te);
		te->rejectime = param->rejectime * TSE_REJECTIME_UNIT;
		TseCfgPrint(te);
		ThreadContinueFamily(pool,TVT_PPT);
		ThreadContinueFamily(pool,TVT_MGMT);
		
	}else if(param->sys_operid == 1){//stop
	
		ThreadPauseFamily(pool,TVT_MGMT);
		ThreadPauseFamily(pool,TVT_PPT);
	}
	
	return 0;
}


static int AdminUserOper(struct policy_ctl_msg_ds * param, struct Tacticsevolve * te)
{
	if(param->isup == POLICY_UP){
		te->enable[param->type_operid] = 1;
	}
	else if(param->isup == POLICY_DOWN){
		te->enable[param->type_operid] = 0;
	}

	/*get default config from file*/
	
	switch(param->type_operid){
		case TSE_PORT:
			AdminPortConfig(param,te);
			break;
		case TSE_TRAFFIC:
			AdminParamConfig(param,&te->traffic);
			break;
		case TSE_PROTO:
			AdminParamConfig(param,&te->proto);
			break;
		case TSE_CONNECT:
			AdminParamConfig(param,&te->ct);
			break;
		default:
			return -1;
			break;
	}
	return 0;
}

static int AdminMsgParse(struct policy_ctl_msg_ds * param, AdminThreadVars *atv)
{
	int mark;
	
	struct Tacticsevolve * te = (struct Tacticsevolve *)atv->exdata;
	
	switch(param->cmd){
		
		case CMD_SYSTEM_OPERATOR:
			mark = AdminSysOper(param,atv);
			break;
		case CMD_TYPE_OPERATOR:
			mark = AdminUserOper(param,te);
			break;
		case CMD_PORT_ADD:
			mark = AdminPortAdd(param,te);
			break;
		case CMD_PORT_DEL:
			mark = AdminPortDel(param,te);
			break;
		default:
			mark = -1;
			break;
	}
	TseCfgPrint(te);
	return mark;
}


static int AdminMsgHandler(AdminThreadVars *atv)
{
	int ret;
	int mark;
	struct policy_ctl_msgbuf recvbuf;
	struct policy_ctl_msgbuf sendbuf;
	
	size_t recvlength;
	size_t sendlength;
	
	memset(&recvbuf,0,sizeof(struct policy_ctl_msgbuf));
	memset(&sendbuf,0,sizeof(struct policy_ctl_msgbuf));
	recvlength = sizeof(struct policy_ctl_msgbuf) - sizeof(long);
	sendlength = sizeof(struct policy_ctl_msgbuf) - sizeof(long);
	/*msgtype = 0 the first msg of "all msg"
	  msgtype > 0 the first msg of "the same msg type"
	  msgtype < 0 the first msg of "type <= |msgtype|"
	*/
	ret = msgrcv(atv->policy_ctl_msgid,(void*)&recvbuf,recvlength,1,IPC_NOWAIT);
	
	if(ret < 0) {
		//printf("errno:%d[%d,%d,%d,%d,%d,%d,%d,%d]\n",errno,E2BIG,EACCES,EAGAIN,EFAULT,EIDRM,EINTR,EINVAL,ENOMSG);
		if(errno == ENOMSG) return 0;
		TRACE_ADMIN(ERR,"%s():recv message fail with errno=%d",__func__,errno);
		return -1;
	}
	TRACE_ADMIN(WARNING,"%s():recv policy-ctl message succ!",__func__);
	
	struct policy_ctl_msg_ds param;
	memcpy(&param,recvbuf.mtext,sizeof(struct policy_ctl_msg_ds));

	sendbuf.mtype = param.mtype;
	
	mark = AdminMsgParse(&param,atv);
	
	snprintf(sendbuf.mtext,sizeof(sendbuf.mtext),"%d",mark);
	TRACE_ADMIN(NOTICE,"%s():send reply message %s",__func__,sendbuf.mtext);
	ret = msgsnd(atv->policy_ctl_msgid,(void*)&sendbuf,sendlength,0); /*IPC_NOWAIT*/

	if(ret < 0){
		TRACE_ADMIN(ERR,"%s():send reply message fail",__func__);
		return -1;
	}
	return 0;
}

static int AdminThreadInit(ThreadVars *tv, void *data)
{
	sigset_t sigs;
	sigfillset(&sigs);
	pthread_sigmask(SIG_BLOCK, &sigs, NULL);

	AdminThreadVars * atv  = (AdminThreadVars *) data;
	ThreadPool	    * pool = (ThreadPool *)tv->threadpool;
	atv->tv 	= tv;
	atv->exdata = pool->data;
	
	int ret = AdminMsgQueueInit();
	if (ret < 0) {
		TRACE_ADMIN(ERR,"%s():admin thread %s failed to initialize!",__func__,tv->name);
		return -1;
	}
	atv->policy_ctl_msgid = ret;
	return 0;
}

static int AdminLoop(ThreadVars *tv, void *data)
{
    AdminThreadVars * atv = (AdminThreadVars *)data;
	int ret;
    while(1) {
        if (tce_ctl_flags != 0) {
			
			if(atv->policy_ctl_msgid >= 0){
				ret = msgctl(atv->policy_ctl_msgid,IPC_RMID,NULL);
				if(ret < 0){
					TRACE_ADMIN(ERR,"%s():rm message queue error!",__func__);
				}
				else {
					TRACE_ADMIN(NOTICE,"%s():rm message queue ok!",__func__);
					atv->policy_ctl_msgid = -1;
				}
			}
            break;
        }
        AdminMsgHandler(atv);
		usleep(50);
    }
	return 0;	
}

static int AdminThreadDeinit(ThreadVars *tv, void *data)
{
	AdminThreadVars * atv = (AdminThreadVars *)data;
	
	if(atv->policy_ctl_msgid < 0) return 0;
	
	int ret = msgctl(atv->policy_ctl_msgid,IPC_RMID,NULL);
	if(ret < 0){
		TRACE_ADMIN(ERR,"%s():rm message queue error!",__func__);
	}
	else {
		TRACE_ADMIN(NOTICE,"%s():rm message queue ok!",__func__);
	}
	atv->policy_ctl_msgid = -1;
	return 0;
}

static void AdminThreadExit(ThreadVars *tv, void *data)
{
	TRACE_ADMIN(NOTICE,"%s():Admin Thread exit,end!",__func__);
}

static AdminThreadVars * AdminGetThreadVar()
{
	return &AdminThread;
}

int RunAdminDoMsg(ThreadPool * tpool)
{
    ThreadVars *tv = ThreadAlloc(tpool);
	if(tv == NULL){
		TRACE_ADMIN(ERR,"%s():install Admin thread fail!",__func__);
		return -1;
	}

	memset(tv, 0, sizeof(ThreadVars));
	snprintf(tv->name, sizeof(tv->name), "Admin-DO-MSG");

	/* default state for every newly created thread */
	ThreadsSetFlag(tv,THV_PAUSE);
	ThreadsSetFlag(tv,THV_USE);

	/* default aof for every newly created thread */
	tv->trf     = &module[ADMIN_MODULE];
	tv->aof     = THV_RESTART_THREAD;
	tv->id      = GetThreadID();
	tv->type    = TVT_CMD;
	tv->tm_func = ThreadRun;

	tv->data    = AdminGetThreadVar();
	tv->threadpool = (void *)tpool;

	if (ThreadStart(tv) != 0) {
		TRACE_ADMIN(ERR,"%s():start admin thread %s fail!",__func__,tv->name);
		exit(-1);
	}
    return 0;
}



