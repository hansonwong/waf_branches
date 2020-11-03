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
import commands
import threading
import utils.logger_init
from os.path import getsize
from logging import getLogger
# from docopt import docopt
from reportlog.log_size_record import log_size_record
from reportlog.mysql_get_tblog import already_running,MysqlGetTblog
from db.config1 import execute_sql,executemany_sql
from utils.log_logger import FWLOG_DEBUG

#log_path = "/home/log/apply_controls/app_mgt_.log"
_path = "/var/log/apply_controls/app_mgt_.log"

#ip_reg = r"(\d{1,3}\.){3}\d{1,3}"
sip_reg = r"(?<=\bip_src = ).*?\s\b"
dip_reg = r"(?<=\bip_dst = ).*?\s\b"
proto_reg = r"(?<=\bproto = ).*?\s\b"
act_reg = r"(?<=\bact = ).*"
appName_reg = r"(?<=\bAppName = ).*?\s\b"
def timestamp(m,d,tm):
     year = time.localtime()[0]
     t = str(year) + ' ' + m + ' ' + d + ' ' + tm
     ts = time.strptime(t,'%Y %b %d %H:%M:%S')
     s = time.mktime(ts)
     date = time.strftime('%Y%m%d',ts)
     return int(s),date




class MysqlGetTblogAppAdmin(MysqlGetTblog):

    event = threading.Event()

    def __init__(self,path = _path):
        super(MysqlGetTblogAppAdmin,self).__init__()
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
            self.time_interval = 0.01

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
            self.tb_name = "m_tblog_app_admin"
            #self.mysql_db_conn = MySQLdb.connect(host='localhost',port=3306,user='root',passwd='123456',db='db_firewall',charset='utf8',unix_socket='/opt/lampp/var/mysql/mysql.sock')
            #self.mysql_db_cur = self.mysql_db_conn.cursor()

            #self.rc_time = re.compile(time_reg)
            self.rc_sip = re.compile(sip_reg)
            self.rc_dip = re.compile(dip_reg)
            self.rc_act = re.compile(act_reg)
            self.rc_proto = re.compile(proto_reg)
            self.rc_appName = re.compile(appName_reg)

#            self.logger.debug("start...")
        except Exception as e:
#            self.logger.debug(e)
             FWLOG_DEBUG(e)


    def init_db(self):
        try:
            #self.mysql_db_conn = MySQLdb.connect(host='localhost',port=3306,user='root',passwd='123456',db='db_firewall',charset='utf8',unix_socket='/opt/lampp/var/mysql/mysql.sock')
            #self.mysql_db_cur = self.mysql_db_conn.cursor()
            pass
        except Exception as e:
