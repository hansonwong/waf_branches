#include <dpdk_warp.h>
#include "dpdk_frame.h"
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/types.h>          
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/un.h>
#include <signal.h>

#include "flow.h"

//#define SEND_OF_TIMER 1
#define RELTIME_MAX_USER 50	//Real-time display  user of home page
#define TSBLOCK_SIZE 256			//Report statistics  the number of a block data
#define TRAFFIC_MAX_TYPE 1024*1024	//max ndpi mark type
#define COUNT_APP_LARGEST_NUM 10 //The number of the maximum value in the application of statistics

#define USER_MAX_NUM 1024	//The maximum number of users
#define MAX_BUF_SIZE 1024		//send buffer max size

#define RELTIME_DATA_PORT 5678	//Home page data port
#define TABLE_DATA_PORT 5679	//Report data port
#define TABLE_NUM_OF_TIMES 50	//The number of data in the report data
#define USER_NUM_OF_TIMES 25	//The number of data in the user data

#define HOME_PAGE_SPACE_TIME 3	//Home page data interval
#define MAX_SPACE_TIME 30			//Report the time interval data
#define TS_FLAG_FILE "/etc/ts_flag"		//Switch the file path traffic statistics
uint64_t PER_SECOND_TICK;			
uint64_t HOME_PAGE_SPACE_TICK;

struct user_traffic_data{
	uint32_t user_ip;
	uint32_t downstream;
	uint32_t upstream;
};
struct flow_info{
	uint32_t sip;
	uint32_t dip;
	uint32_t data[2];
	uint32_t mark;
	uint8_t proto;
};
struct tsblock{
	uint32_t flag;
	uint32_t data_begin_time;
	struct flow_info data[TSBLOCK_SIZE];
	uint32_t read;
	uint32_t write;
};
enum {
	HOME_SOCK,
	TABLE_SOCK,
};
typedef struct source_data{
	uint64_t last_send_time;
	int block_count;	
	int user_num;
	struct tsblock block_data[TSBLOCK_SIZE];
	uint32_t application_num[TRAFFIC_MAX_TYPE];
	uint32_t application_traffic[TRAFFIC_MAX_TYPE];
	struct user_traffic_data user_traffic[USER_MAX_NUM];
} data_t;

struct sock_src{
	int  sock_fd;
	struct sockaddr_in home_addr;
	struct sockaddr_in table_addr;
};

typedef struct table_data{
	uint32_t uip;
	uint32_t tcp_size;
	uint32_t udp_size;
	uint32_t icmp_size;
	uint32_t tcp_app_count;
	uint32_t tcp_app[TSBLOCK_SIZE][2];
	uint32_t udp_app_count;
	uint32_t udp_app[TSBLOCK_SIZE][2];
}table_data_t;

int check_times;
static struct system_info *sysinfo;
struct sock_src sock_data;
data_t data;
uint32_t app_num_count=0;
table_data_t src_data4table[TSBLOCK_SIZE*2];


/*
#define rdtsc(low,high) \
      __asm__ __volatile__("rdtsc" : "=a" (low), "=d" (high))

unsigned long long get_cycles()
{
	unsigned low, high;
	unsigned long long val;
	rdtsc(low,high);
	val = high;
	val = (val << 32) | low;
	return val;
}
*/

static void sock_init(void){
	memset(&sock_data.home_addr,0,sizeof(sock_data.home_addr));
	sock_data.home_addr.sin_family=AF_INET;
	sock_data.home_addr.sin_addr.s_addr=htonl(INADDR_ANY);
	sock_data.home_addr.sin_port=htons(RELTIME_DATA_PORT);

	
	memset(&sock_data.table_addr,0,sizeof(sock_data.table_addr));
	sock_data.table_addr.sin_family=AF_INET;
	sock_data.table_addr.sin_addr.s_addr=htonl(INADDR_ANY);
	sock_data.table_addr.sin_port=htons(TABLE_DATA_PORT);

	sock_data.sock_fd=socket(AF_INET,SOCK_DGRAM,0);
}  

static void send_data2(int sock,char *buffer,int len){
	int ret=0;
	if(sock==HOME_SOCK){
		sendto(sock_data.sock_fd,buffer,len,0,(struct sockaddr *)&sock_data.home_addr,sizeof(sock_data.home_addr));
		//printf("%s\n",buffer);
	}
	else if(sock==TABLE_SOCK){
		sendto(sock_data.sock_fd,buffer,len,0,(struct sockaddr *)&sock_data.table_addr,sizeof(sock_data.table_addr));
		//printf("%s\n",buffer);
	}
}

