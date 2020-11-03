#!/usr/bin/env python
# -*- coding=utf-8 -*-


"""
modify:
    2016-10-31:
        1、修复策略范围为IP段时,获取拆分后每一ip的bug
"""


import os
import sys
import json
from logging import getLogger

from IPy import IP

os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

from db.config import search_data
from utils.logger_init import logger_init
from objectdefine.ip_range import get_ip


LOG_PATH = '/usr/local/bluedon/log/authenticate_type.log'
LOG_NAME = 'AUTHENTICATE_TYPE'

logger_init(LOG_NAME, LOG_PATH)


def judge_data(msql):
    """ 判断查询的记录集是否为空 """

    key_word = ''
    tablename = ''
    condiction = ''
    words = msql.split()
    for word in words:
        if key_word == 'from':
            tablename = word
        elif key_word == 'where':
            condiction = word
        key_word = word.lower()
    results = search_data(msql)
    if not results:
        getLogger(LOG_NAME).debug('%s table not %s' %(tablename, condiction))
        raise RuntimeError
    return results

def search_ips(data):
    """
    获取关联ip/ip组的相关数据
    args:
        data: 记录集
    return:
        ips: ip集
    """
    ips = []

    def netmarkip(result):
        """ 获取ip """
        vips = []
        if str(result['sAddtype']) == '1':
            if result['sAddress'].endswith('.0'):
                if '.' not in result['sNetmask']:
                    addrs = IP('%s/%s' %(result['sAddress'], result['sNetmask']))
                else:
                    addrs = IP('%s/%s' %(result['sAddress'],
                                         result['sNetmask']), make_net=True)
                vips.append(addrs)
            else:
                vips.append(result['sAddress'])
        elif str(result['sAddtype']) == '2':
            vips = get_ip('%s-%s' %(result['sAddress'], result['sNetmask']))
        return  vips

    if str(data['iRangeType']) == '1':	    # ip
        addr_sql = 'select sAddress, sNetmask, sAddtype from m_tbaddress_list\
                where id=%d;' %(int(data['sRange']))
        result = judge_data(addr_sql)[0]
        vips = netmarkip(result)
        ips = ips + vips
    elif str(data['iRangeType']) == '2':    # ip组
        g_sql = 'select HideID, sIP from m_tbaddressgroup where id=%d;'\
                %(int(data['sRange']))
        result = judge_data(g_sql)[0]

        ids = result['sIP'].split(',')
        ids = ['id=%s' %(x) for x in ids]
        ids = ' or '.join(ids)
        addr_sql = 'select sAddress, sNetmask, sAddtype from m_tbaddress_list\
                where %s;' %(ids)
        results = judge_data(addr_sql)
        for result in results:
            vips = netmarkip(result)
            ips = ips + vips

    return set(ips)

def get_authentication_type(userip):
    """
    查找用户ip适用的策略
    return:
        策略类型|短信类型 或 策略类型
    """

    tactics_sql = 'select * from m_tbusers_authentication_tactics\
            where iStatus=1;'
    results = search_data(tactics_sql)

    tactics = None
    imax = 0
    for result in results:
        ips = search_ips(result)
        for item in ips:
            if userip in item and imax < result['iPriority']:
                tactics = result
                imax = result['iPriority']
                break
    if not tactics:
        getLogger(LOG_NAME).debug('not search authentication!')
        print 'False'
        return
    else:
        stype = tactics.get('sAuthenticationType', 'False')
        if int(stype) == 4:
            msg = tactics.get('iSmsServer', '0')
            print str(stype) + '|' + str(msg)
            return
            #return str(stype) + '|' + str(msg)
        print str(stype)
        #return str(stype)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        getLogger(LOG_NAME).debug('more args (eg: python /usr/local/bluedon/usermanage/authenticaton_type.py 1.1.1.1)')
    else:
        get_authentication_type(sys.argv[1])
