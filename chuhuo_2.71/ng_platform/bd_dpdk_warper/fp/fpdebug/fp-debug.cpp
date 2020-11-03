#include <map>
#include <string>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <iostream>
#include <iomanip>
#include <stdint.h>
#include <netinet/in.h>

#include "StringTokenizer.h"
#include "dpdk_frame.h"
#ifdef HAVE_LIBEDIT
#include "readline/readline.h"
#include "readline/history.h"
#endif

struct system_info  *sysinfo;
static fp_debug_t *debug;
uint16_t default_vrfid = 0;

typedef int (*command)(StringTokenizer &tok);

static std::map<std::string,command> cmds;
static std::map<std::string,std::string> help;

static int get_integer(int *val, const char *arg, int base)
{
	long res;
	char *ptr;

	if (!arg || !*arg)
		return -1;

	res = strtol(arg, &ptr, base);

	/* If there were no digits at all, strtol()  stores
         * the original value of nptr in *endptr (and returns 0).
	 * In particular, if *nptr is not '\0' but **endptr is '\0' on return,
	 * the entire string is valid.
	 */
	if (!ptr || ptr == arg || *ptr)
		return -1;

	/* If an underflow occurs, strtol() returns LONG_MIN.
	 * If an overflow occurs,  strtol() returns LONG_MAX.
	 * In both cases, errno is set to ERANGE.
	 */
	if ((res == LONG_MAX || res == LONG_MIN) && errno == ERANGE)
		return -1;

	/* Outside range of int */
	if (res < INT_MIN || res > INT_MAX)
		return -1;

	*val = res;
	return 0;
}

static int get_u32(uint32_t *val, const char *arg, int base)
{
	unsigned long res;
	char *ptr;

	if (!arg || !*arg)
		return -1;
	res = strtoul(arg, &ptr, base);

	/* empty string or trailing non-digits */
	if (!ptr || ptr == arg || *ptr)
		return -1;

	/* overflow */
	if (res == ULONG_MAX && errno == ERANGE)
		return -1;

	/* in case UL > 32 bits */
	if (res > 0xFFFFFFFFUL)
		return -1;

	*val = res;
	return 0;
}

static int get_u8(uint8_t *val, const char *arg, int base)
{
	unsigned long res;
	char *ptr;

	if (!arg || !*arg)
		return -1;

	res = strtoul(arg, &ptr, base);
	/* empty string or trailing non-digits */
	if (!ptr || ptr == arg || *ptr)
		return -1;

	/* overflow */
	if (res == ULONG_MAX && errno == ERANGE)
		return -1;

	if (res > 0xFFUL)
		return -1;

	*val = res;
	return 0;
}

static int myexit(StringTokenizer &tok)
{
    return 1;
}

static int comment(StringTokenizer &tok)
{
    return 0;
}

static int show_help(StringTokenizer &tok)
{
    if (tok.countTokens() == 0) {
		std::map<std::string,std::string>::iterator it;
		for (it = help.begin(); it != help.end(); ++it) {
			std::cout << it->first << ": " <<  it->second << std::endl;
		}
    } else {
		std::string token = tok.nextToken();
        if (help.find(token) != help.end()) {
			std::cout << help[token] << std::endl;
		}
    }
    return 0;
}

static int logmode(StringTokenizer &tok)
{
	std::string type_str = "";
	uint8_t count = tok.countTokens();
	uint8_t mode;

	if (count != 0 && count != 1) {
		printf("wrong arguments: logmode [console|syslog|file]\n");
		return -1;
	}

	if (count == 1) {
		type_str = tok.nextToken();
		if (type_str.compare("console") == 0)
			mode = FP_LOG_MODE_CONSOLE;
		else if (type_str.compare("syslog") == 0)
			mode = FP_LOG_MODE_SYSLOG;
		else if (type_str.compare("file") == 0)
			mode = FP_LOG_MODE_FILE;		
		else {
			printf("wrong arguments: logmode [console|syslog|file]\n");
			return -1;
		}
		debug->mode = mode;
	}

	printf("Log mode is %s\n", debug->mode == FP_LOG_MODE_CONSOLE ?
							   "console" : debug->mode == FP_LOG_MODE_SYSLOG ? "syslog" : "file");
	return 0;
}

