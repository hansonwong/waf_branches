#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <netdb.h>
#include <string.h>
#include <sys/time.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/signal.h>
#include <sys/queue.h>
#include <getopt.h>

#include <asm/byteorder.h>
#include <linux/netfilter.h>
#include <linux/netfilter/nfnetlink.h>
#include <linux/types.h>
#include <linux/netfilter/nfnetlink_queue.h>
#include <libnetfilter_queue/libnetfilter_queue.h>

#include "nfq.h"
#include "connt.h"
#include "admin.h"
#include "monitor.h"
#include "rwini.h"
#include "mem_manage.h"
#include "policyrun.h"
#include "thread.h"
#include "log.h"

#define TRACE_MAIN(level, fmt, args...) do {              \
	TSE_LOG(TSE_LOG_##level, MAIN, fmt "\n", ## args);     \
} while(0)


volatile uint8_t tce_ctl_flags = 0;

#define DEFAULT_POLICYEVOLVE_PIDFILE  "/var/run/policyevolve.pid"
#define DEFAULT_POLICYEVOLVE_CFGFILE  "/var/tmp/policyevolve.ini"
	
static char  pidfilename[256] = DEFAULT_POLICYEVOLVE_PIDFILE;
static char  configfile[256]  = DEFAULT_POLICYEVOLVE_CFGFILE;
static char *progname;

static ThreadPool * pool;
static const char * inicfgfile;

static int qidstart;
static int qidend;

const char policystopt[] ="BF:Q:L:Hh";

const struct option policylgopt[]=
{
	{.name = "background",  .has_arg = 1, .val = 'B'},
	{.name = "config file", .has_arg = 1, .val = 'F'},
	{.name = "queue",       .has_arg = 1, .val = 'Q'},
	{.name = "loglevel",    .has_arg = 1, .val = 'L'},
	{.name = "Help",        .has_arg = 1, .val = 'H'},
	{.name = "help",        .has_arg = 1, .val = 'h'},
	{NULL},
};

static void exit_printhelp(const char * proname)
{
	printf("HOW TO USE %s\n"
		   "Usage: %s -[S] [start|stop|restart] [AUTO]\n"
           "       %s -[T] [port|traffic|protocol|connect] [up|down]\n"
           "       %s -[A] [port]\n"
           "eg.\n"
           "       %s -S start AUTO -r 60\n"
           "       %s -T port up -p 10-100\n"
           "       %s -T traffic up -i 60 -t 10 -m 2\n"
           "       %s -P port -p 300-400\n",
	       proname,proname,proname,
	       proname,proname,proname,
	       proname,proname);
	
	printf(
		   "options:\n"
	 	   "  --interval(seconds)   -i  eg. -i 60\n"
	 	   "  --threshold           -t  eg. -t 1000\n"
	 	   "  note: if it is traffic, the unit is Mb\n"
	 	   "  --max times           -m  eg. -m 2\n"
		   "  --reject time(minute) -r  eg. -r 60\n"
		   "  --port                -p  eg. -p 100-200 or 100\n"
		   "  --help                -h\n");
	exit(0);
}

static int TseExecCmd(const char * cmdstr)
{
	pid_t status = system(cmdstr);
    if (-1 == status){
		return -1;
    }  
    else{
    	if (WIFEXITED(status)){
			if (0 == WEXITSTATUS(status)) return 0; 
            else return -1;
        }
	}
	return 0;
}

static int TseInstallNFQueue()
{
	char cmdstr[256];
	sprintf(cmdstr,"%s -t %s -I %s -j NFQUEUE --queue-balance %d:%d",
		            IPTABLES_CMD,TABLES,NFQUEUE_CHAIN,qidstart,qidend);
	if(TseExecCmd(cmdstr)<0){
		TRACE_MAIN(ERR,"FAIL: %s",cmdstr);
		return -1;
	}
	TRACE_MAIN(INFO,"OK  : %s",cmdstr);
    sprintf(cmdstr,"%s -t %s -A FORWARD -j %s",IPTABLES_CMD,TABLES,NFQUEUE_CHAIN);
	if(TseExecCmd(cmdstr)<0){
		TRACE_MAIN(ERR,"FAIL: %s",cmdstr);
		return -1;
	}
	TRACE_MAIN(INFO,"OK  : %s",cmdstr);
	return 0;
}

static void TseUnInstallNFQueue()
{
	static int cnts = 0;
    
	if(cnts++ > 0) return;
	char cmdstr[256];
	sprintf(cmdstr,"%s -t %s -F %s",IPTABLES_CMD,TABLES,NFQUEUE_CHAIN);
	if(TseExecCmd(cmdstr)<0) 
		TRACE_MAIN(ERR,"FAIL: %s",cmdstr);
	else 
		TRACE_MAIN(INFO,"OK  : %s",cmdstr);
        sprintf(cmdstr,"%s -t %s -D FORWARD -j %s",IPTABLES_CMD,TABLES,NFQUEUE_CHAIN);
	if(TseExecCmd(cmdstr)<0)
		TRACE_MAIN(ERR,"FAIL: %s",cmdstr);
	else
		TRACE_MAIN(INFO,"OK  : %s",cmdstr);
}

