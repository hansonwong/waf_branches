# -*- coding: utf-8 -*-

import MySQLdb, MySQLdb.cursors
import logging


BASE_DIR = '/usr/local/bluedon'

# 全局日志级别
# 可选级别：logging.NOTSET, logging.DEBUG, logging.INFO,
#           logging.WARNING, logging.ERROR, logging.CRITICAL
LOG_LEVEL = logging.NOTSET


# 数据库链接
DB = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': 'bd_123456',
    'db': 'db_firewall',
    'charset': 'utf8',
    'use_unicode':True,
    'unix_socket': '/tmp/mysql3306.sock',
}

DICT_DB = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': 'bd_123456',
    'db': 'db_firewall',
    'charset': 'utf8',
    'use_unicode':True,
    'cursorclass': MySQLdb.cursors.DictCursor,
    'unix_socket': '/tmp/mysql3306.sock'
}


# linux命令全路径
CMD_IPTABLES = '/usr/sbin/iptables'
CMD_IP6TABLES = '/usr/sbin/ip6tables'
CMD_SED = '/usr/bin/sed'
CMD_AT = '/usr/bin/at'
CMD_SERVICE = '/usr/sbin/service'
CMD_HWCLOCK = '/usr/sbin/hwclock'
CMD_IPSET = '/usr/local/sbin/ipset'


# 日志路径
LOG_BASE_PATH = '/usr/local/bluedon/log/'
