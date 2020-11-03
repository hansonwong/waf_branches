#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import re
import subprocess
from logging import getLogger

from netaddr import IPSet, IPNetwork, IPAddress
from psutil import net_if_addrs

from db.mysql_db import select_one, select
from networking.nat64 import exec_cmd
from networking.route import recover as static_route_recover
from utils.logger_init import get_logger


get_logger('main', '/usr/local/bluedon/log/ip_monitor.log')
get_logger('TacticsRoute', '/usr/local/bluedon/log/ip_monitor.log')
from networking.tactics_route import TacticsRoute

def ip_monitor_link():
    """当网口状态改变时，检查是否需要重新配置网口"""

    getLogger('main').info('starting ip-monitor')
    process = subprocess.Popen('ip monitor link', shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    templete = re.compile(r'^\d+:\s+(?P<iface>vEth\d+|en[ps]\d+s\d+|tun0|ppp\d+).+(UNKNOWN|UP|DOWN)')
    while True:
        line = process.stdout.readline()
        _match = templete.search(line)
        if _match:
            getLogger('main').info(_match.group(0))
            iface, status = _match.group(1), _match.group(2)
            status = {'DOWN': 0, 'UNKNOWN': 1, 'UP': 1}.get(status, 0)
            if status == 1:
                time.sleep(1)
                proc_ipv6(iface)
                proc_route(iface)


def proc_route(iface):
    # 静态路由
    static_route_recover(_type='boot_recover')
    # 策略路由
    datas = select('SELECT * FROM m_tbstrategyroute WHERE iStatus=1 and `sIPV`="ipv4";')
    iface_networks = IPSet([IPNetwork('{}/{}'.format(i.address, i.netmask)).cidr
                            for i in net_if_addrs().get(iface, []) if i.family == 2])
    for data in datas:
        if ((data['sJumpName'] and IPAddress(data['sJumpName']) in iface_networks)
                or data['sIfaceName'] == iface):
            TacticsRoute(data, 'del').modify()
            TacticsRoute(data, 'add').modify()


def proc_ipv6(iface):
    data = select_one('SELECT sIPV6Address FROM m_tbnetport where `sPortName`=?', iface)
    if not data:
        getLogger('main').warning('%s nofound in database!', iface)
        return
    for i in data['sIPV6Address'].split(','):
        if not i.strip(): continue
        exec_cmd('ip -6 addr add {} dev {}'.format(IPNetwork(i.strip()), iface))


def start_monitor(_type):
    conf_path = '/usr/lib/systemd/system/ip-monitor.service'
    os.system(r'\cp -f /usr/local/bluedon/conf/systemctl/ip-monitor.service %s' % conf_path)
    os.system('systemctl daemon-reload')
    if _type == 'boot_recover':
        os.system('systemctl restart ip-monitor')
    else:
        os.system('systemctl stop ip-monitor')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        ip_monitor_link()
    elif len(sys.argv) == 2:
        start_monitor(_type=sys.argv[1])
