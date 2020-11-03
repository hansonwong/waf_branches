
#ifndef __API_XMLRPC_DISPATCH__
#define __API_XMLRPC_DISPATCH__

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <jansson.h>

#include <xmlrpc-c/base.h>
#include <xmlrpc-c/client.h>

#define MAX_RPC_FUN_COUNT 64


typedef enum {
	FAULT_CODE_OK = 0,
	FAULT_CODE_FAIL
} XMLRPC_DISPATCH_FAULT_CODE;

typedef int (*RPCFUN)(void*, char**);

typedef struct _tag_xmlrpc_dispatch_remote_fun
{
	char methodName[64];
	RPCFUN fun;
} xmlrpc_dispatch_remote_fun;

typedef struct _tag_xmlrpc_dispatch_client
{
	xmlrpc_env env;
	char clientname[64];
	pthread_t tid;
	char serverurl[128];
	int fault_code;
	char fault_string[256];
	int running;
	
	xmlrpc_dispatch_remote_fun funs[MAX_RPC_FUN_COUNT];
	int fun_count;
	
} xmlrpc_dispatch_client;

int xmlrpc_dispatch_invoke(xmlrpc_dispatch_client *client, const char* clientname, const char* methodname, char* jsonstr, char *retbuf, int retbuflen);

#endif