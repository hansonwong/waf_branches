#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <string.h>
#include <asm/types.h>
#include <linux/netlink.h>
#include <linux/socket.h>
#include <errno.h>

#define NETLINK_KNI 25
#define MAX_PAYLOAD 1024 

enum TYPE {
	USER_START=1,
	KENEL_REQUEST,
	USER_REPLAY,
	USER_STOP
};

char   buf[MAX_PAYLOAD];
int sock_fd=-1;

struct _recvmsg {
	char *buf;
	int len;
	unsigned int type;
	unsigned long seq;
}rcvdata;

static int 
kni_netlink_sendmsg(void *buff,int len,unsigned int type,unsigned long seq) {
	int retval;
	struct nlmsghdr nlh;
	struct sockaddr_nl nladdr;
	struct iovec iov[2] = {
		{ .iov_base = &nlh, .iov_len = sizeof(nlh) },
		{ .iov_base = buff, .iov_len = len }
	};
	struct msghdr msg = {
		.msg_name = &nladdr,
		.msg_namelen = sizeof(nladdr),
		.msg_iov = iov,
		.msg_iovlen = 2,
	};

	memset(&nladdr, 0, sizeof(nladdr));
	nladdr.nl_family = AF_NETLINK;

	nlh.nlmsg_len = NLMSG_LENGTH(len);
	nlh.nlmsg_type = type;
	nlh.nlmsg_flags = 0;
	nlh.nlmsg_pid = getpid();
	nlh.nlmsg_seq = seq;

	retval=sendmsg(sock_fd, &msg, 0);
	if(retval == -1) 
		printf("sendmsg error: %s\n",strerror(errno));
	return retval;
}

static void * kni_netlink_recvmsg(int *stop ){
	int status;
	struct nlmsghdr *h;
	struct sockaddr_nl nladdr;
	struct iovec iov;
	struct msghdr msg = {
		(void*)&nladdr, sizeof(nladdr),
		&iov,	1,
		NULL,	0,
		0
	};
	memset(&nladdr, 0, sizeof(nladdr));

	iov.iov_base = buf;
	iov.iov_len = sizeof(buf);

	status = recvmsg(sock_fd, &msg, 0);

	if (status <= 0) {
		printf("recv error:%s\n",strerror(errno));
		return 0;
	}
	
	h = (struct nlmsghdr*)buf;
	rcvdata.buf=(char *) NLMSG_DATA(h);
	rcvdata.len=h->nlmsg_len-NLMSG_SPACE(0);
      rcvdata.type=h->nlmsg_type;
      rcvdata.seq=h->nlmsg_seq;
      if( rcvdata.type==USER_STOP) {
      		*stop=1;
      		return 0;
      	}
      return  rcvdata.buf;
}

static int kni_netlink_user_reply(void *buff,int len){
	return kni_netlink_sendmsg(buff,len,USER_REPLAY,rcvdata.seq+1);
}

static int kni_netlink_user_stop(void){
	static char stop[]="stop!\n";
	return kni_netlink_sendmsg(stop,strlen(stop),USER_STOP,0);
}

static int kni_netlink_init(void){
	struct sockaddr_nl src_addr;
	int retval;
	static char hello[]="helloworld!\n";
	
	// Create a socket
	sock_fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_KNI);
	if(sock_fd == -1){
		printf("getting socket error: %s",strerror(errno));
		return -1;
	}
#if 0
	{
		struct timeval tv;
		//fcntl(sock_fd,F_SETFL,O_NONBLOCK);
		tv.tv_sec = 1;
		tv.tv_usec = 0;
		if(setsockopt(sock_fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv))<0){
			printf("socket option  SO_RCVTIMEO not support\n");
			return -1;
		}
	}
#endif
	// To prepare binding
	memset(&src_addr, 0, sizeof(src_addr));
	src_addr.nl_family = AF_NETLINK;
	src_addr.nl_pid = getpid(); // self pid
	src_addr.nl_groups = 0; // multi cast

	retval = bind(sock_fd, (struct sockaddr*)&src_addr, sizeof(src_addr));
	if(retval < 0){
		printf("bind failed: %s", strerror(errno));
		close(sock_fd);
		return -1;
   	 }
	kni_netlink_sendmsg(( void *)hello,strlen(hello),USER_START,0);
   	return 0;
}

static int kni_netlink_exit(void) {
    close(sock_fd);
    return 0;
}
