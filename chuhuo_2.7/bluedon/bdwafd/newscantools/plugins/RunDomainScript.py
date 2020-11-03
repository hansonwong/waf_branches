#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
from lib.ex_httplib2 import *
import re


class RunDomainScript():
    def __init__(self,ob):
        try:
            self.ob = ob
            self.vul_id = ob['vul_id']
            self.vul_type = ob['vul_type']
            self.task_id = ob['task_id']
            self.domain_id = ob['domain_id']
            self.max_thread = ob['max_thread']
            self.ip = ob['ip']
#-----start------modify by yinkun 2014-10-14  增加对IPv6地址的处理，如domain为ipv6地址，则应加上[],如fd80::89，应改为[fd80::89]-------
            self.domain = ''
            if checkIpv6(ob['domain']):
                self.domain = '[' + ob['domain'] + ']'
            else:
                self.domain = ob['domain']
#------end----------------------------------------------------------------------------------
            self.web_timeout = ob['web_timeout']
            self.level = ob['level']
            self.script = ob['script']
            self.conn = ''
            self.cursor = ''
            self.asset_scan_id = ob['asset_scan_id']
            
        except Exception,e:
            logging.getLogger().error("File:RunDomainScript.py, RunDomainScript.__init__:" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'] + ",vul_id:" + ob['vul_id'])
        #end try
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
            logging.getLogger().error("File:RunDomainScript.py, RunDomainScript.mysqlConnect:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",vul_id:" + self.vul_id)
            write_scan_log(self.task_id,self.domain_id,"File:RunDomainScript.py, RunDomainScript.mysqlConnect:" + str(e)+ ",vul_id:" + self.vul_id)
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
            logging.getLogger().error("File:RunDomainScript.py, RunDomainScript.mysqlClose:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",vul_id:" + self.vul_id)
            return False
        #end try
    #end def
    
    def start(self):
        try:
            if self.script == "":
                return
            #end if
            
            http = ex_httplib2(self.ob["rec"])
            http.httlib2_set_follow_redirects(False)
            http.httlib2_set_timout(self.web_timeout)

            exec("from %s import *" % (self.script))
            
            #开始扫描
			 
            list = run_domain(http,self.ob)
            if list and len(list) > 0:
                if self.mysqlConnect():
                    write_log(self.conn,self.cursor,self.task_id,list,self.ob["task_name"],self.asset_scan_id)
                else: 
                    logging.getLogger().error("File:RunDomainScript.py, RunDomainScript.main:connect to mysql error,task id:" + self.task_id + ",domain id:" + self.domain_id + ",vul_id:" + self.vul_id)
                    write_scan_log(self.task_id,self.domain_id,"File:RunDomainScript.py, RunDomainScript.main:connect to mysql error"+ ",vul_id:" + self.vul_id)
                #end if
            #end if
            
        except Exception,e:
            logging.getLogger().error("File:RunDomainScript.py, RunDomainScript.start:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",vul_id:" + self.vul_id)
            write_scan_log(self.task_id,self.domain_id,"File:RunDomainScript.py, RunDomainScript.start:" + str(e) + ",vul_id:" + self.vul_id)
        #end try
    #end def
#end class




