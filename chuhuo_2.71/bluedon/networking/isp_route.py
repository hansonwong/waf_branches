#!/usr/bin/env/python
# *-* coding: utf-8 *-*

"""
isp路由设置(2016-4-29)
"""


# Copyright (C) 1998-2015 Bluedon. All Rights Reserve
# This file is part of Bluedon Firewall


import sys
import commands
from db.mysql_db import select
from utils.log_logger import rLog_dbg
from objectdefine.ip_range import deal_ip


LOG_NAME = 'ISP_ROUTE'
COMMANDS = commands.getstatusoutput
DBG = lambda x: rLog_dbg('isp_route', x)
CMD = 'ip route {action} to {ip}{next_hop}{device} table main{metric}'


def set_isp_route(data, action='add'):
    """ 增加isp路由 """
    if not data.get('sNextJump') and not data.get('sOutPort'):
        DBG('can not miss next jump and outport at the same time')
        return
    next_hop = ' via %s' % data['sNextJump'] if data['sNextJump'] else ''
    device = ' dev %s' % data['sOutPort'] if data['sOutPort'] else ''
    metric = ' metric %s' % data['sMetric'] if data['sMetric'] else ''
    i_sql = 'select * from m_tbaddress_isp where sBelongISP="%s";' % (data['sBelongISP'])
    results = select(i_sql)
    if not results:
        DBG('m_tbaddress_isp not sBelongISP=%s' % (data['sIspAddress']))
        return
    for result in results:
        ip, _ = deal_ip(result['sIspAddress'], result['sMask'])
        cmd = CMD.format(
            action=action,
            ip=ip,
            next_hop=next_hop,
            device=device,
            metric=metric,
        )
        status, output = COMMANDS(cmd)
        DBG('status:%s CMD: %s output %s' % (status, cmd, output))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        DBG('more args (eg: python url_filter init/reboot)')
        sys.exit(0)
    if sys.argv[1] == 'reboot':        # 开机重启
        DBG('BEGIN reboot recover')
        a_sql = 'select * from m_tbisproute where iStatus=1;'
        datas = select(a_sql)
        for data in datas:
            set_isp_route(data, action='add')
        DBG('END reboot recover')
    elif sys.argv[1] == 'init':        # 恢复出厂设置
        DBG('BEGIN init recover')
        a_sql = 'select * from m_tbisproute where iStatus=1;'
        datas = select(a_sql)
        for data in datas:
            set_isp_route(data, action='del')
        DBG('END init recover')

