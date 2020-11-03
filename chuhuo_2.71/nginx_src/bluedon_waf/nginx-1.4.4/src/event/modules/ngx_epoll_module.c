
/*
 * Copyright (C) Igor Sysoev
 * Copyright (C) Nginx, Inc.
 */


#include <ngx_config.h>
#include <ngx_core.h>
#include <ngx_event.h>


#if (NGX_TEST_BUILD_EPOLL)

/* epoll declarations */

#define EPOLLIN        0x001
#define EPOLLPRI       0x002
#define EPOLLOUT       0x004
#define EPOLLRDNORM    0x040
#define EPOLLRDBAND    0x080
#define EPOLLWRNORM    0x100
#define EPOLLWRBAND    0x200
#define EPOLLMSG       0x400
#define EPOLLERR       0x008
#define EPOLLHUP       0x010

#define EPOLLET        0x80000000
#define EPOLLONESHOT   0x40000000

#define EPOLL_CTL_ADD  1
#define EPOLL_CTL_DEL  2
#define EPOLL_CTL_MOD  3


typedef union epoll_data {
    void         *ptr;
    int           fd;
    uint32_t      u32;
    uint64_t      u64;
} epoll_data_t;

struct epoll_event {
    uint32_t      events;
    epoll_data_t  data;
};


int epoll_create(int size);

int epoll_create(int size)
{
    return -1;
}


int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);

int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event)
{
    return -1;
}


int epoll_wait(int epfd, struct epoll_event *events, int nevents, int timeout);

int epoll_wait(int epfd, struct epoll_event *events, int nevents, int timeout)
{
    return -1;
}

#if (NGX_HAVE_FILE_AIO)

#define SYS_io_setup      245
#define SYS_io_destroy    246
#define SYS_io_getevents  247
#define SYS_eventfd       323

typedef u_int  aio_context_t;

struct io_event {
    uint64_t  data;  /* the data field from the iocb */
    uint64_t  obj;   /* what iocb this event came from */
    int64_t   res;   /* result code for this event */
    int64_t   res2;  /* secondary result */
};


#endif
#endif


typedef struct {
    ngx_uint_t  events;
    ngx_uint_t  aio_requests;
} ngx_epoll_conf_t;





//add by vincent
struct ether_vlan_hdr {
	struct ether_addr d_addr; 		//Destination address
	struct ether_addr s_addr; 		// Source address
	uint16_t ether_type1;     		// 1 level VLAN type flag
	uint16_t vlanout;				// 1 level VLAN ID
	uint16_t ether_type2;			// 2 level VLAN type flag
	uint16_t vlanin;                // 2 level VLAN ID
	uint16_t ether_type3; 			// ehter type
} __attribute__((__packed__));


//send the data to the dpdk from buf
void ngx_dpdk_send_buf(char *buf, unsigned len, uint8_t outport) {
    dpqk_priv_send(ngx_client_waf, buf, len, outport);
}
//end add by vincent

// add by suntus
int ngx_is_response_ex(int package_dir,int bridge_port) {
    if(package_dir==-1) return ngx_is_response(bridge_port);
    else return package_dir==1?1:0;
}
int ngx_is_response(int bridge_port) {
    int i = 0;
    for (; i < ngx_cycle->bridge_count; i++) {
        if (bridge_port == (ngx_cycle->bridge_set)[i][1])
            return 0;
    }
    return 1;
}

int ngx_get_bridge_out(int bridge_in) {
    int i = 0;

    if(bridge_in < 0)
        return -1;

    //fprintf(stderr, "bridge_count = %d\n", ngx_cycle->bridge_count);
    //fprintf(stderr, "bin[0] = %d, bout[0]=%d, bin[1] = %d, bout[1] = %d\n",
            //(ngx_cycle->bridge_set)[0][0], (ngx_cycle->bridge_set)[0][1],
            //(ngx_cycle->bridge_set)[1][0], (ngx_cycle->bridge_set)[1][1]);

    for (; i < ngx_cycle->bridge_count; i++) {
        if (bridge_in == (ngx_cycle->bridge_set)[i][0]){
            return (ngx_cycle->bridge_set)[i][1];
        }else if(bridge_in == (ngx_cycle->bridge_set)[i][1]){
            return (ngx_cycle->bridge_set)[i][0];
        }
    }

    return -1;
}

int ngx_server_packet(ngx_cycle_t *cycle,int *ppackage_dir,in_addr_t dip,in_addr_t sip)
{
    ngx_str_t * p_server_ip;
    uint32_t i;
    in_addr_t server_ip;

	if(cycle->server_ips.nelts<1) return 1;
	//char cSip[16]={0};
    //char cDip[16]={0};
    //memcpy(cSip,inet_ntoa(*((struct in_addr*)&sip)),strlen(inet_ntoa(*((struct in_addr*)&sip))));
    //memcpy(cDip,inet_ntoa(*((struct in_addr*)&dip)),strlen(inet_ntoa(*((struct in_addr*)&dip))));
    
    p_server_ip = cycle->server_ips.elts;
    *ppackage_dir = 0;
    for(i=0;i<cycle->server_ips.nelts;i++){
        server_ip = inet_addr((char*)p_server_ip[i].data);
        //fprintf(stderr, "return 1 server_ip= %s,%s\n", p_server_ip[i].data,(inet_ntoa(*((struct in_addr*)&server_ip))));
        if(server_ip == dip || server_ip == sip){
            if(server_ip == sip){
                *ppackage_dir = 1; //response packet
            }
            return 1;
        }
    }
    //fprintf(stderr, "return 0,dip = %u,%s,sip = %u,%s\n", dip,cDip,sip,cSip);
    return 0;
}


