#include <dpdk_warp.h>
#include "dpdk_frame.h"
#include "flow.h"


static struct system_info *sysinfo;

int main(int argc, char *argv[]) 
{
	sysinfo = get_dpdkshm("TS", (char*)"program1");
	if (!sysinfo)
		return -1;
	
	struct Flow_entry * entry;
	while(1){
		if(!rte_ring_sc_dequeue(sysinfo->ftab.ts,(void**)&entry)){
			printf("ip_src = %u.%u.%u.%u ip_dst = %u.%u.%u.%u port_src = %u port_dst = %u proto = %u\n",
					NIPQUAD(entry->key[0].ip_src),
					NIPQUAD(entry->key[0].ip_dst),
					entry->key[0].port_src,
					entry->key[0].port_dst,
					entry->key[0].proto);
			printf("appId:%u    allbytes:%lu, bytes:%u, Rallbytes:%lu, Rbytes:%u\n\n",
				   entry->protoapp,
				   entry->stats.totalbytes[0],
				   entry->stats.TS_bytes[0],
				   entry->stats.totalbytes[1],
				   entry->stats.TS_bytes[1]);
			entry->stats.TS_bytes[0] = 0;
			entry->stats.TS_bytes[1] = 0;
		}
		usleep(1);
	}

	return 0;
}


