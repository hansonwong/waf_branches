#! /usr/bin/env python
# coding=utf-8

import os
import sys
import operator
os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

from db.config1 import execute_sql,executemany_sql,get_mysql_db,init_db_table
from db.db_log_tables_reset import TB_3307
from utils.log_logger import FWLOG_DEBUG

TB_EVIL_CODE = 'm_tblog_evilcode_record'

TB = {'m_tblog_evil_code'     :'m_tblog_evilcode_record',
      'm_tblog_ddos'          :'m_tblog_ddos_record',
      'm_tblog_ips'           :'m_tblog_ips_record',
      'm_tblog_webapplication':'m_tblog_webapp_record'}

def evilcode_log_statistics(records):
    if records == []:
        return
    rec_lst = [(item[1],item[6]) for item in records ]
    rec_set = set(rec_lst)
    args = [tuple(list(set_item) + [rec_lst.count(set_item)]*2) for set_item in rec_set]
    sql_insert = "INSERT INTO " + TB['m_tblog_evil_code'] + "(sVirusName,sLogLevel,iCount) VALUES ('%s','%s',%s) ON DUPLICATE KEY UPDATE iCount=iCount+%s;"
    conn,cur = get_mysql_db()
    [cur.execute(sql_insert % arg) for arg in args]
    conn.commit()
    cur.close()
    conn.close()
    pass

def evilcode_log_statistics_new(records):
    if records == []:
        return
    d = {}
    arg_item = operator.itemgetter(1,6)
    for item in records:
        d[arg_item(item)] = 0

    for item in records:
        d[arg_item(item)] += int(item[8])


    args = [tuple(list(key) + [d[key]] * 2) for key in d]

    sql_insert = ("INSERT INTO " + TB['m_tblog_evil_code'] + "(sVirusName,sLogLevel,iCount) "
                  "VALUES ('%s','%s',%s) ON DUPLICATE KEY UPDATE iCount=iCount+%s;")
    #sGrade will be update later
    conn,cur = get_mysql_db()
    [cur.execute(sql_insert % arg) for arg in args]
    conn.commit()
    cur.close()
    conn.close()
    #set_ips_grade(ips_rules)
    pass

def ddos_log_statistics(records):
    if records == []:
        return
    rec_lst = [item[1] for item in records ]
    rec_set = set(rec_lst)
    args = [tuple([set_item] + [rec_lst.count(set_item)]*2) for set_item in rec_set]
    sql_insert = "INSERT INTO " + TB['m_tblog_ddos'] + "(sEventName,iCount) VALUES ('%s',%s) ON DUPLICATE KEY UPDATE iCount=iCount+%s;"
    conn,cur = get_mysql_db()
    [cur.execute(sql_insert % arg) for arg in args]
    conn.commit()
    cur.close()
    conn.close()
    pass

def ddos_log_statistics_new(records):
    if records == []:
        return
    d = {}
    # arg_item = operator.itemgetter(1)
    for item in records:
        d[item[1]] = 0

    for item in records:
        d[item[1]] += int(item[6])


    args = [tuple([key] + [d[key]] * 2) for key in d]

    sql_insert = ("INSERT INTO " + TB['m_tblog_ddos'] + "(sEventName,iCount) "
                  "VALUES ('%s',%s) ON DUPLICATE KEY UPDATE iCount=iCount+%s;")
    #sGrade will be update later
    conn,cur = get_mysql_db()
    [cur.execute(sql_insert % arg) for arg in args]
    conn.commit()
    cur.close()
    conn.close()
    #set_ips_grade(ips_rules)
    pass

def ips_log_statistics(records):
    if records == []:
        return
    rec_lst = [(item[1],item[7],item[8],item[10]) for item in records ]
    rec_set = set(rec_lst)
    args = [tuple(list(set_item) + [rec_lst.count(set_item)]*2) for set_item in rec_set]
    sql_insert = ("INSERT INTO " + TB['m_tblog_ips'] + "(sEventName,sRuleID,sGrade,sRuleType,iCount) "
                  "VALUES ('%s','%s','%s','%s',%s) ON DUPLICATE KEY UPDATE iCount=iCount+%s;")
    #sGrade will be update later
    conn,cur = get_mysql_db()
    [cur.execute(sql_insert % arg) for arg in args]
    conn.commit()
    cur.close()
    conn.close()
    # set_ips_grade(ips_rules)
    pass

