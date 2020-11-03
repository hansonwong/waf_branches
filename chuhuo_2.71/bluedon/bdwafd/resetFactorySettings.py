#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger
from common import logger_init
import os, datetime, shutil, MySQLdb, datetime
from config import config
#from helperforabanalyse import save_data_for_abnormal_analyse

import sqlparse, time
import sys
sys.path.append('/usr/local/bluedon/bdwafd')


files = ['/var/log/messages',
         '/var/log/ddoslog',
         '/var/log/weboutlog',
         '/usr/local/bluedon/bdwaf/logs/access.log',
         '/usr/local/bluedon/bdwaf/logs/error.log',
         '/usr/local/bluedon/bdwaf/logs/syslog/access_syslog.log',
         '/usr/local/bluedon/bdwaf/logs/syslog/error_syslog.log',
         '/usr/local/bluedon/bdwaf/logs/modsec_audit.log',
         '/usr/local/bluedon/bdwaf/logs/modsec_debug.log',
         '/usr/local/bluedon/bdwafd/log/audit.log',
         '/usr/local/bluedon/bdwafd/log/main.log',
         '/var/log/mysql/slowquery.log',
         '/var/log/redis/redis-server.log',
         ]

audit = '/usr/local/bluedon/bdwaf/logs/audit/'

def cleardatabase():
    conn     = MySQLdb.connect(**config['dbacc'])
    cursor   = conn.cursor()
    tblnames = (
                't_alertlogs_bak','t_alertlogs', # 入侵日志
                't_ddoslogs','t_ddoslogs_bak',   # ddos日志
                't_cclogs_bak','t_cclogs',       # CC日志
                't_weboutlogs','t_weboutlogs_bak', # 非法外联日志
                't_bdblockedlogs',                 # 智能阻断日志
                'waf.t_customrules',   # 自定义规则
                'waf.t_baseaccessctrl', # 访问控制
                'waf.t_selfstudyrule',  # 防误报设置
                'logs.t_ruleid',  # 入侵类别统计
                't_counturi_bak','t_counturi','t_countsety','general','robot',
                't_sourceip_bak','t_sourceip','t_syslogs_bak','t_syslogs'
                )
    for tblname in tblnames:
        cursor.execute('truncate table %s' % tblname)

    sql=open("/usr/local/bluedon/bdwafd/data/resetcfg.sql",'r').read()
    sql_parts = sqlparse.split( sql )
    for sql_part in sql_parts:
        if sql_part.strip() ==  '':
            continue
        cursor.execute( sql_part )


    conn.commit()
    cursor.close()
    conn.close()

def clearbiglogs():
    for f in files:
        if os.path.exists(f):
            getLogger('main').info("remove file '%s'" % f)
            # open(f, 'w').close()
            os.system('rm -rf %s' % f)


def clearmsclog(theday=None):
    getLogger('main').info("removing dir '%s'" % audit)
    os.system('rm -rf %s' % audit)
    getLogger('main').info("remove dir '%s', Done." % audit)


def clear_access(total=None, autodiskclean=None):
    access_dir = ['/usr/local/bluedon/bdwaf/logs/logrotate',
                  '/mnt/ramdisk',
                  '/var/log/nginx',
                  '/usr/local/bluedon/bdwaf/logs/access']

    for d in access_dir:
      if os.path.exists(d):
        os.system('rm -rf %s/*' % d)

if __name__ == '__main__':
    from db import Session, row2dict, session_scope
    cwd = config['cwd']
    os.chdir(cwd)
    logger_init('main', config['logger']['cleardisk']['path'], config['logger']['cleardisk']['level'])
    getLogger('main').info('cleardatalogs start.')

    cleardatabase()
    clearmsclog()
    clearbiglogs()
    clear_access()

    time.sleep (1)
    os.system('echo "CMD_DEPLOY_TYPE" >> /tmp/bdwaf.fifo')
    time.sleep (1)
    os.system('echo "CMD_UCARP|deploy" >> /tmp/bdwaf.fifo')
    time.sleep (1)
    os.system('echo "CMD_DDOS" >> /tmp/bdwaf.fifo')
    time.sleep (1)
    os.system('echo "CMD_BYPASS" >> /tmp/bdwaf.fifo')
    time.sleep (1)
    os.system('echo "CMD_NGINX" >> /tmp/bdwaf.fifo')
    getLogger('main').info('reset factory setting Done.')
