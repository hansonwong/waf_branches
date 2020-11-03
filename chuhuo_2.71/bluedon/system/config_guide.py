#!/usr/bin/env python
# coding=utf-8

import os
import commands
import json


def guide():

    # 获取系统端口号
    info = os.popen('ifconfig -a').read()
    info = info.split('\n')
    veth_ports = []
    for item in info:
        if item.startswith('vEth'):
            veth_ports.append(item.split(':')[0])

    ip_ports = []
    for i in range(len(info)):
        if info[i].strip().startswith('inet '):
            port = info[i-1].split(':')[0]
            ip_ports.append(port)

    # brctl show
    cmd_brctl = '/usr/sbin/brctl show'
    info_brctl = os.popen(cmd_brctl).read()
    if len(info_brctl.strip().split('\n')) > 1:
        brctl = 'True'
    else:
        brctl = 'False'

    # nat show
    cmd_nat = '/usr/sbin/iptables -t nat -nvL FWSNAT'
    info_nat = os.popen(cmd_nat).read()
    if len(info_nat.strip().split('\n')) > 2:
        nat = 'True'
    else:
        nat = 'False'

    # route show
    cmd_route = '/usr/sbin/route -n'
    info_route = os.popen(cmd_route).read()
    if len(info_route.strip().split('\n')) > 2:
        route = 'True'
    else:
        route = 'False'

    # securitypolicy show
    cmd_safe = '/usr/sbin/iptables -t filter -nvL SECURITYPOLICY'
    info_safe = os.popen(cmd_safe).read()
    if len(info_safe.strip().split('\n')) > 2:
        safe = 'True'
    else:
        safe = 'False'

    datas ={'veth_port': veth_ports,'ip_port': ip_ports, 'brctl': brctl,
               'nat': nat, 'route': route, 'safe': safe}

    with open('/usr/local/bluedon/conf/config_guide.json', 'w') as f:
        datas = json.dumps(datas)
        f.write(datas)

if __name__ == '__main__':
    guide()

