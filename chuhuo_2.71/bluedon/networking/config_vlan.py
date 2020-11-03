#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

from db.mysql_db import select, Dict
from networking.nat64 import exec_cmd


def config_vlan(data):
    if not isinstance(data, Dict):
        data = Dict(**data)
    vlans = {vlan.split(',')[0]: vlan.split(',')[1:] for vlan in data.sBindVlan.split('#')}

    for vlan_id, addr in vlans.iteritems():
        device = '%s.%s' % (data.sBindPort, vlan_id)
        if str(data.iStatus) == '1':
            exec_cmd("vconfig add %s %s" % (data.sBindPort, vlan_id), msg='VLAN:')
            exec_cmd("ifconfig %s up" % device ,msg='VLAN:')
            for i in addr:
                exec_cmd('ip addr add %s dev %s' % (i, device) ,msg='VLAN:')
        else:
            exec_cmd("vconfig rem %s" % device ,msg='VLAN:')


def recover():
    if len(sys.argv) == 1:
        return

    vlans = select('select * from m_tbvlandevice where iStatus=1')
    for vlan_data in vlans:
        if sys.argv[1] == 'factory_recover':
            config_vlan(vlan_data)
        if sys.argv[1] == 'boot_recover':
            config_vlan(vlan_data)


if __name__ == "__main__":
    recover()
