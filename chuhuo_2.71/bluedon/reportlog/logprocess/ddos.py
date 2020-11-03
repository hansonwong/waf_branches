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
from ..log_statistics import ddos_log_statistics_new
from db.mysql_observer import MysqlObserver
from utils.log_logger import FWLOG_DEBUG, FWLOG_ERR


class LogDDOS(LogProcessBase):


    def __init__(self):
        keys = [
            'iTime','sEventName','sSourceIP','sThreshold','sTargetIP','sStatus',
            'iCount'
        ]
        super(LogDDOS,self).__init__('ddos_log','m_tblog_ddos',
                                     '/var/log/ddos/bd_ddos.log',keys)


    def parser_line(self, line):
        if not line:
            return self.null

        try:
            # old
            # ssip = self.rc_sip.search(l)
            # sdip = self.rc_dip.search(l)
            # sevent = self.rc_event.search(l)
            # sthres = self.rc_thres.search(l)

            # sip = ssip.group(0).strip()
            # dip = sdip.group(0).strip()
            # event = sevent.group(0).strip()
            # thres = sthres.group(0).strip()
            two_sp = line.split(',')

            ls = two_sp[1].split()
            if len(ls) < 4:
                FWLOG_DEBUG('log_split_ddos:len too short[%s]' % line)
                return self.null

            darg = { i.split('=')[0]: i.split('=')[1] for i in ls if len(i.split('=')) == 2}

            event = darg['EVENT']
            sip = darg['SIP']
            dip = darg['DIP']
            thres = darg['THRES']

            #self.logger.debug(l)
            #self.logger.debug(ls[0]+" "+ls[1]+" "+ls[2])
            t, date = self.get_ts_date(two_sp[0], '%a %b %d %H:%M:%S %Y')

            # 'iTime','sEventName','sSourceIP','sThreshold','sTargetIP','sStatus'
            res = (str(t) + '|' + event + '|' + sip + '|' + thres + '|'
                   + dip + '|' + str(0))
            # print res

            return res ,date

        except:
            FWLOG_ERR('%s get wrong line: [%s]' % (self.tb_name, line))
            return self.null



    def other_jobs(self, args):
        pass
        _args = [tuple(line.split('|')) for line in args]
        ddos_log_statistics_new(_args)


if __name__ == '__main__':
    ddos = LogDDOS()
    s = time.time()
    # ddos.main_loop()
    ddos.start()
    time.sleep(10)
    print 'time up'
    ddos.stop()
    print 'Use time = %s' % (time.time() - s)
    pass
