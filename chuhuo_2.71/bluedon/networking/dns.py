#! /usr/bin/env python
# -*-coding:utf-8 -*-

import json
from logging import getLogger

from db.mysql_db import select_one
from networking.nat64 import exec_cmd


def _dns_disable(iptables, info):
    getLogger('main').info('DNS: clean old')
    rules = (
        '{iptables} -t filter -D FWINPUT -p tcp --sport 53 -j ACCEPT;'
        '{iptables} -t filter -D FWINPUT -p udp --sport 53 -j ACCEPT;'
        '{iptables} -t filter -D FWINPUT -p tcp --dport 53 -j ACCEPT;'
        '{iptables} -t filter -D FWINPUT -p udp --dport 53 -j ACCEPT'
    ).format(iptables=iptables)
    exec_cmd(rules)
    for dns in info['dns_all']:
        exec_cmd('sed -i "/%s/d"  /etc/resolv.conf' % dns)
        exec_cmd('%s -t nat -D FWPREROUTING -p udp --dport 53 -j DNAT --to-destination %s'
                 % (iptables, dns))
        exec_cmd('%s -t nat -D FWPREROUTING -p tcp --dport 53 -j DNAT --to-destination %s'
                 % (iptables, dns))


def _dns_enable(iptables, info):
    getLogger('main').info('DNS: add new')
    exec_cmd('%s -t filter -I FWINPUT -p tcp --sport 53 -j ACCEPT' % iptables)
    exec_cmd('%s -t filter -I FWINPUT -p udp --sport 53 -j ACCEPT' % iptables)
    with open('/etc/resolv.conf', 'a') as resolv:
        for dns in info['dns_all']:
            resolv.write('nameserver %s\n' % dns)
    if str(info['iTurnOnDNS']) == '1':
        for dns in info['dns_all']:
            exec_cmd('%s -t nat -A FWPREROUTING -p udp --dport 53 -j DNAT --to-destination %s' % (iptables, dns))
            exec_cmd('%s -t nat -A FWPREROUTING -p tcp --dport 53 -j DNAT --to-destination %s' % (iptables, dns))
        exec_cmd('%s -t filter -I FWINPUT -p tcp --dport 53 -j ACCEPT' % iptables)
        exec_cmd('%s -t filter -I FWINPUT -p udp --dport 53 -j ACCEPT' % iptables)


def config_dns(iptables, info_new, info_old=None, reset=False):
    getLogger('main').info('Begin Config Dns....')
    info_new = json.loads(info_new)
    info_old = info_old and json.loads(info_old) or None
    info_new['dns_all'] = [i.strip() for i in (info_new['sDNSServerOne'], info_new['sDNSServerTwo']) if i.strip()]

    if info_old:
        info_old['dns_all'] = [i.strip() for i in (info_old['sDNSServerOne'], info_old['sDNSServerTwo']) if i.strip()]
        _dns_disable(iptables, info_old)
    if info_new['dns_all']:
        _dns_enable(iptables, info_new)


if __name__ == "__main__":
    open('/etc/resolv.conf', 'w').close()
    dns_v4 = select_one('select sValue from m_tbconfig where sName="DNSSettingIPV4"')
    dns_v6 = select_one('select sValue from m_tbconfig where sName="DNSSettingIPV6"')
    if dns_v4:
        config_dns('iptables', info_new=dns_v4['sValue'])
    if dns_v6:
        config_dns('ip6tables', info_new=dns_v6['sValue'])