static int loglevel(StringTokenizer &tok)
{
	uint8_t count = tok.countTokens();
	uint8_t level;

	if (count != 0 && count != 1) {
		printf("wrong arguments: loglevel [value]\n");
		return 0;
	}

	if (count == 1) {
		if (get_u8(&level,tok.nextToken().c_str(),0) == 0) {
			if (level > 7) {
				printf("wrong arguments: 0 <= loglevel <= 7\n");
				return 0;
			}
			debug->level = level;
		}else{
			printf("ERROR:wrong input!!!\n");
		}
	}
	
	printf("Log level is %d\n", debug->level);
#ifndef MCORE_DEBUG
	printf("MCORE_DEBUG is disabled, hence only messages with "
	       "log level <= FP_LOG_DEFAULT (%d) will be displayed.\n",
	       FP_LOG_DEFAULT);
#endif

	return 0;
}

#define SET_LOG_FLAG(f, on)						\
	do {										\
		if (on)									\
			debug->type |= FP_LOGTYPE_##f;		\
		else									\
			debug->type &= ~(FP_LOGTYPE_##f);	\
	} while(0)

#define PRINT_LOG_FLAG(f)							\
			do {									\
				printf( "log " #f " is %s\n",		\
					(debug->type&FP_LOGTYPE_##f) ?	\
					"on":"off");					\
			} while(0)


#define SET_AND_PRINT_LOG_FLAG(f)						\
	do {												\
		if (count == 2) {								\
			if (all || type_str.compare(#f) == 0) {		\
				SET_LOG_FLAG(f, on);					\
				PRINT_LOG_FLAG(f);						\
				if (!all)								\
					return 0;							\
			}											\
		}												\
		else {											\
			PRINT_LOG_FLAG(f);							\
		}												\
	} while(0)
	

static int logtype(StringTokenizer &tok)
{
	uint8_t count = tok.countTokens();
	std::string type_str = "";
	std::string on_str = "";
	int on = 0;
	int all = 0;

	if (count != 0 && count != 2)
	   goto fail;

	if (count == 2) {
	   type_str = tok.nextToken();
	   if (type_str.compare("all") == 0)
		   all = 1;
	   on_str = tok.nextToken();
	   if (on_str.compare("on") == 0)
		   on = 1;
	   else if (on_str.compare("off") == 0)
		   on = 0;
	   else
		   goto fail;
	}

	SET_AND_PRINT_LOG_FLAG(MAIN_PROC);
	SET_AND_PRINT_LOG_FLAG(EXC);
	SET_AND_PRINT_LOG_FLAG(IP);
	SET_AND_PRINT_LOG_FLAG(FRAG);
	SET_AND_PRINT_LOG_FLAG(IPSEC_IN);
	SET_AND_PRINT_LOG_FLAG(IPSEC_OUT);
	SET_AND_PRINT_LOG_FLAG(IPSEC_REPL);
	SET_AND_PRINT_LOG_FLAG(NF);
	SET_AND_PRINT_LOG_FLAG(REASS);
	SET_AND_PRINT_LOG_FLAG(TUNNEL);
	SET_AND_PRINT_LOG_FLAG(NETFPC);
	SET_AND_PRINT_LOG_FLAG(CRYPTO);
	SET_AND_PRINT_LOG_FLAG(VNB);
	SET_AND_PRINT_LOG_FLAG(TAP);

	if (count == 2 && !all)
	   printf("cannot find logtype <%s>\n", type_str.c_str());

	return 0;
fail:
	printf("wrong arguments: logtype [<type|all> <on|off>]\n");

	return 0;
}
static int loginfoshow(StringTokenizer &tok)
{
	printf("Log level is %d\n\n", debug->level);
	printf("Log ratelimit is %u\n\n", debug->ratelimit);
	printf("Log mode is %s\n\n", debug->mode == FP_LOG_MODE_CONSOLE ?
		                   "console" : debug->mode == FP_LOG_MODE_FILE? "file":"syslog");
	PRINT_LOG_FLAG(MAIN_PROC);
	PRINT_LOG_FLAG(EXC);
	PRINT_LOG_FLAG(IP);
	PRINT_LOG_FLAG(FRAG);
	PRINT_LOG_FLAG(IPSEC_IN);
	PRINT_LOG_FLAG(IPSEC_OUT);
	PRINT_LOG_FLAG(IPSEC_REPL);
	PRINT_LOG_FLAG(NF);
	PRINT_LOG_FLAG(REASS);
	PRINT_LOG_FLAG(TUNNEL);
	PRINT_LOG_FLAG(NETFPC);
	PRINT_LOG_FLAG(CRYPTO);
	PRINT_LOG_FLAG(VNB);
	PRINT_LOG_FLAG(TAP);

    return 0;
}

static int logratelimit(StringTokenizer &tok)
{
	uint32_t val;

	if (tok.countTokens() == 0){
		std::cout << "FP_RATELIMIT = " << debug->ratelimit<< std::endl; 
	}
	else if (tok.countTokens() == 1){
		if (get_u32(&val,tok.nextToken().c_str(),0) == 0) {
			debug->ratelimit = val;
		}else {
			printf("ERROR:wrong input!!!\n");
		}
	}
	else {
		std::cout << help["logratelimit"] << std::endl; 
		return -1;
	}
	
    return 0;
}

static int dump_port_info(StringTokenizer &tok)
{
	if (tok.countTokens() == 0){
		dump_portinfo();
	}
	else {
		std::cout << help["dump_portinfo"] << std::endl; 
		return -1;
	}

	return 0;
}

static int dump_allclients(StringTokenizer &tok)
{
	dump_system1();

	return 0;
}	

static int dump_allclients_byhook(StringTokenizer &tok)
{
	dump_system2();

	return 0;
}

static int dumpclient(StringTokenizer &tok)
{
	struct system_info *system = sysinfo;
	int i,j;
	uint32_t pid;
	const char* str;

	if (tok.countTokens() == 0){
		printf("\t---------------------------\n");
		printf("\tname\t\t\tpid\n");
		printf("\t---------------------------\n");
		for(i=0;i<MAX_CLINET_PRIORITY;i++)
			for(j=0;j<MAX_CLIENT_PARITY;j++){
				if(0!=system->cinfos[i][j].processid)
					printf("\t%s\t\t%u\n", system->cinfos[i][j].name, system->cinfos[i][j].processid);
			}			
		std::cout << "Usage : " << help["dump_client"] << std::endl;
	}
	else if (tok.countTokens() == 1){
		str = tok.nextToken().c_str();
		if (get_u32(&pid, str, 0) == 0) {//num
			for(i=0;i<MAX_CLINET_PRIORITY;i++)
				for(j=0;j<MAX_CLIENT_PARITY;j++){
					if(system->cinfos[i][j].processid == pid)
						dump_client(&system->cinfos[i][j]);
				}
		}else {//string
			for(i=0;i<MAX_CLINET_PRIORITY;i++)
				for(j=0;j<MAX_CLIENT_PARITY;j++){
					if(!strncmp(system->cinfos[i][j].name, str, CLINET_STRING_MAX))
						dump_client(&system->cinfos[i][j]);
				}
		}
	}

	return 0;
}

static int dump_filter(StringTokenizer &tok)
{
	filter_dump_bysystem(sysinfo);

	return 0;
}

static int dump_portmode(StringTokenizer &tok)
{
	list_portmode();

	return 0;
}

static int set_port_mode(StringTokenizer &tok)
{
	struct system_info *system = sysinfo;
	int ret;
	int i;
	int portid;
	int mode;
	int value;

	if (tok.countTokens() == 3){
		if (get_integer(&portid,tok.nextToken().c_str(),0) != 0) {
			printf("ERROR:wrong input!!!\n");
			return 0;
		}
		if (get_integer(&mode,tok.nextToken().c_str(),0) != 0) {
			printf("ERROR:wrong input!!!\n");
			return 0;
		}
		if (get_integer(&value,tok.nextToken().c_str(),0) != 0) {
			printf("ERROR:wrong input!!!\n");
			return 0;
		}
		ret = set_portmode(system, portid, mode, value);
		if (ret == 0) {
			printf("set_portmode success\n");
		}
		else {
			if(mode == MIRROR_PORT) 
				printf("system has one mirror port, can not set another one\n");
			else
				printf("set_portmode failed\n");
		}
	}
	else {
		printf("\t-----------------------------\n");
		printf("\tportid\tmode\t\tvalue\n");
		printf("\t-----------------------------\n");
		for(i = 0; i < system->portinfos.portn; i++) {
			printf("\t%d\t%d(%s)\t%d\n", i, system->portinfos.mode[i].mode, \
				portmode[system->portinfos.mode[i].mode],system->portinfos.mode[i].value);
		}
		printf("mode:\n");
		list_portmode();
		printf("\nusage:\n");
		std::cout << help["set_portmode"] << std::endl; 
	}

	return 0;
}

#if (ENABLE_MIRROR_FUNCTION == 1)
static int set_mirror_rules(StringTokenizer &tok)
{	
	char input[128] = {0};
	int id = 0;
	char *line;
	const char *tmp_str;
	int current_pos[2] = {0};
	int inout = 0; //0:in, 1:out
	int i = 0;

	if (tok.countTokens() == 0) {
		snprintf (input, sizeof(input), "input: ");

		for(i = 0; i < 16; i++) {
			if(strlen(sysinfo->mirror_port[0].user_rule[i]))
				current_pos[0]++;
			if(strlen(sysinfo->mirror_port[1].user_rule[i]))
				current_pos[1]++;
		}
		
		while(1) {
			line = readline(input);
			if(strlen(line) >= 128) {
				printf("the input content must less than 128\n");
			}

			if (!line) {
	            continue;
	        } else {
	            StringTokenizer strtok(line," ");

	            if(strtok.countTokens() == 1) {
					if(!strcmp(line, "exit")) {
						break;
					}else if(!strcmp(line, "ok")) {					
						if(-1 == set_mirror_port_rules(sysinfo, inout))
							printf("ERROR:set mirror port rules fail\n");
						else
							printf("set mirror port rules success\n");
						break;
					}else {
						printf("ERROR: wrong input!!!\n");
					}
	            }else if(strtok.countTokens() == 3) {
					//in or out
					tmp_str = strtok.nextToken().c_str();
					if (get_integer(&inout, tmp_str,0) != 0) {
						printf("ERROR: wrong input!!!\n");
						continue;
					}
					if((inout < 0) || (inout >= 2)) {
						printf("ERROR: the inout must in rang:0-1\n");
						continue;
					}
					
					//id
					tmp_str = strtok.nextToken().c_str();
					if (get_integer(&id, tmp_str,0) != 0) {
						printf("ERROR: wrong input!!!\n");
						continue;
					}
					if((id < 0) || (id >= 16)) {
						printf("ERROR: the id must in rang:0-16\n");
						continue;
					}

					//value
					tmp_str = strtok.nextToken().c_str();
					if(!tmp_str) {
						printf("ERROR: the rules must not be NULL\n");
						continue;
					}

					//save rules
					if(id >= current_pos[inout]) {
						memset(sysinfo->mirror_port[inout].user_rule[current_pos[inout]], 0x00, sizeof(sysinfo->mirror_port[inout].user_rule[current_pos[inout]]));
						rte_memcpy(sysinfo->mirror_port[inout].user_rule[current_pos[inout]++], tmp_str, strlen(tmp_str));
					}else if(id < current_pos[inout]) {
						memset(sysinfo->mirror_port[inout].user_rule[id], 0x00, sizeof(sysinfo->mirror_port[inout].user_rule[id]));
						rte_memcpy(sysinfo->mirror_port[inout].user_rule[id], tmp_str, strlen(tmp_str));
					}
						
	            }else {
	            	printf("ERROR: please input like this: 0 0 proto:6/255\n");
	            }            
	        }
		}
	}else if (tok.countTokens() == 1) {
		if(!strcmp(tok.nextToken().c_str(), "status")) {
			printf("(1)input rules:\n");
			for(i = 0; i < 16; i++) {
				if(strlen(sysinfo->mirror_port[0].user_rule[i])) {
					printf("%d : %s\n", i, sysinfo->mirror_port[0].user_rule[i]);
				}else
					break;
			}

			printf("\n(2)output rules:\n");
			for(i = 0; i < 16; i++) {
				if(strlen(sysinfo->mirror_port[1].user_rule[i])) {
					printf("%d : %s\n", i, sysinfo->mirror_port[1].user_rule[i]);
				}else
					break;
			}
		}
	}

	return 0;
}
#endif

static int set_kernel_stack(StringTokenizer &tok)
{
	int flag = 0;
	
	if(tok.countTokens() == 1) {		
		if (get_integer(&flag,tok.nextToken().c_str(),0) != 0) {
			printf("ERROR:wrong input!!!\n");
			return 0;
		}
		if(flag == 0 || flag == 1)
			sysinfo->kernel_stack_flag = flag;
		else
			printf("usage : set_kernel_stack 0 or set_kernel_stack 1. 0-enable; 1-disable\n");
	}else {
		printf("usage : set_kernel_stack 0 or set_kernel_stack 1. 0-enable; 1-disable\n");
		printf("current status: use kernel is %s\n", (sysinfo->kernel_stack_flag)?"disable":"enable");
	}

	return 0;
}

static int check_mempool(StringTokenizer &tok)
{
	printf("mempool size = %d\n", sysinfo->pktmbuf_pool->size);
	printf("rte_mempool_count = %d\n", rte_mempool_count(sysinfo->pktmbuf_pool));

	return 0;
}

int main(int argc, const char *argv[])
{
#ifdef HAVE_LIBEDIT
		rl_initialize();
		using_history();
#endif
	sysinfo=get_dpdkshm((char*)"fpdebug", (char*)"program1");
	if(!sysinfo){
		printf("get sharemeory fail.exit!\n");
		exit(-1);
	}
	debug=&sysinfo->debug;
		
    cmds["help"] = show_help;
    help["help"] = "Display command list";
    cmds["exit"] = myexit;
    help["exit"] = "Quit";
    cmds["quit"] = myexit;
    help["quit"] = "Quit";
    cmds["loglevel"] = loglevel;
    help["loglevel"] = "set/show the loglevel from 0 (EMERG) to 7 (DEBUG): loglevel [value]";
    cmds["logtype"] = logtype;
    help["logtype"] = "enable/disable logs, show enabled logs: logtype [<type|all> <on|off>]";
    cmds["logmode"] = logmode;
    help["logmode"] = "set/show log mode,default is console:logmode [console|syslog|file]";
	cmds["loginfoshow"] = loginfoshow;
	help["loginfoshow"] = "show loglevel,logtype and logmode info for log:loginfoshow";
    cmds["logratelimit"] = logratelimit;
    help["logratelimit"] = "set/show log rate limit. Default is 10 times per second:logratelimit [value]"; 
	cmds["dump_portinfo"] = dump_port_info;
	help["dump_portinfo"] = "dump port info:dump_portinfo";
	cmds["dump_clients"] = dump_allclients;
	help["dump_clients"] = "dump system info:dump_allclients";
	cmds["dump_clients_byhook"] = dump_allclients_byhook;
	help["dump_clients_byhook"] = "dump system info:dump_allclients_byhook";
	cmds["dump_client"] = dumpclient;
	help["dump_client"] = "dump client info:dump_client <pid|name>";
	cmds["dump_filter"] = dump_filter;
	help["dump_filter"] = "dump filter info:dump_filter";
	cmds["dump_portmode"] = dump_portmode;
	help["dump_portmode"] = "dump port mode info:dump_portmode";
	cmds["set_portmode"] = set_port_mode;//to do
	help["set_portmode"] = "set port mode info:set_portmode [<portid> <mode> <value>]";	

#if (ENABLE_MIRROR_FUNCTION == 1)
	cmds["set_mirror_rules"] = set_mirror_rules; //for test mirror port
	help["set_mirror_rules"] = "set mirror port rules:input [<0:mirror_in,1:mirror_out> <rule_id> <rule>]";
#endif

	cmds["set_kernel_stack"] = set_kernel_stack; 
	help["set_kernel_stack"] = "set kernel stack:set_kernel_stack [flag]";

	cmds["check_mempool"] = check_mempool; 
	help["check_mempool"] = "check_mempool";

    cmds["#"] = comment;
    cmds["//"] = comment;
    cmds[";"] = comment;

    int res = 0;
    while (res == 0) {
		char prompt[16];
		snprintf (prompt, sizeof(prompt), "<fp-%d> ", default_vrfid);		
#ifndef HAVE_LIBEDIT
        char line[200] = {0};
        std::cout << prompt;
        *line = 0;
		gets(line);
#else
        const char* line = readline(prompt);
#endif
        if (!line) {
            res = 1;
        } else {
            StringTokenizer strtok(line," ");

            if (strtok.countTokens()) {
#ifdef HAVE_LIBEDIT
                add_history(line);
#endif

                std::string token = strtok.nextToken();
                if (cmds.find(token) != cmds.end()) 
                    res = (*cmds[token])(strtok);
                else
                    std::cerr << "Command '" << token << "' not found" << std::endl;
            }
        }
    }
    return 0;
}


