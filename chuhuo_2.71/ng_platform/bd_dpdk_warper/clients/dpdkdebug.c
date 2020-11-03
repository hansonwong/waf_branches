#include <dpdk_warp.h>
#include "dpdk_frame.h"
#include "dpi.h"
#include "dpdk_config.h"

struct system_info  *sysinfo;

void help()
{
    printf("usage:dpdkdebug <enable|disable>\n");
    printf("     :dpdkdebug level <ERR|WARNING|NOTICE|INFO|DEBUG>\n");
    printf("     :dpdkdebug type <PLATFORM>\n");
    printf("     :dpdkdebug untype <PLATFORM>\n");
    printf("     :dpdkdebug file <filepath|default>\n");
}

const char * level[] = {"ALL","EMERG","ALERT","CRIT","ERR","WARNING","NOTICE","INFO","DEBUG",NULL};

int main(int argc, char *argv[])
{
    int ret = 0;
    unsigned i   = 0;
    if(!(argc == 3 || argc == 2)) {
        help();
        return -1;
    }
    sysinfo = get_dpdkshm ((char *) "dpdkdebug", (char *) "program1");
    if(!sysinfo) {
        printf("get sharemeory fail\n");
        return -1;
    }    
    struct dpdk_log * log = &sysinfo->log;
    if(!strcmp(argv[1], "enable")) {
        log->dpdk_debug = 1;
        log->flag = 5;
        printf("dpdkdebug enabled\n");
    }
    else if(!strcmp(argv[1], "disable")) {
        log->dpdk_debug = 0;
        log->flag = 6;
        printf("dpdkdebug disabled\n");
    }
    else if(!strcmp(argv[1], "level")){
        for(i = 1; level[i] != NULL; i++){
            if(!strcmp(argv[2],level[i])){
                log->level = i;
                log->flag  = 3;
                break;
            }
        }
        if(!level[i])goto err;
    }
    else if(!strcmp(argv[1], "type")){
        if(!strcmp(argv[2], "PLATFORM")) {
            log->type = RTE_LOGTYPE_PLATFORM;
            log->flag = 1;
        }
        if(!strcmp(argv[2], "FLOW")) {
            log->type = RTE_LOGTYPE_FLOW;
            log->flag = 1;
        }
        if(!strcmp(argv[2], "TS")) {
            log->type = RTE_LOGTYPE_TS;
            log->flag = 1;
        }
        if(!strcmp(argv[2], "DPI")) {
            log->type = RTE_LOGTYPE_DPI;
            log->flag = 1;
        }
    }
    else if(!strcmp(argv[1], "untype")){
        if(!strcmp(argv[2], "PLATFORM")) {
            log->type = RTE_LOGTYPE_PLATFORM;
            log->flag = 2;
        }
        if(!strcmp(argv[2], "FLOW")) {
            log->type = RTE_LOGTYPE_FLOW;
            log->flag = 2;
        }
        if(!strcmp(argv[2], "TS")) {
            log->type = RTE_LOGTYPE_TS;
            log->flag = 2;
        }
        if(!strcmp(argv[2], "DPI")) {
            log->type = RTE_LOGTYPE_DPI;
            log->flag = 2;
        }
    }
    else if(!strcmp(argv[1], "file")){
        memset(log->filepath,0,sizeof(log->filepath));
        strncpy(log->filepath,argv[2],strlen(argv[2]));
        log->flag = 4;
    }
    else if(!strcmp(argv[1], "status")){
        printf("dpdk macro status: %s\n",DPDK_LOG_DEBUG ?"ON":"OFF");
        printf("dpdk debug status: %s\n",log->dpdk_debug?"ON":"OFF");
        printf("dpdk debug level : %s\n",level[log->level]);
        printf("dpdk debug type  : 0x%x\n",log->atype);
        printf("dpdk debug file  : %s\n",log->filepath);
        return 0;
    }
    else goto err;
    
    return 0;

err:
    help();
    return -1;
}

