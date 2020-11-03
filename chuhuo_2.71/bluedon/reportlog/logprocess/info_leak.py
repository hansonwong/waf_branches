#!/usr/bin/env python
# coding=utf-8

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
import cgi
from log_process_base import LogProcessBase
from utils.log_logger import FWLOG_DEBUG, FWLOG_ERR


class LogInfoLeak(LogProcessBase):


    def __init__(self):
        keys = [
            'iTime','sFileKeywork','sFilterType','sSourceIP',
            'sProtocol','sTargetIP','sStatus',
            'iCount'
        ]
        super(LogInfoLeak,self).__init__('info_leak','m_tblog_info_leak',
                                     '/var/log/suricata/smtp.log',keys)


    def parser_line(self, line):
        if not line:
            return self.null

        try:
            #self.logger.debug(l)
            #for l in log_file:

            ls = line.split()
            if len(ls) < 7:
                FWLOG_DEBUG('log_split_info_leak:len too short[%s]' % line)
                return self.null

            if len(ls) > 7:
                keyword = (' ').join(ls[1:-5])
            else:
                keyword = ls[1]
            keyword = cgi.escape(keyword)
            ds = ls[0].split('.')[0]
            t,date = self.get_ts_date(ds, '%m/%d/%Y-%H:%M:%S')
            stat = ls[-1].lstrip('[').rstrip(']')

            res = (str(t) + '|' + keyword + '|' + ls[-5] + '|' + ls[-4] + '|'
                   + ls[-2] + '|' + ls[-3] + '|' + stat)

            return res, date

        # except:
        except Exception as e:
            print e
            FWLOG_ERR('%s get wrong line: [%s]' % (self.tb_name, line))
            return self.null


    def other_jobs(self, args):
        pass


if __name__ == '__main__':
    infoleak = LogInfoLeak()
    s = time.time()
    # infoleak.main_loop()
    infoleak.start()
    time.sleep(10)
    print 'time up'
    infoleak.stop()
    print 'Use time = %s' % (time.time() - s)
    pass
