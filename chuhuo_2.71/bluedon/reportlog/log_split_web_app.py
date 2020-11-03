#!/usr/bin/env python
# coding=utf-8


import os
import sys
import time
import commands
import threading
from db.config import fetchall_sql as fcal_3306
from db.config1 import execute_sql as exec_3307
from db.config1 import executemany_sql as execmany_3307
from reportlog.log_size_record import log_size_record
from reportlog.log_statistics import webapp_log_statistics
from reportlog.mysql_get_tblog import MysqlGetTblog
from db.mysql_observer import MysqlObserver
from utils.log_logger import FWLOG_DEBUG

LOG_PATH = r'/var/log/bdwaf/logs/audit/'
CMP_TMP = r'/tmp/web_audit_compare_file'
FIND_FILES = ('find {p:} -newer {f:} -type f').format(p=LOG_PATH, f=CMP_TMP)
TOUCH_CMP_TMP = ('touch -t %s {f:}').format(f=CMP_TMP)
MAX_COUNT_PER_TIME = 5000


def get_file_name(new_time, path=LOG_PATH):
    pass


class MysqlGetTblogWebApp(MysqlGetTblog):

    event = threading.Event()

    def __init__(self):
        super(MysqlGetTblogWebApp, self).__init__()
        self.recorder = log_size_record()
        self.files = []
        self.newest_time = 0
        self.current_date = ''
        self.rules = {}
        self.log_rules = []
        self.tb = None

        self.update_rules()
        # sql = ('select sRealID,sRuleName,sType '
        #        'from m_tbwebapplication_lib')
        # for res in fcal_3306(sql):
        #     self.rules[res['sRealID']] = (res['sRuleName'],res['sType'])

        MysqlObserver.add_observer('m_tbwebapplication_lib', self.update_rules)
        MysqlObserver.add_observer('m_tbwebapplication_strategy', self.update_rules)
        MysqlObserver.add_observer('m_tbwebapplication_protected', self.update_rules)

    def file_scanner(self):
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
            # parser file
            try:
                self.newest_time = int(os.path.getmtime(_file))
                parser.send(_file)
            except:
                pass

        parser.next()
        self.save_time_record()
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
            return time.strftime('%Y%m%d%H%M.%S',time.localtime(int(ts) + 1))

        self.newest_time = self.recorder.get_record()["web_app"]
        _newest_time = ts_to_s(self.newest_time)
        os.system(TOUCH_CMP_TMP % _newest_time)

    def save_time_record(self):
        """
            Description:
                save the newest_time to database
        """
        self.recorder.set_record("web_app", self.newest_time)


    def commit_records(self):
        if self.args:
            webapp_log_statistics(self.args)
            self.args = []
        if self.log_args:
            sql = ('insert into `{}` '
                   '(iTime, sEventName, sSourceIP, sBugType, sTargetIP,'
                   'sStatus, sSeverity) values(%s,%s,%s,%s,%s,'
                   '%s,%s)').format(self.tb)
            execmany_3307(sql, self.log_args)
            self.log_args = []


    def parser(self):
        """
            Description:
                do the parser job
        """
        count = 0
        self.args = []
        self.log_args = []
        while 1:
            path = yield
            if path:
                self._parser(path, self.args, self.log_args)
                count += 1
            else:
                count = MAX_COUNT_PER_TIME + 1

            if count >= MAX_COUNT_PER_TIME:
                if self.args:
                    webapp_log_statistics(self.args)
                if self.log_args:
                    sql = ('insert into `{}` '
                           '(iTime, sEventName, sSourceIP, sBugType, sTargetIP,'
                           'sStatus, sSeverity) values(%s,%s,%s,%s,%s,'
                           '%s,%s)').format(self.tb)
                    execmany_3307(sql, self.log_args)
                count = 0
                self.args = []
                self.log_args = []
                pass

    def _parser(self,path,args,log_args):
        with open(path, 'r') as fp:
            lines = fp.readlines()
        idd = {'-A--': 0, '-B--': 0, '-F--': 0, '-H--': 0, '-Z--': 0}
        ts = 0
        SourceIP = None
        host = None
        stat = ''
        event_id = ''
        severity = ''

        for l in lines:
            if len(l) < 5: continue
            phase = l[-5:-1]
            if phase in idd.keys():
                idd[phase] = lines.index(l) + 1
        # phase A
        if idd['-B--'] - idd['-A--'] > 0:
            ts, SourceIP = self.phase_A(lines[idd['-A--']: idd['-B--'] - 1])

        if idd['-F--'] - idd['-B--'] > 0:
            host = self.phase_B(lines[idd['-B--']: idd['-F--'] - 1])

        if idd['-H--'] - idd['-F--'] > 0:
            pass
            # if not self.phase_F(lines[idd['-F--']: idd['-H--'] - 1]):
            #     return

        if idd['-Z--'] - idd['-H--'] > 0:
            stat,event_id,severity = self.phase_H(lines[idd['-H--']: idd['-Z--'] - 1])
            if event_id == '':
                return
            if self.rules.has_key(event_id):
                #print event_id
                event_name = self.rules[event_id][0]
                event_type = self.rules[event_id][1]
                if event_id in self.log_rules:
                    log_args.append((ts,event_name,SourceIP,event_type,host,stat,severity))
            else:
                event_name = 'Null'
                event_type = 'Null'

        args.append((ts,event_name,SourceIP,event_type,host,stat,severity))
        pass

    def phase_A(self, lines):
        items = lines[0].split()
        if len(items) < 6:
            return '','',''
        ta = time.strptime(items[0].lstrip('[').rstrip(']'), "%d/%b/%Y:%H:%M:%S")
        date = time.strftime('%Y%m%d', ta)
        if self.current_date != date:
            self.current_date = date
            if self.tb is not None:
                self.commit_records()
            self.tb = 'm_tblog_webapplication' + '_' + self.current_date
            sql = ("CREATE TABLE IF NOT EXISTS `%s` "
                   "LIKE m_tblog_webapplication")
            exec_3307(sql % self.tb)
        ts = int(time.mktime(ta))
        sIP = items[3]
        # dIP = items[5]
        return ts,sIP
        pass

    def phase_B(self, lines):
        Host = ''
        for line in lines:
            if line[0:5] == 'Host:':
                Host = line[5:].strip().strip('\n')
        return Host
        pass

    def phase_F(self, lines):
        pass

    def phase_H(self, lines):
        status = {'alow': 'Access allowed',
                  'deny': 'denied with code',
                  'drop': 'denied with connection close',
                  'warning': 'Warning'}

        stat = ''
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



if __name__ == '__main__':
    wa = MysqlGetTblogWebApp()
    wa.file_scanner()
    # wa.update_rules()
    # wa._parser('/var/log/bdwaf/logs/audit/20160425/20160425-0858/20160425-085812-BcAc5iAcVcAcAcAAAfAcAcAc')
