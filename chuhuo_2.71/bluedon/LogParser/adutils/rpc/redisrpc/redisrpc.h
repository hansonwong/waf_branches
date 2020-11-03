#ifndef __API_REDIS_RPC__
#define __API_REDIS_RPC__

#include <pthread.h>
#include <jansson.h>

enum
{
	REDIS_RPC_TASK_ACTION_INVOKE = 0,	/* 下发执行任务 */
	REDIS_RPC_TASK_ACTION_RESPONSE		/* 接收任务结果 */
};

enum
{
	REDIS_RPC_OK = 0,
	REDIS_RPC_INSTANCE_IS_NULL,			/* redis实例创建失败 */
	REDIS_RPC_REGISTER_FAIL,			/* 客户端注册失败 */
	REDIS_RPC_REGISTER_FUNCTION_FAIL_TO_MANY,	/* 注册的方法太多 */
	
	/* 任务执行结果 */
	REDIS_RPC_TASK_INVOKE_SUCCESS,
	REDIS_RPC_TASK_INVOKE_NO_SUCH_FUNCTION
};

typedef json_t* (*RedisRPCFUNCTION)(json_t*);

#define REDIS_RPC_MAX_FUNS_COUNT 512	/* 最大可以注册的函数 */
#define REDIS_RPC_MAX_TASK_CACHE_COUNT 512	/* 最大任务缓存个数 */

typedef struct _tagResisRPCTask
{
	int action;
	char clientname[256];
	char taskid[256];
	char funname[256];
	int flag;			/* 执行结果，当获取到结果的时候置1 */
	json_t *ret;		/* 保存返回结果 */
	time_t t;
} RedisRPCTask;

typedef struct _tagRedisRPCClient
{
	char clientname[256];
	
	void* context_task;				/* redis句柄 异步任务获取通道 */
	void* context_publish_invoke;			/* redis句柄 发布通道 */
	void* context_publish_response;			/* redis句柄 发布通道 */
	
	
	void* event_base;		
	void *task_root;				/* 保存任务信息的树 */
	pthread_mutex_t task_root_mutex;/* task_root lock */
	pthread_cond_t task_invoke_cond;
	pthread_mutex_t task_invoke_mutex;
	
	RedisRPCTask* tasks[REDIS_RPC_MAX_TASK_CACHE_COUNT];
	int task_head_idx;
	int task_tail_idx;
	
	pthread_t event_dispatch_tid;	/* redis订阅信息接收线程线程ID */
	pthread_t task_invoke_tid;		/* 任务执行线程ID */
	pthread_t event_dump_tid;
	
	RedisRPCFUNCTION funs[REDIS_RPC_MAX_FUNS_COUNT];
	char fun_name_s[REDIS_RPC_MAX_FUNS_COUNT][256];
	int fun_count;					/* 已注册函数数量 */
	
	int action_be_invoke_count;		/* 被调用次数 */
	int action_response_count;		/* 回复接收次数 */
	int action_invoke_count;		/* 远程调用次数 */
	int action_invoke_timeout_count;/* 调用失败次数 */
	int action_invoke_success_count;/* 调用成功次数 */
	
} RedisRPCClient;


/**
 * 注册监听通道
 */
int RedisRPCClientRegister(RedisRPCClient* client, const char* clientname);

int RedisRPCCLientRegisterFunction(RedisRPCClient* client, const char* funname, RedisRPCFUNCTION fun);

json_t* RedisRPCCLientInvoke(RedisRPCClient* client, const char* clientname, const char* funname, json_t* param);


#endif
