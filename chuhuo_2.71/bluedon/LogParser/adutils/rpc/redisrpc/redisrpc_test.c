
#include "redisrpc.h"
json_t* remoteEvent(json_t* param)
{
	//printf("函数 clientAFunctionC 正在执行\n");
	json_t *j_action = json_object_get(param, "action");
	json_t *j_username = json_object_get(param, "username");
	json_t *j_ip = json_object_get(param, "ip");
	
	
	const char* action = json_string_value(j_action);
	const char* username = json_string_value(j_username);
	const char* ip = json_string_value(j_ip);
	
	printf("action = %s, username = %s, ip = %s\n", action, username, ip);
	
	
	return NULL;
}

json_t* clientAFunctionC(json_t* param)
{
	
	
	return NULL;
}

int main(int argc, char** argv)
{
	int ret;
	int i;
	
	RedisRPCClient client;
	
	ret = RedisRPCClientRegister(&client, "clientC");
	
	if (ret == 0)
	{	
		//printf("注册成功\n");
		//RedisRPCCLientRegisterFunction(&client, "remoteEvent", remoteEvent);
		//
		//json_t *jsonret = NULL;
		//
		//jsonret = RedisRPCCLientInvoke(&client, "logparser", "clientGetOnlineUsers", NULL);
		//if (jsonret)
		//{
		//	printf("users = %s\n", json_dumps(jsonret, 0));
		//	json_decref(jsonret);
		//}
		//else
		//{
		//	printf("获取用户信息失败\n");
		//}
		//while (1) sleep(1);
		
		
		printf("注册成功\n");
		
		
		int fail_counter = 0;
		int add_fail_counter = 0;
		
		
		RedisRPCCLientRegisterFunction(&client, "clientAFunctionC", clientAFunctionC);
		
		//while (1) sleep(1);
		for (i = 0; i < 500000; i++)
		{
			json_t *jsonret = NULL;
			
		
			int a = 0;
			a = rand() % 100;
			int b = 0;
			b = rand() % 100;
		
			json_t *p = json_pack("{s:i, s:i}", "a", a, "b", b);
			
			jsonret = RedisRPCCLientInvoke(&client, "clientA", "clientAFunctionA", p);
			if (jsonret != NULL)
			{
				if (json_is_string(jsonret))
				{
					//printf("返回结果 string %s\n", json_string_value(jsonret));
				}
				else if (json_is_integer(jsonret))
				{
					const c = json_integer_value(jsonret);
					
					//printf("返回结果 integer %d + %d = %d\n", a, b, c);
					
					if (c != a + b)
					{
						add_fail_counter++;
					}
					
				}
				else if (json_is_object(jsonret))
				{
					//printf("返回结果 json %s\n", json_dumps(jsonret, 0));
				}
				json_decref(jsonret);
				
			}
			else
			{
				fail_counter++;
			}
			json_decref(p);
			
		}
		
		printf("fail_counter = %d\n", fail_counter);
		printf("add_fail_counter = %d\n", add_fail_counter);
	}
	else
	{
		
		printf("register error, code = %d\n", ret);
	}
	
	while (1) sleep(1);
	
}
