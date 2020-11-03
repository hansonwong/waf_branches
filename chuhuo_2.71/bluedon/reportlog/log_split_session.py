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

import time
import os
import threading
from logging import getLogger

from db.config1 import execute_sql, executemany_sql, search_data
from reportlog.mysql_get_tblog import already_running, MysqlGetTblog
from utils.log_logger import FWLOG_DEBUG


_PATH = "/var/log/suricata/session.log"
#_PATH = "/usr/local/bluedon/tmp/session.log"


def timestamp(path):
    uptime = int(os.stat(path).st_mtime)
    tbtime = time.localtime(uptime)
    tbtime = time.strftime('%Y%m%d', tbtime)
    return int(uptime), tbtime


class MysqlGetTblogSession(MysqlGetTblog):

    event = threading.Event()

    def __init__(self, path=_PATH):
        super(MysqlGetTblogSession, self).__init__()
        self.path = path
        self.current_date = ''
        self.tb = ''
        self.time_interval = 1
        self.tb_name = "m_tbfwsessionstatus"

        self.st = 0
        self.et = 0

    def session_status(self):
        if not os.path.exists(self.path):
            getLogger('log_daemon').debug('SESSION STATUS File %s is NOT EXISTS!!!' % self.path)
            return

        uptime, tbtime = timestamp(self.path)
        self.tb = self.tb_name + '_' + tbtime
        search_table = "select table_name from `INFORMATION_SCHEMA`.`TABLES`\
            where table_name ='{0}' and TABLE_SCHEMA='db_firewall_log';".format(self.tb)
        if not search_data(search_table):
            creat_table = "CREATE TABLE IF NOT EXISTS `{0}` LIKE m_tbfwsessionstatus".format(self.tb)
            # creat_index = "CREATE INDEX i_updatetime ON {0} (sUpdateTime);".format(self.tb)
            execute_sql(creat_table)
            # execute_sql(creat_index)
        else:
            if not os.path.getsize(self.path):
                update_sql = 'UPDATE {0} SET iStatus=0 WHERE sUpdateTime > {st} and \
                    sUpdateTime < {et} and iStatus=1;'.format(self.tb, st=self.st, et=self.et)
                # update_sql = 'UPDATE {0} SET iStatus=0 WHERE iStatus=1;'.format(self.tb)
                execute_sql(update_sql)
                return

        def proc_sql(tbname, args, source_args, target_args):
            if not args:
                return

            # 插入数据前先将之前数据状态改为0(断开连接)
            update_sql = 'UPDATE {0} SET iStatus=0 WHERE sUpdateTime > {st} and \
                sUpdateTime < {et} and iStatus=1;'.format(tbname, st=self.st, et=self.et)
            execute_sql(update_sql)

            mysql_insert_cmd = ("insert into " + tbname + "(sMark, "
                                "sSourceIp, iSourcePort, sTargetIP, iTargetPort, "
                                "sProtocal, sAcProtocal, sCreatTime, sLastTime, "
                                "sOverTime, iStatus, sUpdateTime)"
                                " values('%s','%s',%s,'%s',%s,'%s','%s',%s,%s,'%s','%s',%s)")
            mysql_update_cmd = "update " + tbname + " set sLastTime=%s,sUpdateTime=%s where sMark='%s'"
            s_count = "insert into m_tbfwsessionstatus_sourceip(sSourceIp,\
                sProto,sCount) VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE sCount= (sCount+1);"
            d_count = "insert into m_tbsessionstatus_targetip(sTargetIp,\
                sProto,sCount) VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE sCount= (sCount+1);"
            search_mark = "select sMark from "+ self.tb + " where sMark ='%s';"
            for arg in args:
                if not search_data(search_mark % arg[0]):
                    execute_sql(mysql_insert_cmd % arg)
                else:
                    execute_sql(mysql_update_cmd % (arg[8], arg[11], arg[0]))
            executemany_sql(s_count, source_args)
            executemany_sql(d_count, target_args)

        count = 0
        args = []
        source_args = []
        target_args = []
        log_file = open(self.path, 'r')

        try:
            for line in log_file:
                if line == '':
                    continue
                words = line.split(',')
                if len(words) < 9:
                    FWLOG_DEBUG('SESSION STATUS log_split_Session:len too short {0}'.format(words))
                    #raise RuntimeError('log_split_Session:len too short')
                    continue

                mark = words[0]
                sip = words[1]
                sport = words[2]
                dip = words[3]
                dport = words[4]
                proto = words[5]
                app_proto = words[6]
                ctime = int(time.mktime(time.strptime(words[7], '%Y-%m-%d %H:%M:%S')))
                udtime = int(time.mktime(time.strptime(words[8].strip('\n'), '%Y-%m-%d %H:%M:%S')))

                source_args.append((sip, proto, 1))
                target_args.append((dip, proto, 1))

                args.append((mark, sip, sport, dip, dport, proto, app_proto,
                             ctime, udtime, '0', '1', uptime))

                count += 1
                if count == 5000:
                    self.st = self.et
                    self.et = uptime
                    proc_sql(self.tb, args, source_args, target_args)
                    count = 0
                    args = []
                    source_args = []
                    target_args = []
            if not count == 0:
                self.st = self.et
                self.et = uptime
                proc_sql(self.tb, args, source_args, target_args)
        except Exception as e:
            proc_sql(self.tb, args, source_args, target_args)
            FWLOG_DEBUG(e)
        finally:
            log_file.close()
            del log_file

    def run(self):
        while True:
            if self.event.isSet():
                return
            self.session_status()

            time.sleep(self.time_interval)
            FWLOG_DEBUG('done')

    def stop(self):
        self.event.set()
        self.join()
        FWLOG_DEBUG('Session: STOP')

    def start(self):
        super(MysqlGetTblogSession, self).start()
        FWLOG_DEBUG('Session:START')


if __name__ == '__main__':
    if already_running(__file__):
        exit(0)
    else:
        MysqlGetTblogSession().session_status()
        #session = MysqlGetTblogSession()
        #session.session_status()
        FWLOG_DEBUG('Session log:START')

