#!/usr/bin/env python
#-*-coding:utf-8-*-

import os
# import MySQLdb
# from config import config
from db import BridgeMulIP, Session, WafNicSet
import commands
import re

"""table={}
table['t_bridge_mulip']='''CREATE TABLE IF NOT EXISTS `t_bridge_mulip`(
     `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
     `nic` varchar(45) COLLATE utf8_unicode_ci NOT NULL,
     `ip`  varchar(45) COLLATE utf8_unicode_ci NOT NULL,
     `mask`  varchar(25) COLLATE utf8_unicode_ci NOT NULL,
     PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1;'''

def createtable():
    global table
    conn = MySQLdb.connect(db=config['db']['db'], user=config['db']['user'], passwd=config['db']['passwd'], charset='utf8')
    cursor = conn.cursor()
    for (k,v) in table.items():
        print v
        cursor.execute(v)
    conn.commit()
    cursor.close()
    conn.close()"""


def get_t_bridge_mulip_info():  # data from database
    session = Session()
    info = session.query(BridgeMulIP)
    allinfo = []
    for data in info:
        bridgeinfo = {}
        bridgeinfo['nic'] = data.nic
        bridgeinfo['ip'] = data.ip
        bridgeinfo['mask'] = data.mask
        allinfo.append(bridgeinfo)
    return allinfo


def config_t_nicset_info():
    session = Session()
    infos = session.query(WafNicSet)
    data = []
    for info in infos:
        if "br" in info.nic:
            ip = info.ip
            bridgename = info.nic
            netmask = info.mask
            os.system('ifconfig %s %s netmask %s up' % (bridgename, ip, netmask))


def ConfiguredIP():
    i = 0
    alladdedip = []
    while 1:
        br = 'bridge' + str(i)
        info = os.popen('ip addr show %s' % br).read()
        if i != 0:
            if not info:
                return alladdedip
        fp = open('ip_show.txt', 'w')
        print >>fp, info
        fp.close()
        match = re.compile(r'\s*?inet\s*?(.+?)\s*?scope global')
        fr = open('ip_show.txt', 'r')
        addedip = []
        for line in fr:
            if "scope global" in line and 'brd' not in line:
                line = match.match(line).groups()
                line = line[0].strip(' ').split('/')[0] + " " + br
                addedip.append(line)
        alladdedip.append(','.join(addedip))
        i = i + 1
        fr.close()


def addBridgeIP():
    bridgeinfo = get_t_bridge_mulip_info()
    addedip = ConfiguredIP()
    addedip = ','.join(addedip)
    for i in range(len(bridgeinfo)):
        ip = bridgeinfo[i]['ip']
        dev = bridgeinfo[i]['nic']
        if ip not in addedip:
            configstr = 'ip addr add %s/24 dev %s' % (ip, dev)
            (status, output) = commands.getstatusoutput(configstr)


def delBridgeIP():
    bridgeinfo = get_t_bridge_mulip_info()
    addedip = ConfiguredIP()
    addedip = ','.join(addedip).split(',')
    databaseip = []
    for i in range(len(bridgeinfo)):
        databaseip.append(bridgeinfo[i]['ip'])
    databaseip = ','.join(databaseip)

    for i in range(len(addedip)):
        if addedip[i]:
            ip = addedip[i].split(' ')[0]
            bridgename = addedip[i].split(' ')[1]
            if ip not in databaseip:
                delstr = 'ip addr del %s dev %s' % (ip, bridgename)
                (status, output) = commands.getstatusoutput(delstr)


if __name__ == "__main__":
    # config_t_nicset_info()
    addBridgeIP()
    delBridgeIP()
#   ConfiguredIP()
