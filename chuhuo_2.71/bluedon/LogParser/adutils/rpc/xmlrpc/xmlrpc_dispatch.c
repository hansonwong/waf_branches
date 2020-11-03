
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "xmlrpc_dispatch.h"


void xml_rpc_dispatch_thread(void* arg)
{
	xmlrpc_dispatch_client* client = (xmlrpc_dispatch_client*)arg;
	client->running = 1;
		
	while (client->running == 1)
	{
		xmlrpc_value *valueTask;
		valueTask = xmlrpc_client_call(&client->env, client->serverurl, "getTask", "(s)", client->clientname);
		
		if (client->env.fault_occurred)
		{
			//char name[256];
			//sprintf(name, "%sClient", client->clientname);
			//xmlrpc_client_init2(&client->env, XMLRPC_CLIENT_SKIP_LIBWWW_INIT, name, "1.0", NULL, 0);
			fprintf(stderr, "ERROR: getTask %s (%d)\n", client->env.fault_string, client->env.fault_code);
			usleep(100000);
			continue;
		}
		else
		{
			const char * jsonStr;
			xmlrpc_read_string(&client->env, valueTask, &jsonStr);
			//printf("jsonStr = %s\n", jsonStr);
			if (strlen(jsonStr) > 0)
			{
				
				json_t *j = json_loads(jsonStr, 0, NULL);
				if (j != NULL)
				{
					int i;
					char funname[64] = { 0 };
					char taskid[64] = { 0 };
					
					const char *s;
					int findflag = 0;
					json_t *jfun_name = json_object_get(j, "fun_name");
					strcpy(funname, json_string_value(jfun_name));
					json_t *jtaskid = json_object_get(j, "taskid");
					strcpy(taskid, json_string_value(jtaskid));
					
					//printf("funname = %s, taskid = %s\n", funname, taskid);
					
					json_t *jparam = json_object_get(j, "param");
					
					xmlrpc_dispatch_remote_fun *remote_fun = NULL;
					for (i = 0; i < client->fun_count; i++)
					{
						remote_fun = client->funs + i;
						if (strcmp(remote_fun->methodName, funname) == 0)
						{
							break;
						}
						remote_fun = NULL;
					}
					if (remote_fun != NULL)
					{
						char *outbuf = NULL;
						int ret = 0;
						
						if (json_is_string(jparam)) // 如果参数是字符串
						{
							ret = remote_fun->fun((void*)json_string_value(jparam), &outbuf);
						}
						else if (json_is_object(jparam)) // 如果参数是json对象
						{
							ret = remote_fun->fun((void*)jparam, &outbuf);
						}
					
						char *msg = NULL;
						if (outbuf != NULL)
						{
							msg = outbuf;
						}
						else
						{
							msg = "";
						}
						
						xmlrpc_value *r = xmlrpc_client_call(&client->env, client->serverurl, "sendRet", "(siss)", client->clientname, 1, taskid, msg);
						if (r) xmlrpc_DECREF(r);
						if (outbuf) free(outbuf);
					}
					else
					{
						//sendRet(self.client_name, True, taskid, ret)
						xmlrpc_value *r = xmlrpc_client_call(&client->env, client->serverurl, "sendRet", "(siss)", client->clientname, 1, taskid, "no such function"); 
						if (r) xmlrpc_DECREF(r);
						
					}
					json_decref(jparam);
					json_decref(j);
				}
			}
			//printf("get task valuetype = %d, ret = %s\n", xmlrpc_value_type(valueTask), jsonStr);
		}
		if (valueTask) xmlrpc_DECREF(valueTask);
	}
}


