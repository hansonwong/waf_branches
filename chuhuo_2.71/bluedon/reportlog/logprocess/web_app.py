#!/usr/bin/env python
# coding=utf-8


import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
import random
import string
import threading
import Queue
import commands
from multiprocessing import Pool, Manager
from db.config1 import execute_sql as exec_3307
from db.config import fetchall_sql as fcal_3306
from db.config1 import executemany_sql as execmany_3307
from reportlog.log_statistics import webapp_log_statistics
from log_process_base import LogProcessBase
# from reportlog.log_size_record import log_size_record
from ..log_size_record import log_size_record
# from reportlog.log_statistics import ips_log_statistics_new
from ..log_statistics import webapp_log_statistics_new
from db.mysql_observer import MysqlObserver
from utils.log_logger import FWLOG_DEBUG, FWLOG_ERR

LOG_PATH = r'/var/log/bdwaf/logs/audit/'
CMP_TMP = r'/tmp/web_audit_compare_file'
FIND_FILES = ('find {p:} -newer {f:} -type f').format(p=LOG_PATH, f=CMP_TMP)
TOUCH_CMP_TMP = ('touch -t %s {f:}').format(f=CMP_TMP)
MAX_COUNT_PER_TIME = 5000


class WebApp(LogProcessBase):
    def __init__(self):
        keys = [
            'iTime', 'sEventName', 'sSourceIP', 'sBugType', 'sTargetIP',
            'sStatus', 'sSeverity', 'iEventID'
        ]
        super(WebApp, self).__init__('web_app','m_tblog_webapplication',
                                     '/var/log/bdwaf/logs/audit',keys)

        self.recorder = log_size_record()
        self.files = []
        self.newest_time = 0
        self.current_date = ''
        self.rules = {}
        self.log_rules = []
        self.tb = 'm_tblog_webapplication'

        self.update_rules()
        MysqlObserver.add_observer('m_tbwebapplication_lib', self.update_rules)
        MysqlObserver.add_observer('m_tbwebapplication_strategy', self.update_rules)
        MysqlObserver.add_observer('m_tbwebapplication_protected', self.update_rules)

    def parser_line(self, line):
        if not line:
            return ('','')


    # args is a list of strings of keys
    def other_jobs(self, args):
        pass
        # _args = [tuple(line.split('|')) for line in args]
        # ips_log_statistics_new(_args)

    def main_loop(self):
        """
            Description:
                Use a cmp tmp file to find newer files, everytime files get
                processed done, record the newest_time in database
        """
        parser = self.parser()
        parser.next()
        # update newest_time from database and touch cmp file
        self.touch_cmp_tmp()
        # get new file path
        self.get_new_files()
        for _file in self.files:
            if self.event.isSet(): break
            # parser file
            if not _file: continue
            try:
                ntime = os.path.getmtime(_file)
                parser.send(_file)
                # print 'parsering {} done'.format(_file)
            except:
                pass
            finally:
                self.newest_time = int(ntime)

        parser.next()
        self.save_time_record()
        time.sleep(0.2)
        # break
        pass

    def get_new_files(self):
        """
            Description:
                Use `find` cmd and a tmp file find new files
        """
        self.files = commands.getoutput(FIND_FILES).split('\n')
        self.files.sort(key=self.file_datetime)
        return len(self.files)

    def file_datetime(self, path):
        """
            Description:
                return datetime of a file path
        """
        dt = ''.join(path.split('/')[-1][0:15])
        return dt.replace('-','')

    def touch_cmp_tmp(self):
        """
            Description:
                Get newest_time from database and touch cmp file
        """
        def ts_to_s(ts):
            return time.strftime('%Y%m%d%H%M.%S',time.localtime(ts))

        self.newest_time = self.recorder.get_record()["web_app"]
        _newest_time = ts_to_s(self.newest_time + 1)
        os.system(TOUCH_CMP_TMP % _newest_time)

    def save_time_record(self):
        """
            Description:
                save the newest_time to database
        """
        self.recorder.set_record("web_app", self.newest_time)

    def parser(self):
        """
            Description:
                do the parser job
        """
        count = 0
        new_date = None
        res = None
        self.args = []
        self.log_args = []
        while 1:
            path = yield
            # if no files is found, path is None
            if path:
                try:
                    # get result and date of specified path
                    res, new_date = self._parser(path)
                    # at the beginning set current_date is new_date
                    if self.current_date == '':
                        self.current_date = new_date
                        self.tb = 'm_tblog_webapplication' + '_' + self.current_date
                        sql = ("CREATE TABLE IF NOT EXISTS `%s` "
                               "LIKE m_tblog_webapplication")
                        exec_3307(sql % self.tb)
                    count += 1
                except:
                    # log here
                    FWLOG_ERR('[WebApp] Error Processing [%s]' % path)
                    continue
                finally:
                    os.remove(path)
                # if No result is return just continue
                if res is None or new_date is None:
                    FWLOG_ERR('[WebApp] Get None Processing [%s]' % path)
                    if self.event.isSet(): break
                    time.sleep(0.2)
                    continue
            else:
                # print 'THE END'
                # if path is None, process current result
                count = MAX_COUNT_PER_TIME + 1

            # time to commit result
            if count >= MAX_COUNT_PER_TIME or self.current_date != new_date:
                # print 'Committing...'
                # print '------------------------------------------------------'
                # if new date has come
                if new_date is not None and self.current_date != new_date:
                    self.tb = 'm_tblog_webapplication' + '_' + self.current_date
                    sql = ("CREATE TABLE IF NOT EXISTS `%s` "
                           "LIKE m_tblog_webapplication")
                    exec_3307(sql % self.tb)
                    self.current_date = new_date
                if self.args:
                    webapp_log_statistics(self.args)
                # if self.log_args:
                    sql = ('insert into `{}` '
                           '(iTime, sEventName, sSourceIP, sBugType, sTargetIP,'
                           'sStatus, sSeverity, iEventID) values(%s,%s,%s,%s,%s,'
                           '%s,%s,%s)').format(self.tb)
                    # execmany_3307(sql, self.log_args)
                    execmany_3307(sql, self.args)
                count = 0
                self.args = []
            # after committing the old resutl put result into args list
            if res is not None:
                self.args.append(res)

    def _parser(self,path):
        with open(path, 'r') as fp:
            lines = fp.readlines()
        idd = {'-A--': 0, '-B--': 0, '-F--': 0, '-H--': 0, '-Z--': 0}
        ts = 0
        SourceIP = '-'
        host = '-'
        stat = '-'
        event_id = '-'
        severity = '-'
        res = None
        date = None

        for l in lines:
            if len(l) < 5: continue
            phase = l[-5:-1]
            if phase in idd.keys():
                idd[phase] = lines.index(l) + 1
        # print idd
        # phase A
        if idd['-B--'] - idd['-A--'] > 0:
            ts, SourceIP, date = self.phase_A(lines[idd['-A--']: idd['-B--'] - 1])

        if idd['-F--'] - idd['-B--'] > 0:
            host = self.phase_B(lines[idd['-B--']: idd['-F--'] - 1])

        if idd['-H--'] - idd['-F--'] > 0:
            pass
            # if not self.phase_F(lines[idd['-F--']: idd['-H--'] - 1]):
            #     return

        if idd['-Z--'] - idd['-H--'] > 0:
            stat,event_id,severity = self.phase_H(lines[idd['-H--']: idd['-Z--'] - 1])
            if event_id == '':
                return None, None
            if self.rules.has_key(event_id):
                event_name = self.rules[event_id][0]
                event_type = self.rules[event_id][1]
            else:
                event_name = 'Null'
                event_type = 'Null'

        # args.append((ts,event_name,SourceIP,event_type,host,stat,severity))
        res = (ts,event_name,SourceIP,event_type,host,stat,severity, str(event_id))
        return res, date
        pass

    def phase_A(self, lines):
        # print 'phase_A'
        items = lines[0].split()
        if len(items) < 6:
            return '-','-','-'
        ta = time.strptime(items[0].lstrip('[').rstrip(']'), "%d/%b/%Y:%H:%M:%S")
        date = time.strftime('%Y%m%d', ta)
        # if self.current_date != date:
        #     self.current_date = date
        #     self.tb = 'm_tblog_webapplication' + '_' + self.current_date
        #     sql = ("CREATE TABLE IF NOT EXISTS `%s` "
        #            "LIKE m_tblog_webapplication")
        #     exec_3307(sql % self.tb)
        ts = int(time.mktime(ta))
        sIP = items[3]
        # dIP = items[5]
        return ts,sIP,date
        pass

    def phase_B(self, lines):
        # print 'phase_B'
        # print lines
        Host = ''
        for line in lines:
            if line[0:5] == 'Host:':
                Host = line[5:].strip().strip('\n')
                # print Host
        return Host
        pass

    def phase_F(self, lines):
        # print 'phase_F'
        # print lines
        pass

    def phase_H(self, lines):
        status = {'alow': 'Access allowed',
                  'deny': 'denied with code',
                  'drop': 'denied with connection close',
                  'warning': 'Warning'}

        stat = '-'
        # print 'phase_H'
        # print lines
        for ss in status:
            if status[ss] in lines[0]:
                stat = ss

        items = lines[0].split()
        try:
            idx_id = items.index('[id')
            event_id = items[idx_id + 1].rstrip(']').strip('"')
        except ValueError:
            event_id = ''

        try:
            idx_se = items.index('[severity')
            severity = items[idx_se + 1].rstrip(']').strip('"')
        except ValueError:
            severity = 'OTHER'
        return stat,event_id,severity
        pass

    def update_rules(self, *args, **kwargs):
        t = 0
        # while 1:
        #if int(time.time()) - t > 60:
            # update per minute
        #     t = int(time.time())
        sql = ('select sRealID,sRuleName,sType '
               'from m_tbwebapplication_lib')

        for res in fcal_3306(sql):
            self.rules[res['sRealID']] = (res['sRuleName'],res['sType'])

        # get log rules
        sql = """SELECT
                     sRuleIDS
                 FROM
                     m_tbwebapplication_strategy
                 INNER JOIN m_tbwebapplication_protected ON m_tbwebapplication_strategy.sStrategyTemplate = m_tbwebapplication_protected.id
                 WHERE
                    m_tbwebapplication_strategy.iLog != 0;"""

        self.log_rules = []
        for res in fcal_3306(sql):
            ids = res['sRuleIDS'].strip(',').split(',')
            self.log_rules.extend(ids)


    def other_jobs(self, args):
        # done in parser
        pass
        # _args = [tuple(line.split('|')) for line in args])
        # webapp_log_statistics_new(_args)


if __name__ == '__main__':
    webapp = WebApp()
    s = time.time()
    # webapp.main_loop()
    webapp.start()
    time.sleep(10)
    print 'time up'
    webapp.stop()
    print 'Use time = %s' % (time.time() - s)
    pass
