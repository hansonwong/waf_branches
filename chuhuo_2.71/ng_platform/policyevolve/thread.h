
#ifndef __THREADS_H__
#define __THREADS_H__

#include <unistd.h>

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#include <pthread.h>
#else
#include <pthread.h>
#endif

#include <sys/time.h>
#include <stdint.h>

#define QUEUE_NAME_SIZE  16
#define THREAD_NAME_SIZE 16

#define MAX_THREAD_POOL 16

/** Thread flags set and read by threads to control the threads */
#define THV_USE           1 /** thread is in use */
#define THV_INIT_DONE    (1 << 1) /** thread initialization done */
#define THV_PAUSE        (1 << 2) /** signal thread to pause itself */
#define THV_PAUSED       (1 << 3) /** the thread is paused atm */
#define THV_KILL         (1 << 4) /** thread has been asked to cleanup and exit */
#define THV_FAILED       (1 << 5) /** thread has encountered an error and failed */
#define THV_CLOSED       (1 << 6) /** thread done, should be joinable */
/* used to indicate the thread is going through de-init.  Introduced as more
 * of a hack for solving stream-timeout-shutdown.  Is set by the main thread. */
#define THV_DEINIT       (1 << 7)
#define THV_RUNNING_DONE (1 << 8) /** thread has completed running and is entering
                                   * the de-init phase */

/** Thread flags set and read by threads, to control the threads, when they
 *  encounter certain conditions like failure */
#define THV_RESTART_THREAD 0x01 /** restart the thread */
#define THV_ENGINE_EXIT   0x02 /** shut the engine down gracefully */

/** Maximum no of times a thread can be restarted */
#define THV_MAX_RESTARTS 50


/** thread lock*/
#define Tse_rwlock_t pthread_rwlock_t 
#define Tse_rwlock_init pthread_rwlock_init 
#define Tse_rwlock_destroy pthread_rwlock_destroy
#define Tse_rwlock_rdlock pthread_rwlock_rdlock 
#define Tse_rwlock_wrlock pthread_rwlock_wrlock
#define Tse_rwlock_unlock pthread_rwlock_unlock
#define Tse_rwlock_tryrdlock pthread_rwlock_tryrdlock
#define Tse_rwlock_trywrlock pthread_rwlock_trywrlock

/**thread mutex*/
#define Tse_mutex_t pthread_mutex_t
#define Tse_mutexattr_t pthread_mutexattr_t
#define Tse_mutex_init pthread_mutex_init
#define Tse_mutex_lock pthread_mutex_lock
#define Tse_mutex_unlock pthread_mutex_unlock
#define Tse_mutex_destroy pthread_mutex_destroy

/** \brief Per thread variable structure */

enum {
    TVT_PPT,
    TVT_MGMT,
    TVT_CMD,
    TVT_MAX,
};

struct ThreadRunModule_;


typedef struct ThreadVars_{

	char name[THREAD_NAME_SIZE];
	
	//atomic declare
    pthread_t tid;                         /**<thread id*/
	
	int id;                                /**<local id */
	
    /** aof(action on failure) determines what should be done with the thread
        when it encounters certain conditions like failures */
    uint8_t aof;

	/** no of times the thread has been restarted on failure */
	uint8_t restarted;

	uint8_t thread_setup_flags;

    /** the type of thread as defined in tm-threads.h (TVT_PPT, TVT_MGMT) */
	uint8_t type;

	uint32_t flags;
	
    uint16_t cpu_affinity; /** cpu or core number to set affinity to */
	
    uint16_t rank;
	
    int thread_priority; /** priority (real time) for this thread. Look at threads.h */

	void * (*tm_func)(void *); /*thread run func*/
	void * data;
	void * threadpool;
	struct ThreadRunModule_ *trf;
    struct ThreadVars_      *next;
    struct ThreadVars_      *prev;
}__attribute__((__packed__))  ThreadVars;

typedef struct ThreadPool_ {
	
	char thread_pool_name[THREAD_NAME_SIZE];
	
	pthread_mutex_t queue_lock;
	pthread_cond_t  queue_ready;
	//atomic declare
	
	int pool_id;
	uint16_t using_total;
	uint16_t pause_total;
	
	uint16_t total;
	uint16_t req_total;
	
	void * data;  /**< thread pool extend data,all threads can access the data*/
	ThreadVars * head[TVT_MAX];
    struct ThreadPool_ * next;
} ThreadPool;

typedef struct ThreadRunModule_ {
	
    /** thread handling */
    int  (*ThreadInit)  (ThreadVars *, void *);
	int  (*ThreadDeinit)(ThreadVars *, void *);
    void (*ThreadExit)  (ThreadVars *, void *);
    int  (*ThreadLoop)  (ThreadVars *, void *);
    /** global Init/DeInit */
    int (*Init)(void);
    int (*DeInit)(void);
    uint8_t flags;
    uint8_t priority;
	
}ThreadRunModule;

enum {
	NFQRECVPKT_MODULE,
	NFCT_MODULE,
	ADMIN_MODULE,
	MONITOR_MODULE,
    MAX_MODULE,
};

ThreadRunModule module[MAX_MODULE];


int GetThreadID(void);
int GetThreadPoolID(void);
ThreadPool * ThreadPoolCreate(int threads,char * threadpoolname);
void ThreadPoolFree(ThreadPool * pool);
int ThreadsCheckFlag(ThreadVars *tv, uint16_t flag);
void ThreadsSetFlag(ThreadVars *tv, uint16_t flag);
void ThreadsUnsetFlag(ThreadVars *tv, uint16_t flag);
void ThreadRemove(ThreadVars *tv, int family);
void ThreadKillThread(ThreadVars *tv);
void ThreadKillThreadsFamily(ThreadPool *pool,int family);
void ThreadKillThreads(ThreadPool *pool);
ThreadVars * ThreadAlloc(ThreadPool * pool);
void ThreadFree(ThreadVars *tv);
void ThreadClearThreadsFamily(ThreadPool *pool,int family);
void ThreadClearThreads(ThreadPool * pool);
void ThreadAppend(ThreadVars *tv, int type);
void *ThreadRun(void *td) ;
int ThreadStart(ThreadVars *tv);
void TmThreadSetAOF(ThreadVars *tv, uint8_t aof);
void ThreadTestUnPaused(ThreadVars *tv);
void ThreadTestUnPaused(ThreadVars *tv);
void ThreadWaitForFlag(ThreadVars *tv, uint16_t flags);
void ThreadContinue(ThreadVars *tv);
void ThreadContinueFamily(ThreadPool * pool,int family);
void ThreadContinueThreads(ThreadPool * pool);
void ThreadPause(ThreadVars *tv);
void ThreadPauseFamily(ThreadPool * pool,int family);
void ThreadPauseThreads(ThreadPool * pool);
static void ThreadRestartThread(ThreadVars *tv);
void ThreadCheckThreadState(ThreadPool * pool);
int ThreadWaitOnThreadInit(ThreadPool * pool);
ThreadVars * ThreadsGetCallingThread(ThreadPool * pool);

#endif /* __TM_THREADS_H__ */

