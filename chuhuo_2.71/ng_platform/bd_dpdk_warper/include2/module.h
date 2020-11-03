#ifndef _MODULE_H
#define _MODULE_H


#define MAX_MODULE_NAME   64
#define MAX_MODULES       128


//Module initialization function registered
typedef int (*init_func)(void *);
typedef int (*exit_func)(void *);

struct module_list
{
    char name[MAX_MODULE_NAME];
    init_func func;
};

extern struct module_list module_list_init[MAX_MODULES];
extern volatile uint16_t module_list_init_num;

extern struct module_list module_list_exit[MAX_MODULES];
extern volatile uint16_t module_list_exit_num;


#if 1
#define MODULE_INIT(FUNCTION)  \
    __attribute__((constructor)) static void  MODULE_INIT##_##FUNCTION(void) \
    {                                                    \
        const char *funcname= #FUNCTION;                       \
        printf("%s\n",__FUNCTION__);                       \
        memcpy(module_list_init[module_list_init_num].name,\
                    funcname,strlen(funcname));            \
        module_list_init[module_list_init_num].func=FUNCTION;\
        module_list_init_num++;                             \
    }   

#define MODULE_EXIT(FUNCTION)  \
    __attribute__((constructor)) static void  MODULE_EXIT##_##FUNCTION(void) \
    {                                                    \
        const char *funcname= #FUNCTION;                       \
        printf("%s\n",__FUNCTION__);                       \
        memcpy(module_list_exit[module_list_exit_num].name,\
                    funcname,strlen(funcname));            \
        module_list_exit[module_list_exit_num].func=FUNCTION;\
        module_list_exit_num++;                             \
    }   

#else
#define MODULE_INIT(FUNCTION)
#define MODULE_EXIT(FUNCTION)
#endif

extern void do_module_inits(void *);
extern void do_module_exits(void *);
#endif