static void TseStartCheck()
{
	char cmdstr[256];
	sprintf(cmdstr,"/home/ng_platform/policyevolve/tsecheck.sh &");
	if(TseExecCmd(cmdstr)<0) 
		TRACE_MAIN(ERR,"FAIL: %s",cmdstr);
	else
		TRACE_MAIN(INFO,"OK  : %s",cmdstr);
}
	
void TseCfgPrint(struct Tacticsevolve * te)
{
	char * on;
	char * ptype;
	
	TRACE_MAIN(DEBUG,"[system]:reject time %u(s)",te->rejectime);

	on = te->enable[TSE_PORT] ? "on" : "off";
	if(te->portflag & SRC_PORT) ptype="src";
	if(te->portflag & DST_PORT) ptype="dst";
	if(te->portflag & ALL_PORT) ptype="all";
	TRACE_MAIN(DEBUG,"[port]:enable %s limitbytes %u(B) porttype %s",on,te->limitbytes,ptype);	

	int i;
	int start = -1;
	for (i = 0; i < MAX_PORT_NUMS; i++){
		if(BITMAP_TEST(te->porttable,i) && start < 0){
			start = i;
		}
		if(!BITMAP_TEST(te->porttable,i) && start >= 0){
			TRACE_MAIN(DEBUG,"[port]:none exception port %d-%d",start,i-1);
			start = -1;
		}
	}

	on = te->enable[TSE_TRAFFIC] ? "on" : "off";
	TRACE_MAIN(DEBUG,"[traffic]:enable %s interval %u(s) max times %u threshold %u(MB)",on,
		                                           te->traffic.interval/TSE_TIME_UNIT,
		                                           te->traffic.max_times,
		                                           te->traffic.threshold/TSE_TRAFFIC_UNIT);

	on = te->enable[TSE_PROTO] ? "on" : "off";
	TRACE_MAIN(DEBUG,"[protocol]:enable %s interval %u(s) max times %u threshold %u",on,
		                                           te->proto.interval/TSE_TIME_UNIT,
		                                           te->proto.max_times,
		                                           te->proto.threshold);

	on = te->enable[TSE_CONNECT] ? "on" : "off";
	TRACE_MAIN(DEBUG,"[connects]:enable %s interval %u(s) max times %u threshold %u",on,
		                                           te->ct.interval/TSE_TIME_UNIT,
		                                           te->ct.max_times,
		                                           te->ct.threshold);
}

static int TsePortParse(struct Tacticsevolve * te,char *port_str)
{
	char buf[2][16];
	unsigned short minport;
	unsigned short maxport;
	
	if (strlen(port_str)>=12){
		goto err;
	}
	
	TRACE_MAIN(DEBUG,"parse port : %s",port_str);
	
	int res = sscanf(port_str,"%[0-9]-%[0-9]",buf[0],buf[1]);
	if(res == 1){
		minport = atoi(buf[0]);
		BITMAP_SET(te->porttable,minport);
	}
	else if(res == 2){
		minport = atoi(buf[0]);
		maxport = atoi(buf[1]);
		if(minport > maxport){
			minport = minport ^ maxport;
			maxport = minport ^ maxport;
			minport = minport ^ maxport;
		}
		int index;
		for(index = minport; index <=  maxport; index++){
			BITMAP_SET(te->porttable,index);
		}
	}
	else goto err;
	
	return 0;
err:
	return -1;
}

static void TseCommPortProtoInit()
{
	int ret;
	ret = TseCommPortProto();
	TRACE_MAIN(INFO,":load common port proto %d",ret); 
	return;
}

static void TsePortInit(struct Tacticsevolve * te)
{
	int ret;
	char portstr[2049];
	iniGetString("port","eport",portstr,2048,TSE_DEFAULT_EPORT);
	TRACE_MAIN(DEBUG,"Get exception port %s",portstr);
	char * eport = NULL;
	char * pport = portstr;
	
	while((eport=strsep(&pport,","))!=NULL){
		ret = TsePortParse(te,eport);
		if(ret == 0) TRACE_MAIN(DEBUG,"%s():load port %s",__func__,eport); 
	}
}

