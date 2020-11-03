#! /usr/bin/env python
# -*- coding:utf-8 -*-


import os
import json
from logging import getLogger
from networking.config_zebra import conf_zebra
from networking.config_ospf import conf_ospf, ospf_port_data
from networking.config_rip import conf_rip, rip_port_data
from networking.config_bgp import conf_bgp, bgp_port_data
from db.mysql_db import select_one


def backup():
    cmd_add = "ip addr add %s brd +  dev %s"
    ospf_data, ospf_port, ospf_ip = ospf_port_data()
    rip_data, rip_port, rip_ip = rip_port_data()
    bgp_port, bgp_ip = bgp_port_data()
    try:
        for i in range(len(ospf_port)):
            os.system(cmd_add % (ospf_port[i], ospf_ip[i]))
        for i in range(len(rip_port)):
            os.system(cmd_add % (rip_port[i], rip_ip[i]))
        for i in range(len(bgp_port)):
            os.system(cmd_add % (bgp_port[i], bgp_ip[i]))
    except Exception as e:
        getLogger('main').error(e)

    sql = 'select sValue from m_tbconfig where sName = "BGPSetting"'
    res = select_one(sql)['sValue']
    res = json.loads(res) 
    if res['sRouterID']:
        conf_bgp()

    sql = 'select sValue from m_tbconfig where sName = "OSPFSet"'
    res = select_one(sql)['sValue']
    res = json.loads(res) 
    if res['sOSPFRouterID']:
        conf_ospf()

    sql = 'select sValue from m_tbconfig where sName = "RIPSet"'
    res = select_one(sql)['sValue']
    res = json.loads(res) 
    if res['sRIPRouterON']:
        conf_rip()
    conf_zebra()

if __name__ == "__main__":
    backup()
    print "dynamic route well done"

