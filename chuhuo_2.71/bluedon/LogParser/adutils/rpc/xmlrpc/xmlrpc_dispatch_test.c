
#include "xmlrpc_dispatch.h"

int myTestFun(void* param, char** outbuf)
{
	//printf("doing function myTestFun\n");
	
	*outbuf = malloc(1024);
	strcpy(*outbuf, "my name is ydc");
	return 0;
}


int myAddFun(void* param, char** outbuf)
{
	json_t* jobj = (json_t*)param;	
	
	//printf("myAddFun json_dump %s\n", json_dumps(jobj, 0));
	int c = 10;
	json_t *ja = json_object_get(jobj, "a");
	json_t *jb = json_object_get(jobj, "b");
	
	if (ja && jb)
	{
		int a = json_integer_value(ja);
		int b = json_integer_value(jb);
		c = a + b;
	}
	
	*outbuf = (char*)malloc(1024);
	sprintf(*outbuf, "add result %d", c);
	return 0;
}

int  main(int const argc, const char ** const argv)
{
	xmlrpc_dispatch_client client;

	// 注册客户端
	if (xmlrpc_dispatch_register(&client, "clientTest") == 0)
	{
		// 注册给其他客户端调用的方法
		xmlrpc_dispatch_register_function(&client, "myTestFun", myTestFun);
		xmlrpc_dispatch_register_function(&client, "myAddFun", myAddFun);
	}
	
	while (1)
	{
		sleep(1);
		
	}
    return 0;
}



//printf("connect xml rpc dispatch success\n");
//int len = xmlrpc_dispatch_invoke(&client, "clientA", "getNameAJSON", "xx", NULL, 0);
//if (client.fault_code == FAULT_CODE_OK)
//{
//	int i;
//	printf("ret len = %d\n", len);
//	
//	char *buf = (char*)malloc(len + 1);
//	for (i = 0; i < 9999; i++)
//	{
//		xmlrpc_dispatch_invoke(&client, "clientA", "getNameAJSON", "xx", buf, len + 1);
//		printf("ret len = %d, buf = %s\n", len, buf);
//	}
//	free(buf);
//}
//else
//{
//	
//	printf("invoke fail %s\n", client.fault_string);
//}


