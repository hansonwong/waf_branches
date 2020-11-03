#!/usr/bin/env python
# coding=utf-8

import os
import sys

os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

from db.config import execute_sql as exec_3306
from db.config1 import execute_sql as exec_3307


# TB_3306 = {}

# TB_3307 = {}
def TB_3306(tb):
    sql_file = '/usr/local/bluedon/db/db_user_traffice.sql'
    return get_tb_sql(tb, sql_file)


def TB_3307(tb):
    sql_file = '/usr/local/bluedon/db/db_firewall_log.sql'
    return get_tb_sql(tb, sql_file)


def get_tb_sql(tb, sql_file):
    with open(sql_file, 'r') as fp:
        lines = fp.readlines()
    try:
        start_line = 'DROP TABLE IF EXISTS `%s`;\n' % tb
        idx_start = lines.index(start_line) + 1
    except ValueError:
        start_line = 'DROP TABLE IF EXISTS `%s`;\r\n' % tb
        idx_start = lines.index(start_line) + 1
    lines[idx_start] = 'CREATE TABLE IF NOT EXISTS `%s` (\n' % tb
    idx_end = idx_start
    count = idx_start
    for line in lines[idx_start:]:
        if ';' in line:
            # idx_end = lines.index(line) + 1
            idx_end = count + 1
            break
        count += 1
    return ''.join(lines[idx_start:idx_end]).strip('\n')



def reset_3306_log_tables_old():
    pass


def reset_3307_log_tables_old():
    pass


def reset_log_table(tb):
    pass


def reset_3306_log_tables():
    tb_sql = '/usr/local/bluedon/db/db_user_traffice.sql'
    if not os.path.exists(tb_sql):
        print 'No sql file [%s]' % tb_sql
        return
    cmd = ("/usr/bin/mysql --port=3306 --socket=/tmp/mysql3306.sock "
           "-uroot --password='bd_123456' --port=3306 -e 'source %s'")
    os.system(cmd % tb_sql)
    pass

def reset_3307_log_tables():
    tb_sql = '/usr/local/bluedon/db/db_firewall_log.sql'
    if not os.path.exists(tb_sql):
        print 'No sql file [%s]' % tb_sql
        return
    cmd = ("/usr/bin/mysql --port=3307 --socket=/tmp/mysql3307.sock "
           "-uroot --password='bd_123456' --port=3307 -e 'source %s'")
    os.system(cmd % tb_sql)
    pass

if __name__ == '__main__':
    reset_3306_log_tables()
    reset_3307_log_tables()
    # TB_3307('m_tblog_size_record')
    # reset_log_table('m_tblog_ips')
    pass
