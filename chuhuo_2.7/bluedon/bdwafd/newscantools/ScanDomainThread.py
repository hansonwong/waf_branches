#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import threading
#import Spider
import logging
import httplib2
import time
import datetime
import socket
import urllib
import os
from Queue import Queue
from plugins.RunUrlScript import *
from plugins.RunDomainScript import *
from plugins.RunCgidbScript import *
from lib.common import *
from plugins.lib.common import request_exception_counter
from plugins.lib.common import write_scan_log
from plugins.lib.ex_httplib2 import *

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)

class ScanDomainThread(threading.Thread):
    def __init__(self, task_id, domain_queue, thread_lock):
        try:
            threading.Thread.__init__(self)
            self.conn = ""
            self.cursor = ""
            self.task_id = str(task_id)
            self.user_id = ''
            self.domain_queue = domain_queue
            self.thread_lock = thread_lock
            
            self.task_name = ''
            self.web_spider_enable = 1
            self.vuls_dict = {}
            self.cgidb = {}
            self.vuls = ''
            self.vuls_1 = ''
            self.vuls_2 = ''
            
            self.rfi_url = ""
            self.rfi_keyword = ""
            self.count = 0
            self.check_exp_lock = threading.Lock()
            self.web_exp_try_times = 3
            self.web_exp_try_interval = 5
            self.cookie = ""
            self.isForce = False
            self.web_speed = 0
            self.web_minute_package_count = 0
            self.url_time = {'speed':0}
            
            self.threadname = threading.currentThread().getName()
            self.scan_log_formatter = logging.Formatter('%(asctime)s##%(message)s')
            self.asset_scan_id = 0
            self.web_getdomain_enable = 0
            self.web_getdomain_timeout = 120
        
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.__init__:" + str(e) + ",task id:" + task_id)
        #end try
    #end def
    
    def mysqlConnect(self):
        def reconnect():
            self.conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            if self.conn == '' or self.cursor == '':
                reconnect() 
            else:
                try:
                    self.conn.ping()
                except MySQLdb.OperationalError,e:
                    self.mysqlClose()
                    reconnect()
                    logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.mysqlConnect reconnect:" + str(e) + ",task id:" + self.task_id)
                    #write_scan_log(ob['task_id'],ob['domain_id'],"File:ScanDomainThread.py, ScanDomainThread.mysqlConnect reconnect:" + str(e))
            #end if
            logging.getLogger().error("mysql")
            return True
        except Exception,e:
            self.conn = ''
            self.cursor = ''
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.mysqlConnect:" + str(e) + ",task id:" + self.task_id)
            #write_scan_log(ob['task_id'],ob['domain_id'],"File:ScanDomainThread.py, ScanDomainThread.mysqlConnect:" + str(e))
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
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.mysqlClose:" + str(e) + ",task id:" + self.task_id)
            return False
        #end try
    #end def
    
    def init(self):
        try:
            if self.mysqlConnect():
                sql = "select task_name,asset_scan_id,web_speed,web_minute_package_count,web_exp_try_times,web_exp_try_interval,user_id,web_timeout,web_getdomain_timeout,web_url_count,web_spider_enable,web_policy,web_getdomain_enable from task_manage where id = '%s'" % (self.task_id)
                self.cursor.execute(sql)
                self.conn.commit()
                res = self.cursor.fetchone()
                print '''------------------------------------------------------------
ScanDomainThread init 数据:%s
------------------------------------------------------------'''%res
                if res and len(res) > 0:
                    self.task_name = res['task_name']
                    self.user_id = str(res['user_id'])
                    self.web_spider_enable = res['web_spider_enable']
                    self.web_timeout = res['web_timeout']
                    self.web_getdomain_timeout = res['web_getdomain_timeout']
                    self.web_url_count = res['web_url_count']
                    self.web_policy = res['web_policy']
                    self.web_exp_try_times = int(res['web_exp_try_times'])
                    self.web_exp_try_interval = int(res['web_exp_try_interval'])
                    if self.web_exp_try_times == 0 and self.web_exp_try_interval == 0:
                        self.isForce = True
                    self.web_speed = int(res['web_speed']) if res['web_speed']  else 0
                    self.web_minute_package_count = int(res['web_minute_package_count']) if res['web_minute_package_count'] else 0  
                    self.asset_scan_id = res['asset_scan_id']      
                    self.web_getdomain_enable = res['web_getdomain_enable']
                    temp1 = []
                    temp2 = []
                    temp = []

                    sql = "select `vul_id`,`level`,`vul_name`,`scan_type`,`script` from `web_vul_list` where `vul_id` in (select `vul_id` from `web_policy_ref` where `policy_id` = '%s') order by `priority` asc" % (self.web_policy)
                    self.cursor.execute(sql)
                    self.conn.commit()
                    res = self.cursor.fetchall()
                    for row in res:
                        if row['vul_id'] == "":
                            continue
                        #end if
                        temp.append(str(row['vul_id']))
                        if row['scan_type'] == 1 or row['scan_type'] == 2:
                            temp1.append(str(row['vul_id']))
                        elif row['scan_type'] == 3:
                            temp2.append(str(row['vul_id']))
                        #end if
                        self.vuls_dict[str(row['vul_id'])] = {'vul_name':row['vul_name'].encode('utf8'),'level':row['level'],'scan_type':row['scan_type'],'script':row['script']}
                    #end for
                    self.vuls = '|'.join(temp)
                    self.vuls_1 = '|'.join(temp1)
                    self.vuls_2 = '|'.join(temp2)

                    sql = "select `url`,`method`,`response`,`response_type`,`detail`,`solu`,`vul_id` from `cgidb` where `vul_id` in (select `vul_id` from `web_policy_ref` where `policy_id` = '%s')"% (self.web_policy)
                    self.cursor.execute(sql)
                    self.conn.commit()
                    res = self.cursor.fetchall()
                    for row in res:
                        
                        self.cgidb[str(row['vul_id'])] = {'url':row['url'].encode('utf8'),'method':row['method'],'response':row['response'].encode('utf8'),'response_type':row['response_type']}
                    #end for

                    sql = "select `Value`,`Name` from `user_config` where `user_id` = '%s' and `Name` in ('rfi_url','rfi_keyword')" % (self.user_id)
                    self.cursor.execute(sql)
                    self.conn.commit()
                    res  = self.cursor.fetchall()
                    for row in res:
                        if row['Name'] == 'rfi_url':
                            self.rfi_url = row['Value']
                        elif row['Name'] == 'rfi_keyword':
                            self.rfi_keyword = row['Value']
                        #end if
                    #end for
                    if self.rfi_url == "":
                        self.rfi_url = "http://www.yxlink.com/nvs_test.txt"
                    #end if
                    if self.rfi_keyword == "":
                        self.rfi_keyword = "test_nvs_test"
                    #end if
                    
                    return True
                else:
                    logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.init  : get config error ,task id:" + self.task_id)
                    return False
                #end if
            else:
                logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.init  : mysql connect error ,task id:" + self.task_id)
                return False
            #end if
            logging.getLogger().error("8888888")
        except Exception,e:
            logging.getLogger().error("9999999")
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.init:" + str(e) + ",task id:" + self.task_id)
        #end try
    #end def
    
    def endScanDomain(self,domain_id,ip):
        try:
            current_time = time.strftime("%Y-%m-%d %X",time.localtime())
            if self.mysqlConnect():
                self.vuls = "0|%s" % (self.vuls)
                sql = "update domain_list_%s set `state` = '1' , `exception` = '' , `end_time` = '%s', `progress` = '%s' where `id` = '%s'" % (self.task_id,current_time,self.vuls,domain_id)
                self.cursor.execute(sql)
                self.conn.commit()
                
                sql = ""
                if self.asset_scan_id > 0:
                    sql = "update hostmsg_%s set `web_state` = '1' where (select count(*) from domain_list_%s where `state` <> '1' and `ip` = '%s' and `asset_scan_id` = '%s') = 0 and `ip` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,self.task_id,ip,self.asset_scan_id,ip,self.asset_scan_id)
                else:
                    sql = "update hostmsg_%s set `web_state` = '1' where (select count(*) from domain_list_%s where `state` <> '1' and `ip` = '%s') = 0 and `ip` = '%s'" % (self.task_id,self.task_id,ip,ip)
                #end if
                self.cursor.execute(sql)
                self.conn.commit()
                
                #sql = "update hostmsg_%s set `end_time` = '%s' where `ip` = '%s' and `port_state` = '1' and `web_state` = '1' and `weak_state` = '1' and `host_state` = '1'" % (self.task_id,current_time,ip)
                #self.cursor.execute(sql)
                #self.conn.commit()
            else:
                logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.endScanDomain: mysql connect error ,task id:" + self.task_id + ",domain_id:" + domain_id)
            #end if
            
            self.clearTmpFile(self.task_id, domain_id)
            
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.endScanDomain:" + str(e) + ",task id:" + self.task_id + ",domain_id:" + domain_id)
        #end try
    #end def
    
    def add_scan_log(self,domain_id,spider_state):
        try:
            logfile = "%s#%s" %(self.task_id,domain_id)
            logger = logging.getLogger(logfile)
            logger.setLevel(logging.INFO)
            path = sys_path("/webs/scanlog/%s" % logfile)
            if self.web_spider_enable == 1 and spider_state == 0 and os.path.exists(path): #重新扫描，清空该域名扫描日志
                os.remove(path)
            if not logger.handlers:  # fix BUG #2986(通信异常logger会增加handler,导致重复记录)
                fd = logging.FileHandler(path)
                fd.setFormatter(self.scan_log_formatter)
                logger.addHandler(fd)
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.add_scan_log:" + str(e) + ",task id:" + self.task_id +",domain_id:" + domain_id)
    
    def updateDomainException(self,content,domain_id,ip):
        
        #通信异常，稍后继续尝试
        
        try:
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            sql = "select `exception_count` from domain_list_%s where id = '%s'" % (self.task_id,domain_id)
            cursor.execute(sql)
            ret = cursor.fetchone()
            
            if ret and ret["exception_count"] and int(ret["exception_count"]) >= self.web_exp_try_times:
                #第三次异常 不再进行扫描
                #sql = "update domain_list_%s set `state` = '1', `exception` = '%s' where id = '%s'" % (self.task_id,"通信异常，扫描未完成",domain_id)
                sql = "update domain_list_%s set `state` = '1', `exception` = '%s' where id = '%s'" % (self.task_id,content+"，扫描未完成",domain_id)
                cursor.execute(sql)
                conn.commit()
                write_scan_log(self.task_id,domain_id,content+"，扫描未完成")
                self.clearTmpFile(self.task_id, domain_id)
                
            else:
                
                #sql = "update domain_list_%s set `state` = '2', `exception` = '%s' where id = '%s'" % (self.task_id,"通信异常，稍后继续尝试",domain_id)
                sql = "update domain_list_%s set `state` = '2', `exception` = '%s' where id = '%s'" % (self.task_id,content+"，稍后继续尝试",domain_id)
                cursor.execute(sql)
                conn.commit()
                write_scan_log(self.task_id,domain_id,content+"，稍后继续尝试")
                self.clearTmpFile(self.task_id, domain_id)
            #end if
            
            if ret and ret["exception_count"]:
                sql = "update domain_list_%s set `exception_count` = %d where id = '%s'" % (self.task_id, int(ret["exception_count"]) + 1 , domain_id)
            else:
                sql = "update domain_list_%s set `exception_count` = '1' where id = '%s'" % (self.task_id,domain_id)
            #end if
            cursor.execute(sql)
            conn.commit()
            
            sql = "update domain_list_%s set next_start_time = '%s' where id = '%s'" % (self.task_id, datetime.datetime.fromtimestamp(time.time() + self.web_exp_try_interval * 60), domain_id)
            self.cursor.execute(sql)
            self.conn.commit()
            
            sql = ""
            if self.asset_scan_id > 0:
                sql = "update hostmsg_%s set `web_state` = '1' where (select count(*) from domain_list_%s where `state` <> '1' and `ip` = '%s' and `asset_scan_id` = '%s') = 0 and `ip` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,self.task_id,ip,self.asset_scan_id,ip,self.asset_scan_id)
            else:
                sql = "update hostmsg_%s set `web_state` = '1' where (select count(*) from domain_list_%s where `state` <> '1' and `ip` = '%s') = 0 and `ip` = '%s'" % (self.task_id,self.task_id,ip,ip)
            #end if
            cursor.execute(sql)
            conn.commit()

        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.updateDomainException:" + str(e) + ",task id:" + self.task_id + ",domain_id:" + domain_id)
        #end try
    #end def
    
    def changeCode(self,msg,code):
        if code == 'utf8' or code == 'utf-8':
            return msg
        elif code == 'gbk':
            try:
                return msg.decode('gbk').encode('utf8')
            except Exception,e:
                return msg
            #end try
        elif code == 'gb2312':
            try:
                return msg.decode('gb2312').encode('utf8')
            except Exception,e:
                return msg
            #end try
        else:
            try:
                return msg.decode(code).encode('utf8')
            except Exception,e:
                print "" 
            #end try
            try:
                return msg.decode('utf8').encode('utf8')
            except Exception,e:
                print "" 
            #end try
            try:
                return msg.decode('gb2312').encode('utf8')
            except Exception,e:
                print "" 
            #end try
            try:
                return msg.decode('gbk').encode('utf8')
            except Exception,e:
                print "" 
            #end try
            try:
                return msg.encode('utf8')
            except Exception,e:
                print "" 
            #end try
            return msg
        #end if
    #end def
    
    def updateDomainTitle(self,content,domain_id):
        try:
            title = ""
            match = re.findall(r"<(\s*)title(\s*)>(.*?)<(\s*)/(\s*)title(\s*)>",content,re.I|re.DOTALL)
            if match and len(match) > 0:
                title = match[0][2].replace("\r","").replace("\n","")
            #end if
            if title == "":
                return ""
            #end if
            code = self.getDomainCode(content)
            title = self.changeCode(title, code)
            
            if self.mysqlConnect() and title != "":
                sql = "update domain_list_" + self.task_id + " set `title` = %s where `id` = %s"
                self.cursor.execute(sql,(title,domain_id))
                self.conn.commit()
            #end if
            
            return title
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.updateDomainTitle:" + str(e) + ",task id:" + self.task_id)
            return ""
        #end try
    #end def
    
    def getDomainCode(self,content):
        try:
            code = ""
            match = re.findall(r"<meta(.+?)charset(.*?)=(.+?)(\"|')",content,re.I)
            if match and len(match) > 0:
                code = match[0][2]
            else:
                code = "utf8"
            #end if
            
            return code
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.getDomainCode:" + str(e) + ",task id:" + self.task_id)
            return "utf8"
        #end try
    #end def
    
    def updateSiteType(self,res,domain_id):
        try:
            site_type = ""
            if res.has_key('x-powered-by'):
                site_type_x = res['x-powered-by']
                if site_type_x.lower().find('php') >= 0:
                    site_type = "php"
                elif site_type_x.lower().find('asp') >= 0:
                    site_type = "asp"
                elif site_type_x.lower().find("asp.net") >= 0:
                    site_type = "aspx"
                elif site_type_x.lower().find("jsp") >= 0:
                    site_type = "jsp"
                #end if
            #end if
            if site_type == "":
                if res.has_key('set-cookie'):
                    site_type_c = res['set-cookie']
                    if site_type_c.lower().find('php') >= 0:
                        site_type = "php"
                    elif site_type_c.lower().find('asp') >= 0:
                        site_type = "asp"
                    elif site_type_c.lower().find("jsessionid")>=0:
                        site_type = "jsp"
                #end if
            #end if
            if site_type == "":
                if res.has_key('server'):
                    server = res['server'].lower()
                    if server.lower().find('php') >= 0:
                        site_type = "php"
                #end if
            #end if

            if self.mysqlConnect() and site_type != "":
                sql = "update domain_list_" + self.task_id + " set `site_type` = %s where `id` = %s"
                self.cursor.execute(sql,(site_type,domain_id))
                self.conn.commit()
               
            #end if

            
            return site_type
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.updateSiteType:" + str(e) + ",task id:" + self.task_id)
            return ""
        #end try
    #end def
    
    def PreDomainScan(self,scheme,domain,url):
        try:
            rec = request_exception_counter(100)
            rec.domain = domain
            http = ex_httplib2(rec)
            http.httlib2_set_follow_redirects(False)
            http.httlib2_set_timout(30)