void
ngx_dpdk_forward(struct rte_mbuf *m) {
    dpdk_enqueue(ngx_client_waf, m);
}


// upstream: the tcp communication from client to webserver
static ngx_hash_connection_item_t *connection_hash_table_upstream = NULL;
// downstream: the tcp communication from webserver to client
static ngx_hash_connection_item_t *connection_hash_table_downstream = NULL;

int
ngx_hash_add_connection_item(ngx_hash_connection_key_t *key, struct rte_mbuf *m, ngx_tcp_connection_direction_t direction) {
    ngx_hash_connection_item_t *item = NULL;
    item = ngx_hash_find_connection_item(key, direction);

    if (item != NULL) {
        item->m = m;
    } else {
        item = malloc(sizeof(ngx_hash_connection_item_t));
        memset(item, 0, sizeof(ngx_hash_connection_item_t));
        item->direction = direction;
        item->key.sip = key->sip;
        item->key.sport = key->sport;
        item->key.dip = key->dip;
        item->key.dport = key->dport;
        item->m = m;

        if (direction == ngx_upstream) {
            HASH_ADD(hh, connection_hash_table_upstream, key, sizeof(ngx_hash_connection_key_t), item);
        } else {
            HASH_ADD(hh, connection_hash_table_downstream, key, sizeof(ngx_hash_connection_key_t), item);
        }
    }
    return NGX_OK;
}

int
ngx_hash_del_connection_item(ngx_hash_connection_key_t *key, ngx_tcp_connection_direction_t direction) {
    ngx_hash_connection_item_t *item = NULL;
    item = ngx_hash_find_connection_item(key, direction);
    if (item) {
        if (direction == ngx_upstream) {
            HASH_DEL(connection_hash_table_upstream, item);
        } else {
            HASH_DEL(connection_hash_table_downstream, item);
        }
        free(item);
        item = NULL;
    }
    return 0;
}

ngx_hash_connection_item_t *
ngx_hash_find_connection_item(ngx_hash_connection_key_t *key, ngx_tcp_connection_direction_t direction) {
    ngx_hash_connection_item_t *s = NULL;

    if (direction == ngx_upstream) {
        HASH_FIND(hh, connection_hash_table_upstream, key, sizeof(ngx_hash_connection_key_t), s);
    }
    else {
        HASH_FIND(hh, connection_hash_table_downstream, key, sizeof(ngx_hash_connection_key_t), s);
    }
    return s;
}

int
ngx_hash_foreach_item() {
    ngx_hash_connection_item_t *s, *tmp;
    fprintf(stderr, "----------------upstream---------------\n\n");
    int count = 0;
    HASH_ITER(hh, connection_hash_table_upstream, s, tmp) {
        count++;
    }
    fprintf(stderr, "count = %d\n", count);
    fprintf(stderr, "----------------downstream---------------\n\n");
    count = 0;
    HASH_ITER(hh, connection_hash_table_downstream, s, tmp) {
        count++;
    }
    fprintf(stderr, "count = %d\n", count);
    return 0;
}
// add by suntus end


static ngx_int_t ngx_epoll_init(ngx_cycle_t *cycle, ngx_msec_t timer);
static void ngx_epoll_done(ngx_cycle_t *cycle);
static ngx_int_t ngx_epoll_add_event(ngx_event_t *ev, ngx_int_t event,
                                     ngx_uint_t flags);
static ngx_int_t ngx_epoll_del_event(ngx_event_t *ev, ngx_int_t event,
                                     ngx_uint_t flags);
static ngx_int_t ngx_epoll_add_connection(ngx_connection_t *c);
static ngx_int_t ngx_epoll_del_connection(ngx_connection_t *c,
        ngx_uint_t flags);
static ngx_int_t ngx_epoll_process_events(ngx_cycle_t *cycle, ngx_msec_t timer,
        ngx_uint_t flags);

#if (NGX_HAVE_FILE_AIO)
static void ngx_epoll_eventfd_handler(ngx_event_t *ev);
#endif

static void *ngx_epoll_create_conf(ngx_cycle_t *cycle);
static char *ngx_epoll_init_conf(ngx_cycle_t *cycle, void *conf);

static int                  ep = -1;
static struct epoll_event  *event_list;
static ngx_uint_t           nevents;

#if (NGX_HAVE_FILE_AIO)

int                         ngx_eventfd = -1;
aio_context_t               ngx_aio_ctx = 0;

static ngx_event_t          ngx_eventfd_event;
static ngx_connection_t     ngx_eventfd_conn;

#endif

static ngx_str_t      epoll_name = ngx_string("epoll");

