#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, MySQLdb
from config import config

hadata     = ()
def gethasets(cursor):
    global hadata
    global infip
    cursor.execute('select interface,ip from `t_ha_setting`')
    for hadata in cursor.fetchall():
        break

def setbridge(cursor):
    selsql = "select `nics` from `t_bridge`"
    cursor.execute(selsql)
    for data in cursor.fetchall():
        buff = data[0].split(",")
        iflen = len(buff)
        for i in range(1,iflen):
            cmdstr = '/sbin/ifconfig %s down' % buff[i]
            os.system(cmdstr)

if __name__ == '__main__':
    conn = MySQLdb.connect(**config['db'])
    cursor = conn.cursor()

    gethasets(cursor)
    if hadata[0]:
        os.system('/sbin/ifconfig %s:1 down' % hadata[0])

    cursor.execute("update `t_ha_setting` set `state`='backup'")
    conn.commit()
    cursor.close()
    conn.close()
    
