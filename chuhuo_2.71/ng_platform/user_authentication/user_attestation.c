#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>          
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <fcntl.h>
#include <sys/queue.h>
#include <python2.7/Python.h>

#define LISTENING_PORT 6666
#define MAX_LISTEN_CONNET 10
#define MAX_BUFF_SIZE 2048

#define MAX_USER_INFO_NUM 512
#define UPDATE_TIME_INTERVAL 5

int verbose=0;
int sock_fd;

typedef struct user_push_info{
	uint32_t user_ip;		//user IP addr
	unsigned long time;	//last updata time
	char ip_port[32];		//found ip and port
	TAILQ_ENTRY(user_push_info) next;
}info_t;

TAILQ_HEAD(use_queue_head, user_push_info) use_qhead;
TAILQ_HEAD(free_queue_head, user_push_info) free_qhead;

info_t auth_info[MAX_USER_INFO_NUM]={0};
uint32_t user_num=0;
uint32_t last_check_time=0;

static uint32_t get_timenow(void){
	int ret;
	time_t timenow;
	time(&timenow);
	if(timenow==-1){
		perror("get time now err");
		exit(-1);
	}
	timenow = (uint32_t)timenow;
	return (uint32_t)timenow;
}

void queue_init(void){
	int i = 0;
	info_t *p=NULL;
	TAILQ_INIT(&use_qhead);
	TAILQ_INIT(&free_qhead);

	p=auth_info;
	for(i=0;i<MAX_USER_INFO_NUM;i++){
		TAILQ_INSERT_TAIL(&free_qhead,p,next);
		p++;
	} 
}

static  void InitPyEv(PyObject **pModule){
	Py_Initialize();
	if ( !Py_IsInitialized())
		return;
	PyRun_SimpleString("import sys");
	PyRun_SimpleString("sys.path.append('/usr/local/bluedon/usermanage/')");
	
	*pModule = PyImport_ImportModule("authentication_ip_port");
	if(!*pModule){
		printf("import python failed!!\n");
		exit(-1);
	}
}

//Get the user corresponds to the IP and port
static int  get_ip_and_port(char *userip,char *get_ip_port,PyObject *pModule){

	PyObject *pFunction=NULL;
	PyObject *pArgs=NULL;
	PyObject *pRetValue=NULL;

	//call python mode to get strategy using the IP and port
	pFunction = PyObject_GetAttrString(pModule, "get_ip_and_port");
	if(!pFunction){
		printf("get python function failed!!!\n");
		return -1;
	}	
	pArgs = PyTuple_New(1);
	PyTuple_SetItem(pArgs, 0, Py_BuildValue("s", userip));
	pRetValue = PyObject_CallObject(pFunction, pArgs);
	sprintf(get_ip_port,"%s",PyString_AsString(pRetValue));	
	if(verbose){
		printf("get_ip_port:%s\n", get_ip_port);
	}
	if(strlen(get_ip_port)<=1){
		return -1;
	}

	Py_DECREF(pFunction);
	Py_DECREF(pArgs);
	Py_DECREF(pRetValue);

	return 0;
}

//Find the user corresponds to the IP and port
static int find_ip_and_port(uint32_t userip,char *get_ip_port,PyObject *pModule){
	info_t *p=NULL;
	int ret=-1;
	uint32_t timenow=0;
	char user_addr_str[16]={0};
	struct in_addr user_addr;
	memset(&user_addr,0,sizeof(user_addr));
	
	TAILQ_FOREACH(p,&use_qhead,next){
		if(p->user_ip==userip){
			timenow=get_timenow();
			if((timenow-p->time)>UPDATE_TIME_INTERVAL){
				user_addr.s_addr=p->user_ip;
				p->time=timenow;
				sprintf(user_addr_str,"%s",inet_ntoa(user_addr));
				if((ret=get_ip_and_port(user_addr_str,p->ip_port,pModule))!=0){
					TAILQ_REMOVE(&use_qhead,p,next);
					TAILQ_INSERT_TAIL(&free_qhead,p,next);
					user_num--;
					return -1;
				}
				if(verbose){
					printf("update user ip_port: %s\n",user_addr_str);
				}
			}			
			strcpy(get_ip_port,p->ip_port);
			return 0;
		}
	}
	return -1;
}