#           res, content = http.request(url)
            res, content = nvs_httplib2_request(http,url)
            return True,res,content
        except socket.timeout,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.PreDomainScan: domain timeout ,task id:" + self.task_id + ",domain:" + scheme + "://" + domain)
            return False,{},""
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.PreDomainScan:" + str(e) + ",task id:" + self.task_id + ",domain:" + scheme + "://" + domain)
            return False,{},""
        #end try
    #end def
    
    def checkDomainWorkMode(self,res,title):
        try:
            if res.has_key('status') and (res['status'] == '404' or res['status'] == '400' or res['status'] == '401'):
                return False
            #end if
            
            keyword_list = ['Internal Server Error','401 Unauthorized','Not Found','Bad Request']
            try:
                temp = u"建设中"
                keyword_list.append(temp.encode('utf8'))
                keyword_list.append(temp.encode('gb2312'))
                temp = u"服务器的使用期限已过"
                keyword_list.append(temp.encode('utf8'))
                keyword_list.append(temp.encode('gb2312'))
                temp = u"网站错误"
                keyword_list.append(temp.encode('utf8'))
                keyword_list.append(temp.encode('gb2312'))
            except Exception,e1:
                logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.checkDomainWorkMode encode error:" + str(e1) + ",task id:" + self.task_id)
            #end try
            
            for row in keyword_list:
                try:
                    if title.find(row) >= 0:
                        return False
                    #end if
                except Exception,e1:
                    continue
                #end try
            #end for
            
            return True
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.checkDomainWorkMode:" + str(e) + ",task id:" + self.task_id)
            return True
        #end try
    #end def
    def GetVerification(self):
        isstart='0'
        try:
            
            f = open("/var/www/yx.config.inc.php",'r')
            line=f.read()
            m = re.search(r'feature_set = \'(.{1,35})\';', line,re.I)
            if m:
                isstart= m.group(1)[2]
            #end if
        except Exception,e:
            print e
        return isstart
        #end try

    def checkSpiderFlag(self):
        try:
            sql = "select spider_flag from task_manage where `id` = '%s'"%(self.task_id);
            self.cursor.execute(sql)
            self.conn.commit()
            res = self.cursor.fetchone()
            #logging.getLogger().error(str(res))
            if(res['spider_flag'] == 1):
                return True;
            else:
                return False;
        except Exception, e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.checkSpiderFlag:" + str(e) + ",task id:" + self.task_id)
            return False
        
    #end try

    def startDomainMain(self,domain_id):
        try:
            if self.mysqlConnect():
                if domain_id == None:
                    return
                #end if
                print "domain_id : ",domain_id
                
                ###################################### 获取任务的配置信息开始
                sql = "select `domain`,`scheme`,`ip`,`title`,`state`,`spider_state`,`progress`,`base_path`,`policy`,`policy_detail`,`cookie_url`,`begin_path`,`service_type`,`site_type`,`database_type`, `exclude_url` from domain_list_%s where `id` = '%s'" % (self.task_id,domain_id)
                self.cursor.execute(sql)
                self.conn.commit()
                res = self.cursor.fetchone()
                domain = res['domain'].encode('utf8')
                if checkIpv6(domain):
                    domain = "[%s]" % (domain)
                #end if
                scheme = res['scheme'].encode('utf8')
                ip = res['ip'].encode('utf8')
                title = res['title']#.encode('utf8')
                state = res['state']
                spider_state = res['spider_state']
                progress = res['progress'].encode('utf8')
                base_path = res['base_path'].encode('utf8')
                policy = res['policy']
                policy_detail = ""
                if res['policy_detail'] and res['policy_detail'] != "":
                    policy_detail = res['policy_detail'].encode('utf8')
                #end if
                service_type = ""
                if res['service_type'] and res['service_type'] != "":
                    service_type = res['service_type'].encode('utf8')
                #end if
                site_type = ""
                if res['site_type'] and res['site_type'] != "":
                    site_type = res['site_type'].encode('utf8')
                #end if
                database_type = ""
                if res['database_type'] and res['database_type'] != "":
                    database_type = res['database_type'].encode('utf8')
                #end if
                cookie_url = ""
                cookie = ""
                if res['cookie_url'] and res['cookie_url'] != "":
                    cookie_url = res['cookie_url'].encode("utf8")
                    sql = "select `cookie` from `cookie` where `url` = %s order by `id` desc"
                    self.cursor.execute(sql,(res['cookie_url']))
                    self.conn.commit()
                    temp = self.cursor.fetchone()
                    if temp:
                        cookie = temp['cookie'].encode("utf8")
                    #end if
                #end if
                content_code = ""
                begin_path = ""
                if res['begin_path'] and res['begin_path'] != "":
                    begin_path = res['begin_path'].encode('utf8')
                #end if
                logging.getLogger().error("startDomainMain")
                #加载排序URL列表
                exclude_url = ""
                if res['exclude_url'] and res['exclude_url'] != "":
                    exclude_url = res['exclude_url'].encode('utf8').split("|")
                #end if
                
                
                ######################################## 在DNS配置文件中加入这个域名的DNS信息
                self.thread_lock.acquire()
                self.add_dns(ip, domain, self.task_id, domain_id)
                self.thread_lock.release()
                
                
                ####################################### 判断这个域名是否已扫描
                if state == 1:
                    self.endScanDomain(domain_id,ip)
                    return
                #end if
                
                
                self.add_scan_log(domain_id,spider_state)
                ###################################### 预扫描，首先访问这个域名，查看网站是否可以访问，获取网站名称，网站类型，网站编码
                ###################################### 预扫描5次
                write_scan_log(self.task_id,domain_id,"预扫描开始")
                flag = res = content = checkOk = None
                target = []
                target.append(begin_path) if begin_path != "" else None
                target.append("%s://%s%s"%(scheme,domain,base_path)) if base_path != "/" else None
                target.append("%s://%s"%(scheme,domain))

                for url in target:
                    flag,res,content = self.PreDomainScan(scheme,domain,url)
                    if not flag:
                        write_scan_log(self.task_id,domain_id,"预扫描失败,url:"+url)
                        continue                        
                    else:
                        #################################### 检测网站的状态，有的网站访问后直接访问500或者其他的情况。
                        if self.checkDomainWorkMode(res, title) == False:
                            write_scan_log(self.task_id,domain_id,"网站状态检测未通过,url:"+url)
                            continue
                        else:
                            checkOk = 1
                            break                    
                        #end if       
                    #end if
                #end for
                if not checkOk:
                    self.updateDomainException("网站无法访问", domain_id, ip)
                    return
                else:
                    content_code = self.getDomainCode(content)
                    if title == "" and res and res.has_key('status') and res['status'] == '200':
                        title = self.updateDomainTitle(content, domain_id)
                    #end if
                    if site_type == "":
                        site_type = self.updateSiteType(res, domain_id)
                    #end if
                    if content_code == "":
                        content_code = self.getDomainCode(content)
                    #end if
                #end if
                write_scan_log(self.task_id,domain_id,"预扫描完成")
                updateHostScan(ip,self.cursor,self.conn,self.task_id,self.asset_scan_id) #check host scan
                if self.web_timeout: socket.setdefaulttimeout(self.web_timeout)
                #################################### 开始扫描这个域名
                #Fix BUG #1889
                current_time = time.strftime("%Y-%m-%d %X",time.localtime())
                #sql = "update domain_list_%s set start_time = '%s', exception = '' where id = '%s'" % (self.task_id,current_time,domain_id)
                sql = "update domain_list_%s set state = '0', exception = '' where id = '%s'" % (self.task_id,domain_id)
                self.cursor.execute(sql)
                self.conn.commit()
                sql = "update domain_list_%s set start_time = '%s' where id = '%s' and start_time = '1970-01-02 00:00:00'" % (self.task_id, current_time, domain_id)
                self.cursor.execute(sql)
                self.conn.commit()
                
                
                #################################### 初始化异常统计的计数器
                rec = request_exception_counter(100)
                rec.domain = domain
                
                logging.getLogger().error("startDomainMain1111"+str(domain))
                ###############################
                #policy:
                #    1:快速扫描，只扫描指定的域名
                #    2:完全扫描，扫描指定的域名，并且扫描二级域名
                #    3:扫描指定目录及子目录
                #    4:扫描指定的URL，这个情况下，不需要爬虫
                #    5:通过域名反查得到的域名
                #    6:登陆型扫描
                ###############################
                
                
                ################################### 判断是否开启爬虫并且爬虫未扫描
                if progress == '':
                    progress = '0'
                    sql = "update domain_list_%s set `progress` = '%s' where `id` = '%s'" % (self.task_id,progress,domain_id)
                    self.cursor.execute(sql)
                    self.conn.commit()
                #end if
                if self.web_spider_enable == 1 and spider_state == 0:
                    #如果爬虫开启并且爬虫未扫描，则清空这个域名的所有记录，重新开始扫描
                    progress = '0'
                    
                    sql = ""
                    sql = "delete from scan_result_%s where domain_id = '%s'" % (self.task_id,domain_id)
                    self.cursor.execute(sql)
                    self.conn.commit()
                    
                    sql = ""
                    sql = "delete from url_list_%s where `domain_id` = '%s'" % (self.task_id,domain_id)
                    self.cursor.execute(sql)
                    self.conn.commit()
                    #开启爬虫，当扫描指定的URL时，不需要爬虫
                    if policy != 4:
                        spider_ob = {'task_id':self.task_id,'domain_id':domain_id,'domain':domain,'web_url_count':self.web_url_count,'web_timeout':self.web_timeout,'policy':policy,'base_path':base_path, 'rec':rec}
                        spider_ob['scheme'] = scheme
                        spider_ob['max_timeout_count'] = 30
                        spider_ob['end_time'] = time.time() + 1800
                        spider_ob['title'] = title
                        spider_ob['domain_queue'] = self.domain_queue
                        spider_ob['ip'] = ip
                        spider_ob['policy_detail'] = policy_detail
                        spider_ob['cookie_url'] = cookie_url
                        spider_ob['cookie'] = cookie
                        spider_ob['asset_scan_id'] = self.asset_scan_id
                        spider_ob['begin_path'] = begin_path
                        spider_ob['web_getdomain_enable'] = self.web_getdomain_enable
                        spider_ob['web_getdomain_timeout'] = self.web_getdomain_timeout
                        spider_ob['exclude_url'] = exclude_url
                        write_scan_log(self.task_id,domain_id,"开启爬虫，开始扫描")
                        #Add by xiayuying 2013-09-13 for check which spider to be used.
                        if(self.checkSpiderFlag()):
                          import Spider2 as Spider
                        else:
                          import Spider
                        Spider.main(spider_ob)
                        write_scan_log(self.task_id,domain_id,"爬虫结束")
                    #end if
                #end if
                sql = "update domain_list_%s set `spider_state` = '1' where `id` = '%s'" % (self.task_id,domain_id)
                self.cursor.execute(sql)
                self.conn.commit()
                
                logging.getLogger().error("startDomainMain22222")
                ###################################### 检测是否存在通信异常的情况
                #if rec.err_out() and not self.isForce:
                if flowControl(self,0,rec,self.isForce,self.web_speed,self.url_time,False):
                    write_scan_log(self.task_id,domain_id,"检测异常计数器")
                    self.updateDomainException("通信异常", domain_id, ip)
                    logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.startDomainMain:" \
                                              + ",task id:" + self.task_id + ",domain:" + domain + \
                                              ",recinfo:" + rec.dump_info())
                    logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.startDomainMain: too many error, stop scan, domain:" + domain + ",last vul id:0" )
                    return
                #end if
                
                logging.getLogger().error("startDomainMain44444")
                ###################################### 增加配置信息，开始扫描
                sql = "select domain,base_path,title from domain_list_%s where id = '%s'" % (self.task_id,domain_id)
                self.cursor.execute(sql)
                self.conn.commit()
                res = self.cursor.fetchone()
                domain = res['domain'].encode('utf8')
                base_path = res['base_path'].encode('utf8')
                title = res['title']
                if title != '':
                    title = title.encode('utf8')
                #end if
                
                #################################### 检测网站的状态，有的网站访问后直接访问500或者其他的情况。
                #check status
                if self.checkDomainWorkMode({}, title) == False:
                    self.endScanDomain(domain_id, ip)
                    return
                #end if
                
                max_thread = 10
                error_len_dict = {}
                params_dict = {}
                params_dict['task_id'] = self.task_id
                params_dict['task_name'] = self.task_name
                params_dict['domain_id'] = domain_id
                params_dict['user_id'] = self.user_id
                params_dict['max_thread'] = max_thread
                params_dict['web_timeout'] = self.web_timeout
                params_dict['ip'] = ip
                params_dict['domain'] = domain
                params_dict['scheme'] = scheme
                params_dict['base_path'] = base_path
                params_dict['error_len_dict'] = error_len_dict
                params_dict['site_type'] = site_type
                params_dict['rfi_url'] = self.rfi_url
                params_dict['rfi_keyword'] = self.rfi_keyword
                params_dict['max_timeout_count'] = 20
                params_dict['rec'] = rec
                params_dict['content_code'] = content_code
                params_dict['cookie'] = cookie
                params_dict['isstart']=self.GetVerification()
                params_dict['len_404'] = []
                params_dict['asset_scan_id'] = self.asset_scan_id
                params_dict['isForce'] = self.isForce
                params_dict['web_speed'] = self.web_speed
                params_dict['exclude_url'] = exclude_url
                if self.web_speed == 1:   #middle
                    self.url_time['speed'] = float(60)/360
                    params_dict['web_minute_package_count'] = self.url_time
                elif self.web_speed == 2: #low
                    self.url_time['speed'] = float(60)/180
                    params_dict['web_minute_package_count'] = self.url_time
                elif self.web_speed ==3:  #defined
                    self.url_time['speed'] = float(60)/self.web_minute_package_count
                    params_dict['web_minute_package_count'] = self.url_time
                elif self.web_speed ==4:  #auto
                    self.url_time['speed'] = float(60)/360
                    params_dict['web_minute_package_count'] = self.url_time
                else:
                    params_dict['web_minute_package_count'] = self.url_time
                
                '''
                #################################### 检查网站的错误请求状态  
                
                #不存在的目录的HEAD请求状态

                '''
                write_scan_log(self.task_id,domain_id,"加载未扫描漏洞ID")
                #判断该域名扫描进度，加载未扫描的漏洞ID
                temp = self.vuls_1.split('|')
                progress_list = progress.split('|')
                vul_list = []
                if temp and len(temp) > 0:
                    for vul_id in temp:
                        if vul_id in progress_list:
                            continue
                        else:
                            if vul_id and vul_id != '':
                                vul_list.append(vul_id)
                            #end if
                        #end if
                    #end for
                #end if
                if len(vul_list) > 0:
                    write_scan_log(self.task_id,domain_id,"加载URL列表")
                    #加载爬虫爬出来的URL，当扫描指定的URL时，加载定义好的URL列表
                    url_list = []
                    if policy == 4:
                        temp = policy_detail.split('|')
                        for r in temp:
                            if check_exclude_url(exclude_url,r):
                                continue
                            #end if
                            
                            t = r.split('?')
                            url = t[0]
                            params = ""
                            if len(t) > 1:
                                params = t[1]
                            #end if
                            #fix BUG #3577 by haiboyi,chinese path error
                            if nonascii(url): url = safe_url_string(url)
                            url_list.append({'id':0,'url':url,'params':params,'method':'get'})
                        #end for
                    else:
                        sql = "select * from url_list_%s where `domain_id` = '%s'" % (self.task_id,domain_id)
                        self.cursor.execute(sql)
                        self.conn.commit()
                        res = self.cursor.fetchall()
                        for r in res:
                            url = r['url'].encode('utf8')
                            if nonascii(url): url = safe_url_string(url)
                            url_list.append({'id':str(r['id']),'url':url,'params':r['params'].encode('utf8'),'method':r['method'].encode('utf8'),'refer':r['refer'].encode('utf8')})
                        #end for
                    #end if
                    
                    for vul_id in vul_list:
                        vul_id = vul_id.replace(" ","")
                        if vul_id == "":
                            continue
                        #end if
                        params_dict['rec'].now_vul_id = int(vul_id)
                        logging.getLogger().error("File:progress+++++++++++:" + str(progress))
                        #更新进度
                        progress = "%s|%s" % (progress,vul_id)
                        logging.getLogger().error("File:progress-----------:" + str(progress))
                        sql = "update domain_list_%s set `progress` = '%s' where `id` = '%s'" % (self.task_id,progress,domain_id)
                        self.cursor.execute(sql)
                        self.conn.commit()
                        sql = "delete from scan_result_%s where vul_id = '%s' and domain_id = '%s'" % (self.task_id,vul_id,domain_id)
                        self.cursor.execute(sql)
                        self.conn.commit()
                    
                        params_dict['vul_id'] = vul_id
                        params_dict['vul_type'] = self.vuls_dict[vul_id]['vul_name']
                        params_dict['level'] = self.vuls_dict[vul_id]['level']
                        params_dict['scan_type'] = self.vuls_dict[vul_id]['scan_type']
                        params_dict['script'] = self.vuls_dict[vul_id]['script']
                        params_dict['status'] = '0'
                        params_dict['end_time'] = time.time() + 1800
                        params_dict['timeout_count'] = 0
                    
                        write_scan_log(self.task_id,domain_id,"漏洞ID：%5s 漏洞名：%s 开始扫描" % (vul_id,params_dict['vul_type']))
                        #测试爬虫爬出来的路径
                        if params_dict['scan_type'] == 1:
                            url_queue = Queue()
                            for r in url_list:
                                url_queue.put(r)
                            #end for
                            params_dict['queue'] = url_queue
                            ob = RunUrlScript(params_dict)
                            ob.start()
