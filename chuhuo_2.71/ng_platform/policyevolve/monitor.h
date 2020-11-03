
#ifndef __MONITOR_H_ 
#define __MONITOR_H_

#include "thread.h"
//#define DO_RULES

#define DB_MAX_STR 64

enum DataBaseConn{
	DB_HOST = 0,
	DB_USER,
	DB_PASS,
	DB_BASE,
	DB_PORT,
	DB_SOCK,
	DB_MAX
};

void MonitorModuleRegister(void);
void DataBaseInit();
void DataBaseTabInit();

int RunMonitorModule(ThreadPool * tpool);



#endif /*__MONITOR_H_*/



