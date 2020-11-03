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
from reportlog.mysql_get_tblog import already_running,MysqlGetTblog
from reportlog.log_size_record import log_size_record
from db.config1 import execute_sql,executemany_sql
from utils.log_logger import FWLOG_DEBUG

_path = "/var/log/wifi_audit.log"

KEY_WORDS = ["iPhone","iPad","Android","iPod"]

def timestamp(t):
     ts = time.strptime(t,'%a %b %d %H:%M:%S %Y')
     s = time.mktime(ts)
     date = time.strftime('%Y%m%d',ts)
     return int(s),date



class MysqlGetTblogWebaudit(MysqlGetTblog):

    event = threading.Event()

    def __init__(self,path = _path):
        super(MysqlGetTblogWebaudit,self).__init__()
        #self.logger = getLogger('main') #debug
        self.log_record = log_size_record()
        self.path = path
        self.current_date = ''
        self.tb = ''
        self.time_interval = 5
        self.tb_name = "m_tblog_wifi_audit"

    def log_when_exit(self,size):
        self.log_record.set_record("webaudit_log",size)

    def webaudit_log(self):
        if not os.path.exists(self.path):
            getLogger('log_daemon').debug('File %s is NOT EXISTS!!!' % self.path)
            return
        log_file = open(self.path,"r")
        try:
            imported_size = self.log_record.get_record()["webaudit_log"]
            fsize = os.path.getsize(self.path) if os.path.exists(self.path) else 0
            count = 0
            #self.logger_debug("webaudit_log")
            #self.logger_debug("WEB_AUDIT:%s" % imported_size)
            #self.logger_debug("WEB_AUDIT:%s" % fsize)

            if imported_size == fsize:
                log_file.close()
                return

            if imported_size > fsize:
                self.log_record.set_record("webaudit_log",0)
                log_file.close()
                return

            log_file.seek(imported_size,0)
            where = log_file.tell()
            done  = False
            args = []
            mysql_insert_cmd = "insert into " + self.tb + "(iTime,sShareHost,sTerminal,sTableName)" +" values(%s,%s,%s,%s)"
            while not done:
                l = log_file.readline()
                ##self.logger_debug(l)
                if l == '':
                    done = True
                    continue
            #fo r l in log_file:
                ls = l.split('#')
                if len(ls) < 3:
                    FWLOG_DEBUG('webaudit log len too short %s'% ls)
                    raise RuntimeError('webaudit log len too short')
                    continue
                #self.logger.debug(l)
                #self.logger.debug(ls[0]+" "+ls[1]+" "+ls[2])
                t,date = timestamp(ls[0])
                host = ls[1]
                term = ls[2]
                flag = False
                for key in KEY_WORDS:
                    if key in term:
                        flag = True
                        break
                if not flag:
                    continue

                if self.current_date != date:
                    self.current_date = date
                    self.tb = self.tb_name + '_' + date
                    executemany_sql(mysql_insert_cmd,args)
                    args = []
                    #run mysql cmd CREATE IF NOT EXISTS
                    sql = "CREATE TABLE IF NOT EXISTS `%s` LIKE m_tblog_wifi_audit" % self.tb
                    execute_sql(sql)

                mysql_insert_cmd = "insert into " + self.tb + "(iTime,sShareHost,sTerminal,sTableName)" +" values(%s,%s,%s,%s)"
                args.append((t,host,term,self.tb))

                count += 1
                if count == 5000:
                    where = log_file.tell()
                    #self.logger_debug("WEB_AUDIT:commiting ...... at where = %d" % where)
                    executemany_sql(mysql_insert_cmd,args)
                    self.log_record.set_record("webaudit_log",where)
                    #self.logger_debug("WEB_AUDIT:commiting DONE!!!")
                    count = 0
                    done = True
                    args = []
            #insert to mysql
            if not count == 0:
                where = log_file.tell()
                #self.logger_debug("WEB_AUDIT:commiting ...... at where = %d" % where)
                executemany_sql(mysql_insert_cmd,args)
                self.log_record.set_record("webaudit_log",where)
                #self.logger_debug("WEB_AUDIT:commiting DONE!!!")
                args = []

        except Exception as e:
            where = log_file.tell()
            #self.logger_debug("WEB_AUDIT:commiting ...... at where = %d" % where)
            executemany_sql(mysql_insert_cmd,args)
            self.log_record.set_record("webaudit_log",where)
            #self.logger_debug("WEB_AUDIT:commiting DONE!!!")
            args = []
#            self.logger.debug(e)
            FWLOG_DEBUG(e)

        finally:
            log_file.close()
            del log_file

    def run(self):
        while True:
            if self.event.isSet():
                return
            #self.logger_debug("WEB_AUDIT:importing %s" % self.path)
            self.webaudit_log()
            #self.logger_debug("WEB_AUDIT:%s import done" % self.path)

            time.sleep(self.time_interval)
            FWLOG_DEBUG('done')

    def stop(self):
        self.event.set()
        self.join()
        #self.logger_debug("WEB_AUDIT:STOP")
        FWLOG_DEBUG('WEB_AUDIT:STOP')

    def start(self):
        super(MysqlGetTblogWebaudit,self).start()
        #self.logger_debug('WEB_AUDIT:START')
        FWLOG_DEBUG('WEB_AUDIT:START')


if __name__ == '__main__':
    if already_running(__file__):
        exit(0)
    else:
        MysqlGetTblogWebaudit().run()
        FWLOG_DEBUG('WEB_AUDIT log:START')

#importlog().webaudit_log()
