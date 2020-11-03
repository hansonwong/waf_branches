
#include "redisrpc.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <search.h>

#include <jansson.h>
#include <sys/prctl.h>

#include <hiredis/hiredis.h>
#include <hiredis/async.h>
#include <hiredis/adapters/libevent.h>

static int task_compare(const void *pa, const void *pb)
{
    RedisRPCTask *t1 = (RedisRPCTask*)pa;
	RedisRPCTask *t2 = (RedisRPCTask*)pb;
	//printf("compare %s %s\n", t1->taskid, t2->taskid);
    return strcmp(t1->taskid, t2->taskid);
}


static void* redis_rpc_event_dispatch_thread(void* arg)
{
	prctl(PR_SET_NAME, (unsigned long)"resisrpc_event_dispatch");
	RedisRPCClient* client = (RedisRPCClient*)arg;
	event_base_dispatch(client->event_base);
	return 0;
}

static void sendResponse(
	RedisRPCClient* client,
	int invoke_flag,
	const int action,
	const char *clientname,
	const char *taskid,
	const char *funname,
	json_t *ret
)
{
	if (invoke_flag == REDIS_RPC_TASK_INVOKE_SUCCESS)
	{
		json_t *resp = json_pack("{s:i, s:s, s:s, s:s, s:{}}",
			"action", REDIS_RPC_TASK_ACTION_RESPONSE,
			"clientname", client->clientname,
			"taskid", taskid,
			"funname", funname,
			"param");
		
		json_object_set_new(resp, "param", json_copy(ret)); // 设置参数
		char *p = json_dumps(resp, 0);
		if (p == NULL)
		{
			printf("sendResponse json_dumps fail\n");
			exit(0);
		}
		//printf("PUBLISH redisrpc_%s_task %s\n", clientname, p);
		redisReply* r = (redisReply*)redisCommand(client->context_publish_response, "PUBLISH redisrpc_%s_task %s", clientname, p);
		if (r) freeReplyObject(r);
		free(p);
		json_decref(resp);
		//printf("发送结果 %s\n", taskid);
	}
}

static void task_root_action(const void *nodep, const VISIT which, const int depth) {  
    int *datap;
	RedisRPCTask *task = *((RedisRPCTask**)nodep);
	time_t t = time(NULL);
	if (t - task->t > 3)
		printf("释放 taskid = %s\n", task->taskid);
}

static void* redis_rpc_dump_thread(void* arg)
{
	prctl(PR_SET_NAME, (unsigned long)"resisrpc_dump");
	RedisRPCClient* client = (RedisRPCClient*)arg;
	
	int last_action_invoke_count = 0;
	while (1)
	{
		printf("==========================\n");
		printf("被远程调用次数 : %d\n", client->action_be_invoke_count);
		printf("回复接收次数   : %d\n", client->action_response_count);
		
		printf("*每秒远程调用数: %d\n", client->action_invoke_count - last_action_invoke_count);
		
		printf("*远程调用次数  : %d\n", client->action_invoke_count);
		printf("*调用失败次数  : %d\n", client->action_invoke_timeout_count);
		printf("*调用成功次数  : %d\n", client->action_invoke_success_count);
		
		last_action_invoke_count = client->action_invoke_count;
		
		pthread_mutex_lock(&client->task_root_mutex);
		twalk(client->task_root, task_root_action);
		pthread_mutex_unlock(&client->task_root_mutex);
		
		sleep(1);
	}
	return NULL;
}

static void* redis_rpc_client_task_thread(void* arg)
{
	prctl(PR_SET_NAME, (unsigned long)"resisrpc_task_invoke");
	RedisRPCClient* client = (RedisRPCClient*)arg;
	while (1)
	{
		
		// 获取task并执行
		pthread_cond_wait(&client->task_invoke_cond, &client->task_invoke_mutex);
		pthread_mutex_unlock(&client->task_invoke_mutex);
		
		while (1)
		{
			int nextidx = (client->task_head_idx + 1) % REDIS_RPC_MAX_TASK_CACHE_COUNT;
			
			//printf("获取task并执行 %d\n", nextidx);
			RedisRPCTask *task = client->tasks[nextidx];
			client->task_head_idx = nextidx;
			
			int i;
			int invoke_flag = REDIS_RPC_TASK_INVOKE_NO_SUCH_FUNCTION;
			json_t *ret = NULL;
			for (i = 0; i < client->fun_count; i++)
			{
				//printf("clientname %s\n", client->fun_name_s[i]);
				if (strcmp(client->fun_name_s[i], task->funname) == 0)
				{
					invoke_flag = REDIS_RPC_TASK_INVOKE_SUCCESS;
					ret = client->funs[i](task->ret);
					//printf("找到方法并执行完毕 %s %d\n", task->taskid, time(NULL));
					break;
				}
			}
			
			sendResponse(
				client,
				invoke_flag,
				task->action,
				task->clientname,
				task->taskid,
				task->funname,
				ret);
				
			if (ret != NULL)
			{
				json_decref(ret);
			}
			
			if (task->ret) json_decref(task->ret);
			free(task);
			
			if (nextidx == client->task_tail_idx) break;
		}
		
	}
	return 0;
}