static ngx_command_t  ngx_epoll_commands[] = {

    {   ngx_string("epoll_events"),
        NGX_EVENT_CONF | NGX_CONF_TAKE1,
        ngx_conf_set_num_slot,
        0,
        offsetof(ngx_epoll_conf_t, events),
        NULL
    },

    {   ngx_string("worker_aio_requests"),
        NGX_EVENT_CONF | NGX_CONF_TAKE1,
        ngx_conf_set_num_slot,
        0,
        offsetof(ngx_epoll_conf_t, aio_requests),
        NULL
    },

    ngx_null_command
};


ngx_event_module_t  ngx_epoll_module_ctx = {
    &epoll_name,
    ngx_epoll_create_conf,               /* create configuration */
    ngx_epoll_init_conf,                 /* init configuration */

    {
        ngx_epoll_add_event,             /* add an event */
        ngx_epoll_del_event,             /* delete an event */
        ngx_epoll_add_event,             /* enable an event */
        ngx_epoll_del_event,             /* disable an event */
        ngx_epoll_add_connection,        /* add an connection */
        ngx_epoll_del_connection,        /* delete an connection */
        NULL,                            /* process the changes */
        ngx_epoll_process_events,        /* process the events */
        ngx_epoll_init,                  /* init the events */
        ngx_epoll_done,                  /* done the events */
    }
};

ngx_module_t  ngx_epoll_module = {
    NGX_MODULE_V1,
    &ngx_epoll_module_ctx,               /* module context */
    ngx_epoll_commands,                  /* module directives */
    NGX_EVENT_MODULE,                    /* module type */
    NULL,                                /* init master */
    NULL,                                /* init module */
    NULL,                                /* init process */
    NULL,                                /* init thread */
    NULL,                                /* exit thread */
    NULL,                                /* exit process */
    NULL,                                /* exit master */
    NGX_MODULE_V1_PADDING
};


#if (NGX_HAVE_FILE_AIO)

/*
 * We call io_setup(), io_destroy() io_submit(), and io_getevents() directly
 * as syscalls instead of libaio usage, because the library header file
 * supports eventfd() since 0.3.107 version only.
 *
 * Also we do not use eventfd() in glibc, because glibc supports it
 * since 2.8 version and glibc maps two syscalls eventfd() and eventfd2()
 * into single eventfd() function with different number of parameters.
 */

static int
io_setup(u_int nr_reqs, aio_context_t *ctx)
{
    return syscall(SYS_io_setup, nr_reqs, ctx);
}


static int
io_destroy(aio_context_t ctx)
{
    return syscall(SYS_io_destroy, ctx);
}


static int
io_getevents(aio_context_t ctx, long min_nr, long nr, struct io_event *events,
             struct timespec *tmo)
{
    return syscall(SYS_io_getevents, ctx, min_nr, nr, events, tmo);
}


static void
ngx_epoll_aio_init(ngx_cycle_t *cycle, ngx_epoll_conf_t *epcf)
{
    int                 n;
    struct epoll_event  ee;

    ngx_eventfd = syscall(SYS_eventfd, 0);

    if (ngx_eventfd == -1) {
        ngx_log_error(NGX_LOG_EMERG, cycle->log, ngx_errno,
                      "eventfd() failed");
        ngx_file_aio = 0;
        return;
    }

    ngx_log_debug1(NGX_LOG_DEBUG_EVENT, cycle->log, 0,
                   "eventfd: %d", ngx_eventfd);

    n = 1;

    if (ioctl(ngx_eventfd, FIONBIO, &n) == -1) {
        ngx_log_error(NGX_LOG_EMERG, cycle->log, ngx_errno,
                      "ioctl(eventfd, FIONBIO) failed");
        goto failed;
    }

    if (io_setup(epcf->aio_requests, &ngx_aio_ctx) == -1) {
        ngx_log_error(NGX_LOG_EMERG, cycle->log, ngx_errno,
                      "io_setup() failed");
        goto failed;
    }

    ngx_eventfd_event.data = &ngx_eventfd_conn;
    ngx_eventfd_event.handler = ngx_epoll_eventfd_handler;
    ngx_eventfd_event.log = cycle->log;
    ngx_eventfd_event.active = 1;
    ngx_eventfd_conn.fd = ngx_eventfd;
    ngx_eventfd_conn.read = &ngx_eventfd_event;
    ngx_eventfd_conn.log = cycle->log;

    ee.events = EPOLLIN | EPOLLET;
    ee.data.ptr = &ngx_eventfd_conn;

    if (epoll_ctl(ep, EPOLL_CTL_ADD, ngx_eventfd, &ee) != -1) {
        return;
    }

    ngx_log_error(NGX_LOG_EMERG, cycle->log, ngx_errno,
                  "epoll_ctl(EPOLL_CTL_ADD, eventfd) failed");

    if (io_destroy(ngx_aio_ctx) == -1) {
        ngx_log_error(NGX_LOG_ALERT, cycle->log, ngx_errno,
                      "io_destroy() failed");
    }

failed:

    if (close(ngx_eventfd) == -1) {
        ngx_log_error(NGX_LOG_ALERT, cycle->log, ngx_errno,
                      "eventfd close() failed");
    }

    ngx_eventfd = -1;
    ngx_aio_ctx = 0;
    ngx_file_aio = 0;
}

