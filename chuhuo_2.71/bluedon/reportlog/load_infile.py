#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
Usage:
    mysql_get_tblog_firewall.py -h --help
    mysql_get_tblog_firewall.py [-t <time>] [--loglevel=<log_level>]
    mysql_get_tblog_firewall.py --reset

Options:
    -h,--help                  show help
    --loglevel=<log_level>  set debug level
    -t <time>               set time interval
    --reset                 re-import all data, BEFORE using this command, please CONFIRN that table m_tblog_ips has been CLEAN UP!!

"""

import re
import MySQLdb
import MySQLdb.cursors
import time
import os
import sys
import threading
import json
import logging
import commands
os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')
from os.path import getsize
from utils.log_logger import rLog
from logging import getLogger
from reportlog.log_size_record import log_size_record
from reportlog.mysql_get_tblog import already_running,MysqlGetTblog
from db.config1 import execute_sql,executemany_sql

_path = "/var/log/fw/iptables-ng.log-20160523"

#ip_reg = r"(\d{1,3}\.){3}\d{1,3}"
sip_reg = r"(?<=\bSRC=).*?\s\b"
dip_reg = r"(?<=\bDST=).*?\s\b"
sport_reg = r"(?<=\bSPT=).*?\s\b"
dport_reg = r"(?<=\bDPT=).*?\s\b"
proto_reg = r"(?<=\bPROTO=).*?\s\b"
in_reg = r"(?<=\bIN=).*?\s\b"
out_reg = r"(?<=\bOUT=).*?\s\b"
act_reg = r"(?<=\bipt_log=).*?\s\b"
def timestamp(m,d,tm):
     year = time.localtime()[0]
     t = str(year) + ' ' + m + ' ' + d + ' ' + tm
     ts = time.strptime(t,'%Y %b %d %H:%M:%S')
     s = time.mktime(ts)
     date = time.strftime('%Y%m%d',ts)
     return int(s),date



class MysqlGetTblogFirewall(MysqlGetTblog):

    event = threading.Event()

    def __init__(self,path = _path):
        super(MysqlGetTblogFirewall,self).__init__()
        #self.logger = create_logger("log",logging.DEBUG)
        self.log_record = log_size_record()
        self.path = path
        self.current_date = ''
        self.tb = ''
        try:
#            args = docopt(__doc__)
#
#            if not args['-t'] == None:
#                self.time_interval = int(args['-t'])
#            else:
            self.time_interval = 0.001
#
#            if not args['--loglevel'] == None:
#                self.level = args['--loglevel']
#            else:
#                self.level = "DEBUG"
#
#            if args['--reset'] == True:
#                #can be instead of removing the log_size_record file
#                self.log_record.set_record("ptables-ng_log",0)

            #connect to database
#            self.logger = create_logger("log",self.level)
            self.tb_name = "m_tblog_firewall"

            #self.rc_time = re.compile(time_reg)
            self.rc_sip = re.compile(sip_reg)
            self.rc_dip = re.compile(dip_reg)
            self.rc_sport = re.compile(sport_reg)
            self.rc_dport = re.compile(dport_reg)
            self.rc_proto = re.compile(proto_reg)
            self.rc_in = re.compile(in_reg)
            self.rc_out = re.compile(out_reg)
            self.rc_act = re.compile(act_reg)

#            self.logger.debug("start...")
        except Exception as e:
#            self.logger.debug(e)
            print e

    def init_db(self):
        try:
            pass
        except Exception as e:
#            self.logger.debug(e)
            print e

    def log_when_exit(self,size):
        self.log_record.set_record("iptables-ng_log",size)

    def iptables_ng_log(self):
        if not os.path.exists(self.path):
            getLogger('log_daemon').debug('File %s is NOT EXISTS!!!' % self.path)
            return
        log_file = open(self.path,"r")
        try:
            #imported_size = self.log_record.get_record()["iptables-ng_log"]
            imported_size = 0
            fsize = os.path.getsize(self.path) if os.path.exists(self.path) else 0

            count = 0
            self.logger_debug("Firewall:iptables-ng_log")
            self.logger_debug("Firewall:%s" % imported_size)
            self.logger_debug("Firewall:%s" % fsize)

            if imported_size > fsize:
                self.log_record.set_record("iptables-ng_log",0)
                return

            #log_file.seek(imported_size,0)
            log_file.seek(0,0)
            where = log_file.tell()
            done  = False
            args = []
            mysql_insert_cmd = "insert into " + self.tb + "(iTime,sInputPort,sOutPort,sSourceAddr,sSourcePort,sProtocol,sTargetAddr,sTargetPort,sAction)" +" values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            while not done:
               l = log_file.readline()
               if l == '':
                   done = True
                   continue

               ls = l.split()


               if len(ls) < 21:
                   continue
               #optimize
               res = {i.split('=')[0]:i.split('=')[1] for i in ls if not len(i.split('=')) < 2}
               act = res['ipt_log']
               inp = res['IN']
               out = res['OUT']
               sip = res['SRC']
               dip = res['DST']
               proto = res['PROTO']
               spt = res['SPT'] if res.has_key('SPT') else ''
               dpt = res['DPT'] if res.has_key('DPT') else ''

               order = ['time','IN','OUT','SRC','SPT','PROTO','DST','DPT','ipt_log']

               t,date = timestamp(ls[0],ls[1],ls[2])
               res['time'] = t
               if self.current_date != date:
                   self.current_date = date
                   self.tb = self.tb_name + '_' + date
                   executemany_sql(mysql_insert_cmd,args)
                   args = []
                   sql = """CREATE TABLE IF NOT EXISTS `%s` (
                     `id` bigint(20) NOT NULL AUTO_INCREMENT,
                     `iTime` int(11) NOT NULL COMMENT '时间',
                     `sInputPort` varchar(128) DEFAULT NULL COMMENT '入网口',
                     `sOutPort` varchar(128) DEFAULT NULL COMMENT '出网口',
                     `sSourceAddr` varchar(64) NOT NULL COMMENT '源地址',
                     `sSourcePort` varchar(32) DEFAULT NULL COMMENT '源端口',
                     `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
                     `sTargetAddr` varchar(64) NOT NULL COMMENT '目标地址',
                     `sTargetPort` varchar(32) DEFAULT NULL COMMENT '目标端口',
                     `sAction` varchar(32) NOT NULL COMMENT '动作',
                     PRIMARY KEY (`id`),
                     KEY `I_TimeSipDip` (`iTime`,`sSourceAddr`,`sTargetAddr`)
                     ) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='防火墙日志';""" % self.tb

                   execute_sql(sql)
               #print sip + dip + spt + dpt + proto
               arg = [str(res[key]) if res.has_key(key) else '' for key in order]
               #print ','.join(arg) + '\n'
               with open('/var/log/fw/logs.log','a+') as f:
                   f.write(','.join(arg) + '\n')


        except Exception as e:
#            self.logger.debug(e)
            where = log_file.tell()
            self.logger_debug("Firewall:commiting ...... at where = %d" % where)
            #self.log_record.set_record("iptables-ng_log",where)
            self.logger_debug("Firewall:commiting DONE with Exception!!!")
            print 'Error[Firewall LOG]',l
            print e

        finally:
            log_file.close()

    def run(self):
        #while True:
        #    if self.event.isSet():
        #        return
        #    self.logger_debug("Firewall:importing iptables_ng.log")
        #    self.iptables_ng_log()
        t_start = time.time()
        ##self.iptables_ng_log()
        #    self.logger_debug("Firewall:iptables_ng.log import done")
        #    #print 'done'
        print 'loading infile...'

        #    time.sleep(self.time_interval)
        sql = ('load data infile "/var/log/fw/log.processed" ignore into '
               'table m_tblog_firewall_20160523 fields TERMINATED BY "," '
               'LINES TERMINATED BY "\n" (iTime,sInputPort,sOutPort,sSourceAddr,'
               'sSourcePort,sProtocol,sTargetAddr,sTargetPort,sAction)')
        execute_sql(sql)
        t_use = time.time() - t_start
        print 'Done ! Use Time = ',t_use

    def stop(self):
        self.event.set()
        self.join()
        self.logger_debug('Firewall:STOP')
        print 'Firewall:STOP'

    def start(self):
        super(MysqlGetTblogFirewall,self).start()
        self.logger_debug('Firewall:START')
        print 'Firewall:START'

if __name__ == '__main__':
    print sys.argv
    if len(sys.argv) < 2:
        print 'Usage: python load_infile.py date [create]'
        print 'date format: YYYYMMDD Example 20160621'
        exit(0)
    d = sys.argv[1]
    from datetime import datetime
    try:
        datetime.strptime(d,'%Y%m%d')
    except:
        print 'Usage: python load_infile.py date [create]'
        print 'date format: YYYYMMDD Example 20160621'
        exit(0)

    tb_name = 'm_tblog_firewall_' + str(d)

    if 'create' in sys.argv:
        sql = 'CREATE TABLE IF NOT EXISTS `%s` LIKE m_tblog_firewall' % tb_name
        execute_sql(sql)
    if len(sys.argv) == 3:
        try:
            f = sys.argv[2].split('=')[1]
            print f
        except:
            print 'Usage: python load_infile.py date file=path [create]'
    t_start = time.time()
    print 'loading infile...'
    sql = ('load data infile "%s" ignore into '
           'table %s fields TERMINATED BY "," '
           'LINES TERMINATED BY "\n" (iTime,sInputPort,sOutPort,sSourceAddr,'
           'sSourcePort,sProtocol,sTargetAddr,sTargetPort,sAction)') % (f,tb_name)
    execute_sql(sql)
    t_use = time.time() - t_start
    print 'Done ! Use Time = ',t_use


    # if already_running(__file__):
    #     exit(0)
    # else:
    #     MysqlGetTblogFirewall().run()
#MysqlGetTblogFirewall().iptables_ng_log()
