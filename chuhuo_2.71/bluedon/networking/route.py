#! /usr/bin/env python
# -*- coding:utf-8-*-


import os
import sys
os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')
from commands import getstatusoutput
from logging import getLogger
from jinja2 import Template
from IPy import IP

from db.mysql_db import select


__author__ = 'ruan.lj@foxmail.com'

def ip_route(ip_obj, action, gateway, device):
    _cmd_tmp = Template('ip -{{version}} route {{action}} {{addr}} '
                        '{% if gateway %} via {{gateway}} {% endif %} '
                        '{% if device %} dev {{device}} {% endif %} ')
    route_cmd = _cmd_tmp.render(version=ip_obj.version(),
                                action=action,
                                addr=ip_obj.strNormal(1),
                                gateway=gateway,
                                device=device)
    getLogger('main').info(route_cmd)
    status, output = getstatusoutput(route_cmd)
    if status:
        getLogger('main').warning(output)


def static_routes(action, route_data):
    if action == 'del':
        route_data['iStatus'] = '0'
    version = int(route_data['sIPV'][-1])
    action = {'0': 'del', '1': 'add'}.get(str(route_data['iStatus']), '')
    try:
        target_addr = IP(route_data['sTargetAddress'] + '/' + str(route_data['sMask']))
    except ValueError as e:
        getLogger('main').warning(e)
        return
    gateway = route_data['sNextJumpIP'] and IP(route_data['sNextJumpIP']) or None
    device = route_data['sPort']
    if not (gateway or device) or not action or (version != target_addr.version()):
        getLogger('main').warning('wrong route arg: %s', route_data)
        return
    ip_route(target_addr, action, gateway, route_data['sPort'])


def recover(_type='boot_recover'):
    static_route_info = select('select * from m_tbstaticroute where iStatus=1')
    for info in static_route_info:
        if _type == 'boot_recover':
            static_routes('add', info)
        elif _type == 'factory_recover':
            static_routes('del', info)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        recover(_type=sys.argv[1])
    else:
        print 'wrong args!'