#endif



// add by suntus
void
ss_print(unsigned char *data, size_t size) {

    int is_bin = 0;
    unsigned int char_nbr;
    for (char_nbr = 0; char_nbr < size; char_nbr++)
        if (data[char_nbr] < 9 || data[char_nbr] > 127)
            is_bin = 1;

    char buffer[10240] = "";

    for (char_nbr = 0; char_nbr < size; char_nbr++) {
        if (is_bin)
            sprintf(buffer + strlen(buffer), "%02X",
                    (unsigned char) data[char_nbr]);
        else
            sprintf(buffer + strlen(buffer), "%c", data[char_nbr]);
    }
    buffer[10240 - 1] = 0;
    fprintf(stderr, "\n原始字符 %s\n", buffer);
}
// add by suntus end




static ngx_int_t
ngx_epoll_init(ngx_cycle_t *cycle, ngx_msec_t timer)
{

    ngx_epoll_conf_t  *epcf;

    epcf = ngx_event_get_conf(cycle->conf_ctx, ngx_epoll_module);

    if (ep == -1) {
        ep = epoll_create(cycle->connection_n / 2);

        if (ep == -1) {
            ngx_log_error(NGX_LOG_EMERG, cycle->log, ngx_errno,
                          "epoll_create() failed");
            return NGX_ERROR;
        }

#if (NGX_HAVE_FILE_AIO)
        ngx_epoll_aio_init(cycle, epcf);

#endif
    }
    if (nevents < epcf->events) {
        if (event_list) {
            ngx_free(event_list);
        }

        event_list = ngx_alloc(sizeof(struct epoll_event) * epcf->events,
                               cycle->log);
        if (event_list == NULL) {
            return NGX_ERROR;
        }
    }

    nevents = epcf->events;

    ngx_io = ngx_os_io;

    ngx_event_actions = ngx_epoll_module_ctx.actions;

#if (NGX_HAVE_CLEAR_EVENT)
    ngx_event_flags = NGX_USE_CLEAR_EVENT
#else
    ngx_event_flags = NGX_USE_LEVEL_EVENT
#endif
                      | NGX_USE_GREEDY_EVENT
                      | NGX_USE_EPOLL_EVENT;

    return NGX_OK;
}


static void
ngx_epoll_done(ngx_cycle_t *cycle)
{
    if (close(ep) == -1) {
        ngx_log_error(NGX_LOG_ALERT, cycle->log, ngx_errno,
                      "epoll close() failed");
    }

    ep = -1;

#if (NGX_HAVE_FILE_AIO)

    if (ngx_eventfd != -1) {

        if (io_destroy(ngx_aio_ctx) == -1) {
            ngx_log_error(NGX_LOG_ALERT, cycle->log, ngx_errno,
                          "io_destroy() failed");
        }

        if (close(ngx_eventfd) == -1) {
            ngx_log_error(NGX_LOG_ALERT, cycle->log, ngx_errno,
                          "eventfd close() failed");
        }

        ngx_eventfd = -1;
    }

    ngx_aio_ctx = 0;

#endif

    ngx_free(event_list);

    event_list = NULL;
    nevents = 0;
}


static ngx_int_t
ngx_epoll_add_event(ngx_event_t *ev, ngx_int_t event, ngx_uint_t flags)
{
    // add by suntus
    if (!ngx_cycle->dpdk_bridge) {
        // add by suntus end
        int                  op;
        uint32_t             events, prev;
        ngx_event_t         *e;
        ngx_connection_t    *c;
        struct epoll_event   ee;

        c = ev->data;

        events = (uint32_t) event;

        if (event == NGX_READ_EVENT) {
            e = c->write;
            prev = EPOLLOUT;
#if (NGX_READ_EVENT != EPOLLIN)
            events = EPOLLIN;
#endif

        } else {
            e = c->read;
            prev = EPOLLIN;
#if (NGX_WRITE_EVENT != EPOLLOUT)
            events = EPOLLOUT;
#endif
        }

        if (e->active) {
            op = EPOLL_CTL_MOD;
            events |= prev;

        } else {
            op = EPOLL_CTL_ADD;
        }

        ee.events = events | (uint32_t) flags;
        ee.data.ptr = (void *) ((uintptr_t) c | ev->instance);

        ngx_log_debug3(NGX_LOG_DEBUG_EVENT, ev->log, 0,
                       "epoll add event: fd:%d op:%d ev:%08XD",
                       c->fd, op, ee.events);

        if (epoll_ctl(ep, op, c->fd, &ee) == -1) {
            ngx_log_error(NGX_LOG_ALERT, ev->log, ngx_errno,
                          "epoll_ctl(%d, %d) failed", op, c->fd);
            return NGX_ERROR;
        }
        // add by suntus
    }
    // add by suntus end

// 标记该事件状态为活跃
    ev->active = 1;
#if 0
    ev->oneshot = (flags & NGX_ONESHOT_EVENT) ? 1 : 0;
#endif

    return NGX_OK;

}

