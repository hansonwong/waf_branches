#! /usr/bin/ env python
# -*- coding:utf-8 -*-


"""
ipset 增删改

modify log:
    2016-6-23:
        1、新增ipv6的ipset
    2016-10-8:
        1、ipset增加IP区间(1.2.3.0-1.2.3.10)不再拆分每一个ip逐一添加, 而是直接添加整个区间
        2、新增ipv6区间识别
"""


import os
from netaddr import IPNetwork
from logging import getLogger
from IPy import IP
from db.mysqlconnect import execute_sql
from utils.logger_init import logger_init
from utils.mask_transition import exchange_mask


LOGGER_PATH = '/usr/local/bluedon/log/ipset.log'
LOGGER_NAME = 'IPSET'

logger_init(LOGGER_NAME, LOGGER_PATH, 'DEBUG')


def set_ipset(data, action='add', iptype='ipv4'):
    """ 设置ipset """

    ipset_path = '/usr/local/sbin/ipset'
    cmd_ipset = {
        'delipset': '%s destroy %s',
        'flush': '%s flush %s',
        'ipv4': '%s creat %s hash:net',
        'ipv6': '%s creat %s hash:net family inet6',
        'change_ipset': '%s %s %s %s'
    }

    # 创建ipset
    ipset_cmd = ''
    if action == 'modify':
        ipset_cmd = cmd_ipset['flush'] % (ipset_path, data['HideID'])
    if action == 'del':
        ipset_cmd = cmd_ipset['delipset'] % (ipset_path, data['HideID'])
    if action == 'add':
        ipset_cmd = cmd_ipset[iptype] % (ipset_path, data['HideID'])

    os.system(ipset_cmd)
    getLogger(LOGGER_NAME).debug(ipset_cmd)

    if action == 'del':
        return

    # 把ip添加到ipset中
    sip = str(data['sIP']).split(',')
    if len(sip) == 1:
        addr_sql = 'select * from m_tbaddress_list where id=%s' % (sip[0])
    else:
        sip = tuple([int(item) for item in sip])
        addr_sql = 'select * from m_tbaddress_list where id in %s' % (str(sip))
    results = execute_sql(addr_sql)

    for result in results:
        addr_list = ip_iprange(result)
        for addr in addr_list:
            cmd = cmd_ipset['change_ipset'] % (
                ipset_path, 'add', data['HideID'], addr
            )
            getLogger(LOGGER_NAME).debug(cmd)
            os.system(cmd)
    os.system("ipset save > /etc/ipset.conf")


def ip_iprange(data):
    """
    args:
        data: 记录集
    return:
        addr_list: ip列表
    """

    addr_list = list()
    if data['sIPV'].lower() == 'ipv4':
        if str(data['sAddtype']).strip() == '1':
        # ip和掩码形式
            if '.' not in data['sNetmask']:
                addr_list = ['%s/%s' % (data['sAddress'], data['sNetmask'])]
            else:
                mask = exchange_mask(data['sNetmask'])
                addr_list = ['%s/%s' % (data['sAddress'], mask)]
            ip = IPNetwork(addr_list[0]).ip
            print 'ip', ip
            net = IPNetwork(addr_list[0]).network
            print 'net', net
            if ip != net:
                addr_list.pop()
                addr_list.append(str(ip))
            print addr_list
        elif str(data['sAddtype']).strip() == '2':        # ip段
            iprange = '%s-%s' % (data['sAddress'], data['sNetmask'])
            addr_list = [iprange]
    else:
        if str(data['sAddtype']).strip() == '1':        # ip和掩码形式
            if (data['sAddress'].endswith('::') or
                data['sAddress'].endswith(':0')):
                addr = '%s/%s' % (data['sAddress'], data['sNetmask'])
            else:
                addr = data['sAddress']
            addr_list = [addr]
        else:
            iprange = '%s-%s' % (data['sAddress'], data['sNetmask'])
            addr_list = [iprange]
    return addr_list


def main(args):
    ipset_sql = 'select * from m_tbaddressgroup'
    datas = execute_sql(ipset_sql)
    if args not in ['init', 'reboot']:
        return

    for data in datas:
        set_ipset(data, 'del', data['sGroupIPV'])

    if args == 'reboot':
        for data in datas:
            set_ipset(data, 'add', data['sGroupIPV'])

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        getLogger(LOGGER_NAME).debug('have more args! (eg: python -m objectdefine.set_ipgroup init/reboot)')
    else:
        main(sys.argv[1])
