#! /usr/bin/ env python
# -*- coding:utf-8 -*-


"""
ipset 增删改

modify log:
    2016-6-23:
        1、新增ipv6的ipset
"""


import os
import json
from logging import getLogger

from db.mysqlconnect import execute_sql
from utils.mask_transition import exchange_mask
from objectdefine.ip_range import get_ip
from utils.logger_init import logger_init


from IPy import IP



LOGGER_PATH = '/usr/local/bluedon/log/ipset.log'
LOGGER_NAME = 'IPSET'

logger_init(LOGGER_NAME, LOGGER_PATH, 'DEBUG')


def set_ipset(data, action='add', iptype='ipv4'):
    """ 设置ipset """

    ipset_path = '/usr/local/sbin/ipset'
    cmd_ipset = {'delipset': '%s destroy %s',
                'ipv4': '%s creat %s hash:net',
                'ipv6': '%s creat %s hash:net family inet6',
                'change_ipset': '%s %s %s %s'}

    # 创建ipset
    if action == 'del':
        ipset_cmd = cmd_ipset['delipset'] %(ipset_path, data['HideID'])
    elif action == 'add':
        ipset_cmd = cmd_ipset[iptype] %(ipset_path, data['HideID'])

    os.system(ipset_cmd)
    getLogger(LOGGER_NAME).debug(ipset_cmd)

    if action == 'del':
        return

    # 把ip添加到ipset中
    sip = str(data['sIP']).split(',')
    if len(sip) == 1:
        addr_sql = 'select * from m_tbaddress_list_scm where id=%s' %(sip[0])
    else:
        sip = tuple([int(item) for item in sip])
        addr_sql = 'select * from m_tbaddress_list_scm where id in %s' %(str(sip))
    results = execute_sql(addr_sql)
    for result in results:
        addr_list = ip_iprange(result)
        for addr in addr_list:
            cmd = cmd_ipset['change_ipset'] %(ipset_path, action,
                                                 data['HideID'], addr)
            getLogger(LOGGER_NAME).debug(cmd)
            os.system(cmd)
    os.system("ipset save > /etc/ipset.conf")
    #print data['HideID']

def ip_iprange(data):
    """
    args:
        data: 记录集
    return:
        addr_list: ip列表
    """

    addr_list = list()
    if data['sIPV'].lower() == 'ipv4':
        if str(data['sAddtype']).strip() == '1':        # ip和掩码形式
            if data['sAddress'].endswith('.0'):
                if '.' not in data['sNetmask']:
                    addr_list = ['%s/%s' %(data['sAddress'], data['sNetmask'])]
                else:
                    addr_list = [IP('%s/%s' %(data['sAddress'], data['sNetmask']),
                            make_net=True).strNormal(1)]
            else:
                addr_list = [data['sAddress']]
        elif str(data['sAddtype']).strip() == '2':        # ip段
            iprange = '%s-%s' %(data['sAddress'], data['sNetmask'])
            addr_list = get_ip(iprange)
    else:
        addr_list = [data['sAddress']]
    return addr_list

def main(args):
    ipset_sql = 'select * from m_tbaddressgroup_scm'
    datas = execute_sql(ipset_sql)
    if not args in ['init', 'reboot']:
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
