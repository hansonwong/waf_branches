#!/usr/bin/env python
# -*- coding: utf-8 -*-

# created by szl 2014-03-14

""" Bluedon Web Application Firewall Audit Log Collector Daemon

Usage:
  bdauditd.py [-hv]
  bdauditd.py [-d DIR] -s (start|stop|restart)

Arguments:
  DIR app working directory

Options:
  -h --help                  show this help message and exit
  -v --version               show version and exit
  -d NAME                    set the working directory
"""

import os, time, MySQLdb
from szlmod import taskszl
import stat, time, threading
import os, logging
from config import config

def FileParser():
    ccruleids = []
    fileseat = {'std_dir': 'NULL', 'sdate': 'NULL', 'stime': 'NULL', 'edate': 'NULL', 'etime': 'NULL', 'logid': 0}
    conn = MySQLdb.connect(**config['dbacc'])
    cursor = conn.cursor()
    cursor.execute('select * from t_fileseat')
    for data in cursor.fetchall():
        (fileseat['logid'], fileseat['std_dir'], fileseat['sdate'], fileseat['stime']) = (data[0], data[1].encode('ascii'), data[2].encode('ascii'), data[3].encode('ascii'))
    
    cursor.execute("select realid from waf.t_rules where type='cc'")
    for data in cursor.fetchall():
        ccruleids.append(data[0])
    cursor.close()
    conn.close()

    fileseat['sdate'] = "20141204"
    fileseat['stime'] = "20141204-0800"
    while 1:
        try:
            fileseat['etime'] = time.strftime("%Y%m%d-%H%M", time.localtime())
            fileseat['edate'] = fileseat['etime'][:8]
            if fileseat['stime'] > fileseat['etime']:
                fileseat['sdate'] = fileseat['edate']
                fileseat['stime'] = fileseat['etime']

            for name1 in sorted(os.listdir(fileseat['std_dir'])):
                if (name1 > fileseat['edate']) or (name1 < fileseat['sdate']):
                    continue

                fileseat['sdate'] = name1
                dirname = os.path.join(fileseat['std_dir'], name1)
                for name2 in sorted(os.listdir(dirname)):
                    if(name2 <= fileseat['stime']) or (name2 >= fileseat['etime']):
                        continue
                    taskszl(os.path.join(dirname, name2), ccruleids)
                    fileseat['stime'] = name2
        except Exception, e:
            print e
        break
 
if __name__ == '__main__':
    FileParser()

