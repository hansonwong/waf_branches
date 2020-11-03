#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>
#include <string.h>
#include <signal.h>

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#define __USE_GNU
#endif

#include <pthread.h>


#include "thread.h"
#include "policyrun.h"

/* Action On Failure(AOF).  Determines how the engine should behave when a
 * thread encounters a failure.  Defaults to restart the failed thread */
uint8_t tv_aof = THV_RESTART_THREAD;

int threadids     = 0;
int threadpoolids = 0;

int GetThreadID(void)
{
	return threadids++;
}
int GetThreadPoolID(void)
{
	return threadpoolids++;
}


ThreadPool * ThreadPoolCreate(int threads,char * threadpoolname)
{
	ThreadPool * pool = (ThreadPool *)malloc(sizeof(ThreadPool));
	if(pool != NULL){
		memset(pool,0,sizeof(ThreadPool));
		snprintf(pool->thread_pool_name,sizeof(pool->thread_pool_name),
			 	 "TP-%s",threadpoolname);
		pool->pool_id = GetThreadPoolID();
		pool->total = threads;
	}
	return pool;
}

void ThreadPoolFree(ThreadPool * pool)
{
	if(pool != NULL){
		free(pool);
	}
}

int ThreadsCheckFlag(ThreadVars *tv, uint16_t flag)
{
    return tv->flags & flag ? 1 : 0;
}

/**
 * \brief Set a thread flag.
 */
void ThreadsSetFlag(ThreadVars *tv, uint16_t flag)
{
    tv->flags |= flag;
}

/**
 * \brief Unset a thread flag.
 */
void ThreadsUnsetFlag(ThreadVars *tv, uint16_t flag)
{
    tv->flags &= ~flag;
}


//CPU Affinity Set
/*
static int SetCPUAffinitySet(cpu_set_t *cs) 
{
    pid_t tid = syscall(SYS_gettid);
    int r = sched_setaffinity(tid, sizeof(cpu_set_t), cs);

    if (r != 0) {
        printf("Warning: sched_setaffinity failed (%d): %s\n", r,
               strerror(errno));
        return -1;
    }

    return 0;
}

static int SetCPUAffinity(uint16_t cpuid)
{
    int cpu = (int)cpuid;
	
    cpu_set_t cs;

    CPU_ZERO(&cs);
    CPU_SET(cpu, &cs);
    return SetCPUAffinitySet(&cs);
}

int ThreadSetCPUAffinity(ThreadVars *tv, uint16_t cpu)
{
    tv->thread_setup_flags |= THREAD_SET_AFFINITY;
    tv->cpu_affinity = cpu;

    return 0;
}


int ThreadSetCPU(ThreadVars *tv, uint8_t type)
{
    if (!threading_set_cpu_affinity)
        return 0;

    if (type > MAX_CPU_SET) {
        printf("invalid cpu type family\n");
        return 0;
    }

    tv->thread_setup_flags |= THREAD_SET_AFFTYPE;
    tv->cpu_affinity = type;

    return 0;
}



int ThreadGetNbThreads(uint8_t type)
{
    if (type >= MAX_CPU_SET) {
        printf("invalid cpu type family\n");
        return 0;
    }

    return thread_affinity[type].nb_threads;
}

int ThreadSetupOptions(ThreadVars *tv)
{
    if (tv->thread_setup_flags & THREAD_SET_AFFINITY) {
        printf("Setting affinity for \"%s\" Module to cpu/core "
                  "%d, thread id %lu", tv->name, tv->cpu_affinity,tv->tid);
        SetCPUAffinity(tv->cpu_affinity);
    }
    if (tv->thread_setup_flags & THREAD_SET_AFFTYPE) {
		
        ThreadsAffinityType *taf = &thread_affinity[tv->cpu_affinity];
        SetCPUAffinitySet(&taf->cpu_set);
		tv->thread_priority = taf->prio;
		printf("Setting prio %d for \"%s\" thread "
               ", thread id %lu", tv->thread_priority,tv->name, tv->tid);
    }
    return 0;
}
*/

