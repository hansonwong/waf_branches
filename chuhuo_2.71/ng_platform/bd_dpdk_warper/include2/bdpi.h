#ifndef __BDPI_H__
#define __BDPI_H__


typedef void * (*malloc_func)(size_t);
typedef void   (*free_func)(void *); 
typedef void * (*bdpi_flow_alloc_func)(void);
typedef int    (*bdpi_flow_free_func)(void *);

struct bdpi_init_params {
    uint16_t is_ext_open;     
    uint16_t flowalloctype;  /*0 default, 1 user*/
    uint16_t flowsize;       /*if flowalloctype is user, is size of one flow*/
    uint16_t tcpcount;
    uint16_t udpcount;
    uint16_t othercount;
    unsigned int core_mask;
    const char * extlibpath;
    const char * logconf;
    const char * logtype;
    malloc_func _malloc;
    free_func   _free;
    bdpi_flow_alloc_func flowalloc;
    bdpi_flow_free_func  flowfree;
};

int bdpi_flow_free(void ** flow);
int bdpi_flow_alloc(void ** flow);
int bdpi_init(struct bdpi_init_params * params);
int bdpi_exit(void);
int bdpi_packet_analyzer(void * flow,const unsigned char * packet,const unsigned short  packetlen,unsigned int coreid,unsigned int *appid);
void bdpi_getappname_by_appid(u_int32_t appid,char * appname,u_int32_t ulen);

#endif /*__BDPI_H__*/
