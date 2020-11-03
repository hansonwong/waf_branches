#!/usr/bin/env python
# coding=utf-8

'''
应用计数统计
'''

import os
from logging import getLogger

from db.config import execute_sql, search_data
from utils.logger_init import logger_init


logger = logger_init('SET_APP_MARK', '/usr/local/bluedon/log/app_mark_count.log', 'DEBUG')

def set_app_mark(app_id, action):
    """
    args:
        app_id: 应用的id号(m_tbdefined_application表)
        action: 动作(删/增)
    m_tbdefined_application表记录通道配置、安全策略、策略路由使用应用协议的次数，根据记录的次数是否打mark
    """

    a_sql = 'select * from m_tbdefault_app_list where app_id_ten=%d;' %(app_id)
    result = search_data(a_sql)
    if not result:
        logger.debug('%s: m_tbdefault_app_list table not app_id_ten=%d' %(action, app_id))
        return False
    cmd = '/usr/sbin/iptables -t mangle -%s APPMARK -m ndpi --%s -j MARK --set-xmark %d'
    result = result[0]
    if action == 'add':
        iptable_cmd = cmd %('A', result['sNdpiname'].strip().lower(), result['app_id_ten'])
        logger.debug(iptable_cmd)
        os.system(iptable_cmd)


    elif action == 'del':
        flag = False

        result = search_data(a_sql)[0]
        iptable_cmd = cmd %('D', result['sAppName'].strip().lower(), result['app_id_ten'])
        logger.debug(iptable_cmd)
        os.system(iptable_cmd)

def default_scount_field():
    ''' m_tbndpi_protocol表中所有记录的sCount字段置0 '''

    s_sql = 'update m_tbdefault_app_list set sCount=0 where sCount>0;'
    logger.debug(s_sql)
    execute_sql(s_sql)


if __name__ == '__main__':
    default_scount_field()
