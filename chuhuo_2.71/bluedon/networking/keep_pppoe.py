#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""pppoe断线时自动重播，并且刷新pppoe的ip地址"""

import time
import re
import psutil

from db.mysql_db import select, update
from networking.nat64 import exec_cmd


def keep_pppoe():
    """pppoe重播"""
    pppoe_from_db = select('SELECT sUserName, sIP, sMask FROM m_tbdialdevice WHERE iStatus=1')
    pppoe_from_db = {i.sUserName:(i.sIP, i.sMask) for i in pppoe_from_db if i.sUserName}
    while 1:
        for username, db_addr in pppoe_from_db.iteritems():
            active_pppoe_name = get_pppoe_device_name(username)
            if active_pppoe_name:
                addr = get_pppoe_devices().get(active_pppoe_name, None)
                if addr is not None:
                    if addr != db_addr:  # 如果存在对应ppp拨号口，并且有ip，且ip和数据库的不同
                        update("UPDATE m_tbdialdevice SET `sIP`=?,`sMask`=? WHERE `sUserName`=?",
                               addr[0], addr[1], username)
                        pppoe_from_db[username] = addr
                    continue

            pppoe_cmd = '/usr/sbin/pppoe-start /etc/ppp/pppoe.conf-%s' % username
            status, _ = exec_cmd(pppoe_cmd, msg='re_pppoe:')  # 重新拨号
            if status == 0:  # 拨号成功
                time.sleep(1)
                iface_name = get_pppoe_device_name(username)
                addr = get_pppoe_devices().get(iface_name, ('', ''))
                update("UPDATE m_tbdialdevice SET `sIP`=?,`sMask`=? WHERE `sUserName`=?", addr[0], addr[1], username)
                pppoe_from_db[username] = addr
            else:  # 拨号失败
                update("UPDATE m_tbdialdevice SET `sIP`=?,`sMask`=? WHERE `sUserName`=?", '', '', username)
                pppoe_from_db[username] = ('', '')
        time.sleep(15)


def get_pppoe_device_name(config_name):
    """获取拨号产生的ppp虚拟网口名称，如果找不到对应的ppp网口，则表示拨号不成功"""
    statuse_cmd = '/usr/sbin/pppoe-status /etc/ppp/pppoe.conf-%s' % config_name
    _, output = exec_cmd(statuse_cmd, msg='pppoe_status: ')
    template = re.compile(r'^pppoe-status: Link is up and running on interface (ppp\d{1,2})$', flags=re.MULTILINE)
    _match = template.search(output)
    if _match:
        return _match.group(1)
    return None


def get_pppoe_devices():
    """获得所有成功的拨号设备的ip、掩码信息
    return：
        例如
        {'ppp1': (u'1.2.3.4', u'255.255.255.255'),
         'ppp2': (u'2.2.3.5', u'255.255.255.255')
        }
    """
    all_devices = psutil.net_if_addrs()
    template = re.compile(r'^ppp\d{1,2}$')
    pppoe_devices = {}
    for iface, addrs in all_devices.iteritems():
        if template.search(iface):
            for i in addrs:
                if i.family == 2:
                    pppoe_devices[iface] = (unicode(i.address), unicode(i.netmask))
                    break
    return pppoe_devices


def config_pppoe_systemctl():
    status, output = exec_cmd('systemctl status keep-pppoe')
    if status and 'not-found' in output:
        exec_cmd('/usr/bin/cp /usr/local/bluedon/conf/systemctl/keep-pppoe.service /usr/lib/systemd/system')
    exec_cmd('systemctl disable keep-pppoe')


def start_keep_pppoe_if_need():
    config_pppoe_systemctl()
    pppoe_from_db = select('SELECT sUserName, sIP, sMask FROM m_tbdialdevice WHERE iStatus=1')
    if pppoe_from_db:
        exec_cmd('systemctl restart keep-pppoe')
    else:
        exec_cmd('systemctl stop keep-pppoe')


if __name__ == '__main__':
    from utils.logger_init import get_logger
    get_logger('main', '/usr/local/bluedon/log/pppoe.log')
    keep_pppoe()