//add user node info
void add_user_info(uint32_t userip,char *ip_port){
	info_t *p_node=NULL;
	if(user_num>MAX_USER_INFO_NUM){
		return;
	}
	p_node=TAILQ_FIRST(&free_qhead);
	TAILQ_REMOVE(&free_qhead,p_node,next);
	memset(p_node,0,sizeof(info_t));
	p_node->user_ip=userip;
	strcpy(p_node->ip_port,ip_port);
	p_node->time=get_timenow();
	TAILQ_INSERT_TAIL(&use_qhead,p_node,next);
	user_num++;
}

//get the push url
static int recombine_url(int sock_fd,char *buff,PyObject *pModule){
	int ret;
	char *p=NULL;
	char url_src[512]={0};
	char url_head[]="HTTP/1.1 302 Moved Temporarily\r\n";
	char ip_addr[16]={0};
	char get_ip_port[32]={0};
	uint32_t timenow;
	info_t *p_node=NULL;
	
	struct sockaddr_in get_client_addr;
	socklen_t socklen;
	memset(&get_client_addr,0,sizeof(get_client_addr));
	if((ret = getpeername(sock_fd, (struct sockaddr *)&get_client_addr, &socklen))!=0){
		return -1;
	}
	memset(get_ip_port,0,sizeof(get_ip_port));
	ret=find_ip_and_port(get_client_addr.sin_addr.s_addr,get_ip_port,pModule);
	if(ret != 0){
		sprintf(ip_addr,"%s",inet_ntoa(get_client_addr.sin_addr));
		ret=get_ip_and_port(ip_addr,get_ip_port,pModule);
		if(ret!=0){
			return -1;
		}
		add_user_info(get_client_addr.sin_addr.s_addr,get_ip_port);
		if(verbose){
			printf("add user addr:%s\n", ip_addr);
		}
	}
	
	sprintf(url_src,"Location: https://%s/site/UserLogin",get_ip_port);
	sprintf(buff,"%s%s\r\n\r\n",url_head,url_src);
	timenow=get_timenow();
	if((timenow-last_check_time)>(UPDATE_TIME_INTERVAL*2)){
		if(verbose){
			printf("check time out user\n");
		}
		TAILQ_FOREACH(p_node,&use_qhead,next){
			if((timenow-p_node->time)>(UPDATE_TIME_INTERVAL*2)){
				TAILQ_REMOVE(&use_qhead,p_node,next);
				TAILQ_INSERT_TAIL(&free_qhead,p_node,next);
			}
		}
		last_check_time=timenow;
	}
	return 0;
	}

//set sock to non-blocking mode
void setsockNonBlock(int sock) {
	int flags;
	flags = fcntl(sock, F_GETFL, 0);
	if (flags < 0) {
		perror("fcntl(F_GETFL) failed");
		exit(EXIT_FAILURE);
	}
	if (fcntl(sock, F_SETFL, flags | O_NONBLOCK) < 0) {
		perror("fcntl(F_SETFL) failed");
		exit(EXIT_FAILURE);
	}
}

int sock_init(){
	struct sockaddr_in server_addr;
	int opt = 1;
	int len = sizeof(server_addr);
	memset(&server_addr,0,sizeof(struct sockaddr_in));
	server_addr.sin_family=AF_INET;
	server_addr.sin_addr.s_addr=INADDR_ANY;
	server_addr.sin_port = htons(LISTENING_PORT);
	if((sock_fd = socket(AF_INET, SOCK_STREAM, 0))==-1){
		perror("socket err!");
		exit(-1);
	}
	
	if(setsockopt(sock_fd,SOL_SOCKET,SO_REUSEADDR,(char *)&opt,len)==-1){
		 perror("setsockopt err:");
		 close(sock_fd);
		 exit(-1);
	}
	setsockNonBlock(sock_fd);
	if(bind(sock_fd,(struct sockaddr *)&server_addr,sizeof(server_addr))==-1){
		perror("sock bind err!");
		close(sock_fd);
		exit(-1);
	}
	if(listen(sock_fd, MAX_LISTEN_CONNET) == -1){
		perror("listen sock err!");
		close(sock_fd);
		exit(-1);
	}
	return 0;
}

