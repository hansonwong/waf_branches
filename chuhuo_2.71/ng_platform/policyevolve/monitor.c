#include <stdio.h>
#include <sys/msg.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <signal.h>
#include <errno.h>
#include <time.h>
#include <sys/wait.h>
#include <mysql/mysql.h>

#include "monitor.h"
#include "thread.h"
#include "mem_manage.h"
#include "tse.h"
#include "policyrun.h"
#include "admin.h"
#include "util.h"
#include "log.h"
#include "rwini.h"


#define IPTABLES_PATH "/sbin"
#define RULE_CHAIN_NAME "TSE_CHAIN"

#define DO_RULES 1
//#define DO_IPTABLES_CLEAR 

static char dbc[DB_MAX][DB_MAX_STR];
static MYSQL *conn;

#define TRACE_MONITOR(level, fmt, args...) do {              \
	TSE_LOG(TSE_LOG_##level, MONITOR, fmt "\n", ## args);     \
} while(0)


typedef struct MonitorThreadVars_
{
    ThreadVars *tv;
	void * exdata;   /*public data*/
	char * buff;
	int size;
} MonitorThreadVars;

MonitorThreadVars MonitorThread = {0};

static int MonitorThreadInit(ThreadVars *tv, void *data);

static int MonitorThreadDeinit(ThreadVars *t, void *data);

static int MonitorLoop(ThreadVars *tv, void *data);

static void MonitorThreadExit(ThreadVars *tv, void *data);

void DataBaseInit()
{
	iniGetString("database","host",dbc[DB_HOST],DB_MAX_STR,"localhost");
	iniGetString("database","user",dbc[DB_USER],DB_MAX_STR,"root");
	iniGetString("database","pass",dbc[DB_PASS],DB_MAX_STR,"123456");
	iniGetString("database","base",dbc[DB_BASE],DB_MAX_STR,"db_firewall");
	iniGetString("database","port",dbc[DB_PORT],DB_MAX_STR,"0");
	iniGetString("database","sock",dbc[DB_SOCK],DB_MAX_STR,"/var/lib/mysql/mysql.sock");
	TRACE_MONITOR(INFO,"database info: host %s user %s pass %s database %s port %s sock %s",
		               dbc[DB_HOST],dbc[DB_USER],dbc[DB_PASS],dbc[DB_BASE],dbc[DB_PORT],dbc[DB_SOCK]);
}
void DataBaseTabInit()
{
#ifdef DO_IPTABLES_CLEAR
	MYSQL * ct = mysql_init(NULL);
	if(ct == NULL){
		TRACE_MONITOR(ERR,"init database fail! %s", mysql_error(conn));
	}
	if (!mysql_real_connect(ct,dbc[DB_HOST],dbc[DB_USER],dbc[DB_PASS],dbc[DB_BASE],atoi(dbc[DB_PORT]),dbc[DB_SOCK],0)){
		TRACE_MONITOR(ERR,"connect database fail! %s", mysql_error(conn));
	}
	if(mysql_query(ct,"delete from m_tbauto_strategy_exception")){
		TRACE_MONITOR(ERR,"delete record fail! %s", mysql_error(conn));
	}
	mysql_close(ct);
#endif
}

void MonitorModuleRegister(void) 
{
	/*Global Vars init*/
	/*module*/
	module[MONITOR_MODULE].ThreadInit   = MonitorThreadInit;
	module[MONITOR_MODULE].ThreadDeinit = MonitorThreadDeinit;
	module[MONITOR_MODULE].ThreadLoop   = MonitorLoop;
	module[MONITOR_MODULE].ThreadExit   = MonitorThreadExit;
}

