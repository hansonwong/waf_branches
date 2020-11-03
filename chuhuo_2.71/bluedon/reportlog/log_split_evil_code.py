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
from os.path import getsize
from logging import getLogger
# from docopt import docopt
from db.config1 import execute_sql,executemany_sql
from reportlog.log_size_record import log_size_record
from reportlog.mysql_get_tblog import already_running,MysqlGetTblog
from reportlog.log_statistics import evilcode_log_statistics
from utils.log_logger import FWLOG_DEBUG

_path = "/var/log/suricata/AvScan.log"

#ip_reg = r"(\d{1,3}\.){3}\d{1,3}"
#sip_reg = r"(?<=\bip_src = ).*?\s\b"
#dip_reg = r"(?<=\bip_dst = ).*?\s\b"
#proto_reg = r"(?<=\bproto = ).*?\s\b"
#act_reg = r"(?<=\bact = ).*"
#appName_reg = r"(?<=\bAppName = ).*?\s\b"
def timestamp(ds):
     ts = time.strptime(ds,'%m/%d/%Y-%H:%M:%S')
     s = time.mktime(ts)
     date = time.strftime('%Y%m%d',ts)
     return int(s),date




class MysqlGetTblogEvilCode(MysqlGetTblog):

    event = threading.Event()

    def __init__(self,path=_path):
        super(MysqlGetTblogEvilCode,self).__init__()
        #self.logger = getLogger('main') #debug
        self.log_record = log_size_record()
        self.path = path
        self.current_date = ''
        self.tb = ''
        try:
#            args = docopt(__doc__)

#            if not args['-t'] == None:
#            self.time_interval = int(args['-t'])
#            else:
            self.time_interval = 0.1

#            if not args['--loglevel'] == None:
#            self.level = args['--loglevel']
#            else:
#            self.level = "DEBUG"

#            if args['--reset'] == True:
                #can be instead of removing the log_size_record file
#            self.log_record.set_record("app_admin",0)

            #connect to database
#            self.logger = create_logger("log",self.level)
            #need modify for different log
            self.tb_name = "m_tblog_evil_code"


#            self.logger.debug("start...")
        except Exception as e:
#            self.logger.debug(e)
             FWLOG_DEBUG(e)


    def log_when_exit(self,size):
        self.log_record.set_record("evil_code",size)

    def evil_code(self):
        if not os.path.exists(self.path):
            getLogger('log_daemon').debug('File %s is NOT EXISTS!!!' % self.path)
            return
        log_file = open(self.path,"r")
        try:
            imported_size = self.log_record.get_record()["evil_code"]
            fsize = os.path.getsize(self.path) if os.path.exists(self.path) else 0

            count = 0
            #self.logger_debug("evil_code")
            #self.logger_debug("EVIL_CODE:%s" % imported_size)
            #self.logger_debug("EVIL_CODE:%s" % fsize)

            if imported_size ==  fsize:
                log_file.close()
                return

            if imported_size > fsize:
                log_file.close()
                self.log_record.set_record("evil_code",0)
                return

            log_file.seek(imported_size,0)
            where = log_file.tell()
            done  = False
            args = []
            mysql_insert_cmd = "insert into " + self.tb + "(iTime,sViruesName,sSourceIP,sProtocol,sTargetIP,sStatus,sLogLevel,sFileName)" +" values(%s,%s,%s,%s,%s,%s,%s,%s)"
            while not done:
               l = log_file.readline()
               #self.logger.debug(l)
               if l == '':
                   done = True
                   continue
            #for l in log_file:

               ls = l.split()
               if len(ls) < 7:
                   FWLOG_DEBUG('log_split_evilcode: len too short %s' % ls)
                   raise RuntimeError('log_split_evilcode: len too short')
                   continue
               ds = ls[0].split('.')[0]
               #self.logger.debug(l)
               #self.logger.debug(ls[0]+" "+ls[1]+" "+ls[2])
               t,date = timestamp(ds)
               if self.current_date != date:
                   executemany_sql(mysql_insert_cmd,args)
                   evilcode_log_statistics(args)
                   args = []
                   self.current_date = date
                   self.tb = self.tb_name + '_' + date
                   sql = "CREATE TABLE IF NOT EXISTS `%s` LIKE m_tblog_evil_code" % self.tb
                   execute_sql(sql)

               stat = ls[-1].lstrip('[').rstrip(']')
               #level =" ".join( ls[1:-5]).lstrip('[').rstrip(']')
               level = ls[1]
               vn = ls[-6].encode('string-escape')
               fn = ls[-5].encode('string-escape')
               mysql_insert_cmd = "insert into " + self.tb + "(iTime,sViruesName,sSourceIP,sProtocol,sTargetIP,sStatus,sLogLevel,sFileName)" +" values(%s,%s,%s,%s,%s,%s,%s,%s)"
               #args.append((t,ls[-6],ls[-4],ls[-2],ls[-3],stat,level,ls[-5]))
               args.append((t,vn,ls[-4],ls[-2],ls[-3],stat,level,fn))

               count += 1
               if count == 5000:
                   where = log_file.tell()
                   #self.logger_debug("EVIL_CODE:commiting ...... at where = %d" % where)
                   executemany_sql(mysql_insert_cmd,args)
                   evilcode_log_statistics(args)
                   self.log_record.set_record("evil_code",where)
                   #self.logger_debug("EVIL_CODE:commiting DONE!!!")
                   count = 0
                   args = []
                   done = True
               #self.logger.debug(time +  sip + dip)
            #insert to mysql
            if not count == 0:
                where = log_file.tell()
                #self.logger_debug("EVIL_CODE:commiting ...... at where = %d" % where)
                executemany_sql(mysql_insert_cmd,args)
                evilcode_log_statistics(args)
                self.log_record.set_record("evil_code",where)
                args = []
                #self.logger_debug("EVIL_CODE:commiting DONE!!!")

        except Exception as e:
             where = log_file.tell()
             #self.logger_debug("EVIL_CODE:commiting ...... at where = %d" % where)
             executemany_sql(mysql_insert_cmd,args)
             evilcode_log_statistics(args)
             self.log_record.set_record("evil_code",where)
             args = []
             #self.logger_debug("EVIL_CODE:commiting DONE!!! with execption")
#            self.logger.debug(e)
             FWLOG_DEBUG(e)

        finally:
            log_file.close()
            del log_file

    def run(self):
        while True:
            if self.event.isSet():
                return
            #self.logger_debug("EVIL_CODE:importing %s" % self.path)
            self.evil_code()
            #self.logger_debug("EVIL_CODE:%s import done" % self.path)


            time.sleep(self.time_interval)
            FWLOG_DEBUG('done')

    def stop(self):
        self.event.set()
        self.join()
        #self.logger_debug("EVIL_CODE:STOP")
        FWLOG_DEBUG('EVIL_CODE:STOP')

    def start(self):
        super(MysqlGetTblogEvilCode,self).start()
        #self.logger_debug('EVIL_CODE:START')
        FWLOG_DEBUG('EVIL_CODE:START')


if __name__ == '__main__':
    if already_running(__file__):
        exit(0)
    else:
        MysqlGetTblogEvilCode().run()
        FWLOG_DEBUG('EVIL_CODE log:START')

#importlog().app_admin()