int update_maxfd(fd_set fds, int maxfd) {
	int i;
	int new_maxfd = 0;
	for (i = 0; i <= maxfd; i++) {
		if (FD_ISSET(i, &fds) && i > new_maxfd) {
			new_maxfd = i;
		}
	}
	return new_maxfd;
}

static void redirect_url(void){
	int i;
	struct sockaddr_in client_addr;
	socklen_t addrlen=sizeof(client_addr);
	char http_respone[1024];
	unsigned char recv_buff[MAX_BUFF_SIZE]={0};
	int ret;
	int new_sock;

	//python environment init
	PyObject *pModule=NULL;
	InitPyEv(&pModule);

	sock_init();	
	//recombine_url(http_respone);
	struct timeval tv_out;
	int maxfd;
	int conn_count= 0;
	maxfd=sock_fd;
	fd_set readfds;
	fd_set readfds_bak;
	FD_ZERO(&readfds);
	FD_ZERO(&readfds_bak);
	FD_SET(sock_fd, &readfds_bak);

	while(1){
		readfds = readfds_bak;
		maxfd = update_maxfd(readfds, maxfd);		//update maxfd
		tv_out.tv_sec = 3;
		tv_out.tv_usec = 0;
		
		if(verbose){
			printf("selecting maxfd=%d\n", maxfd);
		}
		ret = select(maxfd + 1, &readfds, NULL, NULL, &tv_out);
		if (ret == -1){
			perror("select failed");
			exit(EXIT_FAILURE);
		} 
		else if (ret == 0){
			continue;
		}
		for (i = 0; i <= maxfd; i++){
			if (!FD_ISSET(i, &readfds)){
				continue;
			}

			if ( i == sock_fd){
				new_sock = accept(sock_fd, (struct sockaddr *) &client_addr, &addrlen); //accept a request
				if (new_sock == -1){
					perror("accept failed");
					exit(EXIT_FAILURE);
				}
				setsockNonBlock(new_sock);
				if (new_sock > maxfd) {
					maxfd = new_sock;
				}
				FD_SET(new_sock, &readfds_bak);
			} 
			else {
				memset(recv_buff, 0, sizeof(recv_buff));
				if ( (ret = recv(i, recv_buff, sizeof(recv_buff), 0)) == -1 ){
					perror("recv failed");
					continue;
				}
				if(verbose){
					printf("recved from new_sock=%d : %s(%d length string)\n", i, recv_buff, ret);
				}
				if(ret != 0 && ret !=-1){					
					memset(http_respone,0,sizeof(http_respone));
					ret=recombine_url(i,http_respone,pModule);	//get post back url
					
					if(verbose){
						printf("resend buff: %s\n", http_respone);
					}
					if(ret==0){
						if((ret=send(i,http_respone,strlen(http_respone),0))==-1){	//send back message
							perror("send err!");
							close(i);
							break;
						}
					}
				}
				if ( close(i) == -1 ) {
					perror("close failed");
					exit(EXIT_FAILURE);
				}
				if(verbose){
					printf("close new_sock=%d done\n", i);
				}
				FD_CLR(i, &readfds_bak);
			}
		}
	}
	close(sock_fd);	
	Py_DECREF(pModule);
	Py_Finalize();
	return;
}

//help information
void usage(char *argv){
	fprintf(stdout,"Usage: %s \n",argv);
	fprintf(stdout,"or\n");
	fprintf(stdout,"Usage: %s  -v 	--for print debug info \n",argv);
}

int main(int argc,char **argv){
	if(argc>2){
		usage(argv[0]);
		exit(-1);
	}
	if(argc==2){
		if(strcmp(argv[1],"-v")==0){
			verbose=1;
		}
		else{
			usage(argv[0]);
			exit(-1);
		}
	}
	queue_init();
	redirect_url();
	return 0;
}

