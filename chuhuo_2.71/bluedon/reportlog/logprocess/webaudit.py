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


KEY_WORDS = ["iPhone","iPad","Android","iPod"]

class LogWebAudit(LogProcessBase):


    def __init__(self):
        keys = [
            'iTime','sShareHost','sTerminal','sTableName',
            'iCount'
        ]
        super(LogWebAudit,self).__init__('webaudit_log','m_tblog_wifi_audit',
                                     '/var/log/wifi_audit.log',keys)


    def parser_line(self, line):
        if not line:
            return self.null

        try:

            ls = line.split('#')
            if len(ls) < 3:
                FWLOG_DEBUG('webaudit log len too short [%s]' % line)
                return self.null

            t,date = self.get_ts_date(ls[0], '%a %b %d %H:%M:%S %Y')
            host = ls[1]
            term = ls[2].strip('\n')
            flag = False
            for key in KEY_WORDS:
                if key in term:
                    flag = True
                    break
            if not flag:
                return self.null

            res = (str(t) + '|' + host + '|' + term)

            return res, date

        except Exception as e:
            print e
            FWLOG_ERR('%s get wrong line: [%s]' % (self.tb_name, line))
            return self.null


    def save_to_file(self, args, name):
        _file = self.create_tmp_file(name)
        _insert = lambda x: x[0:x.rindex('|')] + '|' + name + x[x.rindex('|'):]
        args = [ _insert(item) for item in args ]

        with open(_file, 'a+') as fp:
            fp.write('\n'.join(args))

        return _file, name

    def other_jobs(self, args):
        pass


if __name__ == '__main__':
    webaudit = LogWebAudit()
    s = time.time()
    # webaudit.main_loop()
    webaudit.start()
    time.sleep(10)
    print 'time up'
    webaudit.stop()
    print 'Use time = %s' % (time.time() - s)
    pass
