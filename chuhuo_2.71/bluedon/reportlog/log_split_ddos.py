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
import utils.logger_init
import json
import logging
import commands
import threading
from os.path import getsize
from logging import getLogger
# from docopt import docopt
from db.config1 import execute_sql,executemany_sql
from reportlog.log_size_record import log_size_record
from reportlog.mysql_get_tblog import already_running,MysqlGetTblog
from reportlog.log_statistics import ddos_log_statistics
from utils.log_logger import FWLOG_DEBUG

_path = "/var/log/ddos/bd_ddos.log"

#ip_reg = r"(\d{1,3}\.){3}\d{1,3}"
sip_reg = r"(?<=\bSIP=).*?\s\b"
dip_reg = r"(?<=\bDIP=).*?\s\b"
sport_reg = r"(?<=\bSPT=).*?\s\b"
dport_reg = r"(?<=\bDPT=).*?\s\b"
proto_reg = r"(?<=\bPROTO=).*?\s\b"
event_reg = r"(?<=\bEVENT=).*?\s\b"
thres_reg = r"(?<=\bTHRES=).*"
def timestamp(y,m,d,tm):
     t = y + ' ' + m + ' ' + d + ' ' + tm
     ts = time.strptime(t,'%Y %b %d %H:%M:%S')
     s = time.mktime(ts)
     date = time.strftime('%Y%m%d',ts)
     return int(s),date




class MysqlGetTblogDdos(MysqlGetTblog):

    event = threading.Event()

    def __init__(self,path = _path):
        super(MysqlGetTblogDdos,self).__init__()
        #self.logger = getLogger('main') #debug
        self.log_record = log_size_record()
        self.path = path
        self.current_date = ''
        self.tb = ''
        try:
            self.time_interval = 0.01

            self.tb_name = "m_tblog_ddos"

            self.rc_sip = re.compile(sip_reg)
            self.rc_dip = re.compile(dip_reg)
            self.rc_event = re.compile(event_reg)
            self.rc_thres = re.compile(thres_reg)

#            self.logger.debug("start...")
        except Exception as e:
#            self.logger.debug(e)
             FWLOG_DEBUG(e)


    def init_db(self):
        try:
            pass
        except Exception as e:
#            self.logger.debug(e)
            FWLOG_DEBUG(e)

    def log_when_exit(self,size):
        self.log_record.set_record("ddos_log",size)

    def ddos_log(self):
        if not os.path.exists(self.path):
            getLogger('log_daemon').debug('File %s is NOT EXISTS!!!' % self.path)
            return
        log_file = open(self.path,"r")
        try:
            imported_size = self.log_record.get_record()["ddos_log"]
            fsize = os.path.getsize(self.path) if os.path.exists(self.path) else 0

            count = 0
            #self.logger_debug("ddos_log")
            #self.logger_debug("DDOS:%s" % imported_size)
            #self.logger_debug("DDOS:%s" % fsize)

            if imported_size == fsize:
                log_file.close()
                return

            if imported_size > fsize:
                log_file.close()
                self.log_record.set_record("ddos_log",0)
                return

            log_file.seek(imported_size,0)
            where = log_file.tell()
            done  = False
            args = []
            mysql_insert_cmd = "insert into " + self.tb + "(iTime,sEventName,sSourceIP,sThreshold,sTargetIP,sStatus)" +" values(%s,%s,%s,%s,%s,0)"
            while not done:
                l = log_file.readline()
                ##self.logger_debug(l)
                if l == '':
                    done = True
                    continue
            #fo r l in log_file:
                ssip = self.rc_sip.search(l)
                sdip = self.rc_dip.search(l)
                sevent = self.rc_event.search(l)
                sthres = self.rc_thres.search(l)

                if not ssip == None:
                    sip = ssip.group(0).strip()
                else:
                    continue
                if not sdip == None:
                    dip = sdip.group(0).strip()
                else:
                    continue
                if not sevent == None:
                    event = sevent.group(0).strip()
                else:
                    continue
                if not sthres == None:
                    thres = sthres.group(0).strip()
                else:
                    continue

                ls = l.split()
                if len(ls) < 9:
                    FWLOG_DEBUG('log_split_ddos:len too short %s' % ls)
                    raise RuntimeError('log_split_ddos:len too short')
                    continue
                #self.logger.debug(l)
                #self.logger.debug(ls[0]+" "+ls[1]+" "+ls[2])
                t,date = timestamp(ls[4].rstrip(','),ls[1],ls[2],ls[3])
                if self.current_date != date:
                    self.current_date = date
                    self.tb = self.tb_name + '_' + date
                    executemany_sql(mysql_insert_cmd,args)
                    ddos_log_statistics(args)
                    args = []
                    #run mysql cmd CREATE IF NOT EXISTS
                    sql = "CREATE TABLE IF NOT EXISTS `%s` LIKE m_tblog_ddos" % self.tb
                    execute_sql(sql)

                mysql_insert_cmd = "insert into " + self.tb + "(iTime,sEventName,sSourceIP,sThreshold,sTargetIP,sStatus)" +" values(%s,%s,%s,%s,%s,0)"
                args.append((t,event,sip,thres,dip))

                count += 1
                if count == 5000:
                    where = log_file.tell()
                    #self.logger_debug("DDOS:commiting ...... at where = %d" % where)
                    executemany_sql(mysql_insert_cmd,args)
                    ddos_log_statistics(args)
                    self.log_record.set_record("ddos_log",where)
                    #self.logger_debug("DDOS:commiting DONE!!!")
                    count = 0
                    done = True
                #self.logger.debug(time +  sip + dip)
            #insert to mysql
            if not count == 0:
                where = log_file.tell()
                #self.logger_debug("DDOS:commiting ...... at where = %d" % where)
                executemany_sql(mysql_insert_cmd,args)
                ddos_log_statistics(args)
                self.log_record.set_record("ddos_log",where)
                #self.logger_debug("DDOS:commiting DONE!!!")

        except Exception as e:
             where = log_file.tell()
             #self.logger_debug("DDOS:commiting ...... at where = %d" % where)
             executemany_sql(mysql_insert_cmd,args)
             ddos_log_statistics(args)
             self.log_record.set_record("ddos_log",where)
             #self.logger_debug("DDOS:commiting DONE!!! with exception")
#            self.logger.debug(e)
             FWLOG_DEBUG(e)

        finally:
            log_file.close()
            del log_file

    def run(self):
        while True:
            if self.event.isSet():
                return
            #self.logger_debug("DDOS:importing %s" % self.path)
            self.ddos_log()
            #self.logger_debug("DDOS:%s import done" % self.path)

            time.sleep(self.time_interval)
            FWLOG_DEBUG('done')

    def stop(self):
        self.event.set()
        self.join()
        #self.logger_debug("DDOS:STOP")
        FWLOG_DEBUG('DDOS:STOP')

    def start(self):
        super(MysqlGetTblogDdos,self).start()
        #self.logger_debug('DDOS:START')
        FWLOG_DEBUG('DDOS:START')


if __name__ == '__main__':
    if already_running(__file__):
        exit(0)
    else:
        MysqlGetTblogDdos().run()
        FWLOG_DEBUG('DDOS log:START')

#importlog().ddos_log()