static void TseCfgInit(struct Tacticsevolve * te)
{
	uint32_t rt = iniGetInt("system","reject time",TSE_DEFAULT_REJECT);
	te->rejectime = rt * TSE_REJECTIME_UNIT;
	
	te->enable[TSE_PORT]    = !!iniGetInt("port","enable",TSE_ENABLE);
	te->enable[TSE_TRAFFIC] = !!iniGetInt("traffic","enable",TSE_ENABLE);
	te->enable[TSE_PROTO]   = !!iniGetInt("protocol","enable",TSE_ENABLE);
	te->enable[TSE_CONNECT] = !!iniGetInt("connects","enable",TSE_ENABLE);

	te->limitbytes = iniGetInt("port","limitbytes",PORT_LIMIT_BYTES) * 1024;
	if(te->limitbytes > (PORT_LIMIT_BYTES * 10))	
		te->limitbytes = PORT_LIMIT_BYTES * 10;
	char ptype[16];
	iniGetString("port","porttype",ptype,16,TSE_DEFAULT_PORTTYPE);
	if(strncmp("all",ptype,3)==0)
		te->portflag |= ALL_PORT;
	else if(strncmp("src",ptype,3)==0)
		te->portflag |= SRC_PORT;
	else if(strncmp("dst",ptype,3)==0)
		te->portflag |= DST_PORT;
	
	te->traffic.interval    = iniGetInt("traffic","interval",TRAFFIC_INTERVALS) * TSE_TIME_UNIT;
	te->traffic.max_times   = iniGetInt("traffic","max_times",TRAFFIC_MAX_TIMES);
	uint32_t threshold		= iniGetInt("traffic","threshold",TRAFFIC_THRESHOLD);
	threshold               = (threshold > TSE_TRAFFIC_MAX_VALUE) ? TSE_TRAFFIC_MAX_VALUE : threshold;
	te->traffic.threshold   = threshold * TSE_TRAFFIC_UNIT;

	te->proto.interval      = iniGetInt("protocol","interval",PROTOCO_INTERVALS) * TSE_TIME_UNIT;
	te->proto.max_times     = iniGetInt("protocol","max_times",PROTOCO_MAX_TIMES);
	te->proto.threshold     = iniGetInt("protocol","threshold",PROTOCO_THRESHOLD);

	te->ct.interval         = iniGetInt("connects","interval",CONNECT_INTERVALS) * TSE_TIME_UNIT;
	te->ct.max_times        = iniGetInt("connects","max_times",CONNECT_MAX_TIMES);
	te->ct.threshold        = iniGetInt("connects","threshold",CONNECT_THRESHOLD);
	
}

static int TseLogLevelParse(const char * loglevel)
{
	if(loglevel == NULL ) return TSE_LOG_DEFAULT;
	
	if(strcmp("EMERG",loglevel)==0) return TSE_LOG_EMERG;
	if(strcmp("ALERT",loglevel)==0) return TSE_LOG_ALERT;
	if(strcmp("CRIT",loglevel)==0)  return TSE_LOG_CRIT;
	if(strcmp("ERR",loglevel)==0) return TSE_LOG_ERR;
	if(strcmp("WARNING",loglevel)==0) return TSE_LOG_WARNING;
	if(strcmp("NOTICE",loglevel)==0) return TSE_LOG_NOTICE;
	if(strcmp("INFO",loglevel)==0) return TSE_LOG_INFO;
	if(strcmp("DEBUG",loglevel)==0) return TSE_LOG_DEBUG;
	
	return TSE_LOG_DEFAULT;
}

static int TseQueueParse(const char * str)
{
	char buf[2][32];
	int minqueue = 0;
	int maxqueue = 0;
	int ret;

	char queuestr[32];

	if(str == NULL){
		if(iniFileLoad(inicfgfile) < 0){
			TRACE_MAIN(ERR,"Load config file failed!");
			return -1;
		}
		iniGetString("system","default queue",queuestr,32,TSE_DEFAULT_QUEUE);
		iniFileFree();
	}else{
		strncpy(queuestr,str,31);
		queuestr[31]='\0';
	}
	
	if (strlen(queuestr)>=12) return -1;
		
	int res = sscanf(queuestr,"%[0-9]-%[0-9]",buf[0],buf[1]);
	
	if(res == 1){
		minqueue = atoi(buf[0]);
		maxqueue = minqueue;
	}
	else if(res == 2){
		minqueue = atoi(buf[0]);
		maxqueue = atoi(buf[1]);
		if(minqueue > maxqueue){
			minqueue = minqueue ^ maxqueue;
			maxqueue = minqueue ^ maxqueue;
			minqueue = minqueue ^ maxqueue;
		}
	}
	else return -1;
	
	qidstart = minqueue;
	qidend   = maxqueue;
	
	int index;
	char queueid[32];
	for (index = minqueue; index <= maxqueue; index++){
		sprintf(queueid,"%d",index);
		ret = NFQRegisterQueue(queueid);
		if(ret < 0) return -1;
	}
	return 0;
}

