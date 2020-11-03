#!/usr/bin/env python
# coding=utf-8


import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
from db.config import fetchall_sql as fcal_3306
from log_process_base import LogProcessBase
from ..log_statistics import ips_log_statistics_new
from utils.log_logger import FWLOG_DEBUG, FWLOG_ERR


def get_ips_rules():
    sql = 'select sRuleID,sDesc,sRuleType,sDangerLever from m_tbcustom_ips_lib'
    ips_rules = {}
    for res in fcal_3306(sql):
        ips_rules[res['sRuleID']] =  res
    return ips_rules

class LogIPS(LogProcessBase):
    def __init__(self):
        keys = [
            'iTime','sEventName','sSourceIP','sProtocol','sTargetIP',
            'sStatus','sLogName','sRuleID','sGrade','sDesc','sRuleType','iCount'
        ]
        super(LogIPS, self).__init__('fast_log','m_tblog_ips',
                                     '/var/log/suricata/fast.log',keys)
        self.ips_rules = get_ips_rules()
        # print self.ips_rules

    def parser_line(self, line):
        if not line:
            return ('','')

        sip = dip = protocol = ""

        ls = line.split("[**]")
        if len(ls) < 3:
            FWLOG_DEBUG('log_split_ips:len too short[%s]' % line)
            return ('','')

        #stime = self.rc_time.search(ls[0])
        try:
            el = ls[1].split()[1:]
            event = (' ').join(el)
            rID = ls[1].split()[0].split(':')[1]
            #event = event.strip("'")
            # event = event.encode('string-escape')
            #print 'Event:',event
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

            #time = stime.group(0).strip()
            time = ls[0].split()[0].split('.')[0]
            if ls[0].split()[-1] == '[Drop]':
                stat = 'Drop'
            else:
                stat = 'Alert'

            sip = ip[-3].split(':')[0]
            dip = ip[-1].split(':')[0]
            protocol = ip[-4].lstrip('{').rstrip('}')

            t, date = self.get_ts_date(time, '%m/%d/%Y-%H:%M:%S')

            res = (str(t) + '|' + event + '|' + sip + '|' + protocol + '|'
                   + dip + '|' + stat + '|' + "fast_log" + '|' + str(rID)
                   + '|' + grade + '|' + desc + '|' + ruletype)

            return res, date

        except:
            FWLOG_ERR('%s get wrong line: [%s]' % (self.tb_name, line))
            return self.null

    # args is a list of strings of keys
    def other_jobs(self, args):
        pass
        _args = [tuple(line.split('|')) for line in args]
        ips_log_statistics_new(_args)

if __name__ == '__main__':
    ips = LogIPS()
    s = time.time()
    # ips.main_loop()
    ips.start()
    time.sleep(30)
    print 'time up'
    ips.stop()
    print 'Use time = %s' % (time.time() - s)
    pass
