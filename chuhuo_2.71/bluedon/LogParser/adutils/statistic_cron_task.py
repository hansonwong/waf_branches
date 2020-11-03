#!/usr/bin/env python
# coding=utf-8

import os
import sys

os.chdir('/usr/local/bluedon/LogParser')
if '/usr/local/bluedon/LogParser' not in sys.path:
    sys.path.append('/usr/local/bluedon/LogParser')

import time
from adutils.config1 import fetchall_sql as fcal3307
from adutils.config1 import execute_sql as exec3307
from adutils.config1 import executemany_sql as exec_many3307
from adutils.audit_logger import rLog_dbg, rLog_err

reload(sys)
sys.setdefaultencoding('utf-8')

LOGNAME = 'statistic_cron_task'

LOG_DBG = lambda x: rLog_dbg(LOGNAME, x)
LOG_ERR = lambda x: rLog_err(LOGNAME, x)

TBNAME = 'm_tb_statistics_audit'
TBNAME_HALFHOUR = 'm_tb_statistics_audit_halfhour'
TBNAME_HOUR = 'm_tb_statistics_audit_hour'
TBNAME_DATE = 'm_tb_statistics_audit_date'

TB_TYPE = {'halfhour': TBNAME_HALFHOUR,
           'hour': TBNAME_HOUR,
           'date': TBNAME_DATE}

TB_ORGIN = {'halfhour': TBNAME,
            'hour': TBNAME_HALFHOUR,
            'date': TBNAME_HOUR}

SUFFIX_DATE = lambda x=None : time.strftime("%Y%m%d", time.localtime(int(x)))

TB_DATE = lambda tb, d=None : '_'.join([tb, SUFFIX_DATE(d)])


def is_another_hour():
    time_min = time.localtime().tm_min
    return time_min >= 1 and time_min <= 15


def is_another_day():
    time_now = time.localtime()
    time_min = time_now.tm_min
    time_hour = time_now.tm_hour

    return time_hour == 0 and time_min >= 1 and time_min <= 15


def last_hour_timestamp(half=False):
    delta = 1800 if half is True else 3600
    a = int(time.time())
    e = a - ( a % delta )
    s = e - delta
    return s, e


def last_day_timestamp():
    a = time.localtime()
    e = time.mktime(a) - a.tm_hour * 3600 - a.tm_min * 60 - a.tm_sec
    s = e - 86400
    return s, e


def create_ifnot_exists(tb, tb_date):
    sql = "CREATE TABLE IF NOT EXISTS {tb_date} LIKE {tb};"
    exec3307(sql.format(tb_date=tb_date, tb=tb))


def statistics_record_cron(typ):
    if typ not in TB_TYPE.keys():
        print 'statistics_record_cron: INVALID TYPE %s' % typ

    if typ == 'halfhour':
        s, e = last_hour_timestamp(half=True)
    elif typ == 'hour':
        s, e = last_hour_timestamp(half=False)
    elif typ == 'date':
        s, e = last_day_timestamp()
    # get table name with date
    tb_date = TB_DATE(TB_TYPE[typ], s)

    # create table if not exists
    create_ifnot_exists(TB_TYPE[typ], tb_date)

    # delete same time record in database
    sql = "DELETE FROM {tb} WHERE iTime >={st} AND \
        iTime <={et};".format(tb=tb_date, st=s, et=e)
    exec3307(sql)

    # get new record from origin statistics table
    tb = TB_DATE(TB_ORGIN[typ], s)
    sql = """SELECT
                sAppType, sStatisticsType, sIP, sUsername, sDept, sDeviceID, \
                    sKeyword, iOverseas, SUM(iCount) AS iCount
             FROM
                {tb}
             WHERE
                iTime >= {st}
                AND iTime <= {et}
             GROUP BY
                sAppType, sStatisticsType, sIP, sUsername, sDept, sDeviceID, \
                    sKeyword, iOverseas;
          """.format(tb=tb, st=s, et=e)

    print sql
    keys = None
    values = list()
    # i_sql = "INSERT INTO {tb} (iTime, {k}) VALUES({t}, {v})"
    i_sql = "INSERT INTO {tb} (iTime, {k}) VALUES(%s, %s, %s, %s, %s, %s, %s, \
        %s, %s, %s)"
    for res in fcal3307(sql):
        # exec3307(i_sql.format(tb=tb_date, k=','.join(res.keys()), t=s,
        #              v=','.join(['"{}"'.format(v) for v in res.values()])))
        # print(i_sql.format(tb=tb_date, k=','.join(res.keys()), t=s,
        #              v=','.join(['"{}"'.format(v) for v in res.values()])))

        # try to use execute many
        if keys is None: keys = ','.join(res.keys())
        values.append(tuple([s] + ['{}'.format(v) for v in res.values()]))


    # half hour insert
    exec_many3307(i_sql.format(tb=tb_date, k=keys), values)

def check_service():
    SERVICE_PATH = '/usr/lib/systemd/system'
    LOCAL_SERVICE_PATH = '/usr/local/bluedon/conf/systemctl'
    service_file = 'bdad_statistic_cron_task.service'
    timer_file = 'bdad_statistic_cron_task.timer'
    pass
    SYSTEM_PATH = lambda x : os.path.join(SERVICE_PATH, x)
    LOCAL_PATH = lambda x : os.path.join(LOCAL_SERVICE_PATH, x)
    # check service file
    if not os.path.exists(SYSTEM_PATH(service_file)):
        try:
            # copy service file from local path to system path
            os.system('/usr/bin/cp %s %s' % (LOCAL_PATH(service_file),
                                             SYSTEM_PATH(service_file)))
        except OSError:
            LOG_ERR('%s does not exists' % LOCAL_PATH(service_file))
    else:
        LOG_DBG('%s already exists' % LOCAL_PATH(service_file))

    if not os.path.exists(SYSTEM_PATH(timer_file)):
        try:
            # copy service file from local path to system path
            os.system('/usr/bin/cp %s %s' % (LOCAL_PATH(timer_file),
                                             SYSTEM_PATH(timer_file)))
        except OSError:
            LOG_ERR('%s does not exists' % LOCAL_PATH(timer_file))
    else:
        LOG_DBG('%s already exists' % LOCAL_PATH(timer_file))

    # reset service status
    os.system('systemctl stop bdad_statistic_cron_task.timer')
    os.system('systemctl daemon-reload')
    os.system('systemctl start bdad_statistic_cron_task.timer')


if __name__ == '__main__':
    print time.ctime()
    LOG_DBG(time.ctime())
    statistics_record_cron('halfhour')
    if is_another_hour():
        statistics_record_cron('hour')
    if is_another_day():
        statistics_record_cron('date')
    pass
