#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import MySQLdb
from config import config
from MySQLdb import escape_string
from db import conn_scope

syslogdata = ()
cfgfile = '/usr/local/bluedon/syslog-ng/etc/syslog-ng.conf'
cfgfile_bak = '/usr/local/bluedon/syslog-ng/etc/default.conf'


def getsyslog():
    global syslogdata
    with conn_scope(**config['db']) as (conn, cursor):
        sqlstr = 'select * from t_syslog_up'
        cursor.execute(sqlstr)
        for syslogdata in cursor.fetchall():
            break


def configfile():
    cmdstr = 'cp %s %s' % (cfgfile_bak, cfgfile)
    os.system(cmdstr)
    if not syslogdata[1]:
        return

    flag = 0
    count = 2
    while count < 11:
        num = count
        count += 3
        rexpcheck = re.compile(r'^[\d]{1,3}.[\d]{1,3}.[\d]{1,3}.[\d]{1,3}$')
        match = rexpcheck.search(syslogdata[num])
        if not match:
            continue

        rexpcheck = re.compile(r'^[\d]+$')
        match = rexpcheck.search(syslogdata[num + 1])
        if not match:
            continue

        if syslogdata[num + 2] != 'tcp' and syslogdata[num + 2] != 'udp':
            continue

        flag += 1
        dst_remote = 'destination d_remote_%d {%s("%s" port(%s));};' % \
                     (flag, syslogdata[num + 2],
                      syslogdata[num], syslogdata[num + 1])
        logmod = 'log { source(s_messages); destination(d_remote_%d); };' % flag
        cmdstr1 = "echo '%s' >> %s" % (dst_remote, cfgfile)
        cmdstr2 = "echo '%s' >> %s" % (logmod, cfgfile)
        os.system(cmdstr1)
        os.system(cmdstr2)
    cmdstr = 'echo "\n" >> %s' % cfgfile
    os.system(cmdstr)

if __name__ == '__main__':
    getsyslog()
    configfile()
    os.system('killall -9 syslog-ng')
    os.system('/usr/local/bluedon/syslog-ng/sbin/syslog-ng')
