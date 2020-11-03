#!/usr/bin/env python
# coding=utf-8

import os
import re
from collections import defaultdict
from db.mysql_db import update,select

severity_mean = {'0':'EMERGENCY',
                 '1':'ALERT',
                 '2':'CRITIAL',
                 '3':'ERROR',
                 '4':'WARNING',
                 '5':'NOTICE',
                 '6':'INFO',
                 '7':'DEBUG'}
severity_china_mean ={'0':'紧急',
                      '1':'警报',
                      '2':'严重',
                      '3':'错误',
                      '4':'警告',
                      '5':'通知',
                      '6':'信息',
                      '7':'调试'
                        }

class WebRulesSeverity():
    def __init__(self):
        self.rulefiles =[]
        self.ID_re = r'.*?(id:.[0-9]+.).*?'
        self.severity_re = r'.*?(severity:.[0-9].).*?'

    def get_rule_file(self):
        fr = open('/usr/local/bdwaf/conf/modsecurity.conf','r')
        for line in fr:
            line = line.split(' ')
            if 'Include' == line[0]:
                self.rulefiles.append(os.path.join('/usr/local/bdwaf/conf',line[1].strip('\n')))
        fr.close()

    def parse_rule(self,):
        sum_ =[]
        self.rulefiles_ID_severity = defaultdict()
        for path in self.rulefiles:
            print '*************',path
            ID_=[]
            severity_=[]
            fr = open(path,'r')
            for line in fr:
                if not line.startswith('#'):
                    ID = re.findall(self.ID_re,line)
                    severity = re.findall(self.severity_re,line)
                    if ID:
                        ID_.append(''.join(ID))
                    if severity:
                        severity_.append(''.join(severity))

                    if line.strip(' ').strip('\t').startswith('SecRule'):
                        if len(ID_)==len(severity_):
                            pass
                        if len(severity_)<len(ID_):
                            severity_.extend('N')
            self.rulefiles_ID_severity[os.path.basename(path)]=zip(ID_,severity_)
            fr.close()
        pass

    def ID_severity_table(self,):
        allID=[]
        for key,value in self.rulefiles_ID_severity.items():
            for ID,severity in value:
                sRealID=filter(str.isdigit,ID)
                print sRealID,severity

                allID.append(sRealID)
        #print allID,'\n'
        #print len(allID)

        #table_allID = select('select sRealID from m_tbwebapplication_lib')
        #table_allID = [str(tmp['sRealID']) for tmp in table_allID]
        #print set(table_allID)^set(allID)

                severity_num=filter(str.isdigit,severity)
                update('update m_tbwebapplication_lib set severity_num="%s" ,severity_English="%s",severity_china="%s"\
                       where sRealID="%s"'%(severity_num,severity_mean.get(severity_num,''),severity_china_mean.get(severity_num,''),sRealID))
        pass

if __name__=="__main__":
    cls =WebRulesSeverity()
    cls.get_rule_file()
    cls.parse_rule()
    cls.ID_severity_table()