static void send_user_data(void){
	int i,j;
	struct user_traffic_data temp;
	char info_buf[MAX_BUF_SIZE]={0};
	for(i=0;i<(RELTIME_MAX_USER-1) && i<(data.user_num-1);i++){
		for(j=i+1;j<USER_MAX_NUM && j<data.user_num;j++){
			if((data.user_traffic[i].downstream+data.user_traffic[i].upstream)<(data.user_traffic[j].downstream+data.user_traffic[j].upstream)){
				memset(&temp,0,sizeof(struct user_traffic_data));
				memcpy(&temp,&data.user_traffic[i],sizeof(struct user_traffic_data));
				memcpy(&data.user_traffic[i],&data.user_traffic[j],sizeof(struct user_traffic_data));
				memcpy(&data.user_traffic[j],&temp,sizeof(struct user_traffic_data));
			}
		}
		if(data.user_traffic[i].user_ip==0 ||(data.user_traffic[i].upstream+data.user_traffic[i].downstream)==0){
			break;
		}
	}
	memset(info_buf,0,MAX_BUF_SIZE);
	sprintf(info_buf,"user\n");
	for(i=0;i<RELTIME_MAX_USER && i<data.user_num;i++){
		if(((i%USER_NUM_OF_TIMES)==0) && (i != 0)){
			send_data2(HOME_SOCK,info_buf,strlen(info_buf));
			memset(info_buf,0,MAX_BUF_SIZE);
		}
		sprintf(info_buf+strlen(info_buf),"%u.%u.%u.%u,%d,%d\n",NIPQUAD(data.user_traffic[i].user_ip),
			data.user_traffic[i].upstream,data.user_traffic[i].downstream);
	}
	sprintf(info_buf+strlen(info_buf),"end\n");
	send_data2(HOME_SOCK,info_buf,strlen(info_buf));
	data.user_num=0;
	memset(data.user_traffic,0,sizeof(data.user_traffic));
}

static void send_application_data(void){	
	uint32_t i,j=0;
	int temp=0;
	char info_buf[MAX_BUF_SIZE]={0};
	for(i=0;i<COUNT_APP_LARGEST_NUM && i<app_num_count;i++){
		for(j=i+1;j<app_num_count;j++){
			if(data.application_traffic[data.application_num[i]]<data.application_traffic[data.application_num[j]]){
				temp=data.application_num[i];
				data.application_num[i]=data.application_num[j];
				data.application_num[j]=temp;
			}
		}
	}
	sprintf(info_buf,"application\n");
	for(i=0;i<COUNT_APP_LARGEST_NUM && i<app_num_count;i++){
		sprintf(info_buf+strlen(info_buf),"%d,%d\n",data.application_num[i],data.application_traffic[data.application_num[i]]);
	}	
	send_data2(HOME_SOCK,info_buf,strlen(info_buf));

	app_num_count=0;
	memset(data.application_num,0,sizeof(data.application_num));
	memset(data.application_traffic,0,sizeof(data.application_traffic));
}

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

static void send_table_data(void){
	char data_buf[MAX_BUF_SIZE]={0};
	int i=0;
	uint32_t j=0;
	for(i=0;i<TSBLOCK_SIZE*2;i++){
		if(src_data4table[i].uip==0)
			break;
		memset(data_buf,0,sizeof(data_buf));
		sprintf(data_buf+strlen(data_buf),"%u.%u.%u.%u |1|%d |%d |%d",
			NIPQUAD(src_data4table[i].uip),
			src_data4table[i].tcp_size,
			src_data4table[i].udp_size,
			src_data4table[i].icmp_size
			);
		send_data2(TABLE_SOCK,data_buf,strlen(data_buf));
		memset(data_buf,0,sizeof(data_buf));
		if(src_data4table[i].tcp_app_count>0){
			sprintf(data_buf+strlen(data_buf),"%u.%u.%u.%u |2",NIPQUAD(src_data4table[i].uip));
			
			for(j=0;j<src_data4table[i].tcp_app_count;j++){
				if(j!=0 && (j%TABLE_NUM_OF_TIMES)==0){
					send_data2(TABLE_SOCK,data_buf,strlen(data_buf));
					memset(data_buf,0,sizeof(data_buf));
					sprintf(data_buf+strlen(data_buf),"%u.%u.%u.%u |2",NIPQUAD(src_data4table[i].uip));
				}
				sprintf(data_buf+strlen(data_buf),"|%d,%d",src_data4table[i].tcp_app[j][0],src_data4table[i].tcp_app[j][1]);
			}
			send_data2(TABLE_SOCK,data_buf,strlen(data_buf));
			memset(data_buf,0,sizeof(data_buf));
		}
		if(src_data4table[i].udp_app_count>0){
			sprintf(data_buf+strlen(data_buf),"%u.%u.%u.%u |3",NIPQUAD(src_data4table[i].uip));
			
			for(j=0;j<src_data4table[i].udp_app_count;j++){
				if(j!=0 && (j%TABLE_NUM_OF_TIMES)==0){
					send_data2(TABLE_SOCK,data_buf,strlen(data_buf));
					memset(data_buf,0,sizeof(data_buf));
					sprintf(data_buf+strlen(data_buf),"%u.%u.%u.%u |3",NIPQUAD(src_data4table[i].uip));
				}
				sprintf(data_buf+strlen(data_buf),"|%d,%d",src_data4table[i].udp_app[j][0],src_data4table[i].udp_app[j][1]);
			}
			send_data2(TABLE_SOCK,data_buf,strlen(data_buf));
		}
	}	
	memset(src_data4table,0,sizeof(src_data4table));
}