static ngx_int_t
ngx_epoll_del_event(ngx_event_t *ev, ngx_int_t event, ngx_uint_t flags)
{

// add by suntus
    if (!ngx_cycle->dpdk_bridge) {
// add by suntus end
        int                  op;
        uint32_t             prev;
        ngx_event_t         *e;
        ngx_connection_t    *c;
        struct epoll_event   ee;

        /*
         * when the file descriptor is closed, the epoll automatically deletes
         * it from its queue, so we do not need to delete explicitly the event
         * before the closing the file descriptor
         */

        if (flags & NGX_CLOSE_EVENT) {
            ev->active = 0;
            return NGX_OK;
        }

        c = ev->data;

        if (event == NGX_READ_EVENT) {
            e = c->write;
            prev = EPOLLOUT;

        } else {
            e = c->read;
            prev = EPOLLIN;
        }

        if (e->active) {
            op = EPOLL_CTL_MOD;
            ee.events = prev | (uint32_t) flags;
            ee.data.ptr = (void *) ((uintptr_t) c | ev->instance);

        } else {
            op = EPOLL_CTL_DEL;
            ee.events = 0;
            ee.data.ptr = NULL;
        }

        ngx_log_debug3(NGX_LOG_DEBUG_EVENT, ev->log, 0,
                       "epoll del event: fd:%d op:%d ev:%08XD",
                       c->fd, op, ee.events);

        if (epoll_ctl(ep, op, c->fd, &ee) == -1) {
            ngx_log_error(NGX_LOG_ALERT, ev->log, ngx_errno,
                          "epoll_ctl(%d, %d) failed", op, c->fd);
            return NGX_ERROR;
        }
        // add by suntus
    }
    // add by suntus end
    ev->active = 0;

    return NGX_OK;
}


static ngx_int_t
ngx_epoll_add_connection(ngx_connection_t *c)
{
    // add by suntus
    if (!ngx_cycle->dpdk_bridge) {
        // add by suntus end
        struct epoll_event  ee;

        ee.events = EPOLLIN | EPOLLOUT | EPOLLET;
        ee.data.ptr = (void *) ((uintptr_t) c | c->read->instance);

        ngx_log_debug2(NGX_LOG_DEBUG_EVENT, c->log, 0,
                       "epoll add connection: fd:%d ev:%08XD", c->fd, ee.events);

        if (epoll_ctl(ep, EPOLL_CTL_ADD, c->fd, &ee) == -1) {
            ngx_log_error(NGX_LOG_ALERT, c->log, ngx_errno,
                          "epoll_ctl(EPOLL_CTL_ADD, %d) failed", c->fd);
            return NGX_ERROR;
        }
        // add by suntus
    }
    // add by suntus end
    c->read->active = 1;
    c->write->active = 1;

    return NGX_OK;
}


static ngx_int_t
ngx_epoll_del_connection(ngx_connection_t *c, ngx_uint_t flags)
{

    // add by suntus
    if (!ngx_cycle->dpdk_bridge) {
        // add by suntus end
        int                 op;
        struct epoll_event  ee;

        /*
         * when the file descriptor is closed the epoll automatically deletes
         * it from its queue so we do not need to delete explicitly the event
         * before the closing the file descriptor
         */

        if (flags & NGX_CLOSE_EVENT) {
            c->read->active = 0;
            c->write->active = 0;
            return NGX_OK;
        }

        ngx_log_debug1(NGX_LOG_DEBUG_EVENT, c->log, 0,
                       "epoll del connection: fd:%d", c->fd);

        op = EPOLL_CTL_DEL;
        ee.events = 0;
        ee.data.ptr = NULL;

        if (epoll_ctl(ep, op, c->fd, &ee) == -1) {
            ngx_log_error(NGX_LOG_ALERT, c->log, ngx_errno,
                          "epoll_ctl(%d, %d) failed", op, c->fd);
            return NGX_ERROR;
        }
        // add by suntus
    }
    // add by suntus end
    c->read->active = 0;
    c->write->active = 0;

    return NGX_OK;
}

// add by suntus

static int
in_detection_ports(ngx_cycle_t *cycle, unsigned short ports) {
    int i;
    for (i = 0; i < cycle->waf_detection_portsn; i++) {
        if (ports == cycle->waf_detection_ports[i]) {
            ngx_log_debug1(NGX_LOG_DEBUG_EVENT, cycle->log, 0,
                "[waf] match detection port: %d", ports);
            return 1;
        }
    }
    return 0;
}

static int in_filter_ports(ngx_cycle_t *cycle, int ports) {
    if(cycle->waf_filter_portsn==0)return 1;
    
    int i;
    for (i = 0; i < cycle->waf_filter_portsn; i++) {
        if (ports == cycle->waf_filter_ports[i]) {
            //ngx_log_error(NGX_LOG_ALERT, cycle->log, 0,"return 1 ports= %d\n", ports);           
            return 1;
        }
    }
    //ngx_log_error(NGX_LOG_ALERT, cycle->log, 0,"return 0 ports= %d\n", ports);
    return 0;
}


