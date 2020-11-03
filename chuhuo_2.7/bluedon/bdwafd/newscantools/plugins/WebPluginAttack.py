#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
import random
import time
import ConfigParser
import MySQLdb
import sys
import socket
import urllib
import urllib2
import httplib
import httplib2
import os
import re
from Queue import Queue
import logging
from lib.common import *
from lib.waf_netutil import *

class WebPlugins(object):
    def __init__(self, taskId, domainId):
        try:
            
            self.conn = ""
            self.cursor = ""
            self.taskId = str(taskId)
            self.domainId = str(domainId)
            self.domain_list_table = "domain_list_" + self.taskId
            self.scan_result_table = "scan_result_" + self.taskId
            self.task_summary_table = "task_summary_" + self.taskId
            self.web_vul_table = "web_vul_" + self.taskId
            self.task_name = ''
            self.domain = ''
            self.ip = ''
            self.url_count = 0
            self.web_scan_policy = ''
            
        except Exception,e:
            logging.getLogger().error("init WebPlugins Exception(task_id:"+str(taskId)+",domain_id:"+str(domainId)+"):" + str(e))
    #end def
    
    def mysqlConnect(self):
        try:
            
            if self.conn == '' or self.cursor == '':
                self.conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
                self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
            #end if
            return True
        except Exception,e:
            self.conn = ''
            self.cursor = ''
            logging.getLogger().error("mysql connect Exception(ScanUrlThread)(task_id:"+str(self.taskId)+",domain_id:"+str(self.domainId)+"):" + str(e))
            return False
        #end try
    #end def
    
    def mysqlClose(self):
        try:
            if self.conn != '' and self.cursor != '':
                self.cursor.close()
                self.conn.close()
            #end if
            self.conn = ''
            self.cursor = ''
            return True
        except Exception,e:
            self.conn = ''
            self.cursor = ''
            logging.getLogger().error("mysql close Exception(WebPlugins)(task_id:"+str(self.taskId)+",domain_id:"+str(self.domainId)+"):" + str(e))
            return False
        #end try
    #end def
    
    def init(self):
        try:
            if self.mysqlConnect():
                self.cursor.execute("select d.domain as domain,d.ip as ip,t.url_count as url_count,t.web_scan_policy as web_scan_policy,t.scan_timeout as scan_timeout, t.task_name as task_name from %s d,task_manage t where d.id = '%s' and d.task_id = t.id" % (self.domain_list_table,self.domainId))
                self.conn.commit()
                ret = self.cursor.fetchone()
                if ret and len(ret)> 0:
                    self.task_name = ret['task_name']
                    self.domain = ret['domain']
                    self.ip = ret['ip']
                    self.url_count = ret['url_count']
                    self.web_scan_policy = str(ret['web_scan_policy'])     
                   
                    return True
                else:
                    return False
                #end if
            else:
                logging.getLogger("init(WebPlugins) mysql connect error (task_id:"+str(self.taskId)+",domain_id:"+str(self.domainId)+")")
            #end if
        except Exception,e:
            logging.getLogger().error("init Exception(WebPlugins)(task_id:"+str(self.taskId)+",domain_id:"+str(self.domainId)+"):" + str(e))
        #end try
    #end def
    
    def update_task_summary(self):
        try:
            if self.mysqlConnect():
                self.cursor.execute("update %s set `web_weak` = `web_weak` + 1 , `total_weak` = `total_weak` + 1 where `ip` = '%s'" % (self.task_summary_table,self.ip))
                self.conn.commit()
            else:
                logging.getLogger().error("update_task_summary(WebPlugins) mysql connect error (task_id:"+str(self.taskId)+",domain_id:"+str(self.domainId)+")")
            #end if
        except Exception,e:
            logging.getLogger().error("update_task_summary Exception(WebPlugins)(task_id:"+str(self.taskId)+",domain_id:"+str(self.domainId)+"):" + str(e))
        #end try
    #end def
    
    def update_web_vul(self,url,vul_name,risk):
        try:
            if self.mysqlConnect():
                self.cursor.execute("select count(id) as c from %s where `vul_name` = '%s'" % (self.web_vul_table,vul_name))
                self.conn.commit()
                ret = self.cursor.fetchone()
                flag = False
                if ret and len(ret) > 0 and ret['c'] > 0:
                    self.cursor.execute("select `domain_list` from %s where `vul_name` = '%s'" % (self.web_vul_table,vul_name))
                    self.conn.commit()
                    ret = self.cursor.fetchone()
                    if ret and len(ret) > 0:
                        domain_list = str(ret['domain_list']) + '|' + url
                        query = "update " + self.web_vul_table + " set `domain_list` = %s where `vul_name` = %s"
                        self.cursor.execute(query,(domain_list,vul_name))
                        self.conn.commit()
                        flag = True
                    #end if
                #end if
            
                if flag == False:
                    query = "insert into " + self.web_vul_table + " (task_name,vul_name,risk_factor,domain_list) values (%s,%s,%s,%s)"
                    self.cursor.execute(query,(self.task_name,vul_name,risk,url))
                    self.conn.commit()
                #end if
            else:
                logging.getLogger().error("update_web_vul(WebPlugins) mysql connect error (task_id:"+str(self.taskId)+",domain_id:"+str(self.domainId)+")")
            #end if
        except Exception,e:
            logging.getLogger().error("update_web_vul Exception(WebPlugins)(task_id:"+str(self.taskId)+",domain_id:"+str(self.domainId)+"):" + str(e))
        #end try
    #end def
    
    def checkIfAct(self,type):
        try:
            list = self.web_scan_policy.split(',')
            for i in list:
                if i == type:
                    return True
                #end if
            #end for
            return False
        except Exception,e:
            logging.getLogger().error("checkIfAct Exception(WebPlugins)(task_id:"+str(self.taskId)+",domain_id:"+str(self.domainId)+"):" + str(e))
            return False
        #end try
    #end def
        
    def quote_buffer(self,buf):
        try:
            retstr = ''.join(map(lambda c:'%02x'%ord(c), buf))
            retstr = "x'" + retstr + "'"
            return retstr
        except Exception,e:
            logging.getLogger().error("quote_buffer Exception(WebPlugins)(task_id:"+str(self.taskId)+",domain_id:"+str(self.domainId)+"):" + str(e))
            return buf
        #end try
    #end def
    
    def write_log(self,vul_type,url,domain,detail,request,response,level,vul_id):
        try:
            if self.mysqlConnect():
                query = "select `id` from " + self.scan_result_table + " where `url` = %s and `vul_type` = %s and `domain` = %s and `detail` = %s and `request` = %s and `response` = %s and `level` = %s"
                self.cursor.execute(query,(url,vul_type,domain,detail,request,response,level))
                self.conn.commit()
                ret = self.cursor.fetchone()
            
                if not ret or len(ret) < 1:
                    query = "insert into " + self.scan_result_table + " (`url`,`ip`,`vul_type`,`domain`,`detail`,`request`,`response`,`domain_id`,`level`,`vul_id`) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    self.cursor.execute(query,(url,self.ip,vul_type,domain,detail,request,response,self.domainId,level,vul_id))
                    self.conn.commit()
                
                    self.update_task_summary()
                    self.update_web_vul(url, vul_type, level)
                
                    syslog_web_vul(self.taskId, self.task_name.encode("utf8"), self.ip, vul_type, detail, url.encode("utf8"), domain.encode("utf8"), level)  
                #end if
            else:
                logging.getLogger().error("write_log(ScanUrlThread) mysql connect error")
            #end if
        except Exception,e:
            logging.getLogger().error("write_log Exception(WebPlugins)(task_id:"+str(self.taskId)+",domain_id:"+str(self.domainId)+"):" + str(e))
        #end try
    #end def
    
    def main(self):
        try:
            if self.init() == False:
                return
            #end if
            
            if self.checkIfAct("28"):
                import ResinConfVuls
                ret = ResinConfVuls.main(self.domain)
                
                if ret and len(ret) > 0:
                    self.write_log(ret["vul_type"],ret["url"],self.domain,ret["detail"],"","",ret["level"],28)
    
                import IISFileDisclosure 
                ret = IISFileDisclosure.main(self.domain)
                if ret and len(ret) > 0:
                    self.write_log(ret["vul_type"],ret["url"],self.domain,ret["detail"],"","",ret["level"],28)
                    
            if self.checkIfAct("29"):
                import JBossAnonymousAccess
                #logging.getLogger().error("JBossAnonymousAccess  check.....")
                ret = JBossAnonymousAccess.main(self.domain)
                if ret and len(ret) > 0:
                    self.write_log(ret["vul_type"],ret["url"],self.domain,ret["detail"],"","",ret["level"],29)
                
            #end if
        except Exception,e:
            logging.getLogger().error("main Exception(WebPlugins)(task_id:"+str(self.taskId)+",domain_id:"+str(self.domainId)+"):" + str(e))
    #end def
#end class
        