#                            print "ob.start()"
                        #end if
                    
                        #如果只测试指定的URL则不需要运行测试域名和测试漏洞库
                        if policy != 4:
                            #测试域名
                            if params_dict['scan_type'] == 2:
                                ob = RunDomainScript(params_dict)
                                ob.start()
                            #end if
                        #end if
                        write_scan_log(self.task_id,domain_id,"漏洞ID：%5s 漏洞名：%s 扫描已结束" % (vul_id,params_dict['vul_type']))
                        logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.startDomainMain:" + ",task id:" + self.task_id + ",domain:" + params_dict["domain"] + ",recinfo:" + params_dict["rec"].dump_info())
                        #if params_dict['rec'].err_out() and not self.isForce:
                        if flowControl(self,0,params_dict['rec'],self.isForce,self.web_speed,self.url_time,False):
                            write_scan_log(self.task_id,domain_id,"检测异常计数器")
                            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.startDomainMain: too many error, stop scan, domain:" + params_dict["domain"] + ",last vul id:" + str(vul_id))
                            self.updateDomainException("通信异常", domain_id, ip)
                            return
                        #end if
                    #end for
                    url_list = []
                #end if
                
                
                if policy != 4:
                    temp = self.vuls_2.split('|')
                    progress_list = progress.split('|')
                    vul_list = Queue()
                    if temp and len(temp) > 0:
                        for vul_id in temp:
                            if vul_id in progress_list:
                                continue
                            else:
                                if vul_id and vul_id != '':
                                    vul_list.put(vul_id)
                                #end if
                            #end if
                        #end for
                    #end if
                
                    if vul_list and vul_list.empty() == False:
                        if self.checkHeadRequest(scheme, domain, base_path):
                            params_dict['web_head_request_enable'] = '1'
                        else:
                            params_dict['web_head_request_enable'] = '0'
                        #end if
                        if scheme == 'https':
                            params_dict['ssl_enable'] = True
                        else:
                            params_dict['ssl_enable'] = False
                        #end if
                        
                        ########################### 错误状态获取
                        #不存在的目录的HEAD请求状态
                        if params_dict['web_head_request_enable'] == '1' and self.checkErrorFileStatus(scheme, domain, base_path, "/", "HEAD"):
                            params_dict['web_dir1_status_for_head_enable'] = '1'
                        else:
                            params_dict['web_dir1_status_for_head_enable'] = '0'
                        #end if
                        #print "web_dir1_status_for_head_enable",params_dict['web_dir1_status_for_head_enable']
                        #不存在的目录的GET请求状态
                        if self.checkErrorFileStatus(scheme, domain, base_path, "/", "GET"):
                            params_dict['web_dir1_status_for_get_enable'] = '1'
                        else:
                            params_dict['web_dir1_status_for_get_enable'] = '0'
                        #end if
                        #print "web_dir1_status_for_get_enable",params_dict['web_dir1_status_for_get_enable']
                        #不存在的目录的HEAD请求状态
                        if params_dict['web_head_request_enable'] == '1' and self.checkErrorFileStatus(scheme, domain, base_path, "", "HEAD"):
                            params_dict['web_dir2_status_for_head_enable'] = '1'
                        else:
                            params_dict['web_dir2_status_for_head_enable'] = '0'
                        #end if
                        #print "web_dir2_status_for_head_enable",params_dict['web_dir2_status_for_head_enable']
                        #不存在的目录的GET请求状态
                        if self.checkErrorFileStatus(scheme, domain, base_path, "", "GET"):
                            params_dict['web_dir2_status_for_get_enable'] = '1'
                        else:
                            params_dict['web_dir2_status_for_get_enable'] = '0'
                        #end if
                        #print "web_dir2_status_for_get_enable",params_dict['web_dir2_status_for_get_enable']
                        
                        suffix_list = ['cgi','cfm','php','aspx','asp','html','inc','txt','jsp','xml','mdb','sql','nsf','bak','htx','rar','zip','pm','htm','pl','ini','cnf','htpasswd','cfg','exe','conf','dll','bas','dat','log','listprint','snp','cobalt','db','pwd','ida','idq','htw','btr','box','vts','htr','idc','do']
                        for r in suffix_list:
                            k = 'web_%s_status_for_head_enable' % (r)
                            if params_dict['web_head_request_enable'] == '1' and self.checkErrorFileStatus(scheme, domain, base_path, ".%s" % (r), "HEAD"):
                                params_dict[k] = '1'
                            else:
                                params_dict[k] = '0'
                            #end if
                            #print k,params_dict[k]
                            k = 'web_%s_status_for_get_enable' % (r)
                            if self.checkErrorFileStatus(scheme, domain, base_path, ".%s" % (r), "GET"):
                                params_dict[k] = '1'
                            else:
                                params_dict[k] = '0'
                            #end if
                            #print k,params_dict[k]
                        #end for
                        
                        params_dict['web_404_len_range_min'], params_dict['web_404_len_range_max'] = self.checkWeb404LenRange(scheme, domain, base_path)
                        
                        params_dict['find_vul_count'] = 0
                        ob = RunCgidbScript(params_dict)
                        while vul_list.empty() == False:
                            temp  = []
                            rules = Queue()
                            vul_id = ''
                            for i in range(30):
                                if vul_list.empty() == False:
                                    vul_id = vul_list.get_nowait()
                                    tt = str(vul_id).replace(" ","")
                                    if tt == "":
                                        continue
                                    #end if
                                    temp.append(tt)
                                    rules.put({'vul_id':vul_id,'vul_name':self.vuls_dict[vul_id]['vul_name'],'level':self.vuls_dict[vul_id]['level'],'url':self.cgidb[vul_id]['url'],'method':self.cgidb[vul_id]['method'],'response':self.cgidb[vul_id]['response'],'response_type':self.cgidb[vul_id]['response_type']})
                                else:
                                    break
                                #end if
                            #end for
                            if rules.empty() == False:
                                if len(temp) > 0:
                                    if progress == "":
                                        progress = '|'.join(temp)
                                    else:
                                        progress = "%s|%s" % (progress,'|'.join(temp))
                                    #end if
                                    sql = "update domain_list_%s set `progress` = '%s' where `id` = '%s'" % (self.task_id,progress,domain_id)
                                    self.cursor.execute(sql)
                                    self.conn.commit()
                                #end if
                            
                                ob.start(rules)
                                
                            else:
                                break
                            #end if
                            if params_dict['find_vul_count'] > 10:
                                break
                            #end if
                            
                            #if params_dict['rec'].err_out() and not self.isForce:
                            if flowControl(self,0,params_dict['rec'],self.isForce,self.web_speed,self.url_time,False):
                                logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.startDomainMain: too many error, stop scan, domain:" + params_dict["domain"] + ",last vul id:" + str(vul_id))
                                self.updateDomainException("通信异常", domain_id, ip)
                                return
                            #end if
                        #end while
                    #end if
                    #print params_dict['web_status_enable'],params_dict['web_head_request_enable'],params_dict['ssl_enable']
                #end if
                
                #print ">>>>>>>>>>>>>>>>>>>",params_dict['len_404']
                
                #结束扫描
                self.endScanDomain(domain_id,ip)
                write_scan_log(self.task_id,domain_id,"域名扫描已结束")
                self.thread_lock.acquire()
                self.del_dns(ip, domain, self.task_id, domain_id)
                self.thread_lock.release()
            else:
                logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.startDomainMain: connect to mysql error ,task id:" + self.task_id + ",domain_id:" + domain_id)
                return domain_id  #发生异常将会返回domain_id，并加入队列，继续扫描
            #end try
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.startDomainMain:" + str(e) + ",task id:" + self.task_id + ",domain_id:" + domain_id)
            return domain_id
        #end try
    #end if
    
    def checkWeb404LenRange(self,scheme,domain,base_path):
        try:
            max = 0
            min = 0
            
            http = httplib2.Http(disable_ssl_certificate_validation=True)
            http.follow_redirects = False
            socket.setdefaulttimeout(30)

            if base_path[-1] =='/':
                base_path=base_path[:-1]  # fix BUG #2385
            
            url1 = "%s://%s%s%s" % (scheme,domain,base_path,"/n.html")
