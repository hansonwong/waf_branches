#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import re
import sys

from logging import getLogger

from db.mysql_db import select_one, select, update
from networking.config_iface import IfaceAddress
from networking.nat64 import exec_cmd
from networking.fwdb import insert_interfaces

# pylint: disable=E1101

def get_tbconfig(key, default={}):
    """读取m_tbconfig的sValue，返回json.loads之后的python对象"""
    _tmp = select_one('SELECT sValue FROM m_tbconfig WHERE sName=?;', key)
    conf = json.loads(_tmp and _tmp['sValue'] or "null") or default
    return conf


class BridgeAddress(IfaceAddress):
    def __init__(self, data):
        for key, val in data.iteritems():
            setattr(self, key, val)
        self.sIPV4Address = self.sIPV4 or ''
        self.sIPV6Address = self.sIPV6 or ''
        self.sPortName = self.sBridgeName or ''

    def config(self):
        """配置"""
        if str(self.iStatus) == '1':
            self.enable()
        elif str(self.iStatus) == '0':
            self.disable()

    def disable(self):
        """禁用"""
        self._clean_up()
        self._proc_bridge(is_add=False)
        self._proc_waf()
        getLogger('main').info('disable bridge "%s"', self.sPortName)

    def enable(self):
        """启用"""
        self._clean_up()
        self._proc_bridge(is_add=True)
        self._proc_addresses()
        self._proc_ping_manage()
        self._update_netport_table()
        self._proc_waf()
        getLogger('main').info('enable bridge "%s"', self.sPortName)

    def _proc_bridge(self, is_add=True):
        """配置桥，新建或删除"""
        # waf_bridge.conf记录桥的网口信息，如vEth1,vEth2建了一个桥，文件中就有一行“1 2”，多个桥则多行
        waf_conf = "/usr/local/bdwaf/conf/waf_bridge.conf"
        status, output = exec_cmd('cat %s' % waf_conf)
        bridge_devices = [i.strip() for i in output.split('\n') if i.strip()] if not status else []

        # modify by zyl
        # new_devices = ' '.join(re.findall(r"\d+", self.sBindDevices))
        new_devices = 'br %s 8' % self.sBindDevices

        if is_add:
            exec_cmd("brctl addbr %s" % self.sPortName)
            for i in self.sBindDevices.split(','):
                exec_cmd("brctl addif %s %s" % (self.sPortName, i))
            exec_cmd("ifconfig %s up" % self.sPortName)
            bridge_devices.append(new_devices)
        else:
            exec_cmd("ifconfig %s down" % self.sPortName)
            exec_cmd("brctl delbr %s" % self.sPortName)
            if new_devices in bridge_devices:
                bridge_devices.remove(new_devices)
        with open(waf_conf, 'w') as fp:
            fp.write('\n'.join(bridge_devices))

    def _proc_addresses(self):
        ip_cmd = 'ip -{version} addr add {addr} dev {device}'
        for i in self.sIPV4Address.split(','):
            if not i.strip(): continue
            exec_cmd(ip_cmd.format(version=4, addr=i, device=self.sPortName))
        for i in self.sIPV6Address.split(','):
            if not i.strip(): continue
            exec_cmd(ip_cmd.format(version=6, addr=i, device=self.sPortName))

    def _update_netport_table(self):
        """配置完桥之后更新m_tbnetport中桥的用于管理、允许ping等字段"""
        insert_interfaces()
        update('update m_tbnetport set iAllowPing=?, iAllowTraceRoute=?, iSSH=?, iWeb=? where sPortName=?',
               self.iAllowPing, self.iAllowTraceRoute, self.iSSH, self.iWeb, self.sPortName)

    @staticmethod
    def _proc_waf():
        exec_cmd("killall bdwaf")
        waf_status = get_tbconfig('TimeSet').get('iWAF', '')
        if str(waf_status) == '1':
            exec_cmd('/usr/local/bdwaf/sbin/bdwaf')


def recover():
    if len(sys.argv) == 1:
        return

    open("/usr/local/bdwaf/conf/waf_bridge.conf", "w").close()
    bridges = select('SELECT * FROM m_tbbridgedevice WHERE iStatus=1')
    for bridge_data in bridges:
        if sys.argv[1] == 'factory_recover':
            bridge_data['iStatus'] = 0
            BridgeAddress(bridge_data).config()
        if sys.argv[1] == 'boot_recover':
            BridgeAddress(bridge_data).config()


if __name__ == "__main__":
    recover()
