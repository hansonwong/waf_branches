#!/usr/bin/env python
# coding=utf-8

""" 处理自定义对象中的ip """

import json

from IPy import IP

from utils.mask_transition import int_to_strmask
from db.config import execute_sql, search_data


def handle_ip(data):
    ip_dict = {}
    if str(data['sAddtype']) == '1':    # ip
        if '.' not in data['sNetmask']:
            mask_str = int_to_strmask(data['sNetmask'])
            mask_int = data['sNetmask']
        else:
            mask_str = data['sNetmask']
            mask_int = str(IP(data['sNetmask']).strBin().count('1'))

        addr_str = '%s/%s' %(data['sAddress'], mask_str)
        addr_int = '%s/%s' %(data['sAddress'], mask_int)

        if data['sAddress'].endswith('.0'):
            ip_dict.update({'ipmaskrange_str': addr_str})
            ip_dict.update({'ipmaskrange_int': addr_int})
            #ips = [item for item in IP(addr_int)]
            #ip_dict.update({'ips': ips})
        else:
            ip_dict.update({'ipmaskalone_str': addr_str})
            ip_dict.update({'ipmaskalone_int': addr_int})
            #ip_dict.update({'ips': [data['sAddress']]})
    elif str(data['sAddtype']).strip() == '2':        # ip段
        addr = '%s-%s' %(data['sAddress'], data['sNetmask'])
        ip_dict.update({'iprange': addr})
        #ips = list(split_iprange(addr))
        #ip_dict.update({'ips': [ips]})

    content = json.dumps(ip_dict)
    update_sql = "update m_tbaddress_list set sIPJson='%s' where id=%d;" % (content, int(data['id']))
    execute_sql(update_sql)

def split_iprange(iprange):
    """ 解析ip区间中的所有ip """
    ipdown, ipup = iprange.split('-')
    ip_str, ipdown = ipdown.rsplit('.', 1)
    ipup = ipup.rsplit('.', 1)[1]

    if ipdown > ipup:
        ipdown, ipup = ipup, ipdown

    ips = set()
    for i in range(int(ipdown), int(ipup)+1):
        addr = ip_str + '.%d' %(i)
        ips.add(addr)
    return ips

if __name__ == '__main__':
    sql = 'select * from m_tbaddress_list where sIPV="ipv4";'
    datas = search_data(sql)
    for data in datas:
        handle_ip(data)
