#!/usr/bin/env python
# coding=utf-8

import os
import sys

os.chdir('/usr/local/bluedon/')
if '/usr/local/bluedon/' not in sys.path:
    sys.path.append('/usr/local/bluedon/')

import json
import time
import psutil
from db.config import fetchone_sql as fetch3306
from utils.log_logger import rLog_dbg, rLog_err
from reportlog.log_clear import log_clear_release_disk

LOGNAME = 'logclear_cron_task'

LOG_DBG = lambda x: rLog_dbg(LOGNAME, x)
LOG_ERR = lambda x: rLog_err(LOGNAME, x)


def cron_task():
    # stop service by systemctl first
    LOG_DBG('stop service at %s' % time.ctime())
    os.system('systemctl stop bdad_logclear_cron_task.timer')
    try:
        tnow = time.localtime()
        if tnow.tm_hour == 0 and tnow.tm_min <= 10:
            max_keep = update_max_keep()
            LOG_DBG('run log_clear_release_disk [clear (%s) days ago]' % max_keep)
            LOG_DBG('run log_clear_release_disk [keep=True]')
            log_clear_release_disk(keep=True)
            return

        disk_threshold = update_disk_threshold()
        disk_usage = psutil.disk_usage('/var').percent
        if disk_usage >= disk_threshold:
            LOG_DBG('run log_clear_release_disk [u(%s) >= m(%s)]' % (disk_usage, disk_threshold))
            LOG_DBG('run log_clear_release_disk [disk is full]')
            LOG_DBG('run log_clear_release_disk [x_days_ago = 0 keep=False]')
            log_clear_release_disk(x_days_ago=0, keep=False)
            return
        else:
            LOG_DBG('run log_clear_release_disk [disk is not full (%s)%%]' % disk_usage)


    finally:

        # restart service
        LOG_DBG('statr service at %s' % time.ctime())
        os.system('systemctl start bdad_logclear_cron_task.timer')


def update_disk_threshold():
    disk_threshold = 90
    try:
        res = fetch3306('SELECT sValue FROM m_tbconfig WHERE sName="UseFullRate";')
        thresholds = json.loads(res['sValue'])
        disk_threshold = int(thresholds.get('iDisk', 90))
    except Exception as e:
        LOG_ERR('ERROR updating disk_threshold: %s' % e)

    LOG_DBG('disk_threshold = %s' % disk_threshold)
    return disk_threshold

def update_max_keep():
    max_keep = 30
    try:
        ret = fetch3306("SELECT sValue FROM m_tbconfig WHERE sName='logConfig';")
        js_ret = json.loads(ret['sValue'])
        max_keep = int(js_ret['memoryTime']) * 30
    except Exception as e:
        LOG_ERR('ERROR getting max_keep: %s' % e)

    LOG_DBG('max_keep = %s' % max_keep)
    return max_keep

def check_service():
    SERVICE_PATH = '/usr/lib/systemd/system'
    LOCAL_SERVICE_PATH = '/usr/local/bluedon/conf/systemctl'
    service_file = 'bdad_logclear_cron_task.service'
    timer_file = 'bdad_logclear_cron_task.timer'
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
    os.system('systemctl stop bdad_logclear_cron_task.timer')
    os.system('systemctl daemon-reload')
    os.system('systemctl start bdad_logclear_cron_task.timer')


if __name__ == '__main__':
    cron_task()
