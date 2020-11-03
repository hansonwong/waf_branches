#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, MySQLdb
from config import config
from db import conn_scope

snmpdata    = ()
rexpsnmp    = re.compile(r'/usr/local/bluedon/snmp/sbin/snmpd')
cfgfile     = '/usr/local/bluedon/snmp/share/snmp/snmpd.conf'
cfgfile_bak = '/usr/local/bluedon/snmp/share/snmp/default.conf'

def getsnmp():
    global snmpdata
    with conn_scope(**config['db']) as (conn, cursor):
        cursor.execute('select * from t_snmp_up')
        for snmpdata in cursor.fetchall():
            break

def configfile():
    flag = 0
    pfp = os.popen('ps ax | grep snmpd')
    lines = pfp.readlines()
    for line in lines:
        match = rexpsnmp.search(line)
        if match:
            flag += 1
    if flag:
        os.system('killall snmpd')

    if not snmpdata[1]:
        return
    infp  = open(cfgfile_bak, 'r')
    lines = infp.readlines()
    infp.close()
    outfp = open(cfgfile, 'w')

    count = 3
    outfp.write('#sec.name  source  community\n')
    while count < 14:
        if snmpdata[count]:
            line = 'com2sec  mynetwork  %s %s\n' % (snmpdata[count], snmpdata[count+2])
            outfp.write(line)
        count += 4
    outfp.write('#sec.model  sec.name\n')
    outfp.write('group  myrogroup  v2c  mynetwork\n\n')
    outfp.write('#incl/excl  subtree  mask\n')
    outfp.write('view  all  included  .1\n\n')
    outfp.write('#context  sec.model  sec.level  match  read  write  notif\n')
    outfp.write('access  myrogroup  ""  any  noauth  exact  all  none  none\n\n')

    count = 3
    while count < 14:
        if snmpdata[count]:
            line = 'trap2sink %s:%s %s\n' % (snmpdata[count], snmpdata[count+1], snmpdata[count+2])
            outfp.write(line)
        count += 4

    for line in lines:
        outfp.write(line)
    outfp.close()
    os.system('/usr/local/bluedon/snmp/sbin/snmpd')

if __name__ == '__main__':
    getsnmp()
    configfile()