static void stitistics_table(uint32_t ip,uint8_t proto,uint32_t mark,uint32_t size){
	int i=0;
	for(i=0;i<TSBLOCK_SIZE*2;i++){
		if(src_data4table[i].uip==ip){
			switch(proto){
				case 1:
					src_data4table[i].icmp_size+=size;
					break;
				case 6:
					src_data4table[i].tcp_size+=size;
					src_data4table[i].tcp_app[src_data4table[i].tcp_app_count][0]=mark;
					src_data4table[i].tcp_app[src_data4table[i].tcp_app_count][1]+=size;
					src_data4table[i].tcp_app_count++;
					break;
				case 17:
					src_data4table[i].udp_size+=size;
					src_data4table[i].udp_app[src_data4table[i].udp_app_count][0]=mark;
					src_data4table[i].udp_app[src_data4table[i].udp_app_count][1]+=size;
					src_data4table[i].udp_app_count++;
					break;
				default:
					break;
			}
			break;
		}
		else if(src_data4table[i].uip==0){
			src_data4table[i].uip=ip;
			switch(proto){
				case 1:
					src_data4table[i].icmp_size=size;
					break;
				case 6:
					src_data4table[i].tcp_size=size;
					src_data4table[i].tcp_app[src_data4table[i].tcp_app_count][0]=mark;
					src_data4table[i].tcp_app[src_data4table[i].tcp_app_count][1]=size;
					src_data4table[i].tcp_app_count++;
					break;
				case 17:
					src_data4table[i].udp_size=size;
					src_data4table[i].udp_app[src_data4table[i].udp_app_count][0]=mark;
					src_data4table[i].udp_app[src_data4table[i].udp_app_count][1]=size;
					src_data4table[i].udp_app_count++;
					break;
				default:
					break;
			}
			break;
		}
	}
}

static void count_block_data(int block_num){
	int i=0;
	for(i=0;i<TSBLOCK_SIZE;i++){
		stitistics_table(data.block_data[block_num].data[i].sip,
			data.block_data[block_num].data[i].proto,
			data.block_data[block_num].data[i].mark,
			data.block_data[block_num].data[i].data[0]+data.block_data[block_num].data[i].data[1]
			);
		stitistics_table(data.block_data[block_num].data[i].dip,
			data.block_data[block_num].data[i].proto,
			data.block_data[block_num].data[i].mark,
			data.block_data[block_num].data[i].data[0]+data.block_data[block_num].data[i].data[1]
			);
		data.block_data[block_num].read++;
		if(data.block_data[block_num].read==data.block_data[block_num].write){
			break;
		}
	}
	memset(&data.block_data[block_num],0,sizeof(data.block_data[block_num]));
	send_table_data();
}

static void *process_count_table_data(void){
	int i=0;
	int ret;
	uint32_t time;
	int count_flag=0;
	char info_buf[MAX_BUF_SIZE]={0};
	while(1){
		for(i=0;i<TSBLOCK_SIZE;i++){
			if(data.block_data[i].flag==1){
				count_flag=1;
				count_block_data(i);
			}
		}
		if(count_flag!=1){
			time=get_timenow();
			if(data.block_data[data.block_count].data_begin_time != 0&&
				(time-data.block_data[data.block_count].data_begin_time)>MAX_SPACE_TIME &&
				data.block_data[data.block_count].flag==0){
				data.block_data[data.block_count].flag=1;
				data.block_count++;
				data.block_count=data.block_count&255;
				if(data.block_count==0){
					count_block_data(255);
				}
				else{
					count_block_data(data.block_count-1);
				}
			}
			else{
				usleep(1000);
			}
		}
		count_flag=0;
	}
	pthread_exit(NULL);
}