#           res, content = http.request(url1)
            res, content = nvs_httplib2_request(http,url1)
            if res and res.has_key('content-length'):
                min = int(res['content-length'])
            else:
                min = len(content)
            #end if
            
            url2 = "%s://%s%s%s" % (scheme,domain,base_path,"/nulllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll.html")
#           res, content = http.request(url2)
            res, content = nvs_httplib2_request(http,url2)
            if res and res.has_key('content-length'):
                max = int(res['content-length'])
            else:
                max = len(content)
            #end if
            
            if min > max:
                t = min
                min = max
                max = t
            #end if
            
            return min,max
            
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.checkWeb404LenRange:%s, task id:%s, scheme:%s, domain:%s, base_path:%s" % (str(e), self.task_id, scheme, domain, base_path))
            return 0,0
        #end try
    #end def
    
    def clearTmpFile(self,task_id,domain_id):
        try:
            vulscan_popen("rm -R /var/webs/task%s/*#%s#" % (task_id,domain_id))
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.clearTmpFile:%s, task id:%s, domain_id:%s" % (str(e),task_id,domain_id))
        #end try
    #end def
    
    def checkErrorFileStatus(self,scheme,domain,base_path,type,method):
        try:
            http = httplib2.Http(disable_ssl_certificate_validation=True)
            http.follow_redirects = False
            socket.setdefaulttimeout(30)
            url = "%s://%s%snulllllllllll%s" % (scheme,domain,base_path,type)
            if method.lower() == "head":
