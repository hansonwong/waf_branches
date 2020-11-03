#ifndef __BRIDGE_SIMPLE_H
#define __BRIDGE_SIMPLE_H

//#define BRIDGE_ON

void do_bridge(struct rte_mbuf *m);
uint16_t do_bridge_broadcast(struct rte_mbuf **m_clone,struct rte_mbuf *src_mbuf);
int port_brid_update(struct portinfo  *portinfos,uint8_t  portid,int mode,int value);

#endif /*__BRIDGE_SIMPLE_H*/