static int check_server_alive(void){
	check_times++;
	if(check_times!=12)
		return 0;
	check_times=0;
	char buffer[MAX_BUF_SIZE]={0};
	FILE *fd;
	char cmd[]="ps -ef | grep /home/ng_platform/bd_dpdk_warper/server/mp_server | grep -v grep";
	fd=popen(cmd,"r");
	if(fgets(buffer,sizeof(buffer),fd)!=NULL){
		pclose(fd);
		return 0;
	}
	else{
		pclose(fd);
		return -1;
	}
}

static void table_traffic_count(uint32_t sip,uint32_t dip,uint8_t proto,uint32_t mark,uint32_t size,uint32_t rsize){
	if(data.block_data[data.block_count].flag==0){
		data.block_data[data.block_count].data[data.block_data[data.block_count].write].sip=sip;
		data.block_data[data.block_count].data[data.block_data[data.block_count].write].dip=dip;
		data.block_data[data.block_count].data[data.block_data[data.block_count].write].proto=proto;
		data.block_data[data.block_count].data[data.block_data[data.block_count].write].mark=mark;
		data.block_data[data.block_count].data[data.block_data[data.block_count].write].data[0]=size;
		data.block_data[data.block_count].data[data.block_data[data.block_count].write].data[1]=rsize;
		if(data.block_data[data.block_count].write==0){
			data.block_data[data.block_count].data_begin_time=get_timenow();
		}
		data.block_data[data.block_count].write++;
		if(data.block_data[data.block_count].write==TSBLOCK_SIZE && data.block_data[data.block_count].flag==0){
			data.block_data[data.block_count].flag=1;
			data.block_count++;
			data.block_count=data.block_count & 255;
		}
	}
}

static void reltime_traffic_count(uint32_t ip,uint32_t mark,uint32_t upstream_size,uint32_t downstream_size){
	int i=0;
	uint32_t min_data=upstream_size+downstream_size;
	int index=-1;
	//application traffic
	if(data.application_traffic[mark]==0 && downstream_size!=0){
		data.application_num[app_num_count]=mark;
		app_num_count++;
	}
	data.application_traffic[mark]+=downstream_size;
	if(data.user_num!=USER_MAX_NUM){
		for(i=0;i<USER_MAX_NUM;i++){
			//home page traffic 
			if(data.user_traffic[i].user_ip==ip){
				data.user_traffic[i].upstream+=upstream_size;				
				data.user_traffic[i].downstream+=downstream_size;
				break;
			}
			else if(data.user_traffic[i].user_ip==0){
				data.user_num++;
				data.user_traffic[i].user_ip = ip;
				data.user_traffic[i].upstream=upstream_size;
				data.user_traffic[i].downstream=downstream_size;
				break;
			}
		}
	}
	else{
		for(i=0;i<USER_MAX_NUM;i++){
			//home page traffic 
			if(min_data>(data.user_traffic[i].upstream+data.user_traffic[i].downstream)){
				min_data=data.user_traffic[i].upstream+data.user_traffic[i].downstream;
				index=i;
			}
			if(data.user_traffic[i].user_ip==ip){		
				data.user_traffic[i].upstream+=upstream_size;				
				data.user_traffic[i].downstream+=downstream_size;
				break;
			}
		}
		if(i==USER_MAX_NUM && index!=-1){
			data.user_traffic[index].user_ip = ip;
			data.user_traffic[index].upstream=upstream_size;				
			data.user_traffic[index].downstream=downstream_size;
		}
	}

}

