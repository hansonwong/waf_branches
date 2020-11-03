#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import re
import MySQLdb
import pygeoip
import threading
from logging import getLogger
from config import config
from db import conn_scope

geoipdir = 'data/GeoLiteCity.dat'
ddoslogfile = '/var/log/ddoslog'
backipfile = '/proc/net/xt_recent/DROPLINK'
iptstr = 'ipset add backlist '
rexpip = re.compile(r'^src=([.0-9]+)')
rexplogtime = re.compile(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})")
rexplogtype = re.compile(r'(Probable ddos:\S+flood)')
rexplogsrcip = re.compile(r'SRC=(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})')
rexplogdstip = re.compile(r'DST=(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})')
rexplogdpt = re.compile(r'DPT=(\d+)')
rexplogproto = re.compile(r'PROTO=(\S+)')


class fileparser(threading.Thread):
    event = threading.Event()

    def __init__(self, ):
        super(fileparser, self).__init__(name=self.__class__.__name__)
        self.ipflag = 0
        self.ddosflag = 0

    def start(self):
        getLogger('audit').debug(self.__class__.__name__ + ' starting...')
        super(fileparser, self).start()
        getLogger('audit').info(self.__class__.__name__ + ' started.')

    def stop(self):
        getLogger('audit').debug(self.__class__.__name__ + ' Exiting...')
        self.event.set()
        self.join()
        getLogger('audit').info(self.__class__.__name__ + ' Exited.')

    def proc(self):
        iplen = 0
        if not os.path.isfile(backipfile):
            return 1
        with open(backipfile, 'r') as fr:
            lines = fr.readlines()
            for line in lines:
                getLogger('audit').info(' hello %s' % line)
                iplen += 1
                match = rexpip.search(line)
                if(match.group(1) == '127.0.0.1'):
                    continue
                iptstr1 = iptstr + match.group(1)
                os.system(iptstr1)

        if iplen:
            os.system('iptables -F DROPLINK')
            os.system('iptables -A DROPLINK -m recent --set --name DROPLINK')
            os.system('iptables -A DROPLINK -j DROP')


    def run(self):
        while(1):
            try:
                if self.event.isSet():
                    break
                time.sleep(1)
                self.proc()
            except Exception, e:
                getLogger('audit').exception(e)


class DuDDOSTask(threading.Thread):
    event = threading.Event()

    def __init__(self, ):
        super(DuDDOSTask, self).__init__(name=self.__class__.__name__)
        self.where = 0

    def start(self):
        getLogger('audit').debug(self.__class__.__name__ + ' starting...')
        super(DuDDOSTask, self).start()
        getLogger('audit').info(self.__class__.__name__ + ' started.')

    def stop(self):
        getLogger('audit').debug(self.__class__.__name__ + ' Exiting...')
        self.event.set()
        self.join()
        getLogger('audit').info(self.__class__.__name__ + ' Exited.')

    def proc(self):
        if(not os.path.isfile(ddoslogfile)):
            return 2

        with conn_scope(**config['dbacc']) as (conn, cursor):
            fp = open(ddoslogfile, 'r')
            st_size = os.stat(ddoslogfile)[6]
            if(self.where == 0 or self.where > st_size):
                self.where = st_size
            fp.seek(self.where)

            line = fp.readline()
            while(line):
                try:
                    match = rexplogtime.search(line)
                    if(match):
                        logtime = int(time.mktime(time.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')))
                        sqlstr  = "insert into t_ddoslogs(`logtime`, `srcip`, `CountryCode`, `RegionCode`,\
                                   `City`, `dstip`, `dstport`, `protocol`, `desc`) values"
                    match = rexplogsrcip.search(line)
                    if(match):
                        srcip = match.group(1)
                        gic = pygeoip.GeoIP(geoipdir)
                        addrs = gic.record_by_addr(srcip)
                    if(not addrs):
                        addrs = {}
                        addrs['country_code'] = 'CN'
                        addrs['region_code'] = 'unknown'
                        addrs['city'] = 'unknown'
                    match = rexplogdstip.search(line)
                    if(match):
                        dstip = match.group(1)
                    match = rexplogdpt.search(line)
                    if(match):
                        dstport = match.group(1)
                    match = rexplogproto.search(line)
                    if(match):
                        protocol = match.group(1)
                        if protocol == 'ICMP':
                            dstport = ''
                    match = rexplogtype.search(line)
                    if(match):
                        desc = match.group(1)
                    else:
                        desc = 'Probable ddos:all-flood'

                    if not (srcip and dstip and protocol):
                        self.where = fp.tell()
                        line = fp.readline()
                        continue
                    if not dstport and protocol != 'ICMP':
                        self.where = fp.tell()
                        line = fp.readline()
                        continue

                    sqlstr += "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (logtime, srcip,
                              addrs['country_code'], addrs['region_code'], addrs['city'], dstip, dstport, protocol, desc)
                    cursor.execute(sqlstr)
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
        getLogger('audit').info('DuDDOSTask run')
        while(1):
            try:
                if self.event.isSet():
                    break
                time.sleep(1)
                self.proc()
            except Exception, e:
                getLogger('audit').exception(e)

if __name__ == '__main__':
    pass
