#!/usr/bin/python
#-*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

import time
import json
import commands
from logging import getLogger
from homepage.system_usage import disk_usage
from db.config import fetchone_sql as fetch_3306
from db.config1 import fetchone_sql,fetchall_sql,execute_sql
from utils.log_logger import FWLOG_DEBUG, FWLOG_ERR
from utils.find_file import get_all_files_in, find_files_of_date
from utils.find_file import TYPES as AUDIT_FILE_TYPE
from reportlog.mysql_partition import rebuild_summary_table


PATH_ARCH = r'/var/log_bak/'
PATH_SQLBAK = r'/var/log/log_tables_backup/'
MAX_USAGE = 80

ALL_AUDIT_TYPES = ''.join(AUDIT_FILE_TYPE)


def log_clear_arch(path):
    # FWLOG_DEBUG('processing...arch')
    oldfiles = get_all_files_in(path)
    if len(oldfiles) == 0:
        return False

    for oldfile in oldfiles:
        try:
            os.remove(oldfile)

            # delete oldfile record in m_tblog_library
            oldfilename = os.path.split(oldfile)[-1]
            sql = "delete from m_tblog_library where sFileName='%s'" % oldfilename
            execute_sql(sql)

            FWLOG_DEBUG('Removed[arch file]%s' % oldfile)
        except Exception as e:
            FWLOG_ERR(e)

    return True

def log_clear_sqlbak(path):
    # FWLOG_DEBUG('processing...sqlbak')
    oldfiles = get_all_files_in(path)

    if len(oldfiles) == 0:
        return False

    for oldfile in oldfiles:
        try:
            os.remove(oldfile)
            FWLOG_DEBUG('Removed[sqlbak] %s' % oldfile)
        except Exception as e:
            FWLOG_ERR(e)
    return True


def get_tb_list(x_days=3):
    from itertools import groupby
    get_tb_names = "SELECT TABLE_NAME from information_schema.`TABLES` WHERE TABLE_NAME LIKE 'm_tb%\_2%';"
    tbs = [res['TABLE_NAME'] for res in fetchall_sql(get_tb_names)]

    # keep x days table return the other tables name
    ret_l = sorted(tbs,key=lambda x:x.split('_')[-1])
    for k, g in groupby(sorted(ret_l), key=lambda x : x.split('2')[0]):
        count = 0
        for _k, _g in groupby(sorted(g, reverse=True), key=lambda x : x[len(k):][:8]):
            if x_days == 0: continue
            for __g in _g:
                ret_l.remove(__g)
            count += 1
            if count >= x_days:
                break
    return ret_l


def log_clear_mysql(x_days_ago):
    FWLOG_DEBUG('processing...mysql')
    delete_table = 'DROP TABLE %s'

    # audit file record
    audit_file_record = set()
    for tb in get_tb_list(x_days_ago):
        try:
            # if tb is a audit table, delete audit files in this tb
            if tb.startswith('m_tb_'):
                tb_type = tb.split('_')[2]
                tb_date = tb.split('_')[-1]

                audit_file_record.add((tb_type, tb_date))

                print tb.split('_')[2] + '  ' + tb.split('_')[-1] + '  ' + tb

        except Exception as e:
            FWLOG_ERR(e)

        execute_sql(delete_table % tb)
        FWLOG_DEBUG('Removed[Mysqltb] %s' % tb)

    # delete audit files
    print audit_file_record
    for tb_type, tb_date in audit_file_record:
        print 'removing... ', tb_type, '  ', tb_date
        log_clear_audit_file(tb_type, tb_date)

    return False


def log_clear_audit_file(tb_type, tb_date):
    # check if tb_type has audit file
    if tb_type not in ALL_AUDIT_TYPES:
        print tb_type, ' is not in  ', ALL_AUDIT_TYPES
        return

    tb_type = tb_type + '/'

    print 'searching file of type[%s]' % tb_type
    files = find_files_of_date('/var/suricata', tb_date, tb_type)
    for f in files:
        try:
            os.remove(f)
            print 'Removed %s' % f
        except:
            print '%s not exists' % f
    print len(files)
    pass


def log_clear_release_disk(x_days_ago=3, keep=True):
    path_arch = PATH_ARCH
    path_sqlbak = PATH_SQLBAK
    # while du > max_usage:
    # get max keep day
    if keep:
        try:
            ret = fetch_3306("SELECT sValue FROM m_tbconfig WHERE sName='logConfig';")
            js_ret = json.loads(ret['sValue'])
            x_days_ago = int(js_ret['memoryTime'])
        except:
            FWLOG_ERR('[log_clear]cannot find setting for MAX_KEEP day, use [3] \
                      as default value')
    else:
        pass

    # try to release disk space
    try:
        log_clear_arch(path_arch)
        FWLOG_DEBUG('log_clear_arch done...')
        log_clear_sqlbak(path_sqlbak)
        FWLOG_DEBUG('log_clear_sqlbak done...')
        log_clear_mysql(x_days_ago)
        FWLOG_DEBUG('log_clear_mysql done...')

        # rebuild summary table m_tb_statistics_audit_all
        rebuild_summary_table('m_tb_statistics_audit')
        rebuild_summary_table('m_tb_audit_traffic_statistics')

    except Exception as e:
        FWLOG_ERR(e)
    FWLOG_DEBUG('release disk finish...')

if __name__ == '__main__':
    try:
        x_days = sys.argv[1]
        x_days = int(x_days)
        log_clear_release_disk(x_days_ago=x_days)
    except:
        print "Usage python -m reportlog.log_clear x"
        print "      x is an int, like 0,1,2,..."


    # test
    # print get_tb_list()
    # log_clear_arch(PATH_ARCH)
    # log_clear_sqlbak(PATH_SQLBAK)
    #print oldest_file('/var/log_bak/tmp')
    # log_clear_mysql(3)

    pass
