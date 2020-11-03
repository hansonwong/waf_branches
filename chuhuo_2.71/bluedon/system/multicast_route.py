#!/usr/bin/env python
# coding=utf-8
"""
author:
    cdg
modify:
    2017-03-10:
        添加V1, V2, V3条件的判断
"""

import os
import sys
import json
import shelve
from db.mysql_db import select_one


def multicast_route():
    """
    组播使能的网口,还需判断其在网口配置中状态是否开启,工作模式是否为路由模式
    """
    db = shelve.open('multicast_router')
    if db.has_key('nic'):
        for tmp in db['nic']:
            os.system('echo "0" > /proc/sys/net/ipv4/conf/%s/force_igmp_version' % tmp)
        del db['nic']
    tmp = select_one('select sValue from m_tbconfig where sName = "RouterForward"')
    if tmp:
        multicast_nic = json.loads(tmp['sValue'])
    else:
        db.close()
        return
    nic_list = []
    if multicast_nic['iStatus'] == '1':
        sversion = multicast_nic['sVersion']
        del multicast_nic['iStatus']
        del multicast_nic['sVersion']
        for nic in multicast_nic.values():
            nic_status_mode = select_one('select sWorkMode, iStatus \
                    from m_tbnetport where sPortName = "%s"' % nic)
            if nic_status_mode and nic_status_mode['sWorkMode'] == 'route' \
                    and nic_status_mode['iStatus'] == '1':
                print nic
                if sversion == 'IGMP_V1':
                    os.system('echo "1" > /proc/sys/net/ipv4/conf/%s/force_igmp_version' % nic)
                elif sversion == 'IGMP_V2':
                    os.system('echo "2" > /proc/sys/net/ipv4/conf/%s/force_igmp_version' % nic)
                elif sversion == 'IGMP_V3':
                    os.system('echo "0" > /proc/sys/net/ipv4/conf/%s/force_igmp_version' % nic)
                nic_list.append(nic)
        os.system('pimd')
    else:
        os.system('killall pimd')
    db['nic'] = nic_list
    db.close()


def recover():
    if len(sys.argv) != 2:
        return
    if sys.argv[1] == 'boot_recover':
        multicast_route()
    elif sys.argv[1] == 'factory_recover':
        db = shelve.open('multicast_router')
        if db.has_key('nic'):
            for tmp in db['nic']:
                os.system('echo "0" > /proc/sys/net/ipv4/conf/%s/force_igmp_version' % tmp)
            del db['nic']


if __name__ == "__main__":
    recover()
