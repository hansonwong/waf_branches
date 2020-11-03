#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from logging import getLogger

from db.mysql_db import select
from networking.nat64 import exec_cmd
from system.system_config import get_process_id
from utils.cache import cache

# pylint: disable=E1101


class NodeBase(object):
    def __init__(self, data):
        for key, val in data.iteritems():
            if isinstance(val, int):
                val = str(val)
            elif isinstance(val, basestring):
                val = val.strip()
            setattr(self, key, val)
        self.old_pid = cache.get('%s-%s' % (self.__class__.__name__, self.id), -1)
        self.all_pids = []

    def config(self):
        getLogger('main').info('config %s begin...', self.__class__.__name__)
        if str(self.iStatus) == '1':
            self.enable()
        elif str(self.iStatus) == '0':
            self.disable()

    def enable(self):
        self._clean_up()
        self._start_process()
        self._config_iptables()

    def disable(self):
        self._clean_up()

    def _clean_up(self):
        self._config_iptables(is_add=False)
        if self.old_pid in self.all_pids:
            exec_cmd('kill %s' % self.old_pid)
            cache.set('%s-%s' % (self.__class__.__name__, self.id), -1)

    def _start_process(self):
        pass

    def _config_iptables(self, is_add=True):
        pass


class CenterNode(NodeBase):
    def __init__(self, data):
        super(CenterNode, self).__init__(data)
        self.all_pids = get_process_id('supernode') or []

    def _start_process(self):
        _, pid = exec_cmd('supernode -f %s &>/dev/null & echo $!' % self.sPort)
        cache.set('%s-%s' % (self.__class__.__name__, self.id), int(pid))

    def _config_iptables(self, is_add=True):
        cmd = 'iptables -{action} FWINPUT -p udp --dport {port} -j ACCEPT'
        exec_cmd(cmd.format(action={True: 'I', False: 'D'}[is_add], port=self.sPort))


class EdgeNode(NodeBase):
    def __init__(self, data):
        super(EdgeNode, self).__init__(data)
        self.all_pids = get_process_id('edge') or []

    def _start_process(self):
        public_ip = ' '.join(['-l %s:%s' % (ip, self.sPort) for ip in self.sPublicIp.split(',') if ip])
        mac_next = self.sVirtualIp.split('.')
        mac34 = mac_next[2].zfill(4)
        mac56 = mac_next[3].zfill(4)
        mac = 'aa:bd' + ':' + mac34[:2] + ':' + mac34[2:] + ':' + mac56[:2] + ':' + mac56[2:]
        cmd = 'edge -f -d {iface} -a {vip} -c {network} -u 0 -g 0 -k {key} {public_ip} -m {mac}'.format(
            iface=self.sVirtualName, vip=self.sVirtualIp, network=self.sNetName,
            key=self.sPassword, public_ip=public_ip, mac=mac)
        _, pid = exec_cmd('%s &>/dev/null & echo $!' % cmd)
        cache.set('%s-%s' % (self.__class__.__name__, self.id), int(pid))

    def _config_iptables(self, is_add=True):
        cmd = ('iptables -{action} FWINPUT -p udp -j ACCEPT;'
               'iptables -{action} FWINPUT -s {vip}/24 -d {vip}/24 -j ACCEPT')
        exec_cmd(cmd.format(action={True: 'I', False: 'D'}[is_add], vip=self.sVirtualIp))


def recover():
    """开机恢复与恢复出厂设置"""

    if len(sys.argv) == 1:
        return

    trans_map = {
        CenterNode: select('SELECT * FROM m_tbntn_center WHERE iStatus=1;'),
        EdgeNode: select('SELECT * FROM m_tbntn_edge WHERE iStatus=1;'),
    }

    for proc_class, datas in trans_map.items():
        for data in datas:
            if sys.argv[1] == 'factory_recover':
                data.iStatus = 0
                proc_class(data).config()
            elif sys.argv[1] == 'boot_recover':
                proc_class(data).config()


if __name__ == '__main__':
    recover()
