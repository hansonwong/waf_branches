/*-
 * GPL LICENSE SUMMARY
 *
 *   Copyright(c) 2010-2014 Intel Corporation. All rights reserved.
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of version 2 of the GNU General Public License as
 *   published by the Free Software Foundation.
 *
 *   This program is distributed in the hope that it will be useful, but
 *   WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *   General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program; if not, write to the Free Software
 *   Foundation, Inc., 51 Franklin St - Fifth Floor, Boston, MA 02110-1301 USA.
 *   The full GNU General Public License is included in this distribution
 *   in the file called LICENSE.GPL.
 *
 *   Contact Information:
 *   Intel Corporation
 */

#ifndef _KNI_DEV_H_
#define _KNI_DEV_H_

#include <linux/if.h>
#include <linux/wait.h>
#include <linux/sched.h>
#include <linux/netdevice.h>
#include <linux/spinlock.h>
#include <linux/list.h>

#ifdef RTE_KNI_VHOST
#include <net/sock.h>
#endif

#include <exec-env/rte_kni_common.h>
#define KNI_KTHREAD_RESCHEDULE_INTERVAL 5 /* us */

struct rte_eth_stats {
	uint64_t ipackets;  /**< Total number of successfully received packets. */
	uint64_t opackets;  /**< Total number of successfully transmitted packets.*/
	uint64_t ibytes;    /**< Total number of successfully received bytes. */
	uint64_t obytes;    /**< Total number of successfully transmitted bytes. */
	uint64_t imissed;   /**< Total of RX missed packets (e.g full FIFO). */
	uint64_t ibadcrc;   /**< Total of RX packets with CRC error. */
	uint64_t ibadlen;   /**< Total of RX packets with bad length. */
	uint64_t ierrors;   /**< Total number of erroneous received packets. */
	uint64_t oerrors;   /**< Total number of failed transmitted packets. */
	uint64_t imcasts;   /**< Total number of multicast received packets. */
	uint64_t rx_nombuf; /**< Total number of RX mbuf allocation failures. */
	uint64_t fdirmatch; /**< Total number of RX packets matching a filter. */
	uint64_t fdirmiss;  /**< Total number of RX packets not matching any filter. */
	uint64_t tx_pause_xon;  /**< Total nb. of XON pause frame sent. */
	uint64_t rx_pause_xon;  /**< Total nb. of XON pause frame received. */
	uint64_t tx_pause_xoff; /**< Total nb. of XOFF pause frame sent. */
	uint64_t rx_pause_xoff; /**< Total nb. of XOFF pause frame received. */
	uint64_t q_ipackets[RTE_ETHDEV_QUEUE_STAT_CNTRS];
	/**< Total number of queue RX packets. */
	uint64_t q_opackets[RTE_ETHDEV_QUEUE_STAT_CNTRS];
	/**< Total number of queue TX packets. */
	uint64_t q_ibytes[RTE_ETHDEV_QUEUE_STAT_CNTRS];
	/**< Total number of successfully received queue bytes. */
	uint64_t q_obytes[RTE_ETHDEV_QUEUE_STAT_CNTRS];
	/**< Total number of successfully transmitted queue bytes. */
	uint64_t q_errors[RTE_ETHDEV_QUEUE_STAT_CNTRS];
	/**< Total number of queue packets received that are dropped. */
	uint64_t ilbpackets;
	/**< Total number of good packets received from loopback,VF Only */
	uint64_t olbpackets;
	/**< Total number of good packets transmitted to loopback,VF Only */
	uint64_t ilbbytes;
	/**< Total number of good bytes received from loopback,VF Only */
	uint64_t olbbytes;
	/**< Total number of good bytes transmitted to loopback,VF Only */

	/* add by bluedon */
	uint64_t omissed;  /**< Total of TX missed packets (e.g full FIFO). */
};

/**
 * A structure describing the private information for a kni device.
 */

struct kni_dev {
	/* kni list */
	struct list_head list;

	struct net_device_stats stats;
	int status;
	uint16_t group_id;           /* Group ID of a group of KNI devices */
	unsigned core_id;            /* Core ID to bind */
	char name[RTE_KNI_NAMESIZE]; /* Network device name */
	struct task_struct *pthread;

	/* wait queue for req/resp */
	wait_queue_head_t wq;
	struct mutex sync_lock;

	/* PCI device id */
	uint16_t device_id;

	/* kni device */
	struct net_device *net_dev;
	struct net_device *lad_dev;
	struct pci_dev *pci_dev;

	/* queue for packets to be sent out */
	void *tx_q;

	/* queue for the packets received */
	void *rx_q;

	/* queue for the allocated mbufs those can be used to save sk buffs */
	void *alloc_q;

	/* free queue for the mbufs to be freed */
	void *free_q;

	/* request queue */
	void *req_q;

	/* response queue */
	void *resp_q;

	void * sync_kva;
	void *sync_va;
#define USER_STATUS	0x01
#define KERN_STATUS	0x02
	char *status_uk;
	
	void *mbuf_kva;
	void *mbuf_va;

	struct rte_eth_stats *stats_uk;

	/* mbuf size */
	unsigned mbuf_size;

	/* synchro for request processing */
	unsigned long synchro;

#ifdef RTE_KNI_VHOST
	struct kni_vhost_queue* vhost_queue;
	volatile enum {
		BE_STOP = 0x1,
		BE_START = 0x2,
		BE_FINISH = 0x4,
	}vq_status;
#endif
};

#define KNI_ERR(args...) printk(KERN_DEBUG "KNI: Error: " args)
#define KNI_PRINT(args...) printk(KERN_DEBUG "KNI: " args)
#ifdef RTE_KNI_KO_DEBUG
	#define KNI_DBG(args...) printk(KERN_DEBUG "KNI: " args)
#else
	#define KNI_DBG(args...)
#endif

#ifdef RTE_KNI_VHOST
unsigned int
kni_poll(struct file *file, struct socket *sock, poll_table * wait);
int kni_chk_vhost_rx(struct kni_dev *kni);
int kni_vhost_init(struct kni_dev *kni);
int kni_vhost_backend_release(struct kni_dev *kni);

struct kni_vhost_queue {
	struct sock sk;
	struct socket *sock;
	int vnet_hdr_sz;
	struct kni_dev *kni;
	int sockfd;
	unsigned int flags;
	struct sk_buff* cache;
	struct rte_kni_fifo* fifo;
};

#endif

#ifdef RTE_KNI_VHOST_DEBUG_RX
	#define KNI_DBG_RX(args...) printk(KERN_DEBUG "KNI RX: " args)
#else
	#define KNI_DBG_RX(args...)
#endif

#ifdef RTE_KNI_VHOST_DEBUG_TX
	#define KNI_DBG_TX(args...) printk(KERN_DEBUG "KNI TX: " args)
#else
	#define KNI_DBG_TX(args...)
#endif

#endif

