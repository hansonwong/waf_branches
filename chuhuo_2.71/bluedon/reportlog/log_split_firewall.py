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
import json
import logging
import utils.logger_init
import commands
import threading
import gc
from os.path import getsize
from logging import getLogger
from db.config1 import execute_sql,executemany_sql
from reportlog.log_size_record import log_size_record
from reportlog.log_app_names import get_app_names
from reportlog.mysql_get_tblog import already_running,MysqlGetTblog
from utils.log_logger import FWLOG_DEBUG

_path = "/var/log/fw/iptables-ng.log"

#ip_reg = r"(\d{1,3}\.){3}\d{1,3}"
sip_reg = r"(?<=\bSRC=).*?\s\b"
dip_reg = r"(?<=\bDST=).*?\s\b"
sport_reg = r"(?<=\bSPT=).*?\s\b"
dport_reg = r"(?<=\bDPT=).*?\s\b"
proto_reg = r"(?<=\bPROTO=).*?\s\b"
in_reg = r"(?<=\bIN=).*?\s\b"
out_reg = r"(?<=\bOUT=).*?\s\b"
act_reg = r"(?<=\bipt_log=).*?\s\b"

def timestamp(ts):
    try:
        ta = time.localtime(int(ts))
        date = time.strftime('%Y%m%d',ta)
    except:
        date = None
    return ts,date



class MysqlGetTblogFirewall(MysqlGetTblog):

    event = threading.Event()

    def __init__(self,path = _path):
        super(MysqlGetTblogFirewall,self).__init__()
        #self.logger = create_logger("log",logging.DEBUG)
        self.log_record = log_size_record()
        self.path = path
        self.current_date = ''
        self.tb = ''
        self.app_tb = ''
        self.app_names = get_app_names()
        try:
            self.time_interval = 2
            self.tb_name = "m_tblog_firewall"

            self.rc_sip = re.compile(sip_reg)
            self.rc_dip = re.compile(dip_reg)
            self.rc_sport = re.compile(sport_reg)
            self.rc_dport = re.compile(dport_reg)
            self.rc_proto = re.compile(proto_reg)
            self.rc_in = re.compile(in_reg)
            self.rc_out = re.compile(out_reg)
            self.rc_act = re.compile(act_reg)

            # self.logger.debug("start...")
        except Exception as e:
            #  self.logger.debug(e)
            FWLOG_DEBUG(e)

    def init_db(self):
        try:
            pass
        except Exception as e:
