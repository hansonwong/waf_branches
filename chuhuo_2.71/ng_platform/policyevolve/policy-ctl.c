#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdint.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <getopt.h>
#include <sys/msg.h>
#include <errno.h>

#include "admin.h"


static char * opertype[MSG_TSE_MAX] = {"port","traffic","protocol","connect"};

static struct __policy_ctl{
	const  char * program_name;
	pid_t  pidid;
	int    msqid;
} policy_ctl;

const char policy_short_options[] ="S:T:A:D:r:i:t:m:p:h";

const struct option policy_long_options[]=
{
	{.name = "SYS_OPER",.has_arg = 1, .val = 'S'},
	{.name = "TYPE",    .has_arg = 1, .val = 'T'},
	{.name = "ADD",     .has_arg = 1, .val = 'A'},
	{.name = "DEL",     .has_arg = 1, .val = 'D'},
	{.name = "HELP",    .has_arg = 1, .val = 'h'},
	{NULL},
};

static void exit_printhelp()
{
	const char * proname = policy_ctl.program_name;
	
	printf("HOW TO USE %s\n"
		   "Usage: %s -[S] [start|stop] -r\n" // -[S] [start|stop|restart] -r\n
           "       %s -[T] [port|traffic|protocol|connect] [up|down]\n"
           "       %s -[A] [port]\n"
		   "	   %s -[D] [port]\n"
           "eg.\n"
           "       %s -S start -r 60\n"
           "       %s -T port up -p 10-100\n"
           "       %s -T traffic up -i 60 -t 10 -m 2\n"
           "       %s -A port -p 300-400\n"
           "       %s -D port -p 300-400\n",
	       proname,proname,proname,
	       proname,proname,proname,
	       proname,proname,proname,proname);
	
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


static const char cmdflags[] = {'S','T','A','D'};

static char cmd2char(int option)
{
	const char *ptr;
	for (ptr = cmdflags; option > 1; option >>= 1, ptr++);

	return *ptr;
}

static void add_command(unsigned int *cmd, const int newcmd, const int othercmds)
{
	if (*cmd & (~othercmds)){
		printf("Cannot use -%c with -%c\n",
			   cmd2char(newcmd), cmd2char(*cmd & (~othercmds)));
		exit(-1);
	}
	*cmd |= newcmd;
}


static int type_name2id(const char * type)
{
	int index = 0;
	while ( index < MSG_TSE_MAX ){
		if(strcmp(type,opertype[index])==0)
			return index;
		index++;
	}
	return -1;
}
static int sys_name2id(const char * systype)
{
	int sysid;
	if (strcmp(systype,"start")==0){
		sysid = 0;
	}
	else if (strcmp(systype,"stop")==0){
		sysid = 1;
	}
	/*
	else if (strcmp(systype,"restart")==0){
		sysid = 3;
	}
	*/
	else sysid = -1;
	return sysid;
}
/*
static int port_parse(char *port_str,struct policy_ctl_msg_ds * pctl)
{
	char buf[2][16];
	unsigned short minport;
	unsigned short maxport;
	
	if (strlen(port_str)>=12){
		goto err;
	}
	
	int res = sscanf(port_str,"%[0-9]-%[0-9]",buf[0],buf[1]);
	if(res == 1){
		minport = atoi(buf[0]);
		pctl->minport = minport;
		pctl->maxport = minport;
	}
	else if(res == 2){
		minport = atoi(buf[0]);
		maxport = atoi(buf[1]);
		if(minport > maxport){
			pctl->minport = maxport;
			pctl->maxport = minport;
		}
		else {
			pctl->minport = minport;
			pctl->maxport = maxport;
		}
	}
	else goto err;
	
	return 0;
err:
	printf("The port %s that you input is not correct!\n",port_str);
	return -1;
}
*/
static int post_msg(struct policy_ctl_msg_ds * ds)
{
	int ret;
	
	struct policy_ctl_msgbuf recvbuf;
	struct policy_ctl_msgbuf sendbuf;
	
	size_t recvlength;
	size_t sendlength;

	long mtype = policy_ctl.pidid;
	int  msqid = policy_ctl.msqid;

	ds->mtype = mtype;
	
	memset(&recvbuf,0,sizeof(struct policy_ctl_msgbuf));
	memset(&sendbuf,0,sizeof(struct policy_ctl_msgbuf));
	recvlength = sizeof(struct policy_ctl_msgbuf) - sizeof(long);
	sendlength = sizeof(struct policy_ctl_msgbuf) - sizeof(long);

	sendbuf.mtype = 1; //main message 
	memcpy(sendbuf.mtext,ds,sizeof(struct policy_ctl_msg_ds));
	
	ret = msgsnd(msqid,(void*)&sendbuf,sendlength,IPC_NOWAIT);

	if(ret < 0){
		//printf("all errno:%d,%d,%d,%d,%d,%d,%d",EACCES,EAGAIN,EFAULT,EIDRM,EINTR,EINVAL,ENOMEM);
		printf("send cmd message fail %d!\n",errno);
		return -1;
	}

	
	ret = msgrcv(msqid,(void*)&recvbuf,recvlength,mtype,0);

	if(ret < 0) {
		printf("recv reply message fail!\n");
		return -1;
	}

	int retvalue = 0;

	sscanf(recvbuf.mtext,"%d",&retvalue);
	printf("recv reply %d\n",retvalue);
	return retvalue;
}

/*cmd lines parse*/
int 
do_command(int argc,char *argv[])
{
	int opt = 0;
	unsigned int command = 0;
	int option_index;
	char * oper_type;
	char * sys_type;
	char * port_str;
	char * isauto;
	char * isup;
	struct policy_ctl_msg_ds pctl;
	memset(&pctl,0,sizeof(pctl));
	
	while ((opt = getopt_long(argc,argv,
			                  policy_short_options,
			                  policy_long_options,
			                  &option_index))!=EOF){
			                  
		switch (opt) {
				/*
				 * Command selection
				 */
			case 'S':
				sys_type = optarg;
				pctl.sys_operid = sys_name2id(sys_type);
				if(pctl.sys_operid < 0) {
					exit_printhelp();
					return -1;
				}
				/*
				if (optind < argc && argv[optind][0] != '-'){
					isauto = argv[optind++];
				}
				if (strcmp(isauto,"AUTO")==0){
					pctl.isauto = 1;
				}
				else pctl.isauto = 1;
				*/
				pctl.cmd |= CMD_SYSTEM_OPERATOR;
				add_command(&command,CMD_SYSTEM_OPERATOR,CMD_NONE);
				break;
			case 'T':
				oper_type = optarg;
				pctl.type_operid = type_name2id(oper_type);
				if(pctl.type_operid < 0) {
					exit_printhelp();
					return -1;
				}
				if (optind < argc && argv[optind][0] != '-'){
					isup = argv[optind++];
				}
				if (strcmp(isup,"up")==0){
					pctl.isup = POLICY_UP;
				}
				else if (strcmp(isup,"down")==0){
					pctl.isup = POLICY_DOWN;
				}
				pctl.cmd |= CMD_TYPE_OPERATOR;
				add_command(&command,CMD_TYPE_OPERATOR,CMD_NONE);
				break;
			case 'A':
				oper_type = optarg;
				pctl.type_operid = type_name2id(oper_type);
				if(pctl.type_operid < 0) {
					exit_printhelp();
					return -1;
				}
				pctl.cmd |= CMD_PORT_ADD;
				add_command(&command,CMD_PORT_ADD,CMD_NONE);
				break;
			case 'D':
				oper_type = optarg;
				pctl.type_operid = type_name2id(oper_type);
				if(pctl.type_operid < 0) {
					exit_printhelp();
					return -1;
				}
				pctl.cmd |= CMD_PORT_DEL;
				add_command(&command,CMD_PORT_DEL,CMD_NONE);
				break;

			case 'r':
				pctl.rejectime = atoi(optarg);
				pctl.cmdvalue |= POLICY_VALUE_REJECTIME;
				break;
			case 'i':
				pctl.interval = atoi(optarg);
				pctl.cmdvalue |= POLICY_VALUE_INTERVAL;
				break;
			case 't':
				pctl.threshold = atoi(optarg);
				pctl.cmdvalue |= POLICY_VALUE_THRESHOLD;
				break;
			case 'm':
				pctl.max_times = atoi(optarg);
				pctl.cmdvalue |= POLICY_VALUE_MAXTIMES;
				break;
			case 'p':
				port_str = optarg;
				if(port_str == NULL) break;
				strncpy(pctl.portstr,port_str,512);
				pctl.portstr[512-1] = '\0';
				/*
				if(port_parse(port_str,&pctl) < 0){
					exit_printhelp();
					return -1;
				}
				*/
				pctl.cmdvalue |= POLICY_VALUE_PORT;
				break;
			case 'h':
				exit_printhelp();
				break;
			default:
				printf("There is not a option -%c! Please %s -h for help!\n",opt,argv[0]);
				return -1;		
		}
	}
	int ret = post_msg(&pctl);
	return ret;
}

/*
static void policy_ctl_exit(int signal){
	if(__meminfo != NULL){
		printf("release memory resource! exit(0)!\n");
		free(__meminfo);
	}
	exit(0);
}
*/
int main(int argc, char *argv[])
{
	int ret=0;

	char * name = strrchr(argv[0], '/');
	if(name)
		name++;
	else
		name = argv[0];

	
	policy_ctl.program_name = name;
	/*
	signal(SIGINT, policy_ctl_exit);
	signal(SIGQUIT,policy_ctl_exit);
	signal(SIGABRT,policy_ctl_exit);
	signal(SIGKILL,policy_ctl_exit);
	*/
	int msg = msgget((key_t)POLICY_MSG_KEY_T,  IPC_CREAT|0666);
	//int msg = msgget((key_t)POLICY_MSG_KEY_T, 0666);
	//int msg = msgget((key_t)POLICY_MSG_KEY_T, 0666 | IPC_CREAT);

	if(msg < 0){
		printf("get message queue id fail.exit!\n");
		exit(-1);		
	}

	policy_ctl.pidid = getpid();
	policy_ctl.msqid = msg;
	
	ret = do_command(argc,argv);

	if ( ret < 0 ){
		exit(-1);
	}
	return 0;
}

