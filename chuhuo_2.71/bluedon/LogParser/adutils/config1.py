#!/usr/bin/env python
# coding=utf-8

"""
config file
"""

import MySQLdb, MySQLdb.cursors
import os

from adutils.audit_logger import rLog_err

LOG_ERR = lambda x: rLog_err('audit_mysql', x)

DB = {
        'host': 'localhost',
        'port': 3307,
        'user': 'root',
        'passwd': 'bd_123456',
        'db': 'db_firewall_log',
        'charset': 'utf8',
        #'use_unicode':False,
        'cursorclass': MySQLdb.cursors.DictCursor,
        'unix_socket': '/tmp/mysql3307.sock'
        }

DB1 = {
        'host': 'localhost',
        'port': 3307,
        'user': 'root',
        'passwd': 'bd_123456',
        'db': 'db_firewall_log',
        'charset': 'utf8',
        #'use_unicode':False,
        #'cursorclass': MySQLdb.cursors.DictCursor,
        'unix_socket': '/tmp/mysql3307.sock'
        }

def search_data(sql):
    """
    执行sql语句
    args:
        sql: 查询的sql语句
    return:
        datas: 查询的记录集
    """

    conn = MySQLdb.connect(**DB)
    cur = conn.cursor()
    cur.execute(sql)
    datas = cur.fetchall()
    conn.close()
    return datas

def execute_sql(sql):
    """ 执行sql语句 """

    _ret = True
    conn = MySQLdb.connect(**DB)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print e
        LOG_ERR(sql)
        LOG_ERR(e)
        conn.rollback()
        _ret = False
    finally:
        conn.close()

    return _ret


def mkdir_file(file_path, cmd_type):
    """
    判断文件路径和文件是否存在, 不存在则创建
    args:
        file_path: 文件路径
        cmd_type: 创建的文件类型
    return:
        None
    """

    cmd_dict = {'file': '/usr/bin/touch',
                'fifo': '/usr/bin/mkfifo'}

    if not os.path.exists(file_path):
        file_split = os.path.split(file_path)
        if not os.path.exists(file_split[0]):
            os.system('mkdir %s' %(file_split[0]))
            os.system('%s %s' %(cmd_dict[cmd_type], file_path))
            os.system('/usr/bin/chmod 777 %s' %(file_path))
        return True
    else:
        return False



def executemany_sql(sql,args):
    """
        执行sql语句
        args:
            sql: 要重复执行的SQL语句
            args: 一个列表,列表中的元素为SQL语句的参数(Tuple)
    """
    if args == []:
        return
    conn = MySQLdb.connect(**DB)
    cur = conn.cursor()
    try:
        cur.executemany(sql,args)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print e
        LOG_ERR(sql)
        LOG_ERR(e)
    conn.close()


def get_mysql_db():
    """ 获取数据库链接和游标  """

    try:
        conn = MySQLdb.connect(**DB)
        cur = conn.cursor()
        return conn,cur
    except:
        return None,None

def get_mysql_db1():
    """ 获取数据库链接和游标  """

    try:
        conn = MySQLdb.connect(**DB1)
        cur = conn.cursor()
        return conn,cur
    except:
        return None,None

def fetchone_sql(sql):
    """
    执行sql语句
    args:
        sql: 查询的sql语句
    return:
        datas: 查询的记录集
    """
    datas = None
    try:
        conn = MySQLdb.connect(**DB)
        cur = conn.cursor()
        cur.execute(sql)
        datas = cur.fetchone()
    except Exception as e:
        print e
        LOG_ERR(sql)
        LOG_ERR(e)
    finally:
        conn.close()

    return datas


def fetchall_sql(sql):
    """
    执行sql语句
    args:
        sql: 查询的sql语句
    return:
        datas: 查询的记录集Iterable对象
    """
    datas = {}
    try:
        conn = MySQLdb.connect(**DB)
        cur = conn.cursor()
        cur.execute(sql)
        datas = cur.fetchall()
    except Exception as e:
        print e
        LOG_ERR(sql)
        LOG_ERR(e)
    finally:
        conn.close()

    for res in datas:
        yield res

def record_in_tb(val,attr,tb):
    """
    检查tb数据表中是否存在值为val的字段attr
    args:
        val:字段值
        attr:字段名
        tb:数据表名
    """
    sql = 'select %s from %s where %s="%s" limit 1'
    res = fetchone_sql(sql % (attr,tb,attr,val))
    return res != None


def init_db_table():
    from db.db_log_tables_reset import TB_3307
    tables = [
        'm_tblog_app_admin',
        'm_tblog_ddos',
        'm_tblog_evil_code',
        'm_tblog_firewall',
        'm_tblog_info_leak',
        'm_tblog_ips',
        'm_tblog_url_visit',
        'm_tblog_wifi_audit',
        'm_tblog_webapplication'
    ]
    for tb in tables:
        execute_sql(TB_3307(tb))


    pass
