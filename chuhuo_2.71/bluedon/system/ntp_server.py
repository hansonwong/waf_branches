#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import json
from logging import getLogger

from IPy import IP

from db.mysql_db import select_one
from networking.nat64 import exec_cmd
from system.ha import init_tenv


def ntp_iptables(is_add=False, is_domain=False):
    _tmp = (
        "iptables -{action} FWINPUT -p tcp -m tcp --sport {port} -j ACCEPT;"
        "iptables -{action} FWINPUT -p udp -m udp --sport {port} -j ACCEPT")
    exec_cmd(_tmp.format(action='D', port='53'))
    exec_cmd(_tmp.format(action='D', port='123'))
    if is_add:
        exec_cmd(_tmp.format(action='I', port='123'))
    if is_domain:
        exec_cmd(_tmp.format(action='I', port='53'))


def config_ntp_server(data):
    exec_cmd('iptables -D FWINPUT  -p udp --dport 123 -j ACCEPT')
    pre_data = {}
    pre_data_path = '/dev/shm/ntp_server.json'
    if os.path.exists(pre_data_path):
        _tmp = open(pre_data_path, 'r')
        pre_data = json.load(_tmp)
        _tmp.close()
    for i in pre_data.get('sAllowIp', []):
        exec_cmd('iptables -D FWINPUT  -p udp -s %s --dport 123 -j ACCEPT' % '/'.join(i))

    ntp_iptables(is_add=False, is_domain=False)
    if str(data['iStatus']) != '1':
        exec_cmd('systemctl stop ntpd', msg='Stop Ntp Server. ')
        return

    ntp_server = data.get('sTimeServerIP', '') or data.get('sDomainName', '')
    if not ntp_server:
        getLogger('main').warning('ntp_server failed, mast have a up level ntp sever')
        return

    if str(data['iGetBy']) == '1':
        ntp_iptables(is_add=True, is_domain=False)
    elif str(data['iGetBy']) == '2':
        ntp_iptables(is_add=True, is_domain=True)
    else:
        getLogger('main').warning('wrong args')
        return

    data['sAllowIp'] = [IP(addr).strNormal(2).split('/') for addr in data.setdefault('sAllowIp', [])]
    if str(data.setdefault('iAuth', '0')) == '1':
        exec_cmd('mkdir /etc/ntp; mkdir /Data/apps/wwwroot/firewall/data/ntp')
        exec_cmd('/usr/bin/rm -rf /etc/ntp/*')
        exec_cmd('cd /etc/ntp && ntp-keygen -T -I -p serverpassword -c RSA-SHA')
        exec_cmd('cd /etc/ntp && tar czvf /Data/apps/wwwroot/firewall/data/ntp/ntpkey.tar.gz *')
        exec_cmd('iptables -I FWINPUT  -p udp --dport 123 -j ACCEPT')
    else:
        for i in data.get('sAllowIp', []):
            exec_cmd('iptables -I FWINPUT  -p udp -s %s --dport 123 -j ACCEPT' % '/'.join(i))

    tenv = init_tenv()
    tenv.get_template('ntp_conf').stream(ntp_server=ntp_server,
                                         is_auth=data['iAuth'] and int(data['iAuth']) or 0,
                                         networks=data['sAllowIp']).dump('/etc/ntp.conf')

    exec_cmd('systemctl restart ntpd', msg='Restart Ntp Server.')

    _tmp = open(pre_data_path, 'w')
    json.dump(data, _tmp)
    _tmp.close()


def recover():
    _sql = 'SELECT sValue FROM m_tbconfig WHERE sName="NtpServer";'
    ntp_data = json.loads(select_one(_sql)['sValue'])
    config_ntp_server(ntp_data)


if __name__ == '__main__':
    recover()