int PolicyConfigfileInit(struct Tacticsevolve * te)
{
	if(iniFileLoad(inicfgfile) < 0){
		TRACE_MAIN(ERR,"Load config file failed!");
		return -1;
	}
	TseCfgInit(te);
	TsePortInit(te);
	TseCommPortProtoInit();
	DataBaseInit();
	iniFileFree();
	return 0;
}

static void 
Tce_exit(int s)
{
	/*
	printf("policyevolve is going to exit!\n");
	
	printf("unbinding from AF_INET\n"); 
	//nfq_unbind_pf(h, AF_INET); 

	printf("closing library handler\n");
	//nfq_close(h);
	*/
	TseUnInstallNFQueue();
	tce_ctl_flags = 1;
}

int main(int argc, char **argv)
{
	int f_foreground;
	int logmode;
	int loglevelid;
	int res;
	int opt;
	const char * queuestr = NULL;
	const char * loglevel  = NULL;
	
	//get program name
	progname = strrchr(argv[0], '/');
	if (progname)
		progname++;
	else
		progname = argv[0];

	/*
	 * set stdout and stderr line buffered, so that user can read messages
	 * as soon as line is complete
	 */
	setlinebuf(stdout);
	setlinebuf(stderr);
	
	/*cmd parse*/
	f_foreground  = 1;
	logmode       = TSE_LOGMODE_CONSOLE;
	while ((opt = getopt_long(argc,argv,policystopt,policylgopt,NULL))!=EOF){
		switch (opt) {
			case 'B':
				f_foreground = 0;
				logmode      = TSE_LOGMODE_SYSLOG;
				break;
			case 'F':
				inicfgfile = optarg;
				break;
			case 'Q':
				queuestr = optarg;
				break;
			case 'L':
				loglevel = optarg;
				break;
			case 'H':
			case 'h':
				exit_printhelp(progname);
				break;
			default:
				printf("There is not a option -%c! Please %s -h for help!\n",opt,progname);
				return -1;		
		}
	}
	
	/*
	 * Daemon stuff : 
	 *  - detach terminal
	 *  - keep current working directory
	 *  - keep std outputs opened 
	 */
	if (!f_foreground) {
		FILE *fp;
		if (daemon(1, 1) < 0){
			TRACE_MAIN(ERR,"create daemon fail!");
			exit(-1);
		}
		if ((fp = fopen(pidfilename, "w")) != NULL) {
			fprintf(fp, "%d\n", (int) getpid());
			fclose(fp);
		}
	}

	signal(SIGINT, Tce_exit);
	signal(SIGQUIT,Tce_exit);
	signal(SIGABRT,Tce_exit);
	signal(SIGTERM,Tce_exit);

	//log set
	loglevelid = TseLogLevelParse(loglevel);
	TseSetLogLevel(loglevelid);
	TseSetLogMode(logmode);
	TseSetLogAllType();
	TseUnLogType(TSE_LOGTYPE_PACKET|TSE_LOGTYPE_NFQ|TSE_LOGTYPE_CONNECT);

	TseStartCheck();

	struct Tacticsevolve * te = TseCreate();

	if(PolicyConfigfileInit(te) < 0){
		exit(-1);
	}
	DataBaseTabInit();
	TseCfgPrint(te);
	/*
	 *  Module  Register
	 */
	AdminModuleRegister();
	MonitorModuleRegister();
	NFctModuleRegister();
	NFQRecvPktModuleRegister();

	/*
	 * NFQ Queue Register
	 */
	if(TseQueueParse(queuestr) < 0){
		TRACE_MAIN(WARNING,"nfq queue config error");
		exit(-1);
	}

	/*
	 * install iptables nfqueue 
	 */
	if(TseInstallNFQueue()<0) exit(-1);


	pool = ThreadPoolCreate(32,"TCE");
	if(pool == NULL){
		TRACE_MAIN(ERR,"Create thread pool fail!");
		TseUnInstallNFQueue();
		exit(-1);
	}
	pool->data = (void*)te;
	
	RunAdminDoMsg(pool);
	RunMonitorModule(pool);
	RunNFctDoCT(pool);
	RunNFQRecvPacket(pool);
	
	ThreadContinueThreads(pool);
	
	int run = 1;
	/*
	while(run){
		if(tce_ctl_flags & (TCE_KILL | TCE_STOP)){
			TRACE_MAIN(INFO,"Signal Received.  Stopping engine!");
			break;
		}
		ThreadCheckThreadState(pool);
		usleep(1000);
	}
	*/
	while(run){
		if(tce_ctl_flags == 1){
			ThreadKillThreads(pool);
			break;
		}
		usleep(100);
	}
	//printf("closing library handler\n");
	//nfq_close(h);
	TseUnInstallNFQueue();
	TseFree(te);
	exit(0);
}




