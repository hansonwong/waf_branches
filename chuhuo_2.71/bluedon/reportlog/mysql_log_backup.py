#!/usr/bin/env python
# -*-coding:utf-8-*-

import os
import sys
import MySQLdb
import time
os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')
from utils.logger_init import get_logger
from db.config1 import execute_sql,executemany_sql,fetchone_sql,fetchall_sql
from utils.log_logger import rLog_dbg



BAK_PATH = r'/var/log/log_tables_backup/'
LOG_PATH = r'/usr/local/bluedon/log/backup_log'
FWLOG_DEBUG = lambda x : rLog_dbg('mysql_log_backup', x)
logger = get_logger('BACKUP',LOG_PATH)
class LogDatabaseBackup():
    def __init__(self):
        pass


def mysql_log_backup_old(n):
    """Not Use"""
    if not os.path.exists(BAK_PATH + n):
        os.system('mkdir %s' % BAK_PATH + n)
    bak_list = show_tables(n)
    #pop today's table
    today = time.strftime('%Y%m%d',time.localtime())
    #today = '20160223'
    if n + '_' + today in bak_list:
        bak_list.remove(n + '_' + today)
    [backup_table(n,item) for item in bak_list]

def backup_table(log_type,tb):
    """
    Description:
        Using  sql statement to backup Mysql Tables(at most 100,000)
    INPUT:
        log_type: log type
        tb      : table name which is consist of log type and date(YYYYMMDD)
    OUTPUT:
        None
    """
    try:
        tb_sql = BAK_PATH + log_type + '/' + tb + '.sql'
        if os.path.exists(tb_sql):
            os.remove(tb_sql)
            logger.debug('file %s is exists, removed' % tb_sql)
            pass
        os.system("echo 'use db_firewall_log;' >> %s" % tb_sql)
        cmd = ("/usr/bin/mysqldump --port=3307 --socket=/tmp/mysql3307.sock "
               "-uroot --password='bd_123456' --opt --where='1 limit 100000' "
               "db_firewall_log %s >>%s")
        os.system(cmd % (tb,tb_sql))
    except Exception as e:
        FWLOG_DEBUG(e)



def mysql_log_backup(log_type):
    """Not Use"""
    if not os.path.exists(BAK_PATH + log_type):
        os.system('mkdir %s' % BAK_PATH + log_type)
    [backup_table(log_type,res) for res in show_tables(log_type)]


def mysql_log_recover_by_date(types,date):
    """
        Description:
            recover log table from *.sql if types_date.sql is exists
    """
    # if table is already exists
    if mysql_table_exists(types + '_' + date):
        return 0

    # need recovery
    # find if sql backup file is exists
    tb_sql = BAK_PATH + types + '/' + types + '_' + date + '.sql'

    # if not exists return -1 and log
    if not os.path.exists(tb_sql):
        logger.debug('FILE %s is NOT EXISTS!!!' % tb_sql)
        return -1

    # recover table from types_date.sql
    logger.debug('RECOVER File:%s' % tb_sql)
    try:
        cmd = ("/usr/bin/mysql --port=3307 --socket=/tmp/mysql3307.sock "
               "-uroot --password='bd_123456' --port=3307  -e 'source %s'")
        os.system(cmd % tb_sql)
        return 1
    except Exception as e:
        FWLOG_DEBUG(e)

def mysql_log_recover(types,name):
    """Not Use"""

    if mysql_table_exists(name):
        return
    tb_sql = BAK_PATH + types + '/' + name + '.sql'
    if not os.path.exists(tb_sql):
        logger.debug('FILE %s is NOT EXISTS!!!' % tb_sql)
        return

    try:
        cmd = ("/usr/bin/mysql --port=3307 --socket=/tmp/mysql3307.sock "
               "-uroot --password='bd_123456' --port=3307 -e 'source %s'")
        os.system(cmd % tb_sql)
    except Exception as e:
        FWLOG_DEBUG(e)

def mysql_table_exists(name):
    """return if table is exists"""
    sql = ("select TABLE_NAME from INFORMATION_SCHEMA.TABLES "
           "where TABLE_SCHEMA='db_firewall_log' and TABLE_NAME='%s';") % name
    res = fetchone_sql(sql)
    return res is not None

def ts_from_date(da):
    """YYYYMMDD --> timestamp"""
    ta = time.strptime(da,'%Y%m%d')
    ts = time.mktime(ta)
    return (ts)


def old_enough_to_backup(newest,this):
    """
        Description:
            INPUT:
                newst: newst date
                this:  a date of table
            OUTPUT:
                compare newst date and 'this', return if 'this' is ten days
                older than newst
    """
    #TEN DAYS = 60(s) * 60(min) * 24(h) * 10(d) = 864000(s)
    TEN_DAYS = 864000
    ts_newest = ts_from_date(newest)
    ts_this = ts_from_date(this)
    return (ts_newest - ts_this) > TEN_DAYS