void ThreadRemove(ThreadVars *tv, int family)
{
	ThreadPool * pool = (ThreadPool *)tv->threadpool;
    if (pool->head[family] == NULL) {
        return;
    }
	
    ThreadVars *t = pool->head[family];
    while (t != tv) {
        t = t->next;
    }

    if (t != NULL) {
        if (t->prev != NULL)
            t->prev->next = t->next;
        if (t->next != NULL)
            t->next->prev = t->prev;

    if (t == pool->head[family])
        pool->head[family] = t->next;
    }
	
    return;
}

void ThreadKillThread(ThreadVars *tv)
{

    if (tv == NULL)
        return;
	
    ThreadsSetFlag(tv, THV_KILL);
    ThreadsSetFlag(tv, THV_DEINIT);

    /* to be sure, signal more */
    int cnt = 0;
    while (1) {
        if (ThreadsCheckFlag(tv, THV_CLOSED)) {
            printf("signalled the thread %d times\n", cnt);
            break;
        }

        cnt++;
		
        usleep(10);
    }
	
    /* join it */
    pthread_join(tv->tid, NULL);
    printf("thread %s stopped\n", tv->name);

    return;
}


void ThreadKillThreadsFamily(ThreadPool *pool,int family)
{
    ThreadVars *tv = NULL;

    if ((family < 0) || (family >= TVT_MAX))
        return;

    tv = pool->head[family];

    while (tv) {
        ThreadKillThread(tv);

        tv = tv->next;
    }
}

void ThreadKillThreads(ThreadPool *pool)
{
    int i = 0;

    for (i = 0; i < TVT_MAX; i++) {
        ThreadKillThreadsFamily(pool,i);
    }

    return;
}

ThreadVars * ThreadAlloc(ThreadPool * pool)
{
	if(pool->req_total >= pool->total)
		return NULL;
	ThreadVars * tv = (ThreadVars *)malloc(sizeof(ThreadVars));
	if(tv != NULL){
		pool->req_total++;
	}
	return tv;
}


void ThreadFree(ThreadVars *tv)
{
    if (tv == NULL)
        return;
	
    printf("Freeing thread '%s'.", tv->name);
	ThreadPool * pool = (ThreadPool *)tv->threadpool;
	pool->req_total--;
	free(tv);
}

void ThreadClearThreadsFamily(ThreadPool *pool,int family)
{
    ThreadVars *tv = NULL;
    ThreadVars *ptv = NULL;

    if ((family < 0) || (family >= TVT_MAX))
        return;

    tv = pool->head[family];

    while (tv) {
        ptv = tv;
        tv = tv->next;
        ThreadFree(ptv);
    }
    tv = pool->head[family] = NULL;
	
}

void ThreadClearThreads(ThreadPool * pool)
{
	ThreadKillThreads(pool);

	int i = 0;

	for (i = 0; i < TVT_MAX; i++) {
		ThreadClearThreadsFamily(pool,i);
	}
	return;
}
 
/*add thread to list*/
void ThreadAppend(ThreadVars *tv, int type)
{
	ThreadPool * pool = (ThreadPool *)tv->threadpool;

    if (pool->head[type] == NULL) {
        pool->head[type] = tv;
        tv->next = NULL;
        tv->prev = NULL;
        return;
    }

    ThreadVars *t = pool->head[type];
	
    while (t) {
        if (t->next == NULL) {
            t->next = tv;
            tv->prev = t;
            tv->next = NULL;
            break;
        }

        t = t->next;
    }
	
    return;	
}