static int MonitorVerdict(const uint32_t ip_src,
	                          const uint32_t ip_dst,
	                          const uint32_t rejectime,
	                          int type)
{
	static int tseid = 0;
	char src[32];
	char dst[32];
	sprintf(src,"%u.%u.%u.%u",IPQUAD(ip_src));
	sprintf(dst,"%u.%u.%u.%u",IPQUAD(ip_dst));
	char rule[512];
	char timestart[128];
	char timestop[128];

	struct tm *pstart,*pstop;
	time_t tstart;
	time_t tstop;
#ifdef DO_RULES	
	pid_t status;
#endif
	
	time(&tstart);
	pstart = localtime(&tstart);
	strftime(timestart,sizeof(timestart),"%H:%M:%S",pstart);
	
	tstop = tstart + rejectime;
	pstop = localtime(&tstop);
	strftime(timestop,sizeof(timestop),"%H:%M:%S",pstop);
	
	//printf("%lu  %lu %d\n",tstart,tstop,rejectime);
	sprintf(rule,"%s/iptables -A %s -s %s -d %s -m time --kerneltz --timestart %s --timestop %s -m limit --limit 3/s -j LOG --log-level 4 --log-prefix=\"ipt_log=DROP \"",
		          IPTABLES_PATH,
		          RULE_CHAIN_NAME,
		          src,
		          dst,
		          timestart,
		          timestop);
#ifdef DO_RULES	
	status = system(rule);
        if (-1 == status){
		TRACE_MONITOR(ERR,"call system() error!");
        }  
        else  
        {
    	        if (WIFEXITED(status)){
			if (0 == WEXITSTATUS(status)){  
                                TRACE_MONITOR(INFO,"do iptables rule successfully!");  
                        }     
                        else{  
                                TRACE_MONITOR(ERR,"do iptables rule fail,exit code: %d\n", WEXITSTATUS(status));
				return -1;
                        }  
                }
	}
#endif
	sprintf(rule,"%s/iptables -A %s -s %s -d %s -m time --kerneltz --timestart %s --timestop %s -j DROP",
		          IPTABLES_PATH,
		          RULE_CHAIN_NAME,
		          src,
		          dst,
		          timestart,
		          timestop);
	TRACE_MONITOR(INFO,"do iptables rule: %s", rule);
#ifdef DO_RULES	
	status = system(rule);
        if (-1 == status){
		TRACE_MONITOR(ERR,"call system() error!");
        }  
        else  
        {
    	        if (WIFEXITED(status)){
			if (0 == WEXITSTATUS(status)){  
                                TRACE_MONITOR(INFO,"do iptables rule successfully!");  
                        }     
                        else{  
                                TRACE_MONITOR(ERR,"do iptables rule fail,exit code: %d\n", WEXITSTATUS(status));
				return -1;
                        }  
                }
	}
#endif
	char sqlcmd[512];
	char name[DB_MAX_STR];
	char memo[DB_MAX_STR]={0};
	sprintf(name,"tse-%d",tseid++);
	sprintf(sqlcmd,"insert into m_tbauto_strategy_exception(sName,sSourceIP,sTargetIP,iLifeTime,iStopTime,iStatus,iStartTime,iEndTime) "
		           "values('%s','%s','%s',now(),%d,%d,'%s','%s')",
		           name,src,dst,rejectime/TSE_REJECTIME_UNIT,type,timestart,timestop);
	if(mysql_query(conn,sqlcmd)){
		TRACE_MONITOR(ERR,"insert into database fail! %s", mysql_error(conn));
	}
	return 0;
}