#               res, content = http.request(url, "HEAD")
                res, content = nvs_httplib2_request(http,url,"HEAD")
            else:
#               res, content = http.request(url)
                res, content = nvs_httplib2_request(http,url)
            #end if
            if res and res.has_key('status') and res['status'] == '404':
                return True
            else:
                return False
            #end if
        except Exception,e:
            logging.getLogger().error("File:common.py, checkErrorFileStatus:%s,task id:%s,scheme:%s,domain:%s,base_path:%s,type:%s,method:%s" % (str(e),self.task_id,scheme,domain,base_path,type,method))
            return False
        #end try
    #end def
    
    def add_dns(self,ip,domain,task_id,domain_id):
        try:
            if ip == domain:
                return
            #end if
            f = file("/etc/hosts", "r+")
            lines = f.readlines()
            msg = "%s %s #scanleak#%s#%s#" % (ip,domain,task_id,domain_id)
            for line in lines:
                if line.find(msg) >= 0:
                    f.close()
                    return
                #end if
            #end for
            lines.append(msg + '\n')
            f.close()
            
            f = file("/etc/hosts", "w+")
            f.writelines(lines)
            f.close()
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.add_dns:" + str(e) + ",task id:" + task_id + ", domain id:" + domain_id)
        #end try
    #end def
        
    def del_dns(self,ip,domain,task_id,domain_id):
        try:
            if ip == domain:
                return
            #end if
            f = file("/etc/hosts", "r+")
            lines = f.readlines()
            msg = "%s %s #scanleak#%s#%s#" % (ip,domain,task_id,domain_id)
            for line in lines:
                if line.find(msg) >= 0:
                    lines.remove(line)
                #end if
            #end for
            f.close()
            f = file("/etc/hosts", "w+")
            f.writelines(lines)
            f.close()
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.del_dns:" + str(e) + ",task id:" + task_id + ", domain id:" + domain_id)
        #end try            
    #end def
    
    def checkDomainId(self,domain_id):
        try:
            temp = int(domain_id)
            if temp > 0 and temp < 10000000000:
                return True
            else:
                return False
            #end if
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.checkDomainId:" + str(e) + ",task id:" + self.task_id)
            return False
        #end try  
    #end def
    
    def checkDomainList(self):
        try:
            web_getdomain_state = 0
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            
            sql = "select web_getdomain_state from task_manage where id = '%s'" % (self.task_id)
            cursor.execute(sql)
            conn.commit()
            res = cursor.fetchone()
            web_getdomain_state = res['web_getdomain_state']
            if web_getdomain_state == 0:
                cursor.close()
                conn.close()
                return False
            #end if
            
            sql = ""
            if self.asset_scan_id > 0:
                sql = "select count(*) as c from domain_list_%s where `state` <> '1' and `asset_scan_id` = '%s'" % (self.task_id,self.asset_scan_id)
            else:
                sql = "select count(*) as c from domain_list_%s where `state` <> '1'" % (self.task_id)
            #end if
            logging.getLogger().error("checkDomainList:" + str(sql))
            cursor.execute(sql)
            conn.commit()
            res = cursor.fetchone()
            
            if res['c'] > 0:
                cursor.close()
                conn.close()
                
                return False
            #end if
            
            return True
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.checkDomainList:" + str(e) + ",task id:" + self.task_id)
            return True
        #end try  
    #end def
    
    def check_exception_domain(self):
        flag = False
        self.check_exp_lock.acquire()
        try:
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            sql = ""
            if self.asset_scan_id > 0:
                sql = "select * from domain_list_%s where `state` = 2 and `asset_scan_id` = '%s'" % (self.task_id,self.asset_scan_id)
            else:
                sql = "select * from domain_list_%s where `state` = 2" % self.task_id
            #end if
            cursor.execute(sql)
            ret = cursor.fetchall()
            
            if len(ret) <= 0:
                flag = True
            #end if
            
            if ret:
                for r in ret:
                    if r["next_start_time"]:
                        if int(time.time()) > int(time.mktime(r["next_start_time"].timetuple())):
                            self.domain_queue.put(str(r["id"]))
                            #FIx BUG #2274 
                            #sql = "update domain_list_%s set `state` = 0 where `id` = '%s'" % (self.task_id, str(r["id"]))
                            sql = "update domain_list_%s set `state` = 0, `exception` = '' where `id` = '%s'" % (self.task_id, str(r["id"]))
                            cursor.execute(sql)
                            conn.commit()
                        #end if
                    #end if
                #end for
            #end if
            
                        
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.check_exception_domain:" + str(e))
        #end try
        self.check_exp_lock.release()
        
        if flag:
            self.count += 1
            return
        #end if
        
        time.sleep(30)
    #end def
    
    
    def checkHeadRequest(self,scheme,domain,base_path):
        try:
            http = httplib2.Http(disable_ssl_certificate_validation=True)
            http.follow_redirects = False
            socket.setdefaulttimeout(30)
            
            url = "%s://%s%s" % (scheme,domain,base_path)