def ips_log_statistics_new0(records):
    if records == []:
        return
    args = [(item[1],item[7],item[8],item[10],item[11],item[11]) for item in records ]
    sql_insert = ("INSERT INTO " + TB['m_tblog_ips'] + "(sEventName,sRuleID,sGrade,sRuleType,iCount) "
                  "VALUES ('%s','%s','%s','%s',%s) ON DUPLICATE KEY UPDATE iCount=iCount+%s;")
    #sGrade will be update later
    conn,cur = get_mysql_db()
    [cur.execute(sql_insert % arg) for arg in args]
    conn.commit()
    cur.close()
    conn.close()
    # set_ips_grade(ips_rules)
    pass

def ips_log_statistics_new(records):
    if records == []:
        return
    d = {}
    arg_item = operator.itemgetter(1,7,8,10)
    for item in records:
        d[item[0:11]] = 0

    for item in records:
        d[item[0:11]] += int(item[11])


    args = [tuple(list(arg_item(key)) + [d[key]] * 2) for key in d]
    sql_insert = ("INSERT INTO " + TB['m_tblog_ips'] + "(sEventName,sRuleID,sGrade,sRuleType,iCount) "
                  "VALUES ('%s','%s','%s','%s',%s) ON DUPLICATE KEY UPDATE iCount=iCount+%s;")
    #sGrade will be update later
    conn,cur = get_mysql_db()
    [cur.execute(sql_insert % arg) for arg in args]
    conn.commit()
    cur.close()
    conn.close()
    #set_ips_grade(ips_rules)
    pass

def set_ips_grade(ips_rules):
    pass
    # #need modify if in 241
    # mysql_update_cmd = ('UPDATE ' + TB['m_tblog_ips'] + ' ips_log INNER JOIN '
    # 'm_tbcustom_ips_lib ON ips_log.sRuleID=m_tbcustom_ips_lib.sRuleID SET '
    # 'ips_log.sGrade=m_tbcustom_ips_lib.sDangerLever')
    # execute_sql(mysql_update_cmd)

def webapp_log_statistics(records):
    if records == []:
        return
    rec_lst = [(item[1],item[6],item[3]) for item in records ]
    rec_set = set(rec_lst)
    args = [tuple(list(set_item) + [rec_lst.count(set_item)]*2) for set_item in rec_set]
    sql_insert = ("INSERT INTO " + TB['m_tblog_webapplication'] + "(sEventName,sSeverity,sBugType,iCount) "
                  "VALUES ('%s','%s','%s',%s) ON DUPLICATE KEY UPDATE iCount=iCount+%s;")
    #sGrade will be update later
    conn,cur = get_mysql_db()
    [cur.execute(sql_insert % arg) for arg in args]
    conn.commit()
    cur.close()
    conn.close()
    pass

def webapp_log_statistics_new(records):
    if records == []:
        return
    rec_lst = [(item[1],item[6],item[3]) for item in records ]
    rec_set = set(rec_lst)
    args = [tuple(list(set_item) + [rec_lst.count(set_item)]*2) for set_item in rec_set]
    sql_insert = ("INSERT INTO " + TB['m_tblog_webapplication'] + "(sEventName,sSeverity,sBugType,iCount) "
                  "VALUES ('%s','%s','%s',%s) ON DUPLICATE KEY UPDATE iCount=iCount+%s;")
    #sGrade will be update later
    conn,cur = get_mysql_db()
    [cur.execute(sql_insert % arg) for arg in args]
    conn.commit()
    cur.close()
    conn.close()
    pass

def log_statistics_init():
    for tb in TB.values():
        execute_sql(TB_3307(tb))
    pass

def log_reset_table():
    log_table = ['m_tblog_app_admin','m_tblog_ddos','m_tblog_evil_code','m_tblog_firewall',
                 'm_tblog_info_leak','m_tblog_ips','m_tblog_webapplication','m_tblog_wifi_audit']
    tbs = log_table + TB.values()
    for tb in tbs:
        execute_sql('DROP TABLE %s' % tb)
        FWLOG_DEBUG('Drop table %s' % tb)
    log_statistics_init()
    init_db_table()



if __name__ == '__main__':
    log_statistics_init()
    # log_reset_table()
    pass