static int MonitorThreadInit(ThreadVars *tv, void *data)
{
	int ret;
	sigset_t sigs;
	sigfillset(&sigs);
	pthread_sigmask(SIG_BLOCK, &sigs, NULL);
	MonitorThreadVars * mtv  = (MonitorThreadVars *) data;
	ThreadPool	      * pool = (ThreadPool *)tv->threadpool;
	mtv->tv 	= tv;
	mtv->exdata = pool->data;

	struct Tacticsevolve * te = (struct Tacticsevolve *)mtv->exdata;
	te->cb = MonitorVerdict;
	
	conn = mysql_init(NULL);
	if(conn == NULL){
		TRACE_MONITOR(ERR,"init database fail! %s", mysql_error(conn));
	}
	if (!mysql_real_connect(conn, dbc[DB_HOST],   
                                  dbc[DB_USER],
                                  dbc[DB_PASS],
                                  dbc[DB_BASE],
                                  atoi(dbc[DB_PORT]),
                                  dbc[DB_SOCK],0)){
		TRACE_MONITOR(ERR,"connect database fail! %s", mysql_error(conn));
	}
#ifdef DO_IPTABLES_CLEAR
	char rule[128];
	sprintf(rule,"%s/iptables -N %s",IPTABLES_PATH,RULE_CHAIN_NAME);
	TRACE_MONITOR(INFO,"do iptables rule: %s", rule);
	system(rule);
	sprintf(rule,"%s/iptables -I FORWARD -j %s",IPTABLES_PATH,RULE_CHAIN_NAME);
	TRACE_MONITOR(INFO,"do iptables rule: %s", rule);
	system(rule);
#endif	
	return 0;
}

static int MonitorLoop(ThreadVars *tv, void *data)
{
	int ret;
	struct Tacticsevolve * te;
	MonitorThreadVars    * mtv = (MonitorThreadVars *)data;
	te = (struct Tacticsevolve *)mtv->exdata;
    while(1) {
        if (tce_ctl_flags != 0) {
			mtv->buff = NULL;
			mtv->size = 0;
			if(conn != NULL){
				mysql_close(conn);
				conn = NULL;
			}
            break;
        }
		usleep(50);
		TseAdminVerdict(te);
    }
	return 0;	
}

static int MonitorThreadDeinit(ThreadVars *tv, void *data)
{
	MonitorThreadVars * mtv = (MonitorThreadVars *)data;

	mtv->buff = NULL;
	mtv->size = 0;
	if(conn != NULL){
		mysql_close(conn);
		conn = NULL;
	}
	
	return 0;
}

static void MonitorThreadExit(ThreadVars *tv, void *data)
{
	char rule[128];
#ifdef DO_IPTABLES_CLEAR	
	sprintf(rule,"%s/iptables -D FORWARD -j %s",IPTABLES_PATH,RULE_CHAIN_NAME);
	TRACE_MONITOR(INFO,"do iptables rule: %s", rule);
	system(rule);
	sprintf(rule,"%s/iptables -F %s",IPTABLES_PATH,RULE_CHAIN_NAME);
	TRACE_MONITOR(INFO,"do iptables rule: %s", rule);
	system(rule);
	sprintf(rule,"%s/iptables -X %s",IPTABLES_PATH,RULE_CHAIN_NAME);
	TRACE_MONITOR(INFO,"do iptables rule: %s", rule);
	system(rule);
#endif
	TRACE_MONITOR(INFO,"Monitor Thread exit,end!");
}

static MonitorThreadVars * MonitorGetThreadVar()
{
	return &MonitorThread;
}

int RunMonitorModule(ThreadPool * tpool)
{
    ThreadVars *tv = ThreadAlloc(tpool);
	if(tv == NULL){
		TRACE_MONITOR(WARNING,"%s():install Monitor thread fail!\n",__func__);
		return -1;
	}

	memset(tv, 0, sizeof(ThreadVars));
	snprintf(tv->name, sizeof(tv->name), "Monitor-DO-MSG");

	/* default state for every newly created thread */
	ThreadsSetFlag(tv,THV_PAUSE);
	ThreadsSetFlag(tv,THV_USE);

	/* default aof for every newly created thread */
	tv->trf     = &module[MONITOR_MODULE];
	tv->aof     = THV_RESTART_THREAD;
	tv->id      = GetThreadID();
	tv->type    = TVT_MGMT;
	tv->tm_func = ThreadRun;

	tv->data    = MonitorGetThreadVar();
	tv->threadpool = (void *)tpool;

	if (ThreadStart(tv) != 0) {
		TRACE_MONITOR(ERR,"start thread %s fail!\n",tv->name);
		exit(-1);
	}
    return 0;
}