#            self.logger.debug(e)
            FWLOG_DEBUG(e)

    def log_when_exit(self,size):
        self.log_record.set_record("app_admin",size)

    def app_admin(self):
        if not os.path.exists(self.path):
            getLogger('log_daemon').debug('File %s is NOT EXISTS!!!' % self.path)
            return
        log_file = open(self.path,"r")
        try:
            imported_size = self.log_record.get_record()["app_admin"]
            fsize = os.path.getsize(self.path) if os.path.exists(self.path) else 0

            count = 0
            #self.logger_debug("app_admin")
            #self.logger_debug("APP_ADMIN:%s" % imported_size)
            #self.logger_debug("APP_ADMIN:%s" % fsize)

            if imported_size == fsize:
                log_file.close()
                return

            if imported_size > fsize:
                self.log_record.set_record("app_admin",0)
                log_file.close()
                return

            log_file.seek(imported_size,0)
            where = log_file.tell()
            done  = False
            args = []
            mysql_insert_cmd = "insert into " + self.tb + "(iTime,sAppName,sSourceIP,sProtocol,sTargetIP,sAction)" +" values(%s,%s,%s,%s,%s,%s)"
            while not done:
               l = log_file.readline()
               #self.logger.debug(l)
               if l == '':
                   done = True
                   continue
            #for l in log_file:
               ssip = self.rc_sip.search(l)
               sdip = self.rc_dip.search(l)
               sact = self.rc_act.search(l)
               sproto = self.rc_proto.search(l)
               sappName = self.rc_appName.search(l)

               if not ssip == None:
                   sip = ssip.group(0).strip(', ')
               else:
                   continue
               if not sdip == None:
                   dip = sdip.group(0).strip(', ')
               else:
                   continue
               if not sact == None:
                   act = sact.group(0).strip()
               else:
                   continue
               if not sproto == None:
                   proto = sproto.group(0).strip(', ')
               else:
                   continue
               if not sappName == None:
                   appName = sappName.group(0).strip(', ')
               else:
                   continue
               ls = l.split()
               if len(ls) < 15:
                   continue
               #self.logger.debug(l)
               #self.logger.debug(ls[0]+" "+ls[1]+" "+ls[2])
               t,date = timestamp(ls[0],ls[1],ls[2])
               if self.current_date != date:
                   self.current_date = date
                   self.tb = self.tb_name + '_' + date
                   executemany_sql(mysql_insert_cmd,args)
                   args = []
                   sql = """CREATE TABLE IF NOT EXISTS `%s` (
                     `id` bigint(20) NOT NULL AUTO_INCREMENT,
                     `iTime` int(11) NOT NULL COMMENT '时间',
                     `sAppName` varchar(128) NOT NULL COMMENT '应用名称',
                     `sSourceIP` varchar(64) DEFAULT NULL COMMENT '源地址',
                     `sProtocol` varchar(64) DEFAULT NULL COMMENT '协议',
                     `sTargetIP` varchar(64) DEFAULT NULL COMMENT '目标地址',
                     `sAction` varchar(64) NOT NULL COMMENT '动作',
                     PRIMARY KEY (`id`),
                     KEY `I_iTimeAppName` (`iTime`,`sAppName`)
                     ) ENGINE=MyISAM AUTO_INCREMENT=57 DEFAULT CHARSET=utf8 COMMENT='应用管理日志';""" % self.tb

                   #self.mysql_db_cur.execute(sql)
                   execute_sql(sql)

               mysql_insert_cmd = "insert into " + self.tb + "(iTime,sAppName,sSourceIP,sProtocol,sTargetIP,sAction)" +" values(%s,%s,%s,%s,%s,%s)"
               #self.mysql_db_cur.execute(mysql_insert_cmd,(t,appName,sip,proto,dip,act))
               args.append((t,appName,sip,proto,dip,act))
               count += 1
               if count == 5000:
                   where = log_file.tell()
                   #self.logger_debug("APP_ADMIN:commiting ...... at where = %d" % where)
                   #self.mysql_db_conn.commit()
                   executemany_sql(mysql_insert_cmd,args)
                   self.log_record.set_record("app_admin",where)
                   #self.logger_debug("APP_ADMIN:commiting DONE!!!")
                   count = 0
                   done = True

               #self.logger.debug(time +  sip + dip)
            #insert to mysql
            if not count == 0:
                where = log_file.tell()
                #self.logger_debug("APP_ADMIN:commiting ...... at where = %d" % where)
                #self.mysql_db_conn.commit()
                executemany_sql(mysql_insert_cmd,args)
                self.log_record.set_record("app_admin",where)
                #self.logger_debug("APP_ADMIN:commiting DONE!!!")

        except Exception as e:
#            self.logger.debug(e)
             where = log_file.tell()
             #self.logger_debug("APP_ADMIN:commiting ...... at where = %d" % where)
             executemany_sql(mysql_insert_cmd,args)
             self.log_record.set_record("app_admin",where)
             #self.logger_debug("APP_ADMIN:commiting DONE!!! with exception")
             FWLOG_DEBUG(e)

        finally:
            log_file.close()
            del log_file

    def run(self):
        while True:
            if self.event.isSet():
                return
            self.init_db()
            #self.logger_debug("APP_ADMIN:importing %s" % self.path)
            self.app_admin()
            #self.logger_debug("APP_ADMIN:%s import done" % self.path)

            #self.record_lines(self.mysql_db_cur,self.tb_name)
            #self.mysql_db_cur.close()
            #self.mysql_db_conn.close()
            time.sleep(self.time_interval)

    def stop(self):
        self.event.set()
        self.join()
        #self.logger_debug("APP_ADMIN:STOP")
        FWLOG_DEBUG('APP_ADMIN:STOP')

    def start(self):
        super(MysqlGetTblogAppAdmin,self).start()
        #self.logger_debug('APP_ADMIN:START')
        FWLOG_DEBUG('APP_ADMIN:START')


if __name__ == '__main__':
    if already_running(__file__):
        exit(0)
    else:
        MysqlGetTblogAppAdmin().run()
        FWLOG_DEBUG('APP_ADMIN log:START')

#importlog().app_admin()