static void taskCallback(redisAsyncContext *c, void *r, void *priv) {  
    redisReply *reply = r;  
    if (reply == NULL) return;  
    if ( reply->type == REDIS_REPLY_ARRAY && reply->elements == 3 ) {  
        if ( strcmp( reply->element[0]->str, "subscribe" ) != 0 ) {
			
			RedisRPCClient* client = (RedisRPCClient*)priv;
            //printf( "Received[%s] channel %s: %s\n",  
            //        client->clientname, 
            //        reply->element[1]->str,  
            //        reply->element[2]->str );
			
			json_t *j = json_loads(reply->element[2]->str, 0, NULL);
			if (j != NULL)
			{
				json_t *j_action = json_object_get(j, "action");
				json_t *j_clientname = json_object_get(j, "clientname");
				json_t *j_taskid = json_object_get(j, "taskid");
				json_t *j_funname = json_object_get(j, "funname");
				json_t *j_param = json_object_get(j, "param");
				
				const int action = json_integer_value(j_action);
				const char *clientname = json_string_value(j_clientname);
				const char *taskid = json_string_value(j_taskid);
				const char *funname = json_string_value(j_funname);
				
				
				
				switch(action)
				{
				case REDIS_RPC_TASK_ACTION_INVOKE:
					{
						client->action_be_invoke_count++;
						RedisRPCTask *task = (RedisRPCTask*)calloc(1, sizeof(RedisRPCTask));
						if (task == NULL) exit(0);
						task->action = REDIS_RPC_TASK_ACTION_INVOKE;
						strcpy(task->clientname, clientname);
						strcpy(task->taskid, taskid);
						strcpy(task->funname, funname);
						task->ret = json_copy(j_param);
						pthread_mutex_lock(&client->task_invoke_mutex);
						
						/* 寻找当前task应该应该存放的位置 */
						int idx = (client->task_tail_idx + 1) % REDIS_RPC_MAX_TASK_CACHE_COUNT;
						if (idx == client->task_head_idx)
						{
							// task 缓存空间不足，丢弃当前任务
							printf("drop task\n");
							json_decref(task->ret);
							free(task);
							break;
						}
						client->tasks[idx] = task;
						
						//printf("recvtime %d %s %d\n", idx, taskid, time(NULL));
						
						client->task_tail_idx = idx;
						pthread_cond_signal(&client->task_invoke_cond);
						pthread_mutex_unlock(&client->task_invoke_mutex); 
						
						
						
						//int i;
						//int invoke_flag = REDIS_RPC_TASK_INVOKE_NO_SUCH_FUNCTION;
						//json_t *ret = NULL;
						//for (i = 0; i < client->fun_count; i++)
						//{
						//	//printf("clientname %s\n", client->fun_name_s[i]);
						//	if (strcmp(client->fun_name_s[i], funname) == 0)
						//	{
						//		invoke_flag = REDIS_RPC_TASK_INVOKE_SUCCESS;
						//		ret = client->funs[i](j_param);
						//		break;
						//	}
						//}
						//
						//sendResponse(
						//	client,
						//	invoke_flag,
						//	action,
						//	clientname,
						//	taskid,
						//	funname,
						//	ret);
						//	
						//if (ret != NULL)
						//{
						//	json_decref(ret);
						//}
					}
					break;
				case REDIS_RPC_TASK_ACTION_RESPONSE:
					{
						client->action_response_count++;
						RedisRPCTask task;
						strcpy(task.taskid, taskid);
						/* 查找任务是否已经存在 */
						//printf("get response %s\n", taskid);
						pthread_mutex_lock(&client->task_root_mutex);
						RedisRPCTask **item = (RedisRPCTask**)tfind(&task, &client->task_root, task_compare);
						pthread_mutex_unlock(&client->task_root_mutex);
						if (item)
						{
							json_t *r = json_copy(j_param);
							(*item)->ret = r;
							(*item)->flag = 1;
						}
					}
					break;
				default:
					break;
				}
				json_decref(j);
			}
        }  
    }  
} 

