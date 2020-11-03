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

_path = "/var/log/bdwaf/logs/url_filter.log"

ip_reg = r"(\d{1,3}\.){3}\d{1,3}"
time_reg = r"\d{4}/\d{1,2}/\d{1,2}\s(\d{1,2}:){2}\d{1,2}"

def timestamp(t):
     ts = time.strptime(t,'%Y/%m/%d %H:%M:%S')
     s = time.mktime(ts)
     date = time.strftime('%Y%m%d',ts)
     return int(s),date




class MysqlGetTblogUrl(MysqlGetTblog):

    event = threading.Event()

    def __init__(self,path = _path):
        super(MysqlGetTblogUrl,self).__init__()
        #self.logger = create_logger("log",logging.DEBUG) #debug
        self.log_record = log_size_record()
        self.path = path
        self.current_date = ''
        self.tb = ''
        try:
            self.time_interval = 0.01
            self.tb_name = "m_tblog_url_visit"

            self.rc_sip = re.compile(ip_reg)
            self.rc_dip = re.compile(ip_reg)
            self.rc_time = re.compile(time_reg)


#            self.logger.debug("start...")
        except Exception as e:
#            self.logger.debug(e)
            FWLOG_DEBUG(e)


    def log_when_exit(self,size):
        self.log_record.set_record("url_log",size)

    def url_log(self):
        if not os.path.exists(self.path):
            getLogger('log_daemon').debug('File %s is NOT EXISTS!!!' % self.path)
            return
        #self.logger_debug('URL:Starting url_log processing...')
        log_file = open(self.path,"r")
        try:
            imported_size = self.log_record.get_record()["url_log"]
            fsize = os.path.getsize(self.path) if os.path.exists(self.path) else 0

            count = 0
            #self.logger_debug("URL:url_log")
            #self.logger_debug('URL:%s' % imported_size)
            #self.logger_debug('URL:%s' % fsize)

            if imported_size == fsize:
                log_file.close()
                return

            if imported_size > fsize:
                self.log_record.set_record("url_log",0)
                #self.logger_debug('URL:No newer data')
                log_file.close()
                return

            log_file.seek(imported_size,0)
            where = log_file.tell()
            done  = False
            args = []
            mysql_insert_cmd = "insert into " + self.tb + "(iTime,sUrl,sSourceIP,sWebType,sTargetIP,sAction)" +" values(%s,%s,%s,%s,%s,0)"
            while not done:
                l = log_file.readline()
                #self.logger.debug(l)
                if l == '':
                    done = True
                    continue
                #for l in log_file:
                ls = l.split()
                if len(ls) < 6:
                    FWLOG_DEBUG('log_split_url:len too short %s' % ls)
                    raise RuntimeError('log_split_url:len too short')
                    continue
                ssip = self.rc_sip.search(ls[2])
                sdip = self.rc_dip.search(ls[3])
                stime = self.rc_time.search(ls[0] + ' ' + ls[1])


                if not ssip == None:
                    sip = ssip.group(0).strip()
                else:
                    continue
                if not sdip == None:
                    dip = sdip.group(0).strip()
                else:
                    continue
                if not stime == None:
                    ltime = stime.group(0).strip()
                else:
                    continue

                #self.logger.debug(l)
                #self.logger.debug(ls[0]+" "+ls[1]+" "+ls[2])
                t,date = timestamp(ltime)
                if self.current_date != date:
                    self.current_date = date
                    self.tb = self.tb_name + '_' + date
                    executemany_sql(mysql_insert_cmd,args)
                    args = []
                    sql = "CREATE TABLE IF NOT EXISTS `%s` LIKE m_tblog_url_visit" % self.tb

                    execute_sql(sql)
                mysql_insert_cmd = "insert into " + self.tb + "(iTime,sUrl,sSourceIP,sWebType,sTargetIP,sAction)" +" values(%s,%s,%s,%s,%s,0)"

                sUrl = str(ls[5:]).lstrip('[').rstrip(']').encode('string-escape')
                sUrl = sUrl[2:-2]
                sUrl = cgi.escape(sUrl)
                args.append((t,sUrl,sip,ls[4],dip))


                count += 1
                if count == 5000:
                    where = log_file.tell()
                    #self.logger_debug("URL:commiting ...... at where = %d" % where)
                    executemany_sql(mysql_insert_cmd,args)
                    self.log_record.set_record("url_log",where)
                    #self.logger_debug("URL:commiting DONE!!!")
                    count = 0
                    done = True
                    args = []
                #self.logger.debug(time +  sip + dip)
            #insert to mysql
            if not count == 0:
                where = log_file.tell()
                #self.logger_debug("URL:commiting ...... at where = %d" % where)
                executemany_sql(mysql_insert_cmd,args)
                self.log_record.set_record("url_log",where)
                #self.logger_debug("URL:commiting DONE!!!")
                args = []

        except Exception as e:
            where = log_file.tell()
            #self.logger_debug("URL:commiting ...... at where = %d" % where)
            executemany_sql(mysql_insert_cmd,args)
            self.log_record.set_record("url_log",where)
            #self.logger_debug("URL:commiting DONE!!!")
            args = []
            FWLOG_DEBUG(e)

        finally:
            log_file.close()
            del log_file

    def run(self):
        while True:
            if self.event.isSet():
                return
            #self.logger_debug("URL:importing %s" % self.path)
            self.url_log()
            #self.logger_debug("URL:%s import done" % self.path)

            time.sleep(self.time_interval)

    def stop(self):
        self.event.set()
        self.join()
        #self.logger_debug('Url:STOP')
        FWLOG_DEBUG('Url:STOP')

    def start(self):
        super(MysqlGetTblogUrl,self).start()
        #self.logger_debug('Url:START')
        FWLOG_DEBUG('Url:START')

if __name__ == '__main__':
    if already_running(__file__):
        exit(0)
    else:
        MysqlGetTblogUrl().run()
#MysqlGetTblogUrl().url_log()