void *ThreadRun(void *td) 
{
    /* block usr2.  usr2 to be handled by the main thread only */
    sigset_t x;
    sigemptyset(&x);
	sigaddset(&x,SIGUSR2);
	sigprocmask(SIG_BLOCK, &x, NULL);
	
    ThreadVars * tv = (ThreadVars *)td;
	
    /* Set the thread name */
	char tname[16] = "";
	if(strlen(tv->name) > 16){
		printf("Thread name is too long, truncating it...\n");
	}
	strncpy(tname, tv->name, 15);
	tname[15] = '\0';
	pthread_setname_np(pthread_self(),tname);

    if (tv->thread_setup_flags != 0){
		;//set priority or affinity
    }
	
	int ret;
	
	ret = tv->trf->ThreadInit(tv,tv->data);
	if(ret < 0){
		ThreadsSetFlag(tv, THV_CLOSED | THV_RUNNING_DONE);
		pthread_exit((void *) -1);	
	}
	
    ThreadsSetFlag(tv, THV_INIT_DONE);

	int run = 1;
    while(run) {
        if (ThreadsCheckFlag(tv, THV_PAUSE)) {
            ThreadsSetFlag(tv, THV_PAUSED);
            ThreadTestUnPaused(tv);
            ThreadsUnsetFlag(tv, THV_PAUSED);
        }

        ret = tv->trf->ThreadLoop(tv,tv->data);

        if (ret < 0 || ThreadsCheckFlag(tv, THV_KILL) || tce_ctl_flags) {
            run = 0;
        }
        if (ret == 0) {
            run = 0;
        }
    }
	
    ThreadsSetFlag(tv, THV_RUNNING_DONE);
    ThreadWaitForFlag(tv, THV_DEINIT);

 	tv->trf->ThreadExit(tv,tv->data);
	ret = tv->trf->ThreadDeinit(tv,tv->data);
    if(ret < 0){
		ThreadsSetFlag(tv, THV_CLOSED);
        pthread_exit((void *) -1);
        return NULL;
	}
    ThreadsSetFlag(tv, THV_CLOSED);
    pthread_exit((void *) 0);
    return NULL;
}

int ThreadStart(ThreadVars *tv)
{
    pthread_attr_t attr;
    if (tv->tm_func == NULL) {
        printf("ERROR: no thread function set\n");
        return -1;
    }

    /* Initialize and set thread detached attribute */
    pthread_attr_init(&attr);

    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);

    int rc = pthread_create(&tv->tid, &attr, tv->tm_func, (void *)tv);
    if (rc) {
        printf("ERROR; return code from pthread_create() is %d\n", rc);
        return -1;
    }

    ThreadWaitForFlag(tv, THV_INIT_DONE | THV_RUNNING_DONE);

    ThreadAppend(tv, tv->type);
    return 0;
}

void TmThreadSetAOF(ThreadVars *tv, uint8_t aof)
{
    if (tv != NULL)
        tv->aof = aof;

    return;
}


void ThreadTestUnPaused(ThreadVars *tv)
{
    while (ThreadsCheckFlag(tv, THV_PAUSE)) {
        usleep(100);

        if (ThreadsCheckFlag(tv, THV_KILL))
            break;
    }
    return;
}

void ThreadWaitForFlag(ThreadVars *tv, uint16_t flags)
{
    while (!ThreadsCheckFlag(tv, flags)) {
        usleep(10);
    }

    return;
}

void ThreadContinue(ThreadVars *tv)
{
    ThreadsUnsetFlag(tv, THV_PAUSE);

    return;
}

void ThreadContinueFamily(ThreadPool * pool,int family)
{
    ThreadVars *tv = NULL;
    if ((family < 0) || (family >= TVT_MAX))
        return;
	tv = pool->head[family];
	while ( tv != NULL ) {
		ThreadContinue(tv);
        tv = tv->next;
    }
	return;
}

void ThreadContinueThreads(ThreadPool * pool)
{
    ThreadVars *tv = NULL;
    int i = 0;
	
    for (i = 0; i < TVT_MAX; i++) {
        tv = pool->head[i];
        while (tv != NULL) {
            ThreadContinue(tv);
            tv = tv->next;
        }
    }
	
    return;
}

