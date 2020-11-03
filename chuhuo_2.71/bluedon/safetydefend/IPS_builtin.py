#/usr/bin/env python
# -*- coding:utf-8-*-

import os
import glob
import pickle
from MySQLdb import escape_string
import MySQLdb
import MySQLdb.cursors
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from operator import itemgetter
from itertools import groupby

from db.mysql_db import select
#import log


conn_3306=MySQLdb.connect(host='localhost',port=3306,user='root',passwd='bd_123456',db='db_firewall',charset='utf8',unix_socket='/tmp/mysql3306.sock',cursorclass=MySQLdb.cursors.DictCursor)
cur_3306=conn_3306.cursor()

#conn_3307=MySQLdb.connect(host='localhost',port=3307,user='root',passwd='bd_123456',db='db_firewall_log',charset='utf8',unix_socket='/tmp/mysql3307.sock')
#cur_3307=conn_3307.cursor()



classtype_priority={'attempted-admin':'高',
           'attempted-user':'高',
           'inappropriate-content':'高',
           'policy-violation':'高',
           'shellcode-detect':'高',
           'successful-admin':'高',
           'successful-user':'高',
           'trojan-activity':'高',
           'unsuccessful-user':'高',
           'web-application-attack':'中',
           'attempted-dos':'中',
           'attempted-recon':'中',
           'bad-unknown':'中',
           'default-login-attempt':'中',
           'denial-of-service':'中',
           'misc-attack':'中',
           'non-standard-protocol':'中',
           'rpc-portmap-decode':'中',
           'successful-dos':'中',
           'successful-recon-largescale':'中',
           'successful-recon-limited':'中',
           'suspicious-filename-detect':'中',
           'suspicious-login':'中',
           'system-call-detect':'中',
           'unusual-client-port-connection':'中',
           'web-application-activity':'中',
           'icmp-event':'低',
           'misc-activity':'低',
           'network-scan':'低',
           'not-suspicious':'低',
           'protocol-command-decode':'低',
           'string-detect':'低',
           'unknown':'低',
           'tcp-connection':'低'
          }

classtype_info={'attempted-admin':'管理员特权获取-未遂',
           'attempted-user':'用户特权获取-未遂',
           'inappropriate-content':'不当内容检测',
           'policy-violation':'潜在的侵犯企业隐私',
           'shellcode-detect':'检测可执行代码',
           'successful-admin':'管理员特权获取-成功',
           'successful-user':'用户特权获取-成功',
           'trojan-activity':'网络木马 ',
           'unsuccessful-user':'用户特权获取-失败',
           'web-application-attack':'web应用攻击',
           'attempted-dos':'拒绝服务-未遂',
           'attempted-recon':'信息泄露-未遂',
           'bad-unknown':'潜在不良流量',
           'default-login-attempt':'试图通过默认的用户名和密码登录',
           'denial-of-service':'拒绝服务-成功',
           'misc-attack':'其他攻击',
           'non-standard-protocol':'非标准协议及事件',
           'rpc-portmap-decode':'非正常RPC解码',
           'successful-dos':'拒绝服务-成功',
           'successful-recon-largescale':'大量信息泄露-成功',
           'successful-recon-limited':'信息泄露-成功',
           'suspicious-filename-detect':'检测到可疑文件名',
           'suspicious-login':'未遂可疑用户名登陆',
           'system-call-detect':'检测系统调用',
           'unusual-client-port-connection':'客户端非正常端口使用',
           'web-application-activity':'Web应用程序脆弱性攻击',
           'icmp-event':'通用ICMP事件',
           'misc-activity':'其他行为',
           'network-scan':'网络扫描',
           'not-suspicious':'常规流量',
           'protocol-command-decode':'通用协议命令解码',
           'string-detect':'检测到可疑字符串',
           'unknown':'未知流量',
           'tcp-connection':'检测TCP连接'
          }


rule_path='/home/wfl/rules/suricata/activex.rules'

