#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime as dt
import re
import subprocess
import time
from db.config1 import execute_sql as update, search_data as select


TIME_FORMAT = "%a %b %d %H:%M:%S %Y"
SQL_INSERT_LOG = 'INSERT INTO m_tblog_sys_reboot (`iUserId`, `iLoginTime`, `sIp`, `sStatus`, `sContent` ) '\
                 'VALUES ("%s","%s","%s","%s","%s");'

def shutdown_bluedon(action, data):
    """shutdown or reboot server
    Args:
        action: `reboot` or `shutdown`
        data: dict has keys  `iUserId` and `sIp`
    """

    trans_map = {'reboot': '/usr/sbin/shutdown -r now',
                 'shutdown': '/usr/sbin/shutdown -h now'}
    sql = SQL_INSERT_LOG % (data['iUserId'], int(time.time()), data['sIp'], 1, action)
    update(sql)
    # print trans_map[action]
    subprocess.call(trans_map[action], shell=True)


def analyse_reboot_log():
    """find out last reboot or shutdown time of system"""

    history = subprocess.check_output('last -x -F', shell=True)
    history = history.split('\n')
    boot_time, shut_time, is_crash = None, None, None

    for i in xrange(len(history)):
        if history[i].startswith('reboot'):
            boot_time = dt.datetime.strptime(history[i][39:63], TIME_FORMAT)
            if history[i+1].startswith('shutdown'):
                is_crash = False
                shut_time = dt.datetime.strptime(history[i+1][39:63], TIME_FORMAT)
                break
            else:
                is_crash = True
                for j in range(i+1, len(history)):
                    if history[j].find('crash') > 0:
                        login_time = dt.datetime.strptime(history[j][39:63], TIME_FORMAT)
                        match_ = re.search(r'\(([0-3]?[0-9])?\+?([0-2][0-9]):([0-5][0-9])\)', history[j])
                        days, hours, minutes = match_.group(1), match_.group(2), match_.group(3)
                        duration = dt.timedelta(days=days and int(days) or 0, hours=int(hours), minutes=int(minutes))
                        shut_time = login_time + duration
                        break
                break
    if not (boot_time and shut_time): return
    boot_time, shut_time = [int(time.mktime(i.timetuple())) for i in (boot_time, shut_time)]
    is_reboot = True if boot_time - shut_time < 30 else False
    print 'boot: {}; shut: {}; crash: {}; reboot: {}'.format(boot_time, shut_time, is_crash, is_reboot)

    sql = 'SELECT * FROM m_tblog_sys_reboot ORDER BY id DESC LIMIT 1;'
    log_data = select(sql)
    last_record_time = log_data[0]['iLoginTime'] if log_data else 0
    print 'boot: {}; record_boot: {}; reboot: {};'.format(boot_time, last_record_time, is_reboot)
    if boot_time and shut_time and boot_time - last_record_time > 30:
        if is_crash:
            update(SQL_INSERT_LOG % ('root', shut_time, 'localhost', 1, 'crash'))
            update(SQL_INSERT_LOG % ('root', boot_time, 'localhost', 1, 'boot'))
        elif is_reboot:
            update(SQL_INSERT_LOG % ('root', shut_time, 'localhost', 1, 'reboot'))
        else:
            update(SQL_INSERT_LOG % ('root', shut_time, 'localhost', 1, 'shutdown'))
            update(SQL_INSERT_LOG % ('root', boot_time, 'localhost', 1, 'boot'))


if __name__ == '__main__':
    analyse_reboot_log()