xmlrpc_dispatch_register(xmlrpc_dispatch_client* client, const char* clientname)
{
	xmlrpc_value *valueReg;
	if (client == NULL) return 1;
	memset(client, 0, sizeof(xmlrpc_dispatch_client));
	xmlrpc_env_init(&client->env);
	strcpy(client->clientname, clientname);
	
	char name[256];
	sprintf(name, "%sClient", clientname);
	// MLRPC_CLIENT_NO_FLAGS
	// XMLRPC_CLIENT_SKIP_LIBWWW_INIT
	xmlrpc_client_init2(&client->env, XMLRPC_CLIENT_SKIP_LIBWWW_INIT, name, "1.0", NULL, 0);
	
	if (client->env.fault_occurred)
	{
		
		fprintf(stderr, "ERROR: %s (%d)\n", client->env.fault_string, client->env.fault_code);
		
		return 2;
	}
	
	strcpy(client->serverurl, "http://127.0.0.1:89/");
	valueReg = xmlrpc_client_call(&client->env, client->serverurl, "register", "(s)", clientname); 
	if (client->env.fault_occurred)
	{
		fprintf(stderr, "ERROR: %s (%d)\n", client->env.fault_string, client->env.fault_code);
		return 3;
	}
	else
	{
		xmlrpc_bool b;
		xmlrpc_read_bool(&client->env, valueReg, &b);
		if (valueReg) xmlrpc_DECREF(valueReg);
		pthread_create(&client->tid, NULL, xml_rpc_dispatch_thread, (void*)client);
	}
	
	return 0;
}


int xmlrpc_dispatch_register_function(xmlrpc_dispatch_client* client, char *methodName, RPCFUN fun)
{
	if (client->fun_count == MAX_RPC_FUN_COUNT) return 1;
	
	strcpy(client->funs[client->fun_count].methodName, methodName);
	client->funs[client->fun_count].fun = fun;
	client->fun_count++;
	printf("register function %s\n", methodName);
}

int xmlrpc_dispatch_invoke(xmlrpc_dispatch_client *client, const char* clientname, const char* methodname, char* jsonstr, char *retbuf, int retbuflen)
{
	
	xmlrpc_value * resultP;
	resultP = xmlrpc_client_call(&client->env, client->serverurl, "invoke", "(sss)", clientname, methodname, jsonstr);
	if (client->env.fault_occurred)
	{
		fprintf(stderr, "ERROR: %s (%d)\n", client->env.fault_string, client->env.fault_code);
		return 3;
	}
	else
	{
		const char * ret;
		xmlrpc_read_string(&client->env, resultP, &ret);
		if (ret != NULL)
		{
			json_t *j = json_loads(ret, 0, NULL);
			if (j != NULL)
			{
				json_t *errorInfo = json_object_get(j, "errorInfo");
				if (json_is_string(errorInfo))
				{
					
					const char* s = json_string_value(errorInfo);
					if (s && strcmp(s, "success") == 0)
					{
						json_t *result = json_object_get(j, "result");
						if (json_is_object(result))
						{
							json_t *issuccess = json_object_get(result, "issuccess");
							
							if (issuccess == json_true())
							{
								json_t *result_ret = json_object_get(result, "ret");
								
								if (json_is_string(result_ret))
								{
									const char* s = json_string_value(result_ret);
									
									int cplen = retbuflen - 1 < strlen(s) ? retbuflen - 1 : strlen(s);
									if (retbuf != NULL)
									{
										memcpy(retbuf, s, cplen);
										retbuf[cplen] = 0;
									}
									client->fault_code = FAULT_CODE_OK;
									json_decref(j);
									return cplen;
								}
								else if (json_is_object(result_ret))
								{
									
									char *s = json_dumps(result_ret, 0);
									
									
									int cplen = retbuflen - 1 < strlen(s) ? retbuflen - 1 : strlen(s);
									if (retbuf != NULL)
									{
										memcpy(retbuf, s, cplen);
										retbuf[cplen] = 0;
									}
									free(s);
									client->fault_code = FAULT_CODE_OK;
									json_decref(j);
									return cplen;
								}
							}
							else
							{
								client->fault_code = FAULT_CODE_FAIL;
								strcpy(client->fault_string, "Unknow Task");
							}
							//json_t *issuccess = json_object_get(result, "issuccess");
						}
						else
						{
							client->fault_code = FAULT_CODE_FAIL;
							strcpy(client->fault_string, "No result");
						}
					}
					else
					{
						client->fault_code = FAULT_CODE_FAIL;
						strcpy(client->fault_string, s);
					}
				}
				
				json_decref(j);
				
			}
			
			if (resultP) xmlrpc_DECREF(resultP);
			
		}
		else
		{
			printf("xmlrpc_read_string fail\n");
		}
	}
	return 0;
}

