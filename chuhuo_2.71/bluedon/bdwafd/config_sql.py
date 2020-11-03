#! /usr/bin/env python
# -*- coding:utf-8 -*-


import MySQLdb
import MySQLdb.cursors

DB = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': 'bd_123456',
    'db': 'waf',
    'charset': 'utf8',
    'use_unicode': 'False',
    'unix_socket': '/tmp/mysql3306.sock',
    # 'cursorclass': MySQLdb.cursors.DictCursor,
}

DB_LOGS = {'host': 'localhost',
           'port': 3306,
           'user': 'root',
           'passwd': 'bd_123456',
           'db': 'logs',
           'charset': 'utf8',
           'use_unicode': 'False',
           'unix_socket': '/tmp/mysql3306.sock',
           }


def execute_sql(sql):
    conn = MySQLdb.connect(**DB)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
    except:
        conn.rollback()
    conn.close()


def execute_sql_logs(sql):
    conn = MySQLdb.connect(**DB_LOGS)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
    except:
        conn.rollback()
    conn.close()


def fetchall_sql(sql):
    """
    执行sql语句
    args:
        sql: 查询的sql语句
    return:
        datas: 查询的记录集Iterable对象
    """

    conn = MySQLdb.connect(**DB)
    cur = conn.cursor()
    cur.execute(sql)
    datas = cur.fetchall()
    conn.close()
    for res in datas:
        yield res


def fetchone_sql(sql):
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
    data = cur.fetchone()
    conn.close()
    return data