static void ngx_process_data(ngx_cycle_t *cycle, struct rte_mbuf *m) {


    // bypass设置
    if (cycle->is_bypass) {
        ngx_dpdk_forward(m);
        return ;
    }


    // 1. 过滤非tcp
    // 2. 判断上下游数据（根据端口号)
    // 3. 分别处理上下游数据

    unsigned char *pdata = rte_pktmbuf_mtod(m, unsigned char *);

    struct ether_hdr *eth;

    eth = (struct ether_hdr *)pdata;

    unsigned short ethertype = ntohs(eth->ether_type);
    if (ethertype != 0x0800 && ethertype != 0x8100) {
        ngx_dpdk_forward(m);
        return ;
    }
	//modify by vincent

	//Distinguish the VLAN packet,get the length of vlan tag
	struct ether_vlan_hdr *vlan_eth;
	int vlan_level = 0;

    int vlanhdr_len = 0;
    if (ethertype == 0x8100) {
		vlan_level = 1;

		vlan_eth =  (struct ether_vlan_hdr *)pdata;
		ethertype = ntohs(vlan_eth->ether_type2);
		if(ethertype == 0x8100){
			vlan_level = 2;
		}

		vlanhdr_len = 4*vlan_level;
    }
	//end modify

    ngx_time_update();
    // 获取该数据包的ip和tcp结构体，找到四元组
    struct iphdr *iphdrp = (struct iphdr *) (pdata + sizeof(struct ether_hdr) + vlanhdr_len);
    u_int32_t source_ip = iphdrp->saddr;
    u_int32_t dest_ip = iphdrp->daddr;
    int totle_len = ntohs(iphdrp->tot_len);   // ip数据包总长度(带负载)
    int iph_len = iphdrp->ihl << 2;   // ip头长度

    if (iphdrp->protocol != 0x06) {
        ngx_dpdk_forward(m);
        return ;
    }

    struct tcphdr *tcphdrp = (struct tcphdr *)(pdata + sizeof(struct ether_hdr) + vlanhdr_len + sizeof(struct iphdr));
    unsigned short dest_port = tcphdrp->dest;
    unsigned short source_port = tcphdrp->source;
    int tcph_len = tcphdrp->doff << 2;    // tcp头长度

    unsigned short dest_porth = ntohs(dest_port);

    if (!(in_detection_ports(cycle, dest_porth) || in_detection_ports(cycle, ntohs(source_port)))) {
        ngx_dpdk_forward(m);
        return ;
    }
   
    if (!in_filter_ports(cycle, m->inport)) {
        ngx_dpdk_forward(m);
        return ;
    }
    
    ngx_int_t header_totle_len = iph_len + tcph_len;    // ip+tcp头总长度
    ngx_int_t data_len = totle_len - header_totle_len;  // http数据长度


    // 输出tcp标志位
    u_char *p = (u_char *)&source_ip;
    u_char *q = (u_char *)&dest_ip;
    ngx_log_debug5(NGX_LOG_DEBUG_EVENT, cycle->log,
        0, "[waf] sip = %ud.%ud.%ud.%ud:%d", p[0], p[1], p[2], p[3], ntohs(source_port));
    ngx_log_debug5(NGX_LOG_DEBUG_EVENT, cycle->log,
        0, "[waf] dip = %ud.%ud.%ud.%ud:%d", q[0], q[1], q[2], q[3], ntohs(dest_port));
    ngx_log_debug4(NGX_LOG_DEBUG_EVENT, cycle->log,
        0, "[waf] syn = %d, ack = %d, rst = %d, fin = %d",
                   tcphdrp->syn, tcphdrp->ack, tcphdrp->rst, tcphdrp->fin);


    if (data_len == 0) {
        ngx_dpdk_forward(m);
        ngx_log_debug0(NGX_LOG_DEBUG_EVENT, cycle->log, 0, "data_len = 0");
    }
    else {
	     int npackage_dir=-1;    
         if(ngx_server_packet(cycle,&npackage_dir,(in_addr_t)dest_ip,(in_addr_t)source_ip)==0) {
            ngx_dpdk_forward(m);
            return ;
         }

        if(ngx_is_response_ex(npackage_dir,m->inport) == 0 && !(ngx_cycle->header_hide_server || ngx_cycle->header_hide_x_powered_by)) // 响应包且隐藏服务器信息功能未打开
        {
            //ngx_log_error(NGX_LOG_ERR, ngx_cycle->log, 4,"npackage_dir[%d],inport[%d]  !! %s, %d",npackage_dir,m->inport, __FUNCTION__, __LINE__);
            ngx_dpdk_forward(m);
            return;
        }
         
        ngx_log_debug1(NGX_LOG_DEBUG_EVENT, cycle->log,
            0, "[waf] data_len = %d", (int)data_len);

        ngx_connection_t *c;
        c = ngx_get_connection(1, cycle->log);
        //add by vincent
		c->package_dir = npackage_dir;
        c->is_hide_server = cycle->header_hide_server;
        c->is_hide_x_powered_by = cycle->header_hide_x_powered_by;
	//	c->is_sensitive_word = cycle->sensitive_enabled;
	//	c->sensitive_word_utf8= &cycle->sensitive_word_utf8;
	//	c->sensitive_word_gbk= &cycle->sensitive_word_gbk;
		c->vlan_level = vlan_level;
		
        ngx_log_debug2(NGX_LOG_DEBUG_EVENT, c->log, 0, "[waf] lanport=%d,vlan_level=%d", m->port,c->vlan_level);

        struct sockaddr_in dest_addr;
        bzero(&dest_addr, sizeof(struct sockaddr_in));
        dest_addr.sin_family = AF_INET;
        dest_addr.sin_addr.s_addr = dest_ip;
        dest_addr.sin_port = dest_port;
        //end add by vincent

        // 设置sockaddr_in的相关数值
        struct sockaddr_in servaddr;
        bzero(&servaddr, sizeof(struct sockaddr_in));
        servaddr.sin_family = AF_INET;
        servaddr.sin_addr.s_addr = source_ip;
        servaddr.sin_port = source_port;

        // 说明已经有了该连接，根据情况拿出这些数据或者丢掉
        ngx_nfq_data_t *nfq_data = &c->dd;
        nfq_data->nfq_pdata = pdata + sizeof(struct ether_hdr) + vlanhdr_len ;
        nfq_data->m = m;
        nfq_data->nfq_header_len = header_totle_len;
        nfq_data->nfq_data_len = data_len;

        c->read->ready = 1;
        c->client_waf = ngx_client_waf;

        ngx_event_accept_dpdk(c, cycle, &servaddr,&dest_addr);
        c->read->handler(c->read);    // 那些事件全都是在这里调用的

        if (c->is_forbidden) {
            if (c->dd.m) {
                dpdk_mbuf_drop(c->client_waf, c->dd.m);
                c->dd.m = NULL;
            }
            c->is_forbidden = 0;
        } else {
            if (c->dd.m) {
                ngx_dpdk_forward(c->dd.m);
                c->dd.m = NULL;
            }
        }
    }
}