def newest_date(lst):
    """
        Description:
            find out the newst date of input list, where lst is a list of
            table names, if lst in null return today
    """
    if lst == []:
        return time.strftime('%Y%m%d',time.localtime())
    l = [x.split('_')[-1]  for x in lst]
    return max(l)

    pass

def show_tables(tb):
    """
        Description:
            find out all tables' name of log 'tb', return in a list
    """
    format = tb + '_2%'
    sql = ("SELECT TABLE_NAME FROM information_schema.`TABLES` "
           "WHERE TABLE_SCHEMA='db_firewall_log' and "
           "TABLE_NAME LIKE '%s'") % format
    lst = [ x['TABLE_NAME'] for x in fetchall_sql(sql) ]
    return lst

def update_newest_table(tb_type):
    """
        Description:Not Use

    """
    lst = show_tables(tb_type)
    nd = newest_date(lst)
    today = time.strftime('%Y%m%d',time.localtime())
    #compare newest day in database and today
    if nd == today:
        pass
    else:
        #delete tb
        sql = 'TRUNCATE TABLE %s' % tb_type
        #cur.execute(sql)
        execute_sql(sql)
        #import new data
        sql = 'INSERT INTO %s SELECT * from %s' % (tb_type,tb_type + '_' + nd)
        #cur.execute(sql)
        execute_sql(sql)



#should run everyday
def mysql_log_delete_old_tb(name):
    """
        Description:
            Delete log tables ten days older then the newest log,
            Before deleting, backup tables to PATH:
                BAK_PATH/LogName/LogName_YYYYMMDD.sql
    """
    #mysql_log_query_recovery(name)
    # get all log tables in database
    tb_list = show_tables(name)
    today = time.strftime('%Y%m%d',time.localtime())

    # find out tables which are old_enough_to_backup(delete from database)
    delete_list = [ x for x in tb_list
                   if old_enough_to_backup(newest_date(tb_list),x.split('_')[-1])]

    # set newest_date today(Not Use now)
    #delete_list = [ x for x in tb_list if old_enough_to_backup(today,x.split('_')[-1])]

    #backup before delete tables
    if not os.path.exists(BAK_PATH + name):
        os.system('mkdir %s' % BAK_PATH + name)

    # backup all tables before delete
    [backup_table(name,res) for res in tb_list]

    # backup tables will be delete next(Not Use Now)
    #[backup_table(name,res) for res in delete_list]

    # log
    if delete_list != []:
        logger.debug('BACKUP Before DELETE:%s' % delete_list)


    # drop tables in delete_list
    for tb in delete_list:
       execute_sql('DROP TABLE %s' % tb)


def everyday_task():
    #backup
    tb_list = ['m_tbfwsessionstatus', 'm_tblog_app_admin','m_tblog_ddos','m_tblog_evil_code',
               'm_tblog_firewall','m_tblog_info_leak','m_tblog_ips',
               'm_tblog_url_visit','m_tblog_webapplication','m_tblog_wifi_audit']
    for tb in tb_list:
        mysql_log_delete_old_tb(tb)

def newest_lines_from_table(tb,line):
    lst = show_tables(tb)
    if lst == []:
        return None
    nd = newest_date(lst)

    sql = 'SELECT * from %s ORDER BY id DESC LIMIT %s' % (tb + '_' + nd, line)

    res = [item for item in fetchall_sql(sql)]
    return res
    pass

def get_ten_newest_lines_from_table(tb):
    return newest_lines_from_table(tb,10)

if __name__ == '__main__':

    # KEEP THIS ALIVE!!!!!
    everyday_task()


    #-------------------TEST-------------------
    #mysql_log_backup_old('m_tblog_url_visit')
    #mysql_log_backup('m_tblog_firewall')
    # mysql_log_recover('m_tblog_ips','m_tblog_ips_20160624')
    #mysql_log_recover('m_tblog_url_visit','m_tblog_url_visit_20160126')
    #mysql_log_recover('m_tblog_url_visit','m_tblog_url_visit_20160128')
    # print mysql_table_exists('m_tblog_ips_20160624')
    #ts_from_date('20160307')
    #old_enough_to_backup('20160214','20160203')
    # print show_tables('m_tblog_ips')
    #mysql_log_query_recovery('m_tblog_url_visit')
    #mysql_log_delete_old_tb('m_tblog_url_visit')
    # mysql_log_recover_by_date('m_tblog_ips','20160624')
    #mysql_log_backup('m_tblog_url_visit')
    #update_newest_table('m_tblog_app_admin')
    #newest_lines_from_table('m_tblog_ddos',20)

#if __name__ == '__main__':
#    everyday_task()

