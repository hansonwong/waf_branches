#! /usr/bin/env python
# -*- coding:utf-8-*-

import re
import psutil

from utils.mask_transition import exchange_mask, strmask_to_intv6


ignore_ports = ('lo', 'virbr0', 'gre0', 'gretap0', 'docker0', 'pimreg')

class devices(object):
    def get_interfaces(self):
        """获取网口信息
        return：
            ifaces_addrs: 包含所有网口信息的list，按网口名称排序
                例如 [{'nic': vEth1, 'status': 1, 'ip': '1.1.1.1/24,2.2.2.2/24',
                       'ipv6': '2000::1/64', 'mac': 'DE:C7:AA:E8:AF:E0'}]
            ifaces_names: 包含所有网口名称的list，按网口名称排序
        """
        ifaces_addrs = []
        ifaces_status = psutil.net_if_stats()
        ip_mask_mac = psutil.net_if_addrs()
        for iface in ifaces_status.keys():
            # 过滤一些用户不需要看到的网口, 名称是"v-"和"br-"开头的网口是虚拟防火墙产生的
            if iface in ignore_ports or iface.startswith('v-') or iface.startswith('br-'):
                ifaces_status.pop(iface)

        for key, value in ifaces_status.iteritems():
            tmp = {'nic': key, 'status': {True:'1', False:'0'}[value.isup]}
            tmp['ip'] = ','.join(['{}/{}'.format(i.address, exchange_mask(i.netmask))
                                  for i in ip_mask_mac.get(key, '') if i and i.family==2])
            tmp['ipv6'] = ','.join(['{}/{}'.format(i.address, strmask_to_intv6(i.netmask))
                                    for i in ip_mask_mac.get(key, '')
                                    if i and i.family==10 and '%' not in i.address])  # 排除fe80::开头的ip
            tmp['mac'] = ','.join([i.address for i in ip_mask_mac.get(key, '') if i and i.family==17])
            ifaces_addrs.append(tmp)
        ifaces_addrs = sorted(ifaces_addrs, key=lambda i: i['nic'])
        return ifaces_addrs, sorted(ifaces_status.keys())


def get_physical_ifaces():
    """获得所有物理网口的名称
    return: 含有所有物理网卡名的列表，按字母顺序排序
        例如：[u'enp13s0', u'vEth0', u'vEth1', u'vEth2', u'vEth3']
    """

    conf_path = '/etc/network_config/network_interface.cfg'
    with open(conf_path) as fp:
        json_str = ''.join([line.strip() for line in fp if line.strip()])
        re.findall(r'\w+\d{1,2}', json_str)
    return sorted(re.findall(r'\w+\d{1,2}', json_str))


if __name__ == "__main__":
    cls = devices()
    cls.get_interfaces()