// add by suntus end
static ngx_int_t
ngx_epoll_process_events(ngx_cycle_t *cycle, ngx_msec_t timer, ngx_uint_t flags)
{
    // add by suntus
    if (cycle->dpdk_bridge) {
        uint32_t  j, rx_count = 0;
        struct rte_mbuf *buf[PACKET_READ_SIZE];
        // 用阻塞的也没事，因为局域网肯定会有很多杂乱的包
        rx_count = dpdk_dequeue1(ngx_client_waf, (uint32_t)cycle->dpdk_queue_index,
                                 (void **)buf, PACKET_READ_SIZE);
        for (j = 0; j < rx_count; j++) {
            rte_prefetch0(rte_pktmbuf_mtod(buf[j], void *));
            ngx_process_data(cycle, buf[j]);
        }
        return NGX_OK;
    } else {
        int                events;
        uint32_t           revents;
        ngx_int_t          instance, i;
        ngx_uint_t         level;
        ngx_err_t          err;
        ngx_event_t       *rev, *wev, **queue;
        ngx_connection_t  *c;

        /* NGX_TIMER_INFINITE == INFTIM */

        ngx_log_debug1(NGX_LOG_DEBUG_EVENT, cycle->log, 0,
                       "epoll timer: %M", timer);

        events = epoll_wait(ep, event_list, (int) nevents, timer);

        err = (events == -1) ? ngx_errno : 0;

        if (flags & NGX_UPDATE_TIME || ngx_event_timer_alarm) {
            ngx_time_update();
        }

        if (err) {
            if (err == NGX_EINTR) {

                if (ngx_event_timer_alarm) {
                    ngx_event_timer_alarm = 0;
                    return NGX_OK;
                }

                level = NGX_LOG_INFO;

            } else {
                level = NGX_LOG_ALERT;
            }

            ngx_log_error(level, cycle->log, err, "epoll_wait() failed");
            return NGX_ERROR;
        }

        if (events == 0) {
            if (timer != NGX_TIMER_INFINITE) {
                return NGX_OK;
            }

            ngx_log_error(NGX_LOG_ALERT, cycle->log, 0,
                          "epoll_wait() returned no events without timeout");
            return NGX_ERROR;
        }

        ngx_mutex_lock(ngx_posted_events_mutex);

        for (i = 0; i < events; i++) {
            c = event_list[i].data.ptr;

            instance = (uintptr_t) c & 1;
            c = (ngx_connection_t *) ((uintptr_t) c & (uintptr_t) ~1);

            rev = c->read;

            if (c->fd == -1 || rev->instance != instance) {

                /*
                 * the stale event from a file descriptor
                 * that was just closed in this iteration
                 */

                ngx_log_debug1(NGX_LOG_DEBUG_EVENT, cycle->log, 0,
                               "epoll: stale event %p", c);
                continue;
            }

            revents = event_list[i].events;

            ngx_log_debug3(NGX_LOG_DEBUG_EVENT, cycle->log, 0,
                           "epoll: fd:%d ev:%04XD d:%p",
                           c->fd, revents, event_list[i].data.ptr);

            if (revents & (EPOLLERR | EPOLLHUP)) {
                ngx_log_debug2(NGX_LOG_DEBUG_EVENT, cycle->log, 0,
                               "epoll_wait() error on fd:%d ev:%04XD",
                               c->fd, revents);
            }

#if 0
            if (revents & ~(EPOLLIN | EPOLLOUT | EPOLLERR | EPOLLHUP)) {
                ngx_log_error(NGX_LOG_ALERT, cycle->log, 0,
                              "strange epoll_wait() events fd:%d ev:%04XD",
                              c->fd, revents);
            }
#endif

            if ((revents & (EPOLLERR | EPOLLHUP))
                    && (revents & (EPOLLIN | EPOLLOUT)) == 0)
            {
                /*
                 * if the error events were returned without EPOLLIN or EPOLLOUT,
                 * then add these flags to handle the events at least in one
                 * active handler
                 */

                revents |= EPOLLIN | EPOLLOUT;
            }

            if ((revents & EPOLLIN) && rev->active) {

                if ((flags & NGX_POST_THREAD_EVENTS) && !rev->accept) {
                    rev->posted_ready = 1;

                } else {
                    rev->ready = 1;
                }

                if (flags & NGX_POST_EVENTS) {
                    queue = (ngx_event_t **) (rev->accept ?
                                              &ngx_posted_accept_events : &ngx_posted_events);

                    ngx_locked_post_event(rev, queue);

                } else {
                    rev->handler(rev);
                }
            }

            wev = c->write;

            if ((revents & EPOLLOUT) && wev->active) {

                if (c->fd == -1 || wev->instance != instance) {

                    /*
                     * the stale event from a file descriptor
                     * that was just closed in this iteration
                     */

                    ngx_log_debug1(NGX_LOG_DEBUG_EVENT, cycle->log, 0,
                                   "epoll: stale event %p", c);
                    continue;
                }

                if (flags & NGX_POST_THREAD_EVENTS) {
                    wev->posted_ready = 1;

                } else {
                    wev->ready = 1;
                }

                if (flags & NGX_POST_EVENTS) {
                    ngx_locked_post_event(wev, &ngx_posted_events);

                } else {
                    wev->handler(wev);
                }
            }
        }

        ngx_mutex_unlock(ngx_posted_events_mutex);

        return NGX_OK;
    }
    // add by suntus end
}

