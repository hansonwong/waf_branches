
#include "log.h"


struct Tse_logs tselogs;

void TseSetLogLevel(unsigned lev)
{
	tselogs.level = lev;
}

void TseSetLogMode(int mode)
{
	tselogs.mode = !!mode;
}

void TseSetLogFile(const char * file)
{
	tselogs.file = fopen(file,"a+");
}

void TseSetLogType(int type)
{
	tselogs.type |= type;
}

void TseUnLogType(int type)
{
	tselogs.type &= ~type;
}

void TseSetLogAllType()
{
	tselogs.type |= TSE_LOGTYPE_ADMIN;
	tselogs.type |= TSE_LOGTYPE_MONITOR;
	tselogs.type |= TSE_LOGTYPE_PACKET;
	tselogs.type |= TSE_LOGTYPE_CONNECT;
	tselogs.type |= TSE_LOGTYPE_NFQ;
	tselogs.type |= TSE_LOGTYPE_MAIN;
	tselogs.type |= TSE_LOGTYPE_EXCE;
}

void Tse_syslog(const char *fmt, ...)
{
	return;
}



    

