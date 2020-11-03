#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import MySQLdb
import threading
import pygeoip
from logging import getLogger
from config import config
from db import conn_scope,get_config
from common import del_iptables_rule, insert_iptables_rule

dports = ()
# bridgeinf = []
weblogfile = '/var/log/weboutlog'
rexptime = re.compile(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})")
rexpaction = re.compile(r'weboutlog:(\S+)')
rexpsrcip = re.compile(r'SRC=(\S+)')
rexpsport = re.compile(r'SPT=(\d+)')
rexpdstip = re.compile(r'DST=(\S+)')
rexpdport = re.compile(r'DPT=(\d+)')


class parserweblog(threading.Thread):
    event = threading.Event()

    def __init__(self, ):
        super(parserweblog, self).__init__(name=self.__class__.__name__)
        self.where = 0
        self.gic = pygeoip.GeoIP('data/GeoLiteCity.dat')

    def start(self):
        getLogger('audit').debug(self.__class__.__name__ + ' starting...')
        super(parserweblog, self).start()
        getLogger('audit').info(self.__class__.__name__ + ' started.')

    def stop(self):
        getLogger('audit').debug(self.__class__.__name__ + ' Exiting...')
        self.event.set()
        self.join()
        getLogger('audit').info(self.__class__.__name__ + ' Exited.')

    def proc(self):
        if(not os.path.isfile(weblogfile)):
            return 0

        with conn_scope(**config['dbacc']) as (conn, cursor):
            fp = open(weblogfile, 'r')
            st_size = os.stat(weblogfile)[6]
            if(self.where == 0 or self.where > st_size):
                self.where = st_size
            fp.seek(self.where)

            count = 0
            cursor.execute('SELECT MAX(`number`) FROM `t_weboutlogs`')
            for data in cursor.fetchall():
                count = data[0]

            line = fp.readline()
            while(line):
                try:
                    number = 0
                    concode, regcode, citystr = 'CN', 'unknown', 'unknown'
                    logtime, srcip, dstip, sport, dport, action = '', '', '', '', '', '0'
                    match = rexptime.search(line)
                    if(match):
                        logtime = match.group(1)
                        logsql = "insert into t_weboutlogs(dt, sip, dip, CountryCode, \
                                  RegionCode, City, sport, dport, action, number) values"
                    match = rexpaction.search(line)
                    if(match):
                        action = match.group(1)
                    match = rexpsrcip.search(line)
                    if(match):
                        srcip = match.group(1)
                    match = rexpsport.search(line)
                    if(match):
                        sport = match.group(1)
                    match = rexpdstip.search(line)
                    if(match):
                        dstip = match.group(1)
                    match = rexpdport.search(line)
                    if(match):
                        dport = match.group(1)
                    if not srcip or not dstip or not dport:
                        self.where = fp.tell()
                        line = fp.readline()
                        continue

                    getaddrs = self.gic.record_by_addr(dstip)
                    if getaddrs:
                        concode = getaddrs['country_code']
                        regcode = getaddrs['region_code']
                        citystr = getaddrs['city']
                    if action == '1':
                        count += 1
                        number = count

                    logsql += "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%d');" % \
                        (logtime, srcip, dstip,
                         concode, regcode, citystr, sport, dport, action, number)
                    cursor.execute(logsql)
                    conn.commit()
                    self.where = fp.tell()
                    line = fp.readline()
                except Exception, e:
                    self.where = fp.tell()
                    line = fp.readline()
                    getLogger('audit').exception(e)
            fp.close()
        return 2

    def run(self):
        while(1):
            try:
                st = 0
                while st < 5:
                    if self.event.isSet():
                        return
                    time.sleep(1)
                    st = st + 1
                self.proc()
            except Exception, e:
                getLogger('audit').exception(e)


def weboutset(cursor):
    cursor.execute('select `sBindDevices`, `bridgeType` from '
                    'db_firewall.m_tbbridgedevice where iStatus=1')
    bridgeinf = []
    for data in cursor.fetchall():
        buff = data[0].split(",")
        iflen = len(buff)
        for i in range(iflen / 2, iflen):
            bridgeinf.append((buff[i], data[1]))

    os.system('iptables -F WEB-OUT')
    cursor.execute('select is_use, sip, dip, dport from t_webserver_outbound')
    for data in cursor.fetchall():
        # if not data[0]:
            # continue
        iptstr = "iptables -A WEB-OUT -p tcp -s %s -d %s --dport %s " % (
            data[1], data[2], str(data[3]))
        if data[0]:
            iptstr1 = iptstr + \
                "-m limit --limit 2/min --limit-burst 2 -j LOG --log-prefix='weboutlog:1 '"
            iptstr2 = iptstr + "-j DROP"  # 黑名单
            os.system(iptstr1)
            os.system(iptstr2)

    for infname, inftype in bridgeinf:
        iptstr = ''
        if inftype == 'tproxy':
            iptstr = 'iptables -t mangle -I PREROUTING -p tcp -i %s' % infname
        elif inftype == 'bridge':
            iptstr = 'iptables -A WEB-OUT -p tcp -m physdev --physdev-in %s' % infname
        if not iptstr:
            return
        iptstr = iptstr + ' -m multiport --dport ' + ','.join(dports)
        iptstr += " -m limit --limit 1/sec --limit-burst 1 -j LOG --log-prefix='weboutlog:0 '"
        os.system(iptstr)

    # os.system('iptables -A WEB-OUT -j ACCEPT')

if __name__ == '__main__':
    conn = MySQLdb.connect(**config['db'])
    cursor = conn.cursor()
    data2 = get_config("OutLinkSet")
    del_iptables_rule('mangle', 'PREROUTING', ('weboutlog:0',))
    if data2["enable"]:
        dports = data2["dports"].split("|")
        weboutset(cursor)
    else:
        os.system('iptables -F WEB-OUT')
        # os.system('iptables -A WEB-OUT -j ACCEPT')
    cursor.close()
    conn.close()
