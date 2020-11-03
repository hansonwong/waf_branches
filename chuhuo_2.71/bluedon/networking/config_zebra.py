#! /usr/bin/env python
# -*- coding:utf-8 -*-


from networking.config_ospf import ospf_port_data
from networking.config_rip import rip_port_data
from networking.config_bgp import bgp_port_data


def execute_data():
    item_ospf_port_data, item_ospf_port, item_ospf_ip = ospf_port_data()
    item_rip_port, item_rip_name, item_rip_ip = rip_port_data()
    item_bgp_port, item_bgp_ip = bgp_port_data()

    item_data = []
    for i in range(len(item_ospf_port)):
        item1 = "interface %s" % item_ospf_port[i]
        item2 = "ip address %s" % item_ospf_ip[i]
        item_data.append(item1)
        item_data.append(item2)
    for j in range(len(item_rip_name)):
        item3 = "interface %s" % item_rip_name[j]
        item4 = "ip address %s" % item_rip_ip[j]
        item_data.append(item3)
        item_data.append(item4)
    for i in range(len(item_bgp_port)):
        item5 = "interface %s" % item_bgp_port[i]
        item6 = "ip address %s" % item_bgp_ip[i]
        item_data.append(item5)
        item_data.append(item6)
    return item_data


def conf_zebra():
    item_data = execute_data()
    zebra_data = ["hostname zebra", "password centos7", "enable password centos7"]
    with open("/usr/local/etc/zebra.conf", "w") as f:
        for i in zebra_data:
            f.write(str(i) + "\n")
        for i in item_data:
            f.write(str(i) + "\n")


if __name__ == "__main__":
    conf_zebra()