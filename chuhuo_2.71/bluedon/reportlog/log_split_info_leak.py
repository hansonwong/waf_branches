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
import cgi
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
from reportlog.mysql_get_tblog import already_running,MysqlGetTblog
from reportlog.log_size_record import log_size_record
from db.config1 import execute_sql,executemany_sql
from utils.log_logger import FWLOG_DEBUG

_path = "/var/log/suricata/smtp.log"

def timestamp(ds):
     ts = time.strptime(ds,'%m/%d/%Y-%H:%M:%S')
     s = time.mktime(ts)
     date = time.strftime('%Y%m%d',ts)
     return int(s),date

class MysqlGetTblogInfoLeak(MysqlGetTblog):

    event = threading.Event()

    def __init__(self,path = _path):
        super(MysqlGetTblogInfoLeak,self).__init__()
        #self.logger = getLogger('main') #debug
        self.log_record = log_size_record()
        self.path = path
        self.current_date = ''
        self.tb = ''

        try:
            self.time_interval = 0.01
            self.tb_name = "m_tblog_info_leak"

        except Exception as e:
             FWLOG_DEBUG(e)


    def log_when_exit(self,size):
        self.log_record.set_record("info_leak",size)

    def info_leak(self):
        if not os.path.exists(self.path):
            getLogger('log_daemon').debug('File %s is NOT EXISTS!!!' % self.path)
            return
        log_file = open(self.path,"r")
        try:
            imported_size = self.log_record.get_record()["info_leak"]
            fsize = os.path.getsize(self.path) if os.path.exists(self.path) else 0

            count = 0
            #self.logger_debug("info_leak")
            #self.logger_debug("INFO_LEAK:%s" % imported_size)
            #self.logger_debug("INFO_LEAK:%s" % fsize)

            if imported_size == fsize:
                log_file.close()
                return

            if imported_size > fsize:
                log_file.close()
                self.log_record.set_record("info_leak",0)
                return

            log_file.seek(imported_size,0)
            where = log_file.tell()
            done  = False
            args = []
            mysql_insert_cmd = "insert into " + self.tb + "(iTime,sFileKeywork,sFilterType,sSourceIP,sProtocol,sTargetIP,sStatus)" +" values(%s,%s,%s,%s,%s,%s,%s)"
            while not done:
                l = log_file.readline()
                #self.logger.debug(l)
                if l == '':
                    done = True
                    continue
                #for l in log_file:

                ls = l.split()
                if len(ls) < 7:
                    FWLOG_DEBUG('log_split_info_leak:len too short %s' % ls)
                    raise RuntimeError('log_split_info_leak:len too short')
                    continue
                if len(ls) > 7:
                    keyword = (' ').join(ls[1:-5])
                else:
                    keyword = ls[1]
                keyword = cgi.escape(keyword)
                ds = ls[0].split('.')[0]
                #self.logger.debug(l)
                #self.logger.debug(ls[0]+" "+ls[1]+" "+ls[2])
                t,date = timestamp(ds)
                stat = ls[-1].lstrip('[').rstrip(']')

                if self.current_date != date:
                    self.current_date = date
                    self.tb = self.tb_name + '_' + date
                    executemany_sql(mysql_insert_cmd,args)
                    args = []
                    sql = "CREATE TABLE IF NOT EXISTS `%s` LIKE m_tblog_info_leak" % self.tb
                    execute_sql(sql)

                mysql_insert_cmd = "insert into " + self.tb + "(iTime,sFileKeywork,sFilterType,sSourceIP,sProtocol,sTargetIP,sStatus)" +" values(%s,%s,%s,%s,%s,%s,%s)"
                args.append((t,keyword,ls[-5],ls[-4],ls[-2],ls[-3],stat))

                count += 1
                if count == 5000:
                    where = log_file.tell()
                    #self.logger_debug("INFO_LEAK:commiting ...... at where = %d" % where)
                    executemany_sql(mysql_insert_cmd,args)
                    self.log_record.set_record("info_leak",where)
                    #self.logger_debug("INFO_LEAK:commiting DONE!!!")
                    count = 0
                    args = []
                    done = True
                #self.logger.debug(time +  sip + dip)
            #insert to mysql
            if not count == 0:
                where = log_file.tell()
                #self.logger_debug("INFO_LEAK:commiting ...... at where = %d" % where)
                executemany_sql(mysql_insert_cmd,args)
                self.log_record.set_record("info_leak",where)
                #self.logger_debug("INFO_LEAK:commiting DONE!!!")
                args = []

        except Exception as e:
            where = log_file.tell()
            #self.logger_debug("INFO_LEAK:commiting ...... at where = %d" % where)
            executemany_sql(mysql_insert_cmd,args)
            self.log_record.set_record("info_leak",where)
            #self.logger_debug("INFO_LEAK:commiting DONE!!!")
            args = []
#           self.logger.debug(e)
            FWLOG_ERR(e)

        finally:
            log_file.close()
            del log_file

    def run(self):
        while True:
            if self.event.isSet():
                return
            #self.logger_debug("INFO_LEAK:importing %s" % self.path)
            self.info_leak()
            #self.logger_debug("INFO_LEAK:%s import done" % self.path)

            time.sleep(self.time_interval)

    def stop(self):
        self.event.set()
        self.join()
        #self.logger_debug("INFO_LEAK:STOP")
        FWLOG_DEBUG('INFO_LEAK:STOP')

    def start(self):
        super(MysqlGetTblogInfoLeak,self).start()
        #self.logger_debug('INFO_LEAK:START')
        FWLOG_DEBUG('INFO_LEAK:START')


if __name__ == '__main__':
    if already_running(__file__):
        exit(0)
    else:
        MysqlGetTblogInfoLeak().run()
        FWLOG_DEBUG('INFO_LEAK log:START')

#importlog().app_admin()
