#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, MySQLdb
from config import config
from logging import getLogger
from common import logger_init

if __name__ == '__main__':
    os.chdir('/usr/local/bluedon/bdwafd/')
    logger_init('ntpdate', config['logger']['ntpdate']['path'], config['logger']['ntpdate']['level'])

    conn = MySQLdb.connect(**config['db'])
    cursor = conn.cursor()
    cursor.execute('select * from t_ntp_setting')
    for data in cursor.fetchall():
        if data[2]:
            fp = os.popen('/usr/sbin/ntpdate %s' % data[1])
            lines = fp.readlines()
            for line in lines:
                buff = line[:-1].split("]: ")
                getLogger('main').info(buff[1])
            break
    cursor.close()
    conn.close()

