#!/usr/bin/env python
# -*- coding:utf-8 -*-

''' 创建当日数据表总表及子表

默认数据库设置: 3307, db: db_firewall_log
input: 表名(必须已存在在数据库中),对应的年月日(20161010格式).若无输入日期,则默认输入当天日期

文件路径下: >>>python mysql_partition.py [表名] [日期]
   example: >>>python mysql_partition.py tb_table 20161111
   example: >>>python mysql_partition.py tb_table

建立分表tb_table_20161111_1,tb_table_20161111_2,......,tb_table_20161111_24
建立总表tb_table_20161111

'''
import os
import sys
os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

import MySQLdb
import datetime
import sys
from db.config1 import execute_sql as exec_3307
from db.config1 import fetchall_sql as fcal_3307

now = datetime.datetime.now()
today_str = now.strftime("%Y%m%d")

def exec_partition(tb_name, date):

    parent_table_name = tb_name + '_' + date
    # child_name_list = [parent_table_name + '_' + str(i) for i in range(1, 25)]
    child_name_list = [parent_table_name + '_{n:0>2}'.format(n=i) for i in range(0, 24)]
    uni_child = ','.join(child_name_list)

    create_sql = lambda x: "CREATE TABLE IF NOT EXISTS {} like {}".format(x, tb_name)

    for child_n in child_name_list:
        exec_3307(create_sql(child_n))
        exec_3307("ALTER TABLE %s ENGINE=MyISAM" % child_n)
    exec_3307(create_sql(parent_table_name))
    exec_3307("ALTER TABLE %s ENGINE=MERGE UNION=(%s) INSERT_METHOD=LAST" % (parent_table_name, uni_child))


def create_summary_table(tb_name):
    _tb_all = tb_name + '_all'
    drop_sql = "DROP TABLE IF EXISTS %s"
    exec_3307(drop_sql % (_tb_all))
    create_sql = "CREATE TABLE IF NOT EXISTS %s like %s"
    # create summary table
    exec_3307(create_sql % (_tb_all, tb_name))
    return _tb_all


def get_sub_tables(tb_name):
    _sub_tb = []
    sql = "SELECT TABLE_NAME FROM information_schema.`TABLES` WHERE TABLE_NAME LIKE '{0}_2%';"
    print sql
    for res in fcal_3307(sql.format(tb_name)):
        _tbname = res.get('TABLE_NAME', '')
        if _tbname.startswith(tb_name):
            _sub_tb.append(_tbname)

    return _sub_tb


def add_sub_tables(tb_name):
    _sub_tb = get_sub_tables(tb_name)
    if len(_sub_tb) == 0:
        # log here
        print('[add_sub_tables]no sub table exists')
        return

    tb_all = create_summary_table(tb_name)
    add_sql = "ALTER TABLE %s ENGINE=MERGE UNION=(%s) INSERT_METHOD=LAST"
    exec_3307(add_sql % (tb_all, ','.join(_sub_tb)))
    # print(add_sql % (tb_all, ','.join(_sub_tb)))


def rebuild_summary_table(tb_name):
    add_sub_tables(tb_name)


if __name__ == '__main__':
    add_sub_tables('m_tb_statistics_audit')
    # if len(sys.argv) == 3:
    #     tb_name = sys.argv[1]
    #     input_date = sys.argv[2]
    #     exec_partition(tb_name, input_date)
    # elif len(sys.argv) == 2:
    #     tb_name = sys.argv[1]
    #     input_date = today_str
    #     exec_partition(tb_name, input_date)
    # else:
    #     print "ERROR: PLEASE INPUT TABLE NAME AND DATE CORRECTLY. "