int RedisRPCClientRegister(RedisRPCClient* client, const char* clientname)
{
	srand((int)time(0));
	if (client == NULL) return REDIS_RPC_INSTANCE_IS_NULL;	/* client为空 */
	redisAsyncContext *c = NULL;
	memset(client, 0, sizeof(RedisRPCClient));
	
	
	/* 保存客户端名称 */
	strcpy(client->clientname, clientname);
	
	/* 设置连接超时时间并连接redis服务器 */
	
	struct timeval timeout = { 1, 500000 }; // 1.5 seconds
	c = (void*)redisAsyncConnect("127.0.0.1", 6379);
	if (c == NULL || c->err)
	{
		/* 连接失败 */
		return REDIS_RPC_REGISTER_FAIL;
	}
	else
	{
		/* 保存redis句柄 */
		client->context_task = (void*)c;
		
		client->context_publish_invoke = redisConnect("127.0.0.1", 6379);  
		if (((redisContext*)(client->context_publish_invoke))->err)  
		{  
			redisFree(client->context_publish_invoke);
			redisFree(client->context_task);
			/* 连接失败 */
			return REDIS_RPC_REGISTER_FAIL;
		}
		
		client->context_publish_response = redisConnect("127.0.0.1", 6379);  
		if (((redisContext*)(client->context_publish_response))->err)  
		{  
			redisFree(client->context_publish_invoke);
			redisFree(client->context_publish_response);
			redisFree(client->context_task);
			/* 连接失败 */
			return REDIS_RPC_REGISTER_FAIL;
		}
	}
	//client->task_head_idx = -1;
	//client->task_tail_idx = 0;
	
	pthread_mutex_init(&client->task_root_mutex, NULL);
	pthread_mutex_init(&client->task_invoke_mutex, NULL);
	pthread_cond_init(&client->task_invoke_cond, NULL);
	
	client->event_base = (void*)event_base_new();
	redisLibeventAttach(client->context_task, client->event_base);
	
	char buf[1024];
	sprintf(buf, "SUBSCRIBE redisrpc_%s_task", client->clientname);
	redisAsyncCommand(c, taskCallback, (void*)client, buf);
	
	
	/* 创建任务处理线程 */
	pthread_create(&client->task_invoke_tid, NULL, redis_rpc_client_task_thread, (void*)client);
	usleep(200000);
	/* 创建订阅事件调度线程 */
	pthread_create(&client->event_dispatch_tid, NULL, redis_rpc_event_dispatch_thread, (void*)client);
	usleep(200000);
	/* 创建统计输出线程 */
	pthread_create(&client->event_dump_tid, NULL, redis_rpc_dump_thread, (void*)client);
	return REDIS_RPC_OK;
}

json_t* RedisRPCCLientInvoke(RedisRPCClient* client, const char* clientname, const char* funname, json_t* param)
{
	//if (client == NULL) return REDIS_RPC_INSTANCE_IS_NULL;	/* client为空 */
	if (client == NULL) return NULL;
	client->action_invoke_count++;
	int i;
	char taskid[128];
	
	int rand1 = rand();
	int rand2 = rand();
	sprintf(taskid, "%s_%d_%X_%d_%d", funname, time(NULL), param, rand1, rand2);
	//printf("new taskid = %s\n", taskid);
	void* prt = NULL;
	
	RedisRPCTask *task = (RedisRPCTask*)calloc(1, sizeof(RedisRPCTask));
	if (task == NULL) exit(0);
	task->action = REDIS_RPC_TASK_ACTION_INVOKE;
	strcpy(task->clientname, clientname);
	strcpy(task->taskid, taskid);
	strcpy(task->funname, funname);
	task->t = time(NULL);
	
	/* 查找任务是否已经存在 */
	pthread_mutex_lock(&client->task_root_mutex);
	RedisRPCTask **item = tsearch(task, &client->task_root, task_compare);
	if (*item != task)
	{
		pthread_mutex_unlock(&client->task_root_mutex);
		printf("任务已存在，冲突了\n");
		return NULL;
	}
	pthread_mutex_unlock(&client->task_root_mutex);
	
	/* 格式化要发送的数据 */
	json_t *req = json_pack("{s:i, s:s, s:s, s:s, s:{}}",
		"action", REDIS_RPC_TASK_ACTION_INVOKE,
		"clientname", client->clientname,
		"taskid", taskid,
		"funname", funname,
		"param");
	
	/* 设置参数 */
	json_object_set_new(req, "param", json_copy(param)); // 设置参数
	/* 序列化参数 */
	char *p = json_dumps(req, 0);
	if (p == NULL)
	{
		printf("json_dumps fail\n");
		exit(0);
	}
	
	redisReply* r = (redisReply*)redisCommand(client->context_publish_invoke, "PUBLISH redisrpc_%s_task %s", clientname, p);
	if (r) freeReplyObject(r);
	json_decref(req);
	free(p);
	
	
	for (i = 0; i < 1000; i++)
	{
		
		if (task->flag == 1)
		{
			
			json_t *ret = task->ret;
			pthread_mutex_lock(&client->task_root_mutex);
			tdelete(task, &client->task_root, task_compare);
			pthread_mutex_unlock(&client->task_root_mutex);
			free(task);
			client->action_invoke_success_count++;
			return ret;
		}
		usleep(500);
	}
	free(task);
	client->action_invoke_timeout_count++;
	return NULL;
}

int RedisRPCCLientRegisterFunction(RedisRPCClient* client, const char* funname, RedisRPCFUNCTION fun)
{
	if (client == NULL) return REDIS_RPC_INSTANCE_IS_NULL;	/* client为空 */
	if (client->fun_count + 1 == REDIS_RPC_MAX_FUNS_COUNT) return REDIS_RPC_REGISTER_FUNCTION_FAIL_TO_MANY;
	
	client->funs[client->fun_count] = fun;
	strcpy(client->fun_name_s[client->fun_count], funname);
	client->fun_count++;
	printf("客户端 %s 注册函数 %s\n", client->clientname, funname);
	return REDIS_RPC_OK;
}