void ThreadPause(ThreadVars *tv)
{
    ThreadsSetFlag(tv, THV_PAUSE);

    return;
}

void ThreadPauseFamily(ThreadPool * pool,int family)
{
    ThreadVars *tv = NULL;
    if ((family < 0) || (family >= TVT_MAX))
        return;
	tv = pool->head[family];
	while ( tv != NULL ) {
		ThreadPause(tv);
        tv = tv->next;
    }
	return;
}


void ThreadPauseThreads(ThreadPool * pool)
{
    ThreadVars *tv = NULL;
    int i = 0;

    for (i = 0; i < TVT_MAX; i++) {
        tv = pool->head[i];
        while (tv != NULL) {
            ThreadPause(tv);
            tv = tv->next;
        }
    }
    return;
}

static void ThreadRestartThread(ThreadVars *tv)
{
    if (tv->restarted >= THV_MAX_RESTARTS) {
        printf("thread restarts exceeded threshold limit for thread \"%s\"\n", tv->name);
        exit(-1);
    }

    ThreadsUnsetFlag(tv, THV_CLOSED);
    ThreadsUnsetFlag(tv, THV_FAILED);

    if (ThreadStart(tv) != 0) {
        printf("thread \"%s\" failed to start\n", tv->name);
        exit(-1);
    }

    tv->restarted++;
    printf("thread \"%s\" restarted", tv->name);

    return;
}

void ThreadCheckThreadState(ThreadPool * pool)
{
    ThreadVars *tv = NULL;
    int i = 0;

    for (i = 0; i < TVT_MAX; i++) {
        tv = pool->head[i];

        while (tv) {
            if (ThreadsCheckFlag(tv, THV_FAILED)) {
                ThreadsSetFlag(tv, THV_DEINIT);
                pthread_join(tv->tid, NULL);
                if ((tv_aof & THV_ENGINE_EXIT) || (tv->aof & THV_ENGINE_EXIT)) {
                    tce_ctl_flags |= TCE_KILL;
                    return;
                } else {
                    /* if the engine kill-stop has been received by now, chuck
                     * restarting and return to kill the engine */
                    if ((tce_ctl_flags & TCE_KILL) ||
                        (tce_ctl_flags & TCE_STOP)) {
                        return;
                    }
                    ThreadRestartThread(tv);
                }
            }
            tv = tv->next;
        }
    }
}


int ThreadWaitOnThreadInit(ThreadPool * pool)
{
    ThreadVars *tv = NULL;
    int i = 0;
    uint16_t mgt_num = 0;
    uint16_t ppt_num = 0;

    for (i = 0; i < TVT_MAX; i++) {
        tv = pool->head[i];
        while (tv != NULL) {
            int started = 0;
            while (started == 0) {
                if (ThreadsCheckFlag(tv, THV_INIT_DONE)) {
                    started = 1;
                } else {
                    usleep(100);
                }

                if (ThreadsCheckFlag(tv, THV_FAILED)) {
                    printf("thread \"%s\" failed to initialize.\n", tv->name);
                    return -1;
                }
                if (ThreadsCheckFlag(tv, THV_CLOSED)) {
                    printf("thread \"%s\" closed on initialization.\n", tv->name);
                    return -1;
                }
            }

            if (i == TVT_MGMT) mgt_num++;
            else if (i == TVT_PPT) ppt_num++;

            tv = tv->next;
        }
    }
    printf("all %d packet processing threads, %d management "
              "threads initialized, engine started.\n", ppt_num, mgt_num);

    return 0;
}

ThreadVars * ThreadsGetCallingThread(ThreadPool * pool)
{
    pthread_t self = pthread_self();
    ThreadVars *tv = NULL;
    int i = 0;
	
    for (i = 0; i < TVT_MAX; i++) {
        tv = pool->head[i];
        while (tv) {
            if (pthread_equal(self, tv->tid)) {
                return tv;
            }
            tv = tv->next;
        }
    }
	
    return NULL;
}


