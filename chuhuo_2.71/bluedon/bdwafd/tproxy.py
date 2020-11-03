#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import MySQLdb
import heapq
import subprocess
import commands
from config import config
from logging import getLogger
from db import conn_scope
from common import del_iptables_rule, del_iptables_chain


filterfile = 'rp_filter'
filterdir = '/proc/sys/net/ipv4/conf'
bridgedir = '/proc/sys/net/bridge'
tport = '3129'
ports = ()
innics = []
outnics = []
flag = 0


def get_tproxy_bridge():
    with conn_scope(**config['dbfw']) as (_, cursor):
        cursor.execute('select `sBindDevices` from m_tbbridgedevice'
                       ' where bridgeType="tproxy" where iStatus=1')
        for data in cursor.fetchall():
            if len(data[0]) > 2:
                buff = data[0].split(",")
                nic_small = heapq.nsmallest(1, buff)
                innics.append(nic_small[0])
                buff.remove(nic_small[0])
                for nic_big in buff:
                    outnics.append(nic_big)
    print innics
    print outnics


def delbridge():
    # Remove the routing strategies
    os.system('ip rule del fwmark 1 lookup 100 2>/dev/null')
    os.system('ip -f inet route del local 0.0.0.0/0 dev lo table 100 2>/dev/null')

    # Remove bridge proxy
    for name in os.listdir(bridgedir):
        cmdstr = 'echo 1 > %s/%s' % (bridgedir, name)
        os.system(cmdstr)

    # remove route proxy
    # forward setting
    for name in os.listdir(filterdir):
        cmdstr = 'echo 1 > %s/%s/%s' % (filterdir, name, filterfile)
        os.system(cmdstr)


def get_ports():
    length = len(ports)
    result_list = []
    pages = length / 15
    if length % 15 != 0:
        pages += 1
    for i in range(pages):
        result_list.append(ports[i * 15:(i + 1) * 15])
    getLogger("main").info(result_list)
    return result_list


def get_workingnic():
    niclist = []
    r = subprocess.check_output("ifconfig |grep eth", shell=True)
    r = r.splitlines()
    for line in r:
        nic = line.split()[0]
        # print nic
        niclist.append(nic)
    return niclist


def addbridge():
    # add bridge proxy
    for name in os.listdir(bridgedir):
        cmdstr = 'echo 0 > %s/%s' % (bridgedir, name)
        os.system(cmdstr)

    # add the routing strategies
    os.system('ip rule add fwmark 1 lookup 100 2>/dev/null')
    os.system('ip -f inet route add local 0.0.0.0/0 dev lo table 100 2>/dev/null')
    # enable route forward
    os.system('echo 1 > /proc/sys/net/ipv4/ip_forward')

    # Remove rever route
    # for name in os.listdir(filterdir):
        # cmdstr = 'echo 0 > %s/%s/%s' % (filterdir, name, filterfile)
        # os.system(cmdstr)

    # add ebtables, iptables
    for netport in innics + outnics:
        os.system('ebtables -t broute -A BROUTING -i {netport} -p IPv4 -j redirect '
                  '--redirect-target DROP'.format(netport=netport))
    os.system('iptables -t mangle -N DUPORT')
    os.system('iptables -t mangle -N DIVERT')
    os.system('iptables -t mangle -A DIVERT -j MARK --set-mark 1')
    os.system('iptables -t mangle -A DIVERT -j ACCEPT')

    ports_data = get_ports()
    for innic in innics:
        for tmp_ports in ports_data:
            if "443" in tmp_ports:
                global flag
                flag = 1
                tmp_ports.remove("443")
                os.system("iptables -t mangle -N DUPORT443")
                os.system("iptables -t mangle -A DUPORT443 -p tcp -m socket -j DIVERT")
                os.system("iptables -t mangle -A DUPORT443 -p tcp -j TPROXY --on-port 3130 --on-ip 0.0.0.0 --tproxy-mark 0x1/0x1")
            cmdstr = 'iptables -t mangle -A PREROUTING -i ' + innic + \
                     ' -p tcp -m multiport --dport ' + ','.join(tmp_ports) + ' -j DUPORT'
            os.system(cmdstr)
    for innic in innics:
        if flag == 1:
            cmdstr2 = "iptables -t mangle -A PREROUTING -i %s -p tcp -m multiport --dports 443 -j DUPORT443" % innic
            os.system(cmdstr2)

    for outnic in outnics:
        for tmp_ports in ports_data:
            if "443" in tmp_ports:
                tmp_ports.remove("443")
            cmdstr = 'iptables -t mangle -A PREROUTING -i ' + outnic + \
                     ' -p tcp -m multiport --sport ' + ','.join(tmp_ports) + ' -j DUPORT'
            os.system(cmdstr)
    for outnic in outnics:
        if flag == 1:
            cmdstr2 = "iptables -t mangle -A PREROUTING -i %s -p tcp -m multiport --dports 443 -j DUPORT443" % outnic
            os.system(cmdstr2)

    cmdstr1 = 'iptables -t mangle -A DUPORT -p tcp -m socket -j DIVERT'
    cmdstr2 = 'iptables -t mangle -A DUPORT -p tcp -j TPROXY --tproxy-mark 0x1/0x1 --on-port ' + tport
    os.system(cmdstr1)
    os.system(cmdstr2)


def add_niciptable():
    niclist = get_workingnic()
    for nic in niclist:
        cmd = "iptables -t mangle -A PREROUTING -i %s -p tcp -m multiport --dports 443 -j DUPORT443" % nic
        os.system(cmd)


if __name__ == '__main__':
    if len(sys.argv) < 1:
        exit(1)
    exit(0)  # 暂无透明代理模式
    os.system('ebtables -t broute -F')
    os.system('ebtables -t broute -X')
    # del iptables chains, rules
    del_iptables_rule('mangle', 'PREROUTING', keys=('DUPORT',))
    for chain in ('DUPORT', 'DUPORT443', 'DIVERT'):
        del_iptables_chain('mangle', chain)

    if sys.argv[1] == 'del':
        delbridge()
    elif sys.argv[1] == 'add':
        get_tproxy_bridge()
        if innics:
            ports = sys.argv[2:]
            if ports:
                addbridge()
