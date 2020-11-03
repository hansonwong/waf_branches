#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
Usage:
    mysql_get_tblog_ips.py -h --help
    mysql_get_tblog_ips.py [-t <time>] [--loglevel=<log_level>]
    mysql_get_tblog_ips.py --reset

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
import datetime
from os.path import getsize
from logging import getLogger
# from docopt import docopt
from db.config1 import execute_sql,executemany_sql,fetchone_sql
from db.config import fetchall_sql as fcal_3306
from db.config import fetchone_sql as fetch_3306
from reportlog.log_size_record import log_size_record
from reportlog.log_statistics import ips_log_statistics
from reportlog.mysql_get_tblog import already_running,MysqlGetTblog
from db.mysql_observer import MysqlObserver
from utils.log_logger import FWLOG_DEBUG

_path = "/var/log/suricata/fast.log"
CUSTOM_IPS_LIB = 'm_tbcustom_ips_lib'
#ip_reg = r"(\d{1,3}\.){3}\d{1,3}"
ip_reg = ".*:"
time_reg = r"\d\d/\d\d/\d\d\d\d-\d\d:\d\d:\d\d"
status_reg = r'Alert|Drop|Pass|Reject|wDrop'
def datetime_timestamp(ds):
    ts = time.strptime(ds,'%m/%d/%Y-%H:%M:%S')
    s = time.mktime(ts)
    date = time.strftime('%Y%m%d',ts)
    return int(s),date


