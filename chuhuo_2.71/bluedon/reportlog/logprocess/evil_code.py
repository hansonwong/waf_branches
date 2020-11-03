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
from ..log_statistics import evilcode_log_statistics_new
from db.mysql_observer import MysqlObserver
from utils.log_logger import FWLOG_DEBUG, FWLOG_ERR


class LogEvilCode(LogProcessBase):


    def __init__(self):
        keys = [
            'iTime','sViruesName','sSourceIP','sProtocol',
            'sTargetIP','sStatus','sLogLevel','sFileName',
            'iCount'
        ]
        super(LogEvilCode,self).__init__('evil_code','m_tblog_evil_code',
                                     '/var/log/suricata/AvScan.log',keys)


    def parser_line(self, line):
        if not line:
            return self.null

        try:
            ls = line.split()
            if len(ls) < 7:
                FWLOG_DEBUG('log_split_evilcode: len too short[%s]' % line)
                return self.null
            ds = ls[0].split('.')[0]
            t, date = self.get_ts_date(ds, '%m/%d/%Y-%H:%M:%S')

            stat = ls[-1].lstrip('[').rstrip(']')
            level = ls[1]
            vn = ls[-6].encode('string-escape')
            fn = ls[-5].encode('string-escape')
            res = (str(t) + '|' + vn + '|' + ls[-4] + '|' + ls[-2] + '|'
                   + ls[-3] + '|' + stat + '|' + level + '|' + fn)

            # print res ,date
            return res ,date

        except:
            FWLOG_ERR('%s get wrong line: [%s]' % (self.tb_name, line))
            return self.null

    def other_jobs(self, args):
        _args = [tuple(line.split('|')) for line in args]
        evilcode_log_statistics_new(_args)
        pass

if __name__ == '__main__':
    ddos = LogEvilCode()
    s = time.time()
    # ddos.main_loop()
    ddos.start()
    time.sleep(20)
    print 'time up'
    ddos.stop()
    print 'Use time = %s' % (time.time() - s)
    pass
