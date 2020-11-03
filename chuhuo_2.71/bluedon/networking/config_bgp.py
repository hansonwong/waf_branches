# coding:utf-8

import os
import json
import struct
import socket
import subprocess
from logging import getLogger
from jinja2 import Template

from db.mysql_db import select, select_one


def bgp_set_data():
    """
    获取动态路由bgp的参数配置数据
    """
    sql = 'select sValue from m_tbconfig where sName = "BGPSetting"'
    set_data = select_one(sql)
    set_data = json.loads(set_data['sValue'])
    set_data['ip'] = socket.inet_ntoa(
        struct.pack('I', socket.htonl(int(set_data['sRouterID']))))
    return set_data


def bgp_net_data():
    """
    获取动态路由网络数据
    """
    sql = 'select * from m_tbdynamicroute_bgp_net'
    net_data = select(sql)
    return net_data


def bgp_neighbor_data():
    """
    获取动态路由邻居数据
    """
    sql = 'select * from m_tbdynamicroute_bgp_neighbor'
    bgp_neighbor_data = select(sql)
    return bgp_neighbor_data


def bgp_port_data():
    """
    获取端口配置数据
    """
    sql = 'select * from m_tbdynamicroute_bgp_port'
    port_data = select(sql)
    bgp_port = []
    bgp_ip = []
    for data in port_data:
        bgp_port.append(data['sPort'])
        bgp_ip.append(data['sIP'])
    return bgp_port, bgp_ip


def enable_bgp():
    subprocess.call('/usr/sbin/iptables -I FWINPUT -p tcp --dport 179 -j ACCEPT', shell=True)
    subprocess.call('/usr/sbin/iptables -I FWINPUT -p tcp --sport 179 -j ACCEPT', shell=True)
    subprocess.call('/usr/local/sbin/zebra -d --user=root --group=root', shell=True)
    getLogger('main').info('zebra on')
    subprocess.call('/usr/local/sbin/bgpd -d --user=root --group=root', shell=True)
    getLogger('main').info('bgpd on')


def disable_bgp():
    with open(os.devnull, 'w') as devnull:
        subprocess.call("/usr/sbin/iptables -D FWINPUT -p tcp --sport 179 -j ACCEPT",
                        shell=True, stdout=devnull, stderr=devnull)
        subprocess.call("/usr/sbin/iptables -D FWINPUT -p tcp --dport 179 -j ACCEPT",
                        shell=True, stdout=devnull, stderr=devnull)
        subprocess.call('killall bgpd', shell=True, stdout=devnull,
                        stderr=devnull)
    getLogger('main').info('bgpd down')


def disable_zebra():
    subprocess.call('killall zebra', shell=True)
    getLogger('main').info('zebra down')


def write_bgpd_conf(set_data=None, net_data=None, neighbor_data=None):
    with open('template/bgpd.conf', 'r') as fp:
        conf = Template(fp.read())
    with open('/usr/local/etc/bgpd.conf', 'w') as fp:
        fp.write(conf.render(
            set_data=set_data,
            net_data=net_data,
            neighbor_data=neighbor_data,
        ))


def conf_bgp():
    """
    配置动态路由bgp,写入配置文件以及执行相关命令
    """
    set_data = bgp_set_data()
    bgp_on = set_data['iTurnOnBGP']

    if bgp_on == '1':
        net_data = bgp_net_data()
        neighbor_data = bgp_neighbor_data()
        write_bgpd_conf(set_data, net_data, neighbor_data)
        disable_bgp()
        disable_zebra()
        enable_bgp()
    else:
        write_bgpd_conf()
        disable_bgp()


if __name__ == "__main__":
    conf_bgp()
