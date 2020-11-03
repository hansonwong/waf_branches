#!/usr/bin/env python
# -*- coding=utf-8 -*-


import ConfigParser
from collections import OrderedDict

from utils.logger_init import logger_init


def init_tables():
    """
    TABLES待监控的表存在一定的顺序关系(跟开机恢复类似), 值都是列表
    第一个值: 备份表需加的条件(where),
    第二个值: 需cp的配置文件(绝对路径),
    第三个值: 开机恢复/出厂设置
    第四个值: 修改该表会影响到的其他表
    """

    tables = OrderedDict()
    tables ['m_tbtimeplan_single'] = [[], [], [], ['m_tbSearitystrate']]
    tables['m_tbtimeplan_loop'] = [[], [], [], ['m_tbSearitystrate']]
    tables['m_tbaddress_list'] = [[], [], [], ['m_tbSearitystrate']]
    tables['m_tbaddressgroup'] = [[], [], ['python -m objectdefine.set_ipgroup %s'], ['m_tbSearitystrate']]
    tables['m_tbSearitystrate'] = [[' where (sInputPort="" or sInputPort is Null) and (sOutPort="" or sOutPort is Null);'], [], ['python -m firedam.safe_tactics %s'], []]
    #tables['m_tbSnat'] = [['where iConverType!=3;'], [], ['python -m firedam.nat %s']]
    #tables['m_tbDnat'] = [['where sNetport="" or sNetport is Null;'], [], ['python -m firedam.nat %s']]

    return tables

def get_tables():
    cf = ConfigParser.ConfigParser()
    cf.read('/usr/local/bluedon/system/hasync/sync_tables.ini')
    return cf

#TABLES = init_tables()

cf = get_tables()
logger = logger_init('HASYNC', '/usr/local/bluedon/log/hasync.log')
SYNC_FILE = '/home/rsync/recv'
SEND_FILE = '/home/rsync/send'
BASEPATH = '/usr/local/bluedon/tmp/hasync/'
KEY = 'bluedon'

table_relation = {'m_tbtimeplan_single': 'm_tbSearitystrate'}