class MysqlGetTblogIps(MysqlGetTblog):

    event = threading.Event()

    def __init__(self,path = _path):
        super(MysqlGetTblogIps,self).__init__()
        #self.logger = create_logger("log",logging.DEBUG)
        self.log_record = log_size_record()
        self.path = path
        self.current_date = ''
        self.tb = ''
        self.ips_rules = {}
        self.get_ips_rules()
        self.update_time = datetime.datetime.fromtimestamp(0)
        MysqlObserver.add_observer('m_tbcustom_ips_lib', self.get_ips_rules)
        try:
            self.time_interval = 1
            self.tb_name = "m_tblog_ips"
            self.rc_time = re.compile(time_reg)
            self.rc_ip = re.compile(ip_reg)
            self.rc_stat = re.compile(status_reg)

            #self.logger.debug(result)
            #self.logger.debug("start...")
        except Exception as e:
            #self.logger.debug(e)
            FWLOG_DEBUG(e)

    def get_ips_rules(self, *args, **kwargs):
        sql = 'select sRuleID,sDesc,sRuleType,sDangerLever from m_tbcustom_ips_lib'
        for res in fcal_3306(sql):
            self.ips_rules[res['sRuleID']] =  res


    def fast_log(self):
        if not os.path.exists(self.path):
            getLogger('log_daemon').debug('File %s is NOT EXISTS!!!' % self.path)
            return

        # update custom_ips_lib if it had been updated
        # sql = ("SELECT UPDATE_TIME from information_schema.`TABLES` "
        #        "WHERE TABLE_NAME='m_tbcustom_ips_lib';")
        # update_time = fetch_3306(sql)['UPDATE_TIME']
        # if self.update_time < update_time:
        #     self.update_time = update_time
        #     self.get_ips_rules()

        protocol_reg = "\{.*\}"
        fast_log_file = open(self.path,"r")
        try:

            imported_size = self.log_record.get_record()["fast_log"]
            fsize = os.path.getsize(self.path) if os.path.exists(self.path) else 0

            #self.logger_debug("fast_log")
            #self.logger_debug("FAST_LOG:%s" % imported_size)
            #self.logger_debug("FAST_LOG:%s" % fsize)
            count = 0
            if imported_size == fsize:
                fast_log_file.close()
                return
            if imported_size > fsize:
                self.log_record.set_record("fast_log",0)
                fast_log_file.close()
                return

            #self.log_record.set_record("fast_log",fsize)


            fast_log_file.seek(imported_size,0)
            where = fast_log_file.tell()
            done  = False
            current_date = ''
            args = []
            mysql_insert_cmd = (
                "insert into " + self.tb
                + " (iTime,sEventName,sSourceIP,sTargetIP,sProtocol,sLogName,sRuleID,sStatus)"
                + " values(%s,%s,%s,%s,%s,%s,%s,%s)")

            while not done:
                l = fast_log_file.readline()
                if l == '':
                    done = True
                    continue
                sip = dip = protocol = ""

                ls = l.split("[**]")
                if len(ls) < 3:
                    FWLOG_DEBUG('log_split_ips:len too short %s' % ls)
                    raise RuntimeError('log_split_ips:len too short')
                    continue

                #stime = self.rc_time.search(ls[0])
                sstat = self.rc_stat.search(ls[0])

                el = ls[1].split()[1:]
                event = (' ').join(el)
                rID = ls[1].split()[0].split(':')[1]
                #event = event.strip("'")
                event = event.encode('string-escape')
                if rID in self.ips_rules:
                # try:
                    level = {u'高':'high',u'中':'medium',u'低':'low','':'low'}
                    _grade = self.ips_rules[rID]['sDangerLever']
                    grade = level[_grade]
                    desc = self.ips_rules[rID]['sDesc']
                    ruletype = self.ips_rules[rID]['sRuleType']
                else:
                # except:
                    grade = 'low'
                    desc = '-'
                    ruletype = '-'

                ip = ls[-1].split()
                ssip = self.rc_ip.search(ip[-3])
                sdip = self.rc_ip.search(ip[-1])
                rc_proto = re.compile(protocol_reg)
                sprotocol = rc_proto.search(ls[-1])

                #time = stime.group(0).strip()
                time = ls[0].split()[0].split('.')[0]
                if not ssip == None:
                    sip = ssip.group(0).strip().rstrip(":")
                else:
                    continue
                    pass
                if not sdip == None:
                    dip = sdip.group(0).strip().rstrip(":")
                else:
                    continue
                    pass
                if not sprotocol == None:
                    protocol = sprotocol.group(0).lstrip('{').rstrip('}')
                else:
                    continue
                    pass
                if not sstat == None:
                    stat = sstat.group(0).lstrip('[').rstrip(']')
                    stat = 'Drop' if stat == 'wDrop' else stat
                else:
                    if len(ls[0].split()) == 1 and l.split()[1] == '[**]':
                        stat = 'Alert'
                    else:
                        continue
                    pass


                t,date = datetime_timestamp(time)

                if self.current_date != date:
                    self.current_date = date
                    self.tb = self.tb_name + '_' + date
                    executemany_sql(mysql_insert_cmd,args)
                    ips_log_statistics(args)
                    args = []
                    sql ="CREATE TABLE IF NOT EXISTS `%s` LIKE m_tblog_ips" % self.tb
                    execute_sql(sql)

                mysql_insert_cmd = ("insert into " + self.tb + '  '
                                    "(iTime,sEventName,sSourceIP,sProtocol,"
                                    "sTargetIP,sStatus,sLogName,sRuleID,"
                                    "sGrade,sDesc,sRuleType)"
                                    " values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")

                args.append((t,event,sip,protocol,dip,stat,"fast_log",rID,grade,desc,ruletype))

                count += 1
                if count == 10000:
                    where = fast_log_file.tell()
                    #self.logger_debug("FAST_LOG:commiting ...... at where = %d" % where)
                    executemany_sql(mysql_insert_cmd,args)
                    ips_log_statistics(args)
                    self.log_record.set_record("fast_log",where)
                    #self.logger_debug("FAST_LOG:commiting DONE!!!")
                    count = 0
                    args = []
                    done = True


            if not count == 0:
                where = fast_log_file.tell()
                #self.logger_debug("FAST_LOG:commiting ...... at where = %d" % where)
                executemany_sql(mysql_insert_cmd,args)
                ips_log_statistics(args)
                self.log_record.set_record("fast_log",where)
                #self.logger_debug("FAST_LOG:commiting DONE!!!")
                args = []
        except Exception as e:
            #self.logger.debug(e)
            where = fast_log_file.tell()
            #self.logger_debug("FAST_LOG:commiting ...... at where = %d" % where)
            executemany_sql(mysql_insert_cmd,args)
            ips_log_statistics(args)
            self.log_record.set_record("fast_log",where)
            #self.logger_debug("FAST_LOG:commiting DONE with exception!!!")
            args = []
            FWLOG_DEBUG(e)

        finally:
            fast_log_file.close()
            del fast_log_file



    def run(self):
        while True:
            if self.event.isSet():
                return

            #self.logger_debug("IPS:importing fast.log")
            self.fast_log()
            #self.logger_debug("IPS:fast.log import done")

            time.sleep(self.time_interval)
            FWLOG_DEBUG('done')

    def stop(self):
        self.event.set()
        self.join()
        #self.logger_debug("IPS:STOP")
        FWLOG_DEBUG("IPS:STOP")

    def start(self):
        super(MysqlGetTblogIps,self).start()
        #self.logger_debug("IPS:START")
        FWLOG_DEBUG("IPS:START")


if __name__ == '__main__':
    if already_running(__file__):
        exit(0)
    else:
        #MysqlGetTblogIps().http_log()
        #MysqlGetTblogIps().timer(30)
        #MysqlGetTblogIps().filetest()
        #MysqlGetTblogIps().dns_log()
        #MysqlGetTblogIps().getlogline("http_log")
        MysqlGetTblogIps().run()
        #MysqlGetTblogIps().fast_log()
        #MysqlGetTblogIps().eve_json()
