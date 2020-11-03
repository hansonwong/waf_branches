#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, MySQLdb
from config import config

hadata   = ()
infmask  = ''
def gethasets(cursor):
    global hadata
    global infmask
    cursor.execute('select interface,ip from `t_ha_setting`')
    for hadata in cursor.fetchall():
        break

    cursor.execute("select `mask` from `t_nicset` where nic='%s'" % hadata[0])
    for data in cursor.fetchall():
        infmask = data[0]
        break

def setbridge(cursor):
    selsql = "select `nics` from `t_bridge`"
    cursor.execute(selsql)
    for data in cursor.fetchall():
        buff = data[0].split(",")
        iflen = len(buff)
        for i in range(1,iflen):
            cmdstr = '/sbin/ifconfig %s up' % buff[i]
            os.system(cmdstr)

if __name__ == '__main__':
    conn = MySQLdb.connect(**config['db'])
    cursor = conn.cursor()

    gethasets(cursor)
    if hadata[0]:
        cmdstr = '/sbin/ifconfig %s:1 %s netmask %s up' % (hadata[0], hadata[1], infmask)
        os.system(cmdstr)
    #else:
    #    cmdstr = '/sbin/ifconfig %s:1 %s up' % (hadata[0], hadata[1])
    #    os.system(cmdstr)
    #    setbridge(cursor)

    cursor.execute("update `t_ha_setting` set `state`='master'")
    conn.commit()
    cursor.close()
    conn.close()