#           res, content = http.request(url,"HEAD")
            res, content = nvs_httplib2_request(http,url,"HEAD")
            if res and res.has_key('status') and res['status'] in ['200','301','302','403'] and res.has_key('content-length'):
                return True
            else:
                return False
            #end if
            
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.checkHeadRequest:" + str(e) + ",task id:" + self.task_id)
            return False
        #end try
    #end def
        
    def run(self):
        try:
            #logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.run: function start ,task id:" + self.task_id)
            print '''------------------------------------------------------------
运行ScanDomainThread run: function start ,task id:%s 
------------------------------------------------------------'''%self.task_id
            #循环获取队列里面的域名ID
            if self.init() == False:
                return
            #end if
            while True:
                try:
                    #获取域名ID                
                    self.thread_lock.acquire()
                    flag = self.checkDomainList()
                    self.thread_lock.release()
                    logging.getLogger().error("run2:"+str(flag))
                    if flag:
                        logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.run: thread exit ,task id:" + self.task_id)
                        break
                    #end if
                    domain_id = None
                    try:
                        domain_id = self.domain_queue.get(True,30)
                    except Exception, ge:
                        pass
                    #end try

                    #开始这个域名的扫描
                    if domain_id and self.checkDomainId(domain_id):
                        self.count = 0
                        exception_domain_id = self.startDomainMain(str(domain_id)) #发生异常，加入扫描队列
                        # if exception_domain_id:
                        #     self.domain_queue.put(exception_domain_id)
                    #end if
                    self.check_exception_domain()
                                      
                except Exception,e1:
                    logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.startDomainScan while:" + str(e1) + ",task id:" + self.task_id)
                    self.count += 1
                #end try
                if self.count > 30*5:
                    break
                #end if
            #end while
        except Exception,e:
            logging.getLogger().error("File:ScanDomainThread.py, ScanDomainThread.startDomainScan:" + str(e) + ",task id:" + self.task_id)
        #end try
    #end def
#end class
