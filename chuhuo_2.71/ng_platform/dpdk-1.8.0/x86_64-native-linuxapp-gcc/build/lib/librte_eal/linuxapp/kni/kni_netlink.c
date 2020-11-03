#include <linux/init.h>
#include <linux/module.h>
#include <linux/timer.h>
#include <linux/time.h>
#include <linux/types.h>
#include <net/sock.h>
#include <net/netlink.h> 
#include <linux/wait.h>
#include <linux/version.h>

#define NETLINK_KNI 25
#define MAX_PAYLOAD 1024 

enum TYPE {
	USER_START=1,
	KENEL_REQUEST,
	USER_REPLAY,
	USER_STOP
};

static  int pid=-1;
static  struct sock *nl_sk = NULL;
static  char   buf[MAX_PAYLOAD];
static  unsigned long seq=0;
static  int user_replay=0;
static wait_queue_head_t kni_wq;

void kni_netlink_senddata(void *msg,int slen,int type)
{
    struct sk_buff *skb;
    struct nlmsghdr *nlh;
    int size = NLMSG_SPACE(slen);
    
    if(!msg || !nl_sk) {
        return ;
    }
    if(pid==-1) {
	 printk(KERN_ERR "kni_netlink error:pid==-1\n");
        return ;
    }
    skb = alloc_skb(size,GFP_ATOMIC);
    if(!skb) {
        printk(KERN_ERR "kni_netlink error:alloc_skb fail\n");
        return ;
    }
    
    nlh = nlmsg_put(skb,0,0,0,size-sizeof(struct nlmsghdr),0);
    memcpy(NLMSG_DATA(nlh),msg,slen);
    nlh->nlmsg_len = size; 
    nlh->nlmsg_type =(type==-1)?KENEL_REQUEST:type;
    nlh->nlmsg_seq = seq++;

#if LINUX_VERSION_CODE <= KERNEL_VERSION(2,6,32)
    NETLINK_CB(skb).pid = 0;
#elif LINUX_VERSION_CODE <= KERNEL_VERSION(3,2,29)
    NETLINK_CB(skb).pid = 0;
#else
    NETLINK_CB(skb).portid=0;
#endif
    NETLINK_CB(skb).dst_group = 0;

    user_replay=0;
    netlink_unicast(nl_sk,skb,pid,MSG_DONTWAIT);
}

static void kni_netlink_recvdata(struct sk_buff *__skb)
 {
     struct sk_buff *skb;
     struct nlmsghdr *nlh;
     static char stop[]="stop";
     unsigned long seq_reply;
     skb = skb_get (__skb);
     if(skb->len >= NLMSG_SPACE(0))
     {
         nlh = nlmsg_hdr(skb);
         if(nlh->nlmsg_type==USER_START) {
         	pid = nlh->nlmsg_pid;
		printk("kni_netlink:user start,pid=%d\n",pid) ;
         }else   if(nlh->nlmsg_type==USER_STOP) {
         	pid = nlh->nlmsg_pid;
		printk("kni_netlink:user stop,pid=%d\n",pid) ;
		kni_netlink_senddata(stop,strlen(stop),USER_STOP);
		pid=-1;
         } else {
         	pid = nlh->nlmsg_pid;
         	seq_reply=nlh->nlmsg_seq;
         	printk("kni_netlink:receive user data\n") ;
         	if(seq!=seq_reply) 
         		printk("kni_netlink receive userdata error:expect seq %lu,buf %lu\n",seq,seq_reply) ;
         	else {
         		user_replay=1;
         		wake_up_interruptible(&kni_wq);
			memcpy(buf, NLMSG_DATA(nlh), nlh->nlmsg_len-NLMSG_SPACE(0));
         	}
         }
         kfree_skb(skb);
    }
 }

int kni_netlink_recvcheck(void **reply) {
	int ret_val;
	ret_val = wait_event_interruptible_timeout(kni_wq,
			user_replay, 3 * HZ);
	if (signal_pending(current) || ret_val <= 0) 
		return -1;

	*reply=buf;
	return 0;
}

// Initialize netlink
int kni_netlink_init(void)
{
#if LINUX_VERSION_CODE <= KERNEL_VERSION(2,6,32)
    nl_sk = netlink_kernel_create(&init_net, NETLINK_KNI, 1,
                                 kni_netlink_recvdata, NULL, THIS_MODULE);
#elif LINUX_VERSION_CODE <= KERNEL_VERSION(3,2,29)
    nl_sk = netlink_kernel_create(&init_net, NETLINK_KNI, 1,
                                 kni_netlink_recvdata, NULL, THIS_MODULE);
#else
	struct netlink_kernel_cfg cfg = {
		.groups	= 1,
		.input	= kni_netlink_recvdata,
	};
	nl_sk = netlink_kernel_create(&init_net, NETLINK_KNI, &cfg);
#endif
    if(!nl_sk){
        printk(KERN_ERR "kni_netlink: create netlink socket error.\n");
        return -1;
    }
    init_waitqueue_head(&kni_wq);
    printk("kni_netlink: init\n");
    return 0;
}

void kni_netlink_exit(void)
{
    if(nl_sk != NULL){
        sock_release(nl_sk->sk_socket);
    }
    printk("kni_netlink: module exited\n");
}

