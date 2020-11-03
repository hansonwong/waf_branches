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


class LogURL(LogProcessBase):


    def __init__(self):
        keys = [
            'iTime,sUrl','sSourceIP','sWebType','sTargetIP','sAction',
            'iCount'
        ]
        super(LogURL,self).__init__('url_log','m_tblog_url_visit',
                                         '/var/log/bdwaf/logs/url_filter.log',keys)


    def parser_line(self, line):
        if not line:
            return self.null

        try:
            ls = line.split()
            if len(ls) < 6:
                FWLOG_DEBUG('log_split_url:len too short[%s]' % line)
                return self.null

            isIP = lambda x :x if len(x.split('.')) == 4 else 'Null'
            ssip = isIP(ls[2])
            sdip = isIP(ls[3])
            dt = ls[0].lstrip('[') + ' ' + ls[1].rstrip(']')

            t, date = self.get_ts_date(dt, '%Y/%m/%d %H:%M:%S')

            sUrl = str(ls[5:]).lstrip('[').rstrip(']').encode('string-escape')
            sUrl = sUrl[2:-2]
            sUrl = cgi.escape(sUrl)

            res = (str(t) + '|' + sUrl + '|' + ssip + '|' + ls[4] + '|'
                   + sdip + '|0')


            return res, date

        # except:
        except Exception as e:
            print e
            FWLOG_ERR('%s get wrong line: [%s]' % (self.tb_name, line))
            return self.null



    def other_jobs(self, args):
        pass


if __name__ == '__main__':
    url = LogURL()
    s = time.time()
    # url.main_loop()
    url.start()
    time.sleep(10)
    print 'time up'
    url.stop()
    print 'Use time = %s' % (time.time() - s)
    pass
