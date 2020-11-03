#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import sys
from commands import getstatusoutput
from logging import getLogger

from db.mysql_db import select


# pylint: disable=E1101

def exec_cmd(cmd, msg=''):
    getLogger('main').info('%s %s', msg, cmd)
    status, output = getstatusoutput(cmd)
    if status:
        getLogger('main').warning(output)
    return status, output

class NatSixFour(object):
    def __init__(self, data):
        for key, val in data.iteritems():
            if isinstance(val, int):
                val = str(val)
            elif isinstance(val, basestring):
                val = val.strip()
            setattr(self, key, val)
        self.conf_path = '/usr/local/bluedon/scripts/nat64-config.sh'

    def config(self):
        getLogger('main').info('config %s begin...', self.__class__.__name__)
        if str(self.iStatus) == '1':
            self.enable()
        elif str(self.iStatus) == '0':
            self.disable()

    def enable(self):
        self._conf_nat64()
        exec_cmd('sh %s %s' % (self.conf_path, self.sIPV4Network))
        self._config_iptables(is_add=True)

    def disable(self):
        exec_cmd('/usr/sbin/modprobe -r nf_nat64')
        self._config_iptables(is_add=False)

    def _conf_nat64(self):
        with open(self.conf_path, 'r+') as f:
            result = re.sub(r'^PREFIX_ADDR=".+"', 'PREFIX_ADDR="%s"' % self.sNatPrefix, f.read(), flags=re.MULTILINE)
            result = re.sub(r'^PREFIX_LEN=".+"', 'PREFIX_LEN="%s"' % self.sNatMask, result, flags=re.MULTILINE)
            f.seek(0)
            f.write(result)
            f.truncate()

    def _config_iptables(self, is_add=True):
        rules = (
            'iptables -{action} FWINPUT -i {name} -j ACCEPT;'
            'ip6tables -{action} FWINPUT -i {name} -j ACCEPT;'
            'iptables -{action} FWFORWARD -i {name} -j ACCEPT;'
            'iptables -{action} FWFORWARD -o {name} -j ACCEPT;'
            'iptables -{action} FWINPUT -d {ip_addr} -j ACCEPT;'
            'ip6tables -{action} FWFORWARD -i {name} -j ACCEPT;'
            'ip6tables -{action} FWFORWARD -o {name} -j ACCEPT;'
            'ip6tables -{action} FWFORWARD -d {prefix}/{prefix_mask} -j ACCEPT'
        ).format(action={True: 'I', False: 'D'}[is_add],
                 name='nat64',
                 ip_addr=self.sIPV4Network,
                 prefix=self.sNatPrefix,
                 prefix_mask=self.sNatMask)
        exec_cmd(rules, msg='Nat64 iptables:')


def recover():
    if len(sys.argv) == 1:
        return
    nat64_info = select('select * from m_tbnatsetting where iStatus=1')
    for info in nat64_info:
        if sys.argv[1] == 'factory_recover':
            info.iStatus = 0
            NatSixFour(info).config()
        if sys.argv[1] == 'boot_recover':
            NatSixFour(info).config()


if __name__ == '__main__':
    recover()
