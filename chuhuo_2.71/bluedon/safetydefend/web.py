#! /usr/bin/env python
# -*-coding:utf-8 -*-

from db.mysqlconnect import mysql_connect_dict,mysql_connect,mysql_connect_3307
from system.ha import init_tenv
#import threading
import os
import re
import time
import MySQLdb
from logging import getLogger
from db.config1 import get_mysql_db1
from MySQLdb import escape_string
#from reportlog.log_config import read_config_ini
import commands
from db.mysql_db import select_one
import json


def web_defined():
    cur=mysql_connect_dict()
    sql='select * from m_tbwebapplication_lib where iCustomOrInset=1 order by iPriority,sRealID'
    cur.execute(sql)
    results=cur.fetchall()
    cusrules=[]
    for result in results:
        cus={}
        cus['matchdata']=result['sMatchContent']
        cus['keywords']=result['sFeatureKey']
        #cus['action']=result['sInterceptionMethod']
        cus['action'] = 'block'
        cus['severity']=result['sDangerLever']
        cus['httptype']=result['sHttpRequestType']
        cus['realid']=result['sRealID']
        if result['sMatchAlgorithm']=='1':
           cus['matchalgorithm']='rx'
        else:
           cus['matchalgorithm']='contains'
        dump=[]
        if "URI" in cus['matchdata']:
           dump.append('REQUEST_URI')
        if 'POST' in cus['matchdata']:
           dump.append('REQUEST_BODY')
        if 'COOKIE'in cus['matchdata']:
           dump.append('REQUEST_COOKIES|REQUEST_COOKIES_NAMES')
        cus['matchdata']='|'.join(dump)
        cusrules.append(cus)
    cur.close()
    tenv=init_tenv()
    tenv.get_template('web_cusrule').stream(cusrules=cusrules).dump('/usr/local/bdwaf/conf/activated_rules/cusrule.conf')

def all_ruleid():
    allID=[]
    cur=mysql_connect()
    sql='select sRealID from m_tbwebapplication_lib'
    cur.execute(sql)
    ruleids=cur.fetchall()
    for ruleid in ruleids :
        allID.append(ruleid[0])
    cur.close()
    return allID



def web_strategy():
    """
    配置文件/usr/local/bdwaf/conf/modsecurity.conf

    """
    def write_config(log,action):
        re_sub = lambda log,string,result:int(log) and \
                    re.sub(r'^.*?%s'%string,'%s'%string,result,flags=re.MULTILINE)\
                    or re.sub(r'^.*?%s'%string,'#'+'%s'%string,result,flags=re.MULTILINE)
        with open('/usr/local/bdwaf/conf/modsecurity.conf', 'r+') as f:
            result = re.sub(r'^SecDefaultAction\s+\w+.*', action, f.read(), flags=re.MULTILINE)
            result = re_sub(log,'SecAuditLogType',result)
            result = re_sub(log,'SecAuditLog',result)
            result = re_sub(log,'SecAuditLogStorageDir',result)
            f.seek(0)
            f.write(result)
    allID=all_ruleid()
    tenv=init_tenv()

    cur=mysql_connect_dict()
    sql="select sStrategyTemplate,iAction,iLog,sPortCheck from  m_tbwebapplication_strategy where iStatus=1"
    cur.execute(sql)
    results=cur.fetchall()
    if not len(results):    #没有waf应用策略
        write_config(1,'SecDefaultAction phase:1,log,auditlog,allow')
        tenv.get_template('limits').stream(removeID=allID).dump('/usr/local/bdwaf/conf/activated_rules/limits.conf')
    else:
        results=results[0]
        action = results['iAction']==1 and 'SecDefaultAction phase:1,log,auditlog,allow'\
                or 'SecDefaultAction phase:1,log,auditlog,deny'
        write_config(int(results['iLog']),action)

        template=int(results['sStrategyTemplate'])
        sql_template='select sRuleIDS from m_tbwebapplication_protected where id =%d'%template
        cur.execute(sql_template)
        ruleID=cur.fetchone()
        ruleID = ruleID and ruleID or {'sRuleIDS':''}
        removeID=[]
        for ID in allID:
            if ID in ruleID['sRuleIDS']:
               continue
            else:
               removeID.append(ID)

        with open('/usr/local/bdwaf/conf/waf_port.conf','w') as fw:
             fw.write(results['sPortCheck'])

        tenv=init_tenv()
        tenv.get_template('limits').stream(removeID=removeID).dump('/usr/local/bdwaf/conf/activated_rules/limits.conf')
        cur.close()
    waf_on_off = select_one('select sValue from m_tbconfig where sName="TimeSet"')
    waf_on_off = waf_on_off and json.loads(waf_on_off['sValue']).has_key('iWAF')\
                and json.loads(waf_on_off['sValue'])['iWAF'] or '0'
    if waf_on_off=='1':
        commands.getstatusoutput('killall -9 bdwaf')
        commands.getstatusoutput('/usr/local/bdwaf/sbin/bdwaf')


def recover():
    web_defined()
    web_strategy()

if __name__=="__main__":
   recover()
   #th=WebLog()
   #th.start()
   #th.run()