#if (NGX_HAVE_FILE_AIO)

static void
ngx_epoll_eventfd_handler(ngx_event_t *ev)
{
    int               n, events;
    long              i;
    uint64_t          ready;
    ngx_err_t         err;
    ngx_event_t      *e;
    ngx_event_aio_t  *aio;
    struct io_event   event[64];
    struct timespec   ts;

    ngx_log_debug0(NGX_LOG_DEBUG_EVENT, ev->log, 0, "eventfd handler");

    n = read(ngx_eventfd, &ready, 8);

    err = ngx_errno;

    ngx_log_debug1(NGX_LOG_DEBUG_EVENT, ev->log, 0, "eventfd: %d", n);

    if (n != 8) {
        if (n == -1) {
            if (err == NGX_EAGAIN) {
                return;
            }

            ngx_log_error(NGX_LOG_ALERT, ev->log, err, "read(eventfd) failed");
            return;
        }

        ngx_log_error(NGX_LOG_ALERT, ev->log, 0,
                      "read(eventfd) returned only %d bytes", n);
        return;
    }

    ts.tv_sec = 0;
    ts.tv_nsec = 0;

    while (ready) {

        events = io_getevents(ngx_aio_ctx, 1, 64, event, &ts);

        ngx_log_debug1(NGX_LOG_DEBUG_EVENT, ev->log, 0,
                       "io_getevents: %l", events);

        if (events > 0) {
            ready -= events;

            for (i = 0; i < events; i++) {

                ngx_log_debug4(NGX_LOG_DEBUG_EVENT, ev->log, 0,
                               "io_event: %uXL %uXL %L %L",
                               event[i].data, event[i].obj,
                               event[i].res, event[i].res2);

                e = (ngx_event_t *) (uintptr_t) event[i].data;

                e->complete = 1;
                e->active = 0;
                e->ready = 1;

                aio = e->data;
                aio->res = event[i].res;

                ngx_post_event(e, &ngx_posted_events);
            }

            continue;
        }

        if (events == 0) {
            return;
        }

        /* events == -1 */
        ngx_log_error(NGX_LOG_ALERT, ev->log, ngx_errno,
                      "io_getevents() failed");
        return;
    }
}

#endif


static void *
ngx_epoll_create_conf(ngx_cycle_t *cycle)
{
    ngx_epoll_conf_t  *epcf;

    epcf = ngx_palloc(cycle->pool, sizeof(ngx_epoll_conf_t));
    if (epcf == NULL) {
        return NULL;
    }

    epcf->events = NGX_CONF_UNSET;
    epcf->aio_requests = NGX_CONF_UNSET;

    return epcf;
}


static char *
ngx_epoll_init_conf(ngx_cycle_t *cycle, void *conf)
{
    ngx_epoll_conf_t *epcf = conf;

    ngx_conf_init_uint_value(epcf->events, 512);
    ngx_conf_init_uint_value(epcf->aio_requests, 32);

    return NGX_CONF_OK;
}