class IPSRules():  #get all rules
      _ruleregex = re.compile(r"(.+?)\s*\((.+)\)\s*")
      _parmregex = re.compile(r"([a-zA-Z]+):?(\".*?\"|.*?);")

      def _parseRule(self, rule):
 #         print rule
          prefix, parms = self._ruleregex.match(rule).groups()
          rule = dict(prefix=prefix)
          rule['CVE'] = ''
          for (key, value) in self._parmregex.findall(parms):
              if value.startswith('"') and value.endswith('"'):
                 value = value[1:-1]
              if key == 'reference':
                  if value.startswith('cve,'):
                      ref = value.split(',')
                      if ref[1].lower().startswith('cve'):
                          rule['CVE'] = ref[1].upper()
                      else:
                          rule['CVE'] = 'CVE-' + ref[1]
              rule[key] = value
          return rule

      def _loadRuleFile(self,rule_path):
         rules=[]
         fd = open(rule_path, 'r')
         for line in fd:
             line = line.strip()
             if line.startswith("#") or not line:
                continue
             rule = self._parseRule(line)
             sid = int(rule.get("sid", -1))
             rule["sid"] = str(sid)
             rule["ipsrule"]=line
             rules.append(rule)
             """rule = self._parseRule(line)
             sid = int(rule.get("sid", -1))
             tmp[str(sid)]=line"""
             #rules.append(tmp)
         fd.close()
         return rules

      def _loadRule(self,rule_path,ips_or_malicious=None):
          rule=[]
          rules=self._loadRuleFile(rule_path)
          # print '_loadRule:',rules
          for line in rules:
              a=[]
              line['action']=line['prefix'].split(' ')[0]
              line['protocol']=line['prefix'].split(' ')[1]
              msg_sql = 'select sContent from m_tbipsrules where iSID=%s'%line['sid']
              cur_3306.execute(msg_sql)
              msg = cur_3306.fetchall()
              msg = msg and msg[0]['sContent'].replace("'","") or line['msg'].replace("'"," ")

              line['msg'] = msg
              a.append(line['sid'])
              a.append(line['msg'])
              if "classtype" in line:
                 a.append(classtype_info[line['classtype']])
                 a.append(classtype_priority[line['classtype']])
              else:
                 a.append('')
                 a.append('')
              if "classtype" in line and (classtype_priority[line['classtype']] == "高" \
                      or classtype_priority[line['classtype']] == "中"):
                  if line['action'] == 'alert':
                      a.append('drop')
                  else:
                      a.append(line['action'])

                  if line['ipsrule'].startswith('alert'):
                      line['ipsrule'] = line['ipsrule'].replace('alert','drop',1)
                      a.append(str(line['ipsrule']).encode('string-escape'))
                  else:
                      a.append(str(line['ipsrule']).encode('string-escape'))
              else:
                  a.append(line['action'])
                  a.append(str(line['ipsrule']).encode('string-escape'))

              #a.append(line['action'])
              if ips_or_malicious:
                 a.append(line['protocol'])
              #a.append(str(line['ipsrule']).encode('string-escape'))
              a.append(line['CVE'])
              b=tuple(list(a))
              rule.append(b)
          return rule



def insert_IPSrule():
    tmp=[]
    delete_sql = 'truncate table m_tbcustom_ips_lib'
    cur_3306.execute(delete_sql)
    #for name in os.listdir('/etc/suricata/rules/'):
    #    rule_path=os.path.join('/etc/suricata/rules/',name)
    #    if not name.endswith('.rules'):
    #        continue
        #if name == 'recommend.rules':
        #   continue
    rule_path='/etc/suricata/rules/recommend.rules'
    print rule_path
    rule_obj = IPSRules()
    rule = rule_obj. _loadRule(rule_path)
    for i in xrange(len(rule)):
        try:
           dates = list(tuple(rule[i]))
           dates.append(rule_path)
           dates = tuple(list(dates))
           #print dates
           sqli = "insert into m_tbcustom_ips_lib (sRuleID,sDesc,sRuleType,sDangerLever,sAction,sRule,sCVE,sRuleBelongFile)values\
               ('{sid:}','{desc:}','{type_:}','{lever:}','{act:}','{rule:}','{cve:}','{belong:}')"\
               .format(sid=dates[0],desc=dates[1],type_=dates[2],lever=dates[3],act=dates[4],rule=dates[5],cve=dates[6],belong=dates[7])
           cur_3306.execute(sqli)
        except Exception as e:

            print rule[i]
            for tmp1 in rule[i]:
                print tmp1
            print '************************************'
            tmp.append(dates)

    conn_3306.commit()

    cur_3306.close()
    conn_3306.close()

def rules_action_edit():
    table_rule = select('select sRule,sRuleBelongFile from m_tbcustom_ips_lib')
    table_rule.sort(key=itemgetter('sRuleBelongFile'))
    f = open('/etc/suricata/rules/recommend.rules','w')
    for sRuleBelongFile, items in groupby(table_rule, key=itemgetter('sRuleBelongFile')):
        print sRuleBelongFile
        print items
        for num,rule in enumerate(items):
            print rule['sRule']
            print>>f,rule['sRule']
            print '*******num',num
    f.close()

def maliciousCodeRule():

    rule_path='/etc/suricata/rules/trojan.rules'
    rule_obj = IPSRules()
    rule = rule_obj. _loadRule(rule_path,ips_or_malicious='true')
    for i in xrange(len(rule)):
        dates = list(tuple(rule[i]))
        tmp=[]
        tmp.append(dates[0])
        tmp.append(dates[-1])
        tmp.append(dates[-2])
        tmp = tuple(tmp)
        print tmp
        sqli = "insert into m_tbmalicious_code values(Null,'%s','%s','%s')" %tmp
        cur.execute(sqli)
    conn.commit()
    cur.close()
    conn.close()


if __name__=="__main__":
    if sys.argv[1]=='database':
        insert_IPSrule()
    if sys.argv[1]=='drop':
        rules_action_edit()