static void count_traffic_data(void){
	 int ret;
	 double flow_space_time;
	 //double space_last_time;
	 struct Flow_entry * entry;
	 uint32_t flow_size[2]={0};
	 while(1){
		if(sysinfo->ftab.ts_flag==1 && sysinfo->ftab.ts!=NULL){
			 if(!rte_ring_sc_dequeue(sysinfo->ftab.ts,(void**)&entry)){			 	
#ifndef	SEND_OF_TIMER	
				if((entry->stats.curr_count-data.last_send_time)>HOME_PAGE_SPACE_TICK){
					if(data.last_send_time != 0){
						send_application_data();
						send_user_data();
						check_server_alive();
					}
					data.last_send_time=entry->stats.curr_count;
				}
#endif								
				flow_space_time=(double)(entry->stats.curr_count-entry->stats.last_count)/PER_SECOND_TICK;
				flow_size[0]=(uint32_t)(entry->stats.TS_bytes[0]/flow_space_time);
				flow_size[1]=(uint32_t)(entry->stats.TS_bytes[1]/flow_space_time);
				if(entry->key[0].ip_src == 0 ||entry->key[0].ip_dst==0 ||(flow_size[0]==0 &&flow_size[1]==0))
					continue;
				
				//printf("ip_src = %u.%u.%u.%u,  ip_dst = %u.%u.%u.%u, proto = %d, appId:%d\n  bytes:%d   Rbytes:%d\n",
				//NIPQUAD(entry->key[0].ip_src),NIPQUAD(entry->key[0].ip_dst),entry->key[0].proto,entry->protoapp,entry->stats.TS_bytes[0],entry->stats.TS_bytes[1]);
				//src [0]up [1]down
				reltime_traffic_count(entry->key[0].ip_src,entry->protoapp,flow_size[0],flow_size[1]);
				//dst [1]up [0]down
				reltime_traffic_count(entry->key[0].ip_dst,entry->protoapp,flow_size[1],flow_size[0]);
				//count table data
				table_traffic_count(entry->key[0].ip_src,entry->key[0].ip_dst,entry->key[0].proto,entry->protoapp,
				entry->stats.TS_bytes[0],entry->stats.TS_bytes[1]);
				
				entry->stats.TS_bytes[0] = 0;
				entry->stats.TS_bytes[1] = 0;
			}	
			 else{
				 usleep(10000);
			 }
		}
		else{
			sleep(HOME_PAGE_SPACE_TIME);
		}
	}
}

static void  progress_exit(int singo){
	void * buf[1];	
	struct Flow_entry * entry;
	int i;
	sysinfo->ftab.ts_flag=0;
	for(i=0;i<1024;i++){
		if(!rte_ring_sc_dequeue(sysinfo->ftab.ts,(void**)&entry)){
			entry->stats.TS_bytes[0] = 0;
			entry->stats.TS_bytes[1] = 0;
		}
	}
	close(sock_data.sock_fd);
	printf("count progress exit\n");
	exit(-1);
}

#ifdef SEND_OF_TIMER
static void timer_to_do(int singo){	
	//send application count data
	send_application_data();	
	//send user count data
	send_user_data();
	check_server_alive();
}
#endif

static int data_init(void){	
	int res = 0;
	int i=0;
	struct itimerval tick;
	memset(&tick, 0, sizeof(tick));
	memset(&data,0,sizeof(data));
	memset(&sock_data,0,sizeof(sock_data));
	memset(src_data4table,0,sizeof(src_data4table));
	
	PER_SECOND_TICK = sysinfo->hz;
	HOME_PAGE_SPACE_TICK=HOME_PAGE_SPACE_TIME * PER_SECOND_TICK;
	sysinfo->ftab.tstime=(HOME_PAGE_SPACE_TIME * PER_SECOND_TICK);
	if(!access(TS_FLAG_FILE,0)){
	    sysinfo->ftab.ts_flag=1;
	}
	check_times=0;
	sock_init();

	//create pthread
	pthread_t pid;
	if(pthread_create(&pid,NULL,(void *)process_count_table_data,NULL)!=0){
		perror("pthread_create err!");
		exit(-1);
	}
	signal(SIGTERM,progress_exit);
	signal(SIGINT,progress_exit);
#ifdef SEND_OF_TIMER
	//Timeout to run first time
	tick.it_value.tv_sec = HOME_PAGE_SPACE_TIME;
	tick.it_value.tv_usec = 0;
	//After first, the Interval time for clock
	tick.it_interval.tv_sec = HOME_PAGE_SPACE_TIME;
	tick.it_interval.tv_usec = 0;	
	signal(SIGALRM, timer_to_do);
	if(setitimer(ITIMER_REAL, &tick, NULL) < 0){
		printf("Set timer failed!\n");
		return -1;
	}
#endif
	return 0;
}

int main(int argc, char *argv[])
{
	int ret;
	ret = check_server_alive();
	if(ret == -1){
		printf("mp_server is not alive,exit!\n");
		exit(-1);
	}
        //sysinfo=get_dpdkshm((char*)"dpdk-system-info", (char*)"program1");
        sysinfo=get_dpdkshm("TS", (char*)"program1");
        if(!sysinfo) {
                printf("get sharemeory fail\n");
                return -1;
        }	
	ret =data_init();
	if(ret ==-1){
		exit(-1);
	}
	count_traffic_data();
	return 0;
}

