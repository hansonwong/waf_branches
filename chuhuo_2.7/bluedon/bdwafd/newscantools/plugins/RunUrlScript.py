#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import threading
import time
from  threading import Thread
from Queue import Queue
from lib.common import *
from lib.ex_httplib2 import *

class RunUrlScript():
    def __init__(self,ob):
        try:
            self.ob = ob
            self.vul_id = ob['vul_id']
            self.vul_type = ob['vul_type']
            self.task_id = ob['task_id']
            self.domain_id = ob['domain_id']
            self.max_thread = ob['max_thread']
            self.ip = ob['ip']
            self.domain = ob['domain']
            self.web_timeout = ob['web_timeout']
            self.queue = ob['queue']
            self.level = ob['level']
            self.script = ob['script']
            self.max_timeout_count = ob['max_timeout_count']
            self.end_time = ob['end_time']
            self.cookie = ob['cookie']
            self.asset_scan_id = ob['asset_scan_id']
            
            self.rec = ob['rec']
            

            self.thread_lock = threading.Lock()
            
            self.conn = ''
            self.cursor = ''

            self.exclude_url = []
            if ob.has_key('exclude_url'):
                self.exclude_url = ob['exclude_url']
            #end if
            
        except Exception,e:
            logging.getLogger().error("File:RunUrlScript.py, RunUrlScript.__init__:" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'] + ",vul_id:" + ob['vul_id'])
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
            logging.getLogger().error("File:RunUrlScript.py, RunUrlScript.mysqlConnect:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",vul_id:" + self.vul_id)
            write_scan_log(self.task_id,self.domain_id,"File:RunUrlScript.py, RunUrlScript.mysqlConnect:" + str(e)+ ",vul_id:" + self.vul_id)
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
            logging.getLogger().error("File:RunUrlScript.py, RunUrlScript.mysqlClose:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",vul_id:" + self.vul_id)
            return False
        #end try
    #end def
    
    def checkTimeOut(self):
        if self.ob['timeout_count'] > self.ob['max_timeout_count']:
            return False
        #end if
        if self.ob['end_time'] < time.time():
            return False
        #end if
        
        return True
    #end def

    
    def main(self):
        try:
            #http = httplib2.Http(timeout=self.web_timeout)
            #http.follow_redirects = False
            
            
            http = ex_httplib2(self.rec, self.cookie)
            http.httlib2_set_follow_redirects(True)
            http.httlib2_set_timout(self.web_timeout)
            #加载模块

            exec("from %s import *" % (self.script))
            
            
            #临时计数器
            temp_num = 0
            #开始扫描
            while True:
                if self.queue.qsize() < 1:
                    break
                #end if
                #check timeout
                #if self.checkTimeOut() == False:
                    #break
                #end if
                
                
                list = []
                
                try:
                    item = self.queue.get_nowait()
                    
                except Exception, e:
                    break
                
                url = item['url']
                if item['method'] == 'get' and item['params'] != '':
                    url = "%s?%s" % (url,item['params'])
                #end if
                if check_exclude_url(self.exclude_url,url):
                    continue
                #end if

                prev =time.time()
                list = run_url(http,self.ob,item)

                if list and len(list) > 0:
                    temp_num += len(list)
                    
                    #对于邮件信息泄露和HTML注释信息泄露做了部分特殊处理
                    if self.script in ['HtmlSourceLeakScript','EmailDiscloseScript'] and temp_num > 10:
                        break
                    #end if

                    self.thread_lock.acquire()

                    if self.mysqlConnect():
                        write_log(self.conn,self.cursor,self.task_id,list,self.ob["task_name"],self.asset_scan_id)
                    else:
                        logging.getLogger().error("File:RunUrlScript.py, RunUrlScript.main:connect to mysql error,task id:" + self.task_id + ",domain id:" + self.domain_id + ",vul_id:" + self.vul_id)
                    #end if

                    self.thread_lock.release()

                #end if
                
                #if self.ob["rec"].err_out() and not self.ob["isForce"]:
                    #break
                if flowControl(self,time.time()-prev,self.ob["rec"],self.ob["isForce"],self.ob["web_speed"],self.ob["web_minute_package_count"],True):
                    break

            #end while
            #http.dump_debug_info()
        
        except Exception,e:
            logging.getLogger().error("File:RunUrlScript.py, RunUrlScript.main:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",vul_id:" + self.vul_id)
            write_scan_log(self.task_id,self.domain_id,"File:RunUrlScript.py, RunUrlScript.main:" + str(e)+ ",vul_id:" + self.vul_id)
        #end try
    #end def
    
    def start(self):
        try:
            if self.script == "":
                return
            #end if
            list = []
            

            for i in range(self.max_thread):
            #for i in range(1):
                list.append(Thread(target=self.main, args=()))
            #end for
            for t in list:
                t.start()
            #end for
            for t in list:
                t.join()
            #end for
            
        
        except Exception,e:
            logging.getLogger().error("File:RunUrlScript.py, RunUrlScript.start:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",vul_id:" + self.vul_id)
            write_scan_log(self.task_id,self.domain_id,"File:RunUrlScript.py, RunUrlScript.start:" + str(e)+ ",vul_id:" + self.vul_id)
        #end try
    #end def
#end class




