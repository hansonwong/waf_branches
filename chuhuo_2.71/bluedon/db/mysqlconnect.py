#! /usr/bin/env python
# -*- coding:utf-8-*-

import MySQLdb
import MySQLdb.cursors
from logging import getLogger

from utils.logger_init import get_logger


get_logger('db','log/database.log','INFO')

class MySQLConnectAdapter(object):
    """用来包装mysql_connect函数
    使之在调用cur.close的时候能够关闭conn，解决旧代码中conn不能关闭的bug
    """

    def __init__(self, conn, cur):
        self._conn = conn
        self._cur = cur

    def __getattribute__(self, name):
        if name in ('close', '_conn', '_cur'):
            return object.__getattribute__(self, name)
        else:
            return object.__getattribute__(self, '_cur').__getattribute__(name)

    def close(self):
        getLogger('db.mysqlconnect').info('close cursor <%s>...' % hex(id(self._cur)))
        self._cur.close()
        getLogger('db.mysqlconnect').info('close connection <%s>...' % hex(id(self._conn)))
        self._conn.close()


def mysql_connect():
    conn = MySQLdb.connect(host='localhost', port=3306, user='root',
                           passwd='bd_123456', db='db_firewall', charset='utf8',
                           use_unicode=False, unix_socket='/tmp/mysql3306.sock')
    cur = conn.cursor()
    safe_cur = MySQLConnectAdapter(conn, cur)
    return safe_cur


def mysql_connect_dict():
    conn = MySQLdb.connect(host='localhost', port=3306, user='root',
                           passwd='bd_123456', db='db_firewall', charset='utf8',
                           use_unicode=False, unix_socket='/tmp/mysql3306.sock',
                           cursorclass=MySQLdb.cursors.DictCursor)
    cur = conn.cursor()
    safe_cur = MySQLConnectAdapter(conn, cur)
    return safe_cur


def mysql_connect_3307():
    conn = MySQLdb.connect(host='localhost', port=3307, user='root',
                           passwd='bd_123456', db='db_firewall_log', charset='utf8',
                           use_unicode=False, unix_socket='/tmp/mysql3307.sock')
    cur = conn.cursor()
    safe_cur = MySQLConnectAdapter(conn, cur)
    return safe_cur


def mysql_connect_dict_3307():
    conn = MySQLdb.connect(host='localhost', port=3307, user='root',
                           passwd='bd_123456', db='db_firewall_log', charset='utf8',
                           use_unicode=False, unix_socket='/tmp/mysql3307.sock',
                           cursorclass=MySQLdb.cursors.DictCursor)
    cur = conn.cursor()
    safe_cur = MySQLConnectAdapter(conn, cur)
    return safe_cur


def execute_sql(sql):
    """
    从数据库提前数据
    """
    cur = mysql_connect_dict()
    cur.execute(sql)
    results = cur.fetchall()
    cur.close()
    return results

class fw_db_cur():
    cmd_sql_one = 'select * from %s where id=%d'
    cmd_sql_ipaddr = 'select * from %s where sPortName = \'%s\''
    def __init__(self, dict = True):
        if dict:
            self.cur = mysql_connect_dict()
        else:
            self.cur = mysql_connect()
    def get_theone(self, tablename, id):
        theone = None
        try:
            self.cur.execute(fw_db_cur.cmd_sql_one % (tablename, id))
            theone = self.cur.fetchone()
        except Exception as e:
            getLogger('main').exception(e)
        return theone
    def get_ipaddr_v4(self, iface, tablename = 'm_tbnetport'):
        ip = ''
        try:
            self.cur.execute(fw_db_cur.cmd_sql_ipaddr % (tablename, iface))
            r = self.cur.fetchone()
            ip = r['sIPV4Address']
        except Exception as e:
            getLogger('main').exception(e)
        return ip

    def get_ipaddr_v6(self, iface, tablename = 'm_tbnetport'):
        ip = ''
        try:
            self.cur.execute(fw_db_cur.cmd_sql_ipaddr % (tablename, iface))
            r = self.cur.fetchone()
            ip = r['sIPV6Address']
        except Exception as e:
            getLogger('main').exception(e)
        return ip


