#!/usr/bin/env python
# -*-coding:utf-8-*-


"""
    Description:
        Pack up specified `*.sql` by date, according to the period setting by WebPage
        The execute period is determined by /etc/cron.d/bd_log_cron
        If it didn't work, check /etc/cron.d/bd_log_cron
        Setting action is in /usr/local/bluedon/log_config.py/set_crontab
"""

import os
import sys
import commands
import time
import datetime

os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

from utils.log_logger import rLog_dbg
from reportlog.log_config import read_config_ini
from db.config1 import execute_sql,fetchone_sql

LOG_BAK_PATH=r'/var/log_bak/'
SQL_BAK_PATH=r'/var/log/log_tables_backup/'
TB = 'm_tblog_library'
FWLOG_DEBUG = lambda x : rLog_dbg('log_backup_lib', x)

def record_log_backup_lib():
    """
        Description:
            record the newest archive file(s) in database
    """
    sql = """CREATE TABLE IF NOT EXISTS `m_tblog_library` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `sDate` varchar(32) NOT NULL,
    `sFileName` varchar(64) NOT NULL,
    `sSize` varchar(64) NOT NULL,
    `iTime` int(11) DEFAULT NULL,
    PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;"""
    execute_sql(sql)


    #find if there is any record in table `m_tblog_library`
    try:
        # get newest date in database
        newest = fetchone_sql('select * from ' + TB + ' order by iTime DESC limit 1')['iTime']
    except:
        newest = 0

    FWLOG_DEBUG(newest)
    sql = 'insert into ' + TB + '(sFileName,sSize,sDate,iTime) values("%s","%s","%s","%s")'
    # get archive files, order by date desc
    res = commands.getoutput('ls -ltAr %s' % LOG_BAK_PATH)
    # get all *.gz files' name
    fp = [bak.split()[-1] for bak in res.split('\n')[1:]
          if os.path.splitext(LOG_BAK_PATH + bak.split()[-1])[1] == '.gz']

    for file_name in fp:
        file_path = LOG_BAK_PATH + file_name
        date = file_name.split('.')[0]
        size = os.path.getsize(file_path)
        t = time.mktime(time.strptime(date + ' 00:00:00','%Y%m%d %H:%M:%S'))
        if t > newest:
            execute_sql(sql % (file_name,size,date,t))


def _today():
    return datetime.datetime.now()

def _date(day):
    return datetime.datetime.strftime(day, '%Y%m%d')

def _find(p):
    pat = _date(p)
    return commands.getoutput('find %s -name *%s*' % (SQL_BAK_PATH,pat)).split('\n')

def _backup(d,backup_list):
    """
    Description:
        backup all files in `backup_list`, target name is `date.tar.gz`
    """
    if not ''.join(backup_list):
        # FWLOG_DEBUG('no file to Package')
        return
    date = _date(d)
    tar = LOG_BAK_PATH + date + '.tar.gz'
    if os.path.exists(tar):
        os.system('rm -f %s' % tar)
    os.system('tar -czf %s %s' % (tar,' '.join(backup_list)))
    return (date + '.tar.gz')
    pass

def _lastday_of(day):
    """
    Description:
        return the date of last day, input and output is a string of
        "YYYYMMDD"
    """
    return day - datetime.timedelta(days=1)


def backup_every_day():
    """
    Description:
        Backup `*.sql` in the same date
    """
    _day = _lastday_of(_today())
    #today = '20160517'

    backup_list = _find(_day)
    res = _backup(_today(),backup_list)
    return res
    FWLOG_DEBUG(backup_list)
    FWLOG_DEBUG(_lastday_of(today))

    pass

def backup_every_week():
    """
    Description:
        Backup `*.sql` in the same week
    """
    _day = _today()
    #_day = '20160529'
    week_days = []
    #acquire days in the most recent week
    for _ in range(7):
        _day = _lastday_of(_day)
        week_days.append(_day)

    backup_list = []
    #acquire file paths of the most recent week
    for week_day in week_days:
        backup_list.extend(_find(week_day))

    FWLOG_DEBUG(week_days)
    FWLOG_DEBUG(backup_list)

    #backup files
    res =_backup(_today(),backup_list)
    return res

def backup_every_month():
    """
    Description:
        Backup `*.sql` in the same month(last month)
    """
    _day = _today()
    #_day = '20160601'
    _day = (datetime.datetime(day=1, month=_day.month, year=_day.year) -
                  datetime.timedelta(days=1))
    days_in_month = _day.day


    month_days = []
    #acquire days in the most recent month
    for _ in range(days_in_month):
        month_days.append(_day)
        _day = _lastday_of(_day)

    backup_list = []
    #acquire file paths of the most recent month
    for month_day in month_days:
        backup_list.extend(_find(month_day))

    FWLOG_DEBUG(month_days)
    FWLOG_DEBUG(backup_list)

    #backup files
    res = _backup(_today(),backup_list)
    return res
    pass


def record_log_backup():
    """
    Description:
        Execute different action according to the value of `cycle` in log_config_ini
        After Packing sepcified files, insert a record in db to tell
        The Package Name, Size and Time.
    """
    conf = read_config_ini('ARCH Config')['cycle']

    if not os.path.exists(LOG_BAK_PATH):
        os.system('mkdir -p %s' % LOG_BAK_PATH)
    # FWLOG_DEBUG(conf)
    if conf == 'every_day':
        res = backup_every_day()
    elif conf == 'every_week':
        res = backup_every_week()
    elif conf == 'every_month':
        res = backup_every_month()
    else:
        res = backup_every_week()
        FWLOG_DEBUG('log_backup_lib:invalid conf')

    record_log_backup_lib()




if __name__ == '__main__':
    record_log_backup()


    #test
    # record_log_backup_lib()
    # FWLOG_DEBUG(backup_every_day())
    # FWLOG_DEBUG(backup_every_week())
    # FWLOG_DEBUG(backup_every_month())
    pass
