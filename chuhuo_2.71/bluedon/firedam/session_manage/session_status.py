#!/usr/bin/env python
# coding=utf-8


"""
会话管理--> 会话状态
2016-8-26:
    1、新增判断文件是否为空，减少IO压力
"""


import os
import commands
import time
from logging import getLogger

from utils.logger_init import logger_init
from reportlog.log_split_session import MysqlGetTblogSession


_PATH = "/var/log/suricata/session.log"
LOG_NAME = 'SESSION_STATUS'
LOG_PATH = '/usr/local/bluedon/log/session_status.log'

logger_init(LOG_NAME, LOG_PATH)


def proce_session_log(event=0):
    """ 日志入库 """

    ips_cmd = 'ps -ef | grep /home/suricata/bin/suricata | grep -v sh | grep -v grep | awk "{print $2}"'
    flag = True
    filetime = int(os.stat(_PATH).st_mtime)
    oday = time.localtime().tm_wday
    count = 0
    session = MysqlGetTblogSession()

    while not event.isSet():
        # 判断ips进程是否存在
        # ips_fork = commands.getoutput(ips_cmd)
        # if not ips_fork:
        #     time.sleep(5)
        #     continue

        nday = time.localtime().tm_wday
        if not os.path.getsize(_PATH) and oday == nday and count != 0:
            time.sleep(5)
            continue
        else:
            count = 0
            oday = nday

        count = 1

        if flag:
            session.session_status()
            flag = False
            time.sleep(5)
            continue

        mfiletime = int(os.stat(_PATH).st_mtime)
        if filetime == mfiletime:
            time.sleep(5)
            continue
        filetime = mfiletime
        session.session_status()
        time.sleep(5)


def stop_session(smark):
    """ 断开连接 """

    cmd = '/home/suricata/client/session_reset {0} &'.format(smark)
    os.system(cmd)
    getLogger(LOG_NAME).debug(cmd)


if __name__ == '__main__':
    proce_session_log(0)