#            self.logger.debug(e)
            FWLOG_DEBUG(e)

    def log_when_exit(self,size):
        self.log_record.set_record("iptables-ng_log",size)

    def iptables_ng_log(self):
        if not os.path.exists(self.path):
            getLogger('log_daemon').debug('File %s is NOT EXISTS!!!' % self.path)
            return
        log_file = open(self.path,"r")
        try:
            imported_size = self.log_record.get_record()["iptables-ng_log"]
            fsize = os.path.getsize(self.path) if os.path.exists(self.path) else 0

            count = 0
            #self.logger_debug("Firewall:iptables-ng_log")
            #self.logger_debug("Firewall:%s" % imported_size)
            #self.logger_debug("Firewall:%s" % fsize)


            if imported_size == fsize:
                log_file.close()
                return
            if imported_size > fsize:
                self.log_record.set_record("iptables-ng_log",0)
                log_file.close()
                return

            log_file.seek(imported_size,0)
            where = log_file.tell()
            done  = False
            args = []
            app_args = []
            mysql_insert_cmd = ("insert into " + self.tb +''
                                "(iTime,sInputPort,sOutPort,sSourceAddr,"
                                "sSourcePort,sProtocol,sTargetAddr,sTargetPort,sAction)"
                                " values(%s,%s,%s,%s,%s,%s,%s,%s,%s)")

            app_mysql_insert_cmd = ("insert into " + self.app_tb +''
                                    "(iTime,sAppName,sSourceIP,sProtocol,sTargetIP,sAction)"
                                    " values(%s,%s,%s,%s,%s,%s)")
            while not done:
                l = log_file.readline()
                if l == '':
                    done = True
                    continue

                mark = ''
                ls = l.split()

                #if len(ls) < 3:
                if len(ls) < 14:
                    FWLOG_DEBUG('log_split_firewall:len too short %s' % ls)
                    raise RuntimeError('log_split_firewall:len too short')
                    continue
                #optimize
                res = {i.split('=')[0]:i.split('=')[1] for i in ls if not len(i.split('=')) < 2}
                act = '-' if res['ipt_log'] == '' else res['ipt_log']
                inp = res['IN']
                out = res['OUT']
                sip = res['SRC']
                dip = res['DST']
                proto = res['PROTO']
                spt = res['SPT'] if res.has_key('SPT') else '-'
                dpt = res['DPT'] if res.has_key('DPT') else '-'
                mark = res['MARK'] if res.has_key('MARK') else ''

                if res.get('PHYSIN') and res.get('PHYSOUT'):
                    inp = res['PHYSIN']
                    out = res['PHYSOUT']

                t,date = timestamp(ls[0])

                if t == 0 or date == None:
                    continue
                if self.current_date != date:
                    self.current_date = date
                    self.tb = self.tb_name + '_' + date
                    self.app_tb = 'm_tblog_app_admin_' + date

                    executemany_sql(mysql_insert_cmd,args)
                    args = []
                    sql = "CREATE TABLE IF NOT EXISTS `%s` LIKE m_tblog_firewall" % self.tb
                    execute_sql(sql)

                    executemany_sql(app_mysql_insert_cmd,app_args)
                    app_args = []
                    app_sql = "CREATE TABLE IF NOT EXISTS `%s` LIKE m_tblog_app_admin" % self.app_tb
                    execute_sql(app_sql)

                # new date data will insert into new table
                mysql_insert_cmd = ("insert into " + self.tb +''
                                    "(iTime,sInputPort,sOutPort,sSourceAddr,"
                                    "sSourcePort,sProtocol,sTargetAddr,sTargetPort,sAction)"
                                    " values(%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                args.append((t,inp,out,sip,spt,proto,dip,dpt,act))

                app_mysql_insert_cmd = ("insert into " + self.app_tb +''
                                        "(iTime,sAppName,sSourceIP,sProtocol,sTargetIP,sAction)"
                                        " values(%s,%s,%s,%s,%s,%s)")
                if mark != '':
                    mark = int(mark, 16) & 0xFF
                    mark = self.app_names[mark]
                    app_args.append((t,mark,sip,proto,dip,act))


                count += 1
                if count== 10000:
                    where = log_file.tell()
                    #self.logger_debug("Firewall:commiting ...... at where = %d" % where)
                    if args:
                        executemany_sql(mysql_insert_cmd,args)
                    if app_args:
                        executemany_sql(app_mysql_insert_cmd,app_args)
                    self.log_record.set_record("iptables-ng_log",where)
                    #self.logger_debug("Firewall:commiting DONE!!!")
                    count = 0
                    args = []
                    app_args = []
                    done = True

            #insert to mysql
            if not count == 0:
                where = log_file.tell()
                #self.logger_debug("Firewall:commiting ...... at where = %d" % where)
                if args:
                    executemany_sql(mysql_insert_cmd,args)
                if app_args:
                    executemany_sql(app_mysql_insert_cmd,app_args)
                args = []
                app_args = []
                self.log_record.set_record("iptables-ng_log",where)
                #self.logger_debug("Firewall:commiting DONE!!!")

        except Exception as e:
#            self.logger.debug(e)
            where = log_file.tell()
            #self.logger_debug("Firewall:commiting ...... at where = %d" % where)
            if args:
                executemany_sql(mysql_insert_cmd,args)
            if app_args:
                executemany_sql(app_mysql_insert_cmd,app_args)
            args = []
            app_args = []
            self.log_record.set_record("iptables-ng_log",where)
            #self.logger_debug("Firewall:commiting DONE with Exception!!!")
            FWLOG_ERR('Error[Firewall LOG] %s' % l)
            FWLOG_ERR(e)
            print('Error[Firewall LOG] %s' % l)

        finally:
            log_file.close()
            del log_file

    def run(self):
        while True:
            if self.event.isSet():
                return
            #self.logger_debug("Firewall:importing iptables_ng.log")
            self.iptables_ng_log()
            #self.logger_debug("Firewall:iptables_ng.log import done")

            time.sleep(self.time_interval)

    def stop(self):
        self.event.set()
        self.join()
        #self.logger_debug('Firewall:STOP')
        FWLOG_DEBUG('Firewall:STOP')

    def start(self):
        super(MysqlGetTblogFirewall,self).start()
        #self.logger_debug('Firewall:START')
        FWLOG_DEBUG('Firewall:START')

if __name__ == '__main__':
    #if already_running(__file__):
    #    exit(0)
    #else:
        MysqlGetTblogFirewall().run()
#MysqlGetTblogFirewall().iptables_ng_log()
