#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib2
import urllib2
import socket
import re
import urlparse
import hashlib
from Queue import Queue
import os
import sys
import MySQLdb
import HTMLParser
import json
import logging
import time
from lib.common import *
from plugins.lib.ex_httplib2 import *
from xml import sax
from LinkageWaf import *

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)

class Spider:
    def __init__(self,dic):
        try:
            self.domain_queue = dic['domain_queue']
            self.task_id = dic['task_id']
            self.domain_id = dic['domain_id']
            self.scheme = dic['scheme']
            self.domain = dic['domain'].lower()
#-------START yinkun 2014-10-16 ------------------------
            if checkIpv6(dic['domain']):
                self.domain = easyIpv6(dic['domain'])
                self.domain = '[' + self.domain + ']'
#-------END----------------------------------------
            self.ip = dic['ip']
            if checkIpv6(dic['ip']):
                self.ip = dic['ip'].lower()
                self.ip = easyIpv6(self.ip)

            self.title = dic['title']
            self.policy = dic['policy']
            self.policy_detail = dic['policy_detail']
            self.cookie_url = dic['cookie_url']
            self.cookie = dic['cookie']
            self.base_path = dic['base_path']
            self.base_url = "%s://%s%s" % (self.scheme,self.domain,self.base_path)
            self.begin_path = dic['begin_path']
            self.status = True
            self.code = ""
            self.result = dic['result']
            self.form_result = dic['form_result']
            self.temp_queue = dic['temp_queue']
            self.pattern_dict = dic['pattern_dict']
            self.html_patten = dic['html_patten']
            self.nomatch_type_list = dic['nomatch_type_list']
            self.uncontent_type_list = dic['uncontent_type_list']
            self.error_rule_list = dic['error_rule_list']
            self.maxnum = dic['maxnum']
            self.web_timeout = dic['web_timeout']
            self.web_getdomain_timeout = dic['web_getdomain_timeout']
            self.max_timeout_count = dic['max_timeout_count']
            self.end_time = dic['end_time']
            self.num = 0
            self.downloadDir = dic['downloadDir']
            self.rec = dic['rec']
            self.same_url_pattern_count= dic['same_url_pattern_count']
            #self.http = httplib2.Http(timeout=self.web_timeout)
            #self.http.follow_redirects = True
            self.http = ex_httplib2(self.rec, self.cookie)
            self.http.httlib2_set_follow_redirects(True)
            self.http.httlib2_set_timout(self.web_timeout)
            self.domainhttp = httplib2.Http(timeout=self.web_getdomain_timeout)
            self.domainhttp.follow_redirects = True
            self.html_parser = HTMLParser.HTMLParser()
            self.sep = '####################'
            self.name_not_found = 'name_not_found'
            self.timeout_content = "timeout"
            self.current_dir = self.base_path
            self.conn = ""
            self.cursor = ""
            self.hasSpace = True
            self.asset_scan_id = dic['asset_scan_id']
            self.web_getdomain_enable = dic['web_getdomain_enable']
            self.swfs = []
            self.postPattern = set()

            #self.top_domain = '.'.join(self.domain.split(':')[0].split('.')[1:])
            #self.top_domain = self.getHost(self.domain)
            self.top_domain = getTopDomain(self.domain)

            self.timeout_count = 0
            self.ip_patten = re.compile("^([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})$")
            self.ipv6_patten = re.compile("^((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?$")

            self.other_domain_list = []
            
            self.exclude_url = dic['exclude_url']

            self.init()
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.__init__:" + str(e) + ",task id:" + str(dic['task_id']) + ",domain id:" + str(dic['domain_id']))
        #end try
    #end def

    def checkOtherDomain(self,url):
        try:
            if self.policy != 5:
                return
            #end if
            temp = ""
            parse = urlparse.urlparse(url)
            scheme = parse[0].lower()
            if scheme != 'http' and scheme != 'https':
                return
            #end if
            domain = parse[1].lower()
            if domain.find("]:") > 0 or domain.find(":") > 0:
                if domain.find("]:") > 0:
                    port = domain.split("]:")[1]
                else:
                    port = domain.split(":")[1]
                #end if
                if port == "80":
                    scheme = "http"
                    if domain.find("]:") > 0:
                        domain = domain.split("]:")[0]+"]"
                    else:
                        domain = domain.split(":")[0]
                    #end if
                elif port == "443":
                    scheme = "https"
                    if domain.find("]:") > 0:
                        domain = domain.split("]:")[0]+"]"
                    else:
                        domain = domain.split(":")[0]
                    #end if
                #end if
            #end if

            temp = "%s://%s" % (scheme,domain)
            if temp in self.other_domain_list:
                return
            else:
                self.other_domain_list.append(temp)
            #end if

            ip = ""
            if domain == self.domain or len(domain.split('.')) < 3:
                return
            #end if
            if checkIpv4Inner(domain) or checkIpv6Inner(domain):
                return
            else:
                ip = domainToip(domain)
            #end if
            if self.ip != ip:
                return
            #end if

            flag,scheme,domain,base_path = getRedirect("%s://%s/" % (scheme,domain))
            if flag == False:
                return
            #end if
            if scheme != 'http' and scheme != 'https':
                scheme = 'http'
            #end if
            if len(domain.split('.')) < 3:
                return
            #end if

            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            sql = ""
            if self.asset_scan_id > 0:
                sql = "select count(*) as c from domain_list_%s where `domain` = '%s' and `scheme` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,domain,scheme,self.asset_scan_id)
            else:
                sql = "select count(*) as c from domain_list_%s where `domain` = '%s' and `scheme` = '%s'" % (self.task_id,domain,scheme)
            #end if
            cursor.execute(sql)
            conn.commit()
            res = cursor.fetchone()
            if res and len(res) > 0 and res['c'] > 0:
                cursor.close()
                conn.close()
                return
            #end if

            sql = "insert into domain_list_" + self.task_id + " (`task_id`,`task_name`,`domain`,`scheme`,`ip`,`state`,`spider_state`,`progress`,`title`,`base_path`,`policy`,`policy_detail`,`service_type`,`site_type`,`database_type`,`start_time`,`end_time`,`asset_scan_id`) values (%s,'',%s,%s,%s,'0','0','','',%s,%s,'','','','','0000-00-00 00:00:00','0000-00-00 00:00:00',%s)"
            cursor.execute(sql,(self.task_id,domain,scheme,ip,base_path,self.policy,self.asset_scan_id))
            conn.commit()
            sql = "select LAST_INSERT_ID() as domain_id"
            cursor.execute(sql)
            conn.commit()
            res = cursor.fetchone()
            if res and len(res) > 0 and res['domain_id'] > 0:
                self.domain_queue.put(str(res['domain_id']))
            #end if
            cursor.close()
            conn.close()
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.checkOtherDomain:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",url:" + url)
        #end try
    #end def
    
    def getHost(self,url):
        try:
            domainSuffix = {'info':None,'coop':None,'co':None,'kr':None,'com':None,'cn':None,'net':None,'org':None,'gov':None,'edu':None,'name':None,'biz':None,'cc':None,'tv':None}
        
            domain = ""
            temp_domain = ''
            url = url.lower()
#-------START 2014-10-15 yinkun-----------------------------------            
            if url.find("http://") >= 0 or url.find("https://") >= 0:
                parse = urlparse.urlparse(url)
#               domain = parse[1].split(":")[0]
                temp_domain = parse[1]                
            else:
#                domain = url.split("/")[0].split(":")[0]
                 temp_domain = url.split("/")[0]
            #end if
            if temp_domain.find('[') >= 0 and temp_domain.find(']:') >= 0:
                a = temp_domain.find(']:')
                domain = temp_domain[:a] + ']'
            else:
                domain = parse[1].split(":")[0]
#-------END-----------------------------------------------------------
        
            result = []
            list = domain.split(".")
            if len(list) == 1:
                return domain
            elif len(list) < 1:
                return False
            #end if
            list = domain.split('.')
            if len(filter(lambda x: not x.isdigit(), list)) == 0:
                return domain
            #end if
            if domainSuffix.has_key(list[-2].lower()):
                result = list[-3:]
            elif domainSuffix.has_key(list[-1].lower()):
                result = list[-2:]
            else:
                result = list[-2:]
            #end if
        
            return '.'.join(result)
            
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getHost:%s,task id:%s,domain id:%s,url:%s" % (str(e),self.task_id,self.domain_id,url))
            return False
        #end try
    #end def

    def checkPolicy(self,url):
        try:
            if checkIpv4Inner(url) or checkIpv6Inner(url):
                return
            #end if
            parse = urlparse.urlparse(url)
            if self.policy == 2 or self.policy == 55:
                #完整扫描，获取二级域名
                scheme = parse[0]
                top_domain = getTopDomain(parse[1])
                temp = parse[1].split(':')[0]
                if top_domain == self.top_domain and temp != self.domain.split(':')[0]:
                    #发现二级域名
                    domain = parse[1]
                    if domain.find(":") > 0:
                        port = domain.split(":")[1]
                        if port == "80":
                            scheme = 'http'
                            domain = domain.split(":")[0]
                        elif port == '443':
                            scheme = 'https'
                            domain = domain.split(":")[0]
                        #end if
                    #end if

                    flag,scheme,domain,base_path = getRedirect("%s://%s/" % (scheme,domain))
                    if flag == False:
                        return
                    #end if
                    if scheme != 'http' and scheme != 'https':
                        scheme = 'http'
                    #end if
                    if len(domain.split('.')) < 3:
                        return
                    #end if

                    if self.mysqlConnect():
                        sql = ""
                        if self.asset_scan_id > 0:
                            sql = "select count(*) as c from domain_list_%s where `domain` like '%s' and `scheme` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,"%"+domain+"%",scheme,self.asset_scan_id)
                        else:
                            sql = "select count(*) as c from domain_list_%s where `domain` like '%s' and `scheme` = '%s'" % (self.task_id,"%"+domain+"%",scheme)
                        #end if
                        self.cursor.execute(sql)
                        self.conn.commit()
                        res = self.cursor.fetchone()
                        if res and len(res) > 0 and res['c'] == 0:
                            ip = domainToip(domain)
                            #ip = self.get_ip_by_host(domain.split(':')[0])
                            if ip and ip != '' and (checkIpv4(ip) or checkIpv6(ip)):
                                sql = "insert into domain_list_" + self.task_id + " (`task_id`,`task_name`,`domain`,`scheme`,`ip`,`state`,`spider_state`,`progress`,`title`,`base_path`,`policy`,`policy_detail`,`service_type`,`site_type`,`database_type`,`start_time`,`end_time`,`asset_scan_id`) values (%s,'',%s,%s,%s,'0','0','','',%s,%s,'','','','','0000-00-00 00:00:00','0000-00-00 00:00:00',%s) "
                                self.cursor.execute(sql,(self.task_id,domain,scheme,ip,base_path,'55',self.asset_scan_id))
                                self.conn.commit()
                                sql = "select LAST_INSERT_ID() as domain_id"
                                self.cursor.execute(sql)
                                self.conn.commit()
                                res = self.cursor.fetchone()
                                if res and len(res) > 0 and res['domain_id'] > 0:
                                    self.domain_queue.put(str(res['domain_id']))
                                #end if
                                #更新主机和弱密码扫描
                                sql = ""
                                if self.asset_scan_id > 0:
                                    sql = "select count(*) as c from hostmsg_%s where `ip` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,ip,self.asset_scan_id)
                                else:
                                    sql = "select count(*) as c from hostmsg_%s where ip = '%s'" % (self.task_id,ip)
                                #end if
                                self.cursor.execute(sql)
                                self.conn.commit()
                                res = self.cursor.fetchone()
                                if res and len(res) > 0 and res['c'] == 0:
                                    current_time = time.strftime("%Y-%m-%d %X",time.localtime())
                                    sql = "insert into hostmsg_%s (`task_id`,`task_name`,`ip`,`state`,`port_state`,`host_state`,`web_state`,`weak_state`,`start_time`,`asset_scan_id`) values ('%s','','%s','1','0','0','0','0','%s','%s')" % (self.task_id,self.task_id,ip,current_time,self.asset_scan_id)
                                    self.cursor.execute(sql)
                                    self.conn.commit()
                                    sql = "update `task_manage` set `host_state` = '0',`weak_state` = '0',`port_state` = '0' where `id` = '%s'" % (self.task_id)
                                    self.cursor.execute(sql)
                                    self.conn.commit()
                                #end if
                                if self.web_getdomain_enable and self.policy == 2:
                                    getDomainPolicy(self,self.domainhttp,ip,domain,'55')
                            #end if
                        #end if
                #end if
            #end if

        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.checkPolicy:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
        #end try
    #end def

    def checklogout(self,url,url_content=""):
        try:
            list1 = ['logout','exit','tuichu','quit','abort','withdraw']
            list2 = []
            temp = u"注销"
            list2.append(temp.encode('utf8'))
            list2.append(temp.encode('gb2312'))
            temp = u"退出"
            list2.append(temp.encode('utf8'))
            list2.append(temp.encode('gb2312'))

            parse = urlparse.urlparse(url)
            path = parse[2]

            for row in list1:
                if path.find("%s." % (row)) >= 0:
                    return True
                #end if
            #end for

            url_content = url_content.replace(" ","")
            if url_content == "":
                return False
            #end if
            for row in list2:
                if url_content.find(row) == 0:
                    return True
                #end if
            #end for

            return False
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.checklogout:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",url:" + url)
            return False
        #end try
    #end def

    def get_ip_by_host(self,domain):
        try:
#-------START  yinkun 2104-10-16 --------------------
#gethostbyname 不能处理ipv6地址
            a = domain.find('[')
            b = domain.find(']')
            if a >= 0 and b >= 0:
                return domain[a+1:b]
#-------END
            ip = socket.gethostbyname(domain)
            return ip
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.get_ip_by_host:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ", domain:" + str(domain))
            return ''
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
                    logging.getLogger().error("File:Spider.py, Spider.mysqlConnect reconnect:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            #end if
            return True
        except Exception,e:
            self.conn = ''
            self.cursor = ''
            logging.getLogger().error("File:Spider.py, Spider.mysqlConnect:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
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
            logging.getLogger().error("File:Spider.py, Spider.mysqlClose:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return False
        #end try
    #end def

    def write_url_log(self,url,method='get',params='',refer=''):
        try:
            if url == '':
                return
            #end if
            if self.mysqlConnect():
                sql = ""
                if self.asset_scan_id > 0:
                    sql = "select count(id) as c from url_list_" + self.task_id + " where `url`=%s and `params`=%s and `method`=%s and `domain_id`=%s and `asset_scan_id`='"+str(self.asset_scan_id)+"'"
                else:
                    sql = "select count(id) as c from url_list_" + self.task_id + " where `url`=%s and `params`=%s and `method`=%s and `domain_id`=%s"
                #end if
                self.cursor.execute(sql,(url,params,method,self.domain_id))
                self.conn.commit()
                res = self.cursor.fetchone()
                if res and len(res) > 0 and res['c'] > 0:
                    return
                #end if
                url = url.decode('gb2312','replace').encode('utf-8')
                refer = refer.decode('gb2312','replace').encode('utf-8')
                params = params.decode('utf8','replace').encode('utf8')
                self.cursor.execute("set names utf8")
                self.conn.commit()
                sql = "insert into url_list_" + self.task_id + " (`url`,`method`,`params`,`domain_id`,`refer`,`asset_scan_id`) values (%s,%s,%s,%s,%s,%s)"
                self.cursor.execute(sql,(url,method,params,self.domain_id,refer,self.asset_scan_id))
                self.conn.commit()
            else:
                logging.getLogger().error("File:Spider.py, Spider.write_url_log: mysql connect error ,task id:" + str(dic['task_id']) + ",domain id:" + str(dic['domain_id']))
            #end if
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.write_url_log:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
        #end try
    #end def

    def changeCode(self,msg):
        if self.code == 'utf8' or self.code == 'utf-8':
            return msg
        elif self.code == 'gbk':
            try:
                return msg.decode('gbk').encode('utf8')
            except Exception,e:
                return msg
            #end try
        elif self.code == 'gb2312':
            try:
                return msg.decode('gb2312').encode('utf8')
            except Exception,e:
                return msg
            #end try
        else:
            try:
                return msg.decode(self.code).encode('utf8')
            except Exception,e:
                pass
            #end try
            try:
                return msg.decode('utf8').encode('utf8')
            except Exception,e:
                pass
            #end try
            try:
                return msg.decode('gb2312').encode('utf8')
            except Exception,e:
                pass
            #end try
            try:
                return msg.decode('gbk').encode('utf8')
            except Exception,e:
                pass
            #end try
            try:
                return msg.encode('utf8')
            except Exception,e:
                pass
            #end try
            return msg
        #end if
    #end def

    def getBasePath(self,url):
        try:
            base_path = ""
            parse = urlparse.urlparse(url)
            if parse[2] == "":
                base_path = "/"
            elif parse[2][-1] == "/":
                base_path = parse[2]
            elif parse[2].find('.') > 0 or parse[2].find('?') > 0:
                t = parse[2].split('/')
                if len(t) <= 2:
                    base_path = "/"
                else:
                    base_path = "%s/" % ("/".join(t[0:-1]))
                #end if
            else:
                base_path = "%s/" % (parse[2])
            #end if
            if base_path == "":
                base_path = "/"
            #end if

            return base_path
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getBasePath:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",url:" + url)
            return "/"
        #end try
    #end def

    def getBaseUrl(self,url):
        try:
            if url.lower().find('http://') < 0 and url.lower().find('https://') < 0:
                if url == '':
                    url = '%s://%s/' % (self.scheme,self.domain)
                elif url[0] == '/':
                    url = '%s://%s%s' % (self.scheme,self.domain,url)
                else:
                    url = '%s://%s/%s' % (self.scheme,self.domain,url)
                #end if
            #end if
            res, content = self.requestUrl(url)
            if res.has_key('content-location'):
                url = res['content-location']
            #end if

            return url
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getBaseUrl:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",url:" + url)
            return "%s://%s/" % (self.scheme,self.domain)
        #end try
    #end def

    def getBase(self):
        try:
            res, content = self.requestUrl(self.scheme + "://" + self.domain + "/")
            match = re.findall(r"<(\s*)meta(\s+)http-equiv=(\s*)(\"|')(\s*)refresh(\s*)(\4)(\s+)content=(\s*)(\"|')([\.0-9\s]+);(\s*)url=(.+?)(\10)(\s*)[/]*>",content,re.I)
            if match and len(match) > 0:
                self.base_url = self.getBaseUrl(match[0][-3].replace(" ",""))
                return
            #end if
            #method 1 end

            #action 2 start
            if res.has_key('status') and (res['status'] == '302' or res['status'] == '301'):
                if res.has_key('location'):
                    self.base_url = self.getBaseUrl(res['location'])
                    return
                #end if
            #end if
            #action 2 end

            '''
            #method2
            match = re.findall(r"(window\.location|window\.location\.href|location\.href)(\s*)=(\s*)(\"|')(.+?)\4",content,re.I)
            for row in match:
                temp = "%s%s=%s%s%s%s" % (row[0],row[1],row[2],row[3],row[4],row[3])
                url = row[4]
                flag = True
                if flag:
                    url = self.changeUrl("http://%s/" % (self.domain), url)
                    self.base_url = url
                    parse = urlparse.urlparse(url)
                    if parse[2] == "":
                        self.base_path = "/"
                    elif parse[2][-1] == "/":
                        self.base_path = parse[2]
                    elif parse[2].find('.') > 0 or parse[2].find('?') > 0:
                        t = parse[2].split('/')
                        if len(t) <= 2:
                            self.base_path = "/"
                        else:
                            self.base_path = "%s/" % ("/".join(t[0:-1]))
                        #end if
                    else:
                        self.base_path = "%s/" % (parse[2])
                    #end if
                    return
                #end if
            #end for
            '''

            if res.has_key('content-location'):
                self.base_url = res['content-location']
            else:
                self.base_url = self.scheme + "://" + self.domain + "/"
            #end if
            #self.base_path = self.getBasePath(self.base_url)

        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getBase:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
        #end try
    #end def

    def loadInitUrl(self):
        try:
            self.addUrl(self.base_url,"%s://%s/" % (self.scheme,self.domain))
            self.temp_queue.put(self.base_url)

            if self.begin_path != '':
                self.addUrl(self.begin_path,self.base_url)
                self.temp_queue.put(self.begin_path)
            #end if

            if self.current_dir != '/':
                current = "%s://%s%s" % (self.scheme,self.domain,self.current_dir)
                self.addUrl(current,self.base_url)
                self.temp_queue.put(current)
            #end if

            if self.policy == 6:
                #当为登陆型扫描模式
                self.addUrl(self.policy_detail,"%s://%s/" % (self.scheme,self.domain))
                self.temp_queue.put(self.policy_detail)
                self.addUrl(self.cookie_url,"%s://%s/" % (self.scheme,self.domain))
                self.temp_queue.put(self.cookie_url)
            #end if


            lines = []

            dic_path = sys_path("/vuls_db/path")
            f = file(dic_path, "r+")
            temp = f.readlines()
            f.close()
            for line in temp:
                url = "%s://%s%s%s" % (self.scheme,self.domain,self.base_path,line[1:])
                url = url.replace("\n","").replace("\r","")
                lines.append(url)
            #end for

            timeout_count = 0
            result = []
            for line in lines:
                #res, content = self.http.request(line) 
                res, content = nvs_httplib2_request(self.http,line)
                if content == self.timeout_content:
                    timeout_count = timeout_count + 1
                #end if
                if timeout_count > 10:
                    break
                #end if
                if self.rec.err_out():
                    break
                #end if
                if res['status'] == '200' or res['status'] == '403' or res['status'] == '401':
                    content = content.lower()
                    if content.find('转到父目录')>=0 or content.find('返回上一级目录')>=0 or  content.find('directory listing for')>=0 or content.find('directory listing denied') >= 0 or content.find('index of') >= 0 or content.find('href') >= 0 or content.find('action') >= 0:
                        result.append(line)
                        #self.addUrl(url,"")
                    #end if
                #end if
            #end for
            if len(result) > 4:
                return
            else:
                for line in result:
                    self.addUrl(line, "")
                #end for
            #end if

            #create getswf tmp dir
            path = "/tmp/%s" % self.task_id
            if not os.path.exists(path):
                os.mkdir(path)

        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.loadInitUrl:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
        #end try
    #end def

    def getRobots(self):
        """
        Disallow: /admin/
        Disallow: /api/
        Disallow: /apps/
                /category/*/page/
                */feed/
        """
        try:
            base = "%s://%s/" % (self.scheme,self.domain)
            robotsUrl = base + "robots.txt"
            res,content=self.requestUrl(robotsUrl)
            rows=[]
            if content.find('allow') > -1:
                lines = content.splitlines()
                allow_compile = re.compile(r"allow(\s*):(\s*)(.+)",re.I)
                for line in lines:
                    match=allow_compile.search(line.rstrip())
                    if match:
                        row=match.group(3).split('*')[0]
                        if row != '':
                            rows.append(row)
                        #end if
                    #end if
                #end for
            #end if
            for row in rows:
                url=self.changeUrl(base, row)
                res , content = self.requestUrl(url)
                if res['status'] == '200' or res['status'] == '403' or res['status'] == '401':
                    self.addUrl(url,robotsUrl)
                    url_tuple = urlparse.urlparse(url)
                    row_list = url_tuple[2].split('/')
                    for i in range(10):
                        if len(row_list) > 2:
                            row_list = row_list[0:-1]
                            self.addUrl("%s://%s%s/" % (url_tuple[0],url_tuple[1],'/'.join(row_list)),robotsUrl)
                        else:
                            break
                        #end if
                    #end for
                #end if
            #end for
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getRobots:" + str(e)+ ",task id:" + self.task_id + ",domain id:" + self.domain_id)


    def getSitemap(self):

        class LocsHandler(sax.ContentHandler):

            def __init__(self):
                self.isLoc = 0
                self.__locs = []

            @property
            def urls(self):
                return self.__locs

            def startElement(self, name, attributes):
                if name == 'loc':
                    self.url = ""
                    self.isLoc = 1

            def characters(self, data):
                if self.isLoc:
                    self.url += data

            def endElement(self, name):
                if name == "loc":
                    self.isLoc = 0
                    self.__locs.append( self.url )

        try:
            sitemap="%s://%s/%s" % (self.scheme,self.domain,'sitemap.xml')
            parser =sax.make_parser( )
            handler = LocsHandler( )
            parser.setContentHandler(handler)
            parser.parse(sitemap)
            for url in handler.urls:
                self.addUrl(url.encode('utf8'),sitemap )
        except sax.SAXException:
            pass
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getSitemap:" + str(e)+ ",task id:" + self.task_id + ",domain id:" + self.domain_id)


    def getCode(self):
        try:
            res, content = self.requestUrl(self.base_url)
            match = re.findall(r"<meta(.+?)charset(.*?)=(.+?)\"",content,re.I)
            if match and len(match) > 0:
                row = match[0][2]
                row = row.replace(" ","")
                row = row.lower()
                self.code = row
            #end if

            self.updateDomainTitle(content)

        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getCode:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
        #end try
    #end def

    def updateDomainTitle(self,content):
        try:
            '''
            if self.title and self.title != '':
                return
            #end if
            '''
            match = re.findall(r"<(\s*)title(\s*)>(.*?)<(\s*)/(\s*)title(\s*)>",content,re.I|re.DOTALL)
            if match and len(match) > 0:
                self.title = match[0][2].replace("\r","").replace("\n","")
            #end if
            if self.title == "":
                return
            #end if
            self.title = self.changeCode(self.title)
            if self.mysqlConnect() and self.title != "":
                sql = "update domain_list_" + self.task_id + " set `title` = %s where `id` = %s"
                self.cursor.execute(sql,(self.title,self.domain_id))
                self.conn.commit()
            #end if

        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.updateDomainTitle:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
        #end try
    #end def

    def getCurrentDir(self):
        try:
            if self.mysqlConnect() and len(self.current_dir) ==0 :
                sql = "select `target` from task_manage where `id` = %s"
                self.cursor.execute(sql,self.task_id)
                self.conn.commit()
                res = self.cursor.fetchone()
                # target: www.hx168.com.cn#3#/hxzq/|/kk/#http
                if res :
                    dirs = res['target'].split('#')[2]
                    self.current_dir = dirs.split('|') if dirs != '' else self.current_dir
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.checkPolicy:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)

    def indexForbidden(self):
        try:
            base = "%s://%s/" % (self.scheme,self.domain)
            #res ,content = self.http.request(base)
            res ,content = nvs_httplib2_request(self.http,base)
            if res.has_key('status') and res['status'] == '403':
                index_urls=['index.html','index.php','index.asp','index.aspx','index.jsp']
                for index in index_urls:
                    url="%s%s" %(base,index)
                    r ,c = self.requestUrl(url)
                    if r.has_key('status') and r['status'] == '200':
                        self.addUrl(url, base)
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.indexForbidden:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)


    def urlfromwaf(self):
        try:
            refer = "addurl2"
            linkagewaf = LinkageWaf(self.task_id,self.domain_id)
            urllist = linkagewaf.main()
            if urllist and len(urllist) > 0:
                for url in urllist:
                    if url.find("%2E") >= 0 or url.find("%2e") >= 0 or url.find("%5C") >= 0 or url.find("%5c") >= 0:
                        url = urllib2.unquote(url)
                    #end if
                    if url.find("/./") >= 0 or url.find("'") >= 0 or url.find("\"") >= 0 or url.find("\\") >= 0 or url.find("..") >= 0 or url.find("--") >= 0:
                        continue
                    #end if
                    url_tuple = urlparse.urlparse(url)
                    row_list = url_tuple[2].split('/')
                    for i in range(10):
                        if len(row_list) > 2:
                            row_list = row_list[0:-1]
                            self.addUrl2("%s://%s%s/" % (url_tuple[0],url_tuple[1],'/'.join(row_list)), refer)
                        else:
                            break
                        #end if
                    #end for
                    
                    self.addUrl2(url, refer)
                #end for
            #end if
            
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.urlfromwaf:%s, task_id:%s, domain_id:%s" % (str(e),self.task_id,self.domain_id))
        #end try
    #end def


    def init(self):
        try:
            '''
            if self.base_path == "" or self.base_path == "/":

                self.getBase()
                parse = urlparse.urlparse(self.base_url)
                if parse[1] != "":
                    self.domain = parse[1]
                #end if
                if self.base_path == "":
                    self.base_path = "/"
                #end if
                if self.mysqlConnect():
                    print ">>>>>>>>>>>>>>>>>>>>>>>>update domain_list ",self.domain,self.base_path,self.domain_id
                    sql = "update domain_list_%s set `domain` = '%s', `base_path` = '%s' where `id` = '%s'" % (self.task_id,self.domain,self.base_path,self.domain_id)
                    self.cursor.execute(sql)
                    self.conn.commit()
                #end if
            #end if
            '''
            self.getBase()
            self.getCode()
            self.indexForbidden()
            self.loadInitUrl()
            self.getRobots()
            self.getSitemap()
            self.urlfromwaf()

        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.init:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
        #end try
    #end def

    def checkTimeOut(self):
        if self.timeout_count > self.max_timeout_count:
            return False
        #end if
        if self.end_time < time.time():
            return False
        #end if

        return True
    #end def

    def start(self):
        try:
            i = 0
            while True:
                i += 1
                if self.temp_queue.empty():
                    print "Spider is end"
                    break
                #end if

                if self.rec.err_out():
                    break
                #end if

                #checkTimeOutCount
                if self.checkTimeOut() == False:
                    break
                #end if

                ###############################
                url = self.temp_queue.get(True,5)

                #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",i,url

                if url == None or url == '':
                    continue
                #end if
                if url == -1:
                    break
                #end if

                if self.num >= self.maxnum:
                    print "Spider is end"
                    break
                #end if

                url = url.strip()

                if self.ifScan(url) == False:
                    continue
                #end if

                urllist = self.getList(url)
                for row in urllist:
                    #self.addNewDomain(row)
                    self.checkOtherDomain(row)
                    self.checkPolicy(row)
                    self.addUrl(row,url)
                #end for
            #end while
            self.clearSwf()
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.start:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return -1
        #end try
    #end def

    def ifScan(self,url):
        try:
            parse = urlparse.urlparse(url)
            path = parse[2].lower()
            if self.nomatch_type_list and len(self.nomatch_type_list) > 0:
                for row in self.nomatch_type_list:
                    if path.find(row) > 0:
                        return False
                    #end if
                #end for
            #end if

            '''
            if path != '':
                #爬虫扫目录的时候存在遗漏的目录

                count1 = len(path.split('/'))
                count2 = len(self.base_path.split('/'))
                if path[-1] == '/' and path.find(self.base_path):
                    return False
                #end if

                if path.find(self.base_path) != 0:
                    #return False
                    print "path not find base_path"
                #end if
            #end if
            '''
            return True
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.ifScan:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return False
        #end try
    #end def

    def pathPattern(self,path):
        patten = ""
        #1:[alpha],2:[int]
        flag = 0
        for i in range(len(path)):
            num = ord(path[i])
            if (num >= 65 and num <= 90) or (num >= 97 and num <= 122):
                if flag == 0:
                    flag = 1
                elif flag == 1:
                    flag = 1
                elif flag == 2:
                    patten = "%s[int]" % (patten)
                    flag = 1
                #end if
            elif num >= 48 and num <= 57:
                if flag == 0:
                    flag = 2
                elif flag == 1:
                    patten = "%s[alpha]" % (patten)
                    flag = 2
                elif flag == 2:
                    flag = 2
                #end if
            else:
                if flag == 0:
                    patten = "%s%s" % (patten,path[i])
                elif flag == 1:
                    patten = "%s[alpha]%s" % (patten,path[i])
                    flag = 0
                elif flag == 2:
                    patten = "%s[int]%s" % (patten,path[i])
                    flag = 0
                #end if
            #end if
            if i == len(path) - 1 and flag != 0:
                if flag == 1:
                    patten = "%s[alpha]" % (patten)
                elif flag == 2:
                    patten = "%s[int]" % (patten)
                #end if
            #end if
        #end for
        if patten.find('.') > 0:
            patten = "%s.%s" % (patten.split('.')[0],path.split('.')[1])
        #end if
        return patten
        
    def checkHtmlPatten(self,url):
        try:
            parse = urlparse.urlparse(url)
            url = parse[2]
            if len(url.split('/')) <= len(self.base_path.split('/')):
                return True
            #end if
            patten = self.pathPattern(url)
            if patten in self.html_patten:
                if patten.find('.html') > 0 or patten.find('.htm') > 0 or patten.find('.xhtml') > 0 or patten.find('.shtml') > 0:
                    filename = patten.split('/')[-1].split('.')[0]
                    if filename.find('[alpha]') < 0 or filename.find('-[int]') > 0 or filename.find('_[int]') > 0:
                        return False
                    #end if
                elif patten[-1] == '/':
                    if patten.split('/')[-2].find('[alpha]') < 0:
                        return False
                    #end if
                #end if
            else:
                self.html_patten.append(patten)
            #end if   

            return True
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.checkHtmlPatten:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",url: " + url)
            return True
        #end try
    #end def

    def addNewDomain(self,url):
        try:
            if checkIpv4Inner(url) or checkIpv6Inner(url):
                return
            #end if
            parse = urlparse.urlparse(url)
            scheme = parse[0]
            domain = parse[1]

            if domain.find(':') > 0:
                port = domain.split(':')[1]
                if port == '80':
                    scheme = 'http'
                    domain = domain.split(':')[0]
                elif port == '443':
                    scheme = 'https'
                    domain = domain.split(':')[0]
                #end if
            #end if

            flag,scheme,domain,base_path = getRedirect("%s://%s/" % (scheme,domain))
            if flag == False:
                return
            #end if
            if scheme != 'http' and scheme != 'https':
                scheme = 'http'
            #end if
            if len(domain.split('.')) < 3:
                return
            #end if
            
            sql = ""
            if domain.find(':') > 0:
                if self.asset_scan_id > 0:
                    sql = "select count(*) as c from domain_list_%s where (`domain` = '%s' or `domain` = '%s:%s') and `scheme` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,domain,self.ip,domain.split(':')[1],scheme,self.asset_scan_id)
                else:
                    sql = "select count(*) as c from domain_list_%s where (`domain` = '%s' or `domain` = '%s:%s') and `scheme` = '%s'" % (self.task_id,domain,self.ip,domain.split(':')[1],scheme)
                #end if
            else:
                if self.asset_scan_id > 0:
                    sql = "select count(*) as c from domain_list_%s where (`domain` = '%s' or `domain` = '%s') and `scheme` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,domain,self.ip,scheme,self.asset_scan_id)
                else:
                    sql = "select count(*) as c from domain_list_%s where (`domain` = '%s' or `domain` = '%s') and `scheme` = '%s'" % (self.task_id,domain,self.ip,scheme)
                #end if
            #end if
            if self.mysqlConnect():
                self.cursor.execute(sql)
                self.conn.commit()
                res = self.cursor.fetchone()
                if res and len(res) > 0 and res['c'] <= 0:
                    sql = "insert into domain_list_"+self.task_id+"(task_id,task_name,domain,scheme,ip,state,spider_state,progress,title,base_path,policy,policy_detail,service_type,site_type,database_type,start_time,end_time,asset_scan_id) values (%s,'',%s,%s,%s,'0','0','','',%s,%s,'','','','','0000-00-00 00:00:00','0000-00-00 00:00:00',%s)"
                    self.cursor.execute(sql,(self.task_id,domain,scheme,self.ip,base_path,'1',self.asset_scan_id))
                    sql = "select LAST_INSERT_ID() as domain_id"
                    self.cursor.execute(sql)
                    self.conn.commit()
                    res = self.cursor.fetchone()
                    if res and len(res) > 0 and res['domain_id'] > 0:
                        self.domain_queue.put(str(res['domain_id']))
                #end if
            #end if

        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.addNewDomain:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",url: " + url)
        #end try
    #end def

    _filtercompile = re.compile(r"[(\"\'\\)]") #remove some special url
    def urlFilter(self,url):
        return self._filtercompile.search(url)
    #end def

    def parameterPattern(self,parameters):
        try:
            params_list = map(lambda s: s.split('=',1) if len(s.split('='))>1 else [s[:s.find('=')],''] if s.find('=') != -1  else [s,''],parameters.split('&'))
            params_list.sort()
            params = []
            needhandleNum = False
            for k,v in params_list:
                try:
                    int(v)
                    params.append("%s=%s" %(k,'[int]'))
                    needhandleNum = True
                except ValueError:
                    params.append("%s=%s" %(k,v))
            #end for  
            return needhandleNum,'&'.join(params)
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.parameterPattern:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",params: " + params)
        #end try
    #end def

    def patternExist(self,parse):
        try:
            pathExist = False
            paramsExist = False
            patterns = {'path':None,'params':None}
            path = parse[2]
            parameters = parse[4]

            parametersPattern = self.parameterPattern(parameters)
            if parametersPattern:
                needhandleNum,pattern = parametersPattern
                patterns['params'] = (path,needhandleNum,pattern)           
                paramsExist = self.pattern_dict.has_key(path) and self.pattern_dict[path].has_key(pattern)
            #end if   
            pathPattern = self.pathPattern(path)
            patterns['path'] = pathPattern
            if pathPattern in self.html_patten:
                if pathPattern.find('.html') > 0 or pathPattern.find('.htm') > 0 or pathPattern.find('.xhtml') > 0 or pathPattern.find('.shtml') > 0:
                    filename = pathPattern.split('/')[-1].split('.')[0]
                    if filename.find('[alpha]') < 0 or filename.find('-[int]') > 0 or filename.find('_[int]') > 0:
                        pathExist = True
                    #end if
                elif pathPattern[-1] == '/':
                    if pathPattern.split('/')[-2].find('[alpha]') < 0:
                        pathExist = True
                    #end if
                #end if
            #end if
            return pathExist or paramsExist,patterns
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.patternExist:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",parse" + str(parse))
            return True,''
        #end try
    #end def

    def updatePattern(self,patterns):
        try:
            if patterns['path']:
                patten = patterns['path']
                if patten not in self.html_patten:
                    self.html_patten.append(patten)
                #end if
            #end if

            if not patterns['params']:
                return
            path,needhandleNum,pattern = patterns['params']
            if needhandleNum:
                if self.pattern_dict.has_key(path):
                    if self.pattern_dict[path].has_key(pattern):
                        self.pattern_dict[path][pattern] += 1
                        if self.pattern_dict[path][pattern] > self.same_url_pattern_count:
                            return
                        else:
                            self.pattern_dict[path][pattern] = 1
                    else:
                        self.pattern_dict[path][pattern] = 1
                    #end if
                else:
                    self.pattern_dict[path] = {pattern:1}
                #end if
            #end if
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.updatePattern:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",patterns: " + str(patterns))
        #end try
    #end def


    def checkSpecialPatternExist(self,path,parameters):
        try:
            #1. index.cgi?c46
            if parameters.find('=') == -1:
                if not hasattr(self,"noequalPattern"):
                    self.noequalPattern = set()
                flag = 0
                pattern = []
                for s in parameters:
                    if s.isdigit():
                        if flag != 1: pattern.append('d')
                        flag = 1
                    elif s.isalpha():
                        if flag != 2: pattern.append('w')
                        flag = 2
                    else:
                        pattern.append(s)
                        flag = 3
                pattern = "%s#%s" % (path,''.join(pattern))
                key = hashlib.md5(pattern).hexdigest()
                if key not in self.noequalPattern:
                    self.noequalPattern.add(key)
                    return False
                else:
                    return True
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.updatePattern:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",patterns: " + str(patterns))
            return False
        #end try
    #end def

    def addUrl2(self,url,refer):
        
        if check_exclude_url(self.exclude_url,url):
            return False
        #end if
        
        if self.ifScan(url) == False:
            return False
        #end if

        if url in self.result:
            return False
        #end if

        parse = urlparse.urlparse(url)

        if  parse[0] != 'http' and parse[0] != 'https':
            return False

        #end if

        if parse[1].find(self.domain) < 0:
            return False
        #end if
        
        path = parse[2]
        if path.find(".\\") >= 0 or path.find("\\.") >= 0 or path.find("/./") == 0 or path.find("\\") >= 0 or parse[4].find("'") >= 0 or parse[4].find("..") >= 0 or parse[4].find("--") >= 0:
            return False
        #end if
        path = path.replace("/////","/").replace("////","/").replace("///","/").replace("//","/")
        if len(path) == 1 and path == "/":
            path = ""
        elif len(path) > 1 and path[0] == "/":
            path = path[1:]
        #end if
        if url.find("?") >= 0:
            url = "%s://%s/%s?%s" % (parse[0],parse[1],path,parse[4])
        else:
            url = "%s://%s/%s" % (parse[0],parse[1],path)
        #url = urlparse.urlunparse(urlparse.urlunparse((parse[0],parse[1],path,parse[3],parse[4],parse[5])))
        parse = urlparse.urlparse(url)

        if parse[1] != self.domain:
#-------START by yinkun  2014-10-15-------------   
            if checkIpv6Inner(parse[1]) and checkIpv6Inner(self.domain):
                a = parse[1].find(']')
                b = self.domain.find(']')
                if parse[1][:a+1] == self.domain[:b+1]:
                    self.addNewDomain(url)
                return False
            
            if parse[1].lower().split(':')[0] == self.domain.split(':')[0]:
                self.addNewDomain(url)
            return False
#-------END----------------------------------------         
        #end if

        isJs = refer.find(".js") != -1 #just handle js file
        if isJs and self.urlFilter(url):
            return False
        #end if
        
        flag, patterns = self.patternExist(parse)
        if flag:
            return False
        #end if
        res = valid_urls(parse[1],[url],[200,403])
        if res and len(res) > 0:
            self.updatePattern(patterns)
        else:
            return False
        #end if
        
        self.num += 1
        if url.find('%25') or url.find('%20'):
            url = urllib2.unquote(url)
        #end if
        self.result.append(url)
        self.temp_queue.put(url)
                
        if self.policy == 3 and self.current_dir!= '': # only scan current assign dir
            #if len([d for d in self.current_dir if parse[2].startswith(d)]) < 1:
            if not parse[2].startswith(self.current_dir):
                return False
            #end if
        #end if
                        
        temp = self.changeCode(url)
        if temp.find('?') > 0:
            self.write_url_log(temp.split('?')[0], 'get', temp.split('?')[1], refer)
        else:
            self.write_url_log(temp, 'get', '', refer)
        #end if

        return True
    #end def

    def addUrl(self,url,refer):
        
        if check_exclude_url(self.exclude_url,url):
            return False
        #end if
        
        if self.ifScan(url) == False:
            return False
        #end if

        if url in self.result:
            return False
        #end if

        parse = urlparse.urlparse(url)

        if  parse[0] != 'http' and parse[0] != 'https':
            return False

        #end if

        '''
        if parse[1].find(self.domain) < 0 or parse[2].find(self.base_path) != 0:
            return False
        #end if
        '''
        if parse[1].find(self.domain) < 0:
            return False
        #end if

        '''
        if parse[1] != self.domain or parse[2].find(self.base_path) != 0:
            if parse[1].split(':')[0] == self.domain.split(':')[0]:
                self.addNewDomain(url)
            #end if
            return False
        #end if
        '''
        if parse[1] != self.domain:
#-------START by yinkun  2014-10-15-------------   
            if checkIpv6Inner(parse[1]) and checkIpv6Inner(self.domain):
                a = parse[1].find(']')
                b = self.domain.find(']')
                if parse[1][:a+1] == self.domain[:b+1]:
                    self.addNewDomain(url)
                return False
            if parse[1].lower().split(':')[0] == self.domain.split(':')[0]:
                self.addNewDomain(url)

            return False
#-------END----------------------------------------
        #end if

        isJs = refer.find(".js") != -1 #just handle js file
        if isJs and self.urlFilter(url):
            return False

        if self.checkHtmlPatten(url) == False:
            return False
        #end if

        flag = True
        path = parse[2]
        parameters = parse[4]

        if self.checkSpecialPatternExist(path,parameters):
            return False

        if self.pattern_dict.has_key(path):
            if parameters == '':
                return False
            else:
                result = self.parameterPattern(parameters)
                if result:
                    needhandleNum,pattern = result
                    if needhandleNum:
                        if self.pattern_dict[path].has_key(pattern):
                            self.pattern_dict[path][pattern] += 1
                            if self.pattern_dict[path][pattern] > self.same_url_pattern_count:
                                flag = False
                            #end if
                        else:
                            self.pattern_dict[path][pattern] = 1
                        #end if
                    #end if
                #end if

                """
                temp = parameters.split('&')
                for row in temp:
                    if row.find('=') >= 0:
                        if self.pattern_dict[path].has_key(row.split('=')[0]):
                            self.pattern_dict[path][row.split('=')[0]]+=1
                            if self.pattern_dict[path][row.split('=')[0]] > self.same_url_pattern_count:
                                flag = False
                        else:
                            if row.split('=')[0] != '':
                                self.pattern_dict[path][row.split('=')[0]] = 1
                            else:
                                self.pattern_dict[path][self.name_not_found] = 1
                    else:
                        if row != '':
                            if self.pattern_dict[path].has_key(row):
                                flag = False
                        else:
                            if self.pattern_dict[path].has_key(self.name_not_found):
                                flag = False

                        #end if
                    #end if
                #end for
                """
            #end if
        else:
            self.pattern_dict[path] = {}
            if parameters != '':
                result = self.parameterPattern(parameters)
                if result:
                    needhandleNum,pattern = result
                    if needhandleNum:
                        self.pattern_dict[path][pattern] = 1
                    #end if
                #end if

                """
                temp = parameters.split('&')
                for row in temp:
                    if row.find('=') >= 0:
                        if row.split('=')[0] != '':
                            self.pattern_dict[path][row.split('=')[0]] = 1
                        else:
                            self.pattern_dict[path][self.name_not_found] = 1
                        #end if
                    else:
                        if row != '':
                            self.pattern_dict[path][row] = 1
                        else:
                            self.pattern_dict[path][self.name_not_found] = 1

                    #end if
                #end for
                """
            #end if


        #end if
        if flag:
            self.num += 1
            if url.find('%25') or url.find('%20'):
                url = urllib2.unquote(url)
            #end if
            self.result.append(url)
            self.temp_queue.put(url)
                
            if self.policy == 3 and self.current_dir!= '': # only scan current assign dir
                #if len([d for d in self.current_dir if parse[2].startswith(d)]) < 1:
                if not parse[2].startswith(self.current_dir):
                    return False
                #end if
            #end if
                        
            temp = self.changeCode(url)
            if temp.find('?') > 0:
                self.write_url_log(temp.split('?')[0], 'get', temp.split('?')[1], refer)
            else:
                self.write_url_log(temp, 'get', '', refer)
            #end if

            return True
        else:
            return False
        #end if
    #end def


    def requestUrl(self,url):
        try:
            res = {}
            content = ""
            isquoted = False 
            try:
                tmp_url = urllib2.unquote(url)
                parse = urlparse.urlparse(tmp_url)
                #fix bug 2399
                if  parse[0] != 'http' and parse[0] != 'https':
                    return {'status':'404','content-location':tmp_url},""

                if tmp_url.find('%') < 0:
                    tmp_url = urllib2.quote(tmp_url,'%:/?=#&;,')
                    isquoted = True
                tmp_url = urllib2.unquote(tmp_url)    
                #res, content = self.http.request(tmp_url)
                res, content = nvs_httplib2_request(self.http,tmp_url)
            except socket.timeout,e1:
                res['status'] = '404'
                res['content-location'] = tmp_url
            #end try

            if res.has_key('content-location'):
                if res['content-location'] != tmp_url:
                    unquoteLocation=res['content-location']
                    if isquoted:
                        unquoteLocation = urllib2.unquote(res['content-location'])
                    self.addUrl(unquoteLocation, tmp_url)
                    #url = unquoteLocation 
                    res={'status':'302','content-location':unquoteLocation}
                    content=""

            if self.hasSpace:
                try:
                    lines = []
                    for k in res:
                        lines.append(k+':'+res[k] + "\n")
                    #end for
                    lines.append(self.sep+"\n")
                    lines.append(content) 

                    filename = hashlib.sha1(tmp_url).hexdigest()
                    filename = "%s#%s#" % (filename,self.domain_id)
                    f = file(self.downloadDir + filename,'w+')
                    f.writelines(lines)
                    f.close()
                except IOError:
                    self.hasSpace = False
            #end if
            return res,content  # res['content-location'] may quoted
        except socket.timeout,e:
            self.timeout_count = self.timeout_count + 1
            logging.getLogger().debug("File:Spider.py, Spider.requestUrl Exception(url):" + str(e) + " ,url:" + url)
            return {'status':'404','content-location':url},self.timeout_content
        except Exception,e:
            content = str(e)
            logging.getLogger().error("File:Spider.py, Spider.requestUrl Exception(content):" + content + " ,url:" + url)
            return {'status':'404','content-location':url},""
        #end try
    #end def

    '''
    def testUrl(self,url,force=False):
        try:
            if force == False:
                list = ['.rar','.zip','.doc','.txt','.docx']
                for row in list:
                    if url.lower().find(row) >= 0:
                        return True
                    #end if
                #end for
            #end if
            res, content = self.requestUrl(url)
            self.http.follow_redirects = True
            for row in self.error_rule_list:
                if row['status'] == res['status']:
                    keyword_utf8 = row['keyword'].encode('utf8')
                    keyword_gb2312 = row['keyword'].encode('gb2312')
                    keyword_gbk = row['keyword'].encode('gbk')
                    if content.find(keyword_utf8) > 0 or content.find(keyword_gb2312) or content.find(keyword_gbk):
                        return False
                    #end if
                #end if
            #end for
            return True
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.testUrl:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return False
        #end try
    #end def
    '''

    '''
    def getUrlContent(self,url):
        try:
            self.http.follow_redirects = True
            res, content = self.requestUrl(url)
            return content
        except Exception,e:
            return ""
        #end try
    #end def
    '''

    def ifUrlRight(self,url):
        try:

            if url == '#' or url.lower().find('javascript:') >= 0 or url.find('{#') >= 0:
                return False
            else:
                return True
            #end if

            '''
            if url == '#' or url.lower().find('javascript:') >= 0:
                return False
            else:
                return True
            #end if
            '''
        except Exception,e:
            return False
        #end try
    #end if

    def changeUrl(self,source_url,url):
        try:
            if self.ifUrlRight(url) == False:
                return source_url
            #end if
            source_url = source_url.strip()
            source_url_tuple = urlparse.urlparse(source_url)
            source_url_domain = source_url_tuple[1]
            source_url_dir = source_url_tuple[2]
            if source_url_dir == '' or source_url_dir[0] != '/':
                source_url_dir = '/'
            #end if

            url = url.strip()
            url_tuple = urlparse.urlparse(url)
            if url_tuple[0] == '':
                path = ""
                if url_tuple[2] != '':
                    temp_list = source_url_dir.split('/')[0:-1]
                    temp = url_tuple[2]
                    if temp[0:3] == '../':
                        if len(temp_list) > 1:
                            temp_list = temp_list[0:-1]
                        #end if
                        temp = temp[3:]
                        for i in range(10):
                            if temp[0:3] == '../':
                                if len(temp_list) > 1:
                                    temp_list = temp_list[0:-1]
                                #end if
                                temp = temp[3:]
                            else:
                                break
                            #end if
                        #end for
                        temp_list.append(temp)
                    elif temp[0:2] == './':
                        temp_list.append(temp[2:])
                    elif temp[0] == '/':
                        temp_list = ['']
                        temp_list.append(temp[1:])
                    elif temp[0] == '?':
                        file = source_url_dir[-1]
                        if file.find('?') >= 0:
                            temp_list.append("%s%s" % (file.split('?')[0],url))
                        else:
                            temp_list.append("%s%s" % (file,url))
                        #end if
                    else:
                        temp_list.append(temp)
                    #end if
                    path = '/'.join(temp_list)
                else:
                    path = source_url_dir

                #end if
                #fix BUG #2417 
                if path.find('/../') > 0:
                    for x in xrange(10):
                        p = path.split('/../',1)
                        path = '/'.join(p[0].split('/')[:-1])+'/'+p[1]
                        if path.find('../') < 0:
                            break
                if path.find('./'):
                    path = path.replace('./','')

                #at this point, path may contain '..' or '.' at the end ,eg, /kk/.. ,/kk/.
                path = path[:-2] if path[-2:]==".." else path

                path = path[:-1] if path[-1:]=="." else path  # not path[-1],if path='',will throw "index of range"
                
                path = path.replace("//",'/')

                temp_tuple = (self.scheme,source_url_domain,path,url_tuple[3],url_tuple[4],url_tuple[5])
                url = urlparse.urlunparse(temp_tuple)

            #end if
            return url
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.changeUrl:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return url
        #end try
    #end def

    def specialDir(self,url):
        try:
            parse = urlparse.urlparse(url)

            if parse[2].find('thumb') > 0:
                return False
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.specialDir:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return True


    def specialAction(self,url):
        try:
            parse = urlparse.urlparse(url)

            if parse[4] == "N=D" or parse[4] == "M=A" or parse[4] == "S=A" or parse[4] == "D=A" or re.search(r"C=[MNSD];O=[AD]",parse[4],re.I):
                return False
            else:
                return True
            #end if
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.specialAction:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return True
        #end try
    #end def

    def getUrlFromJs(self,url,content):
        try:

            list = []
            if content.find('url') >= 0:
                match = re.findall(r"[^_]url(\s*)=(\s*)(\"|')(.+?)\3",content,re.I)
                for row in match:
                    list.append({'url':row[3],'url_content':''})
                    #list.append(row[3])
                #end for
            #end if

            if content.find('.href') >= 0:
                match = re.findall(r"\.href(\s*)=(\s*)(\"|')(.+?)\3",content,re.I)
                for row in match:
                    list.append({'url':row[3],'url_content':''})
                    #list.append(row[3])
                #end for
            #end if

            if content.find('window.open') >= 0:
                match = re.findall(r"window\.open(\s*)\((\s*)('|\")(.+?)\3(,?)",content,re.I)
                for row in match:
                    list.append({'url':row[3],'url_content':''})
                    #list.append(row[3])
                #end for
            #end if

            if content.find('window.navigate') >= 0:
                match = re.findall(r"window\.navigate(\s*)\((\s*)('|\")(.+?)\3",content,re.I)
                for row in match:
                    list.append({'url':row[3],'url_content':''})
                    #list.append(row[3])
                #end for
            #end if

            if content.find('.location') >= 0:
                match = re.findall(r"\.location(\s*)=(\s*)('|\")(.+?)\3",content,re.I)
                for row in match:
                    list.append({'url':row[3],'url_content':''})
                    #list.append(row[3])
                #end for
            #end if

            if content.find('location.replace') >=0 or content.find('location.assign') >=0:
                match = re.findall(r"location\.(replace|assign)(\s*)\((\s*)('|\")(.+?)\4",content,re.I)
                for row in match:
                    list.append({'url':row[4],'url_content':''})
                    #list.append(row[3])
                #end for
            #end if

            return list
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getUrlFromJs:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return []
        #end try
    #end def

    def getUrlByFullPath(self,url,content):
        try:
            list = []
            match = re.findall(r"('|\")(http|https)://(.+?)\1",content,re.I)
            for row in match:
                list.append({'url':"%s://%s" % (row[1],row[2]),'url_content':''})
                #list.append("%s://%s" % (row[1],row[2]))
            #end for
            return list
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getUrlByFullPath:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return []
    #end def

    def getATag(self,url,content):
        try:
            list = []
            if content != '' and (content.find('href') > 0 or content.find('HREF') > 0):
                #match = re.findall(r"(\s+)href=(.+?)('/|\"/|>| )",content,re.I)
                #match = re.findall(r"(\s+)href(\s*)=(\s*)('|\")(.+?)\4(.*?)>(.*?)<",content,re.I|re.DOTALL)
                match = re.findall(r"(\s+)href(\s*)=(\s*)('|\")(.*?)\4(.*?)>(.*?)<",content,re.I|re.DOTALL) # in case ,<a href='' id='slide_link'>
                
                if len(match) > 0:
                    for row in match:
                        if row[4] != '':
                            t = {'url':row[4],'url_content':row[6]}
                            #list.append(row[1])
                            list.append(t)
                        #end if
                    #end for
                #end if
                match = re.findall(r"(\s+)href(\s*)=(\s*)([\d\w#].*?)(/>|>| )",content,re.I|re.DOTALL)
                if len(match) > 0:
                    for row in match:
                        t = {'url':row[3],'url_content':''}
                        list.append(t)
                    #end for
                #end if
                return list
            else:
                return []
            #end if
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getATag:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return []
        #end try
    #end def

    def getIframeSrc(self,url,content):
        try:
            list = []
            '''
            if content != '' and content.find('iframe') >= 0 and content.find('src') >= 0:
                match = re.findall(r"src(\s*)=(\s*)('|\")(.+?)\3",content,re.I)
                for row in match:
                    list.append(row[3])
                #end for
            #end if
            '''
            if content != '' and (content.find('src') >= 0 or content.find('SRC') >= 0):
                #match = re.findall(r"src(\s*)=(\s*)('|\")(.+?)\3",content,re.I)
                match = re.findall(r"src(\s*)=(\s*)('|\")(.*?)\3",content,re.I)  # in case, <img src='' name='slide' border=0
                for row in match:
                    if row[3] != '':
                        list.append({'url':row[3],'url_content':''})
                        #list.append(row[3])
                #end for
                match = re.findall(r"src(\s*)=(\s*)([\d\w#].*?)(/>|>| )",content,re.I)
                if len(match) > 0:
                    for row in match:
                        t = {'url':row[2],'url_content':''}
                        list.append(t)
                    #end for
                #end if

            #end if
            return list
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getIframeSrc:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return []
        #end try
    #end def


    def getSwf(self,url,content):
        #<embed src="subscribe.swf"
        try:
            urls = []
            if content != '' and content.find('.swf') >= 0:
                temp = []
                match = re.findall(r"embed(\s*)src(\s*)=(\s*)('|\")(.+?)\.swf\4",content,re.I)
                for row in match:
                    temp.append(self.changeUrl(url,row[4]+'.swf'))
                #end for
                _action = None
                _code = None
                for swf_url in temp:
                    if swf_url not in self.swfs:
                        self.swfs.append(swf_url)
                        filename = hashlib.sha1(swf_url).hexdigest()
                        filename = "%s#%s#" % (filename,self.domain_id)
                        path = "/tmp/%s/%s" % (self.task_id,filename)
                        vulscan_popen(" wget -O %s %s " % (path,swf_url))
                        if os.path.exists(path):
                            isbig = os.stat(path).st_size > 512*1024
                            swf_content = ''.join(vulscan_popen("swfdump -a %s" % path))
                            #   (   16 bytes) action: GetUrl URL:"subscribe.aspx" Label:""  -> http://www.testfire.net/subscribe.swf
                            if _action is None:
                                _action = re.compile(r"URL(\s*):(\s*)('|\")(.+?)\3",re.I)
                            match = _action.findall(swf_content)
                            for row in match:
                                urls.append({'url':row[3],'url_content':''})
                            #end for
                            if isbig:
                               continue
                            swf_file = open(path)
                            swf_content = swf_file.read()
                            swf_file.close()
                            #x00/redir.php?r=http://www.eclectasy.com/Fractal-Explorer/index.html\x00 -> http://testphp.vulnweb.com/Flash/add.swf
                            if _code is None:
                                _code = re.compile(r"(.+)\x00((.+?)\.(php|asp|aspx|jsp|html|htm)(.*?))\x00",re.I)
                            for line in swf_content.splitlines():
                                match = _code.search(line)
                                if match:
                                    urls.append({'url':match.group(2),'url_content':''})
                                #end if
                            #end for
                        #end if
                    #end if
                #end for
            return urls
            #end if
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getSwf:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return urls
        #end try
    #end def

    def clearSwf(self):
        try:
            vulscan_popen("rm -rf /tmp/%s/" % self.task_id)
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.clearSwf:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
        #end try
    #end def


    '''
    def getATag(self,url,content):
        try:
            list = []
            if content != '':
                match = re.findall(r"(\s+)href=(.+?)('/|\"/|>| )",content,re.I)
                for row in match:
                    try:
                        row = self.html_parser.unescape(row[1])
                        row = row.strip()
                        if row == "" or row[0] == '#':
                            continue
                        #end if
                        if row.find('#') > 0:
                            row = row.split('#')[0]
                        #end if
                        if row[0] == "'":
                            row = row.split("'")[1]
                        elif row[0] == "\"":
                            row = row.split("\"")[1]
                        #end if
                        if row == '':
                            continue
                        #end if
                        if row.find("'") >= 0 or row.find("\"") >= 0 or row.find("{") >= 0 or row.find("}") >= 0:
                            continue
                        #end if
                        temp = self.changeUrl(url, row)
                        if self.specialAction(temp) == False:
                            continue
                        #end if

                        url_tuple = urlparse.urlparse(temp)
                        temp_list = url_tuple[2].split('/')
                        for i in range(10):
                            if len(temp_list) > 2:
                                temp_list = temp_list[0:-1]
                                t = "%s://%s%s/" % (url_tuple[0],url_tuple[1],'/'.join(temp_list))
                                #logging.getLogger().error(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"+t)
                                list.append(t)
                            else:
                                break
                            #end if
                        #end for
                        list.append(temp)

                        #print temp
                    except Exception,e1:
                        logging.getLogger().error("File:Spider.py, Spider.getATag:" + str(e1) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
                    #end try
                #end for
                return list
            else:
                return []
            #end if
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getATag:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return []
        #end try
    #end def


    def getIframeSrc(self,url,content):
        try:
            list = []
            if content != '':
                match = re.findall(r"<(\s*)iframe(.+?)src(\s*)=(\s*)\"(.+?)\"",content,re.I)
                for row in match:
                    temp = self.changeUrl(url, row[-1])
                    if temp != '':
                        list.append(temp)
                    #end if
                #end for
            #end if
            return list
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getIframeSrc:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return []
        #end try
    #end def
    '''

    def dirEndswithSlash(self,url):
        try:
            if not url.endswith('/'):
                url=urllib2.quote(url,'%:/?=#&;,')
                #res,content = self.http.request(url)
                res,content = nvs_httplib2_request(self.http,url)
                if res.has_key('content-location') and res['content-location'].endswith('/'):
                    if res['content-location'][:-1] == url:
                        url = res['content-location']
                return urllib2.unquote(url)
            else:
                return url
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.dirEndswithSlash:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return url

    def checkPostPattern(self,url,fields):
        try:
            params = [':'.join((p['name'],p['type'])) for p in fields]
            params.sort()
            pattern = '%s#%s' % (url,'&'.join(params))
            key = hashlib.md5(pattern).hexdigest()
            if key not in self.postPattern:
                self.postPattern.add(key)
                return False
            return True
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.checkPostPattern:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return False

    def getForm(self,url,content):
        try:
            url = self.html_parser.unescape(url)
            isJs = url.find(".js") != -1
            match = re.findall(r"<(\s*)form(.+?)>(.+?)<(\s*)/(\s*)form(\s*)>",content,re.I|re.DOTALL)
            for row in match:
                method = ''
                action = None
                fields = []

                if row[1].lower().find("action") >= 0:
                    temp = re.findall(r"action(\s*)=(\s*)('|\")(.*?)(\3)",row[1],re.I)  # not *+? ,may loss action=""
                    if len(temp) > 0:
                        action = temp[0][3].replace(' ','')
                    else:
                        temp = re.findall(r"action(\s*)=(\s*)(.+?)(\s|$)",row[1],re.I)
                        if len(temp) >0:
                            action = temp[0][2]
                    #end if
                else:
                    action = url

                if action == None:
                    continue

                if isJs:
                    m = re.search(r"(['\"])(.*?)(\1)",action.decode('string_escape'))   #action: '\\"\\"'
                    if m: action = m.group(2)

                if action == '':
                    action = url
                #end if

                temp = re.findall(r"method(\s*)=(\s*)('|\")(.*?)(\3)",row[1],re.I)  # the same as above
                if len(temp) > 0:
                    method = temp[0][3].lower().replace(' ','')
                else:
                    temp = re.findall(r"method(\s*)=(\s*)(.+?)(\s|$)",row[1],re.I)
                    if len(temp) >0:
                        method = temp[0][2].lower()
                #end if
                if method == '':
                    method = 'get'
                #end if



                input_match = re.findall(r"<(\s*)input(.+?)>",row[2],re.I|re.DOTALL)
                if len(input_match) > 0:
                    for input_row in input_match:
                        type = ''
                        name = ''
                        value = ''
                        temp = re.findall(r"type(\s*)=(\s*)('|\")(.+?)(\3)",input_row[1],re.I)
                        if len(temp) > 0:
                            type = temp[0][3].lower().replace(' ','')
                        else:
                            temp = re.findall(r"type(\s*)=(\s*)(.+?)(\s|/|$)",input_row[1],re.I)
                            if len(temp) >0:
                                type = temp[0][2].lower()
                            #end if
                        #end if
                        if type == '':
                            type = 'text'
                        #end if

                        temp = re.findall(r"name(\s*)=(\s*)('|\")(.+?)(\3)",input_row[1],re.I)
                        if len(temp) > 0:
                            name = temp[0][3].replace(' ','')
                        else:
                            temp = re.findall(r"name(\s*)=(\s*)(.+?)(\s|/|$)",input_row[1],re.I)
                            if len(temp) >0:
                                name = temp[0][2]
                            #end if
                        #end if

                        temp = re.findall(r"value(\s*)=(\s*)('|\")(.*?)(\3)",input_row[1],re.I)
                        if len(temp) > 0:
                            value = temp[0][3].replace(' ','')
                        else:
                            temp = re.findall(r"value(\s*)=(\s*)(.+?)(\s|/|$)",input_row[1],re.I)
                            if len(temp) >0:
                                value = temp[0][2]
                            #end if
                        #end if

                        if type in ['reset','button']:
                            continue
                        #end if
                        if name == '':
                            continue
                        #end if
                        fields.append({'type':type,'name':name,'value':value})
                    #end for
                #end if

                select_match = re.findall("<(\s*)select(.+?)>(.+?)<(\s*)/(\s*)select(\s*)>",row[2],re.I|re.DOTALL)
                if len(select_match) > 0:
                    for select_row in select_match:
                        name = ''
                        value = ''
                        temp = re.findall(r"name(\s*)=(\s*)('|\")(.+?)(\3)",select_row[1],re.I)
                        if len(temp) > 0:
                            name = temp[0][3].replace(' ','')
                        #end if
                        temp = re.findall(r"<(\s*)option(.+?)value(\s*)=(\s*)('|\")(.*?)(\5)(.*?)>(.+?)<(\s*)/(\s*)option(\s*)>",select_row[2],re.I)
                        if len(temp) > 0:
                            for temp_row in temp:
                                if temp_row[1].find('selected') >= 0 or temp_row[7].find('selected') >= 0:
                                    value = temp_row[5].replace(' ','')
                                    break
                                #end if
                            #end for
                            if value == '':
                                value = temp[0][5].replace(' ','')
                            #end if
                        else:
                            temp = re.findall(r"<(\s*)option(.+?)>(.+?)<(\s*)/(\s*)option(\s*)>",select_row[2],re.I)
                            if len(temp) > 0:
                                for temp_row in temp:
                                    if temp_row[1].find('selected') >= 0:
                                        value = temp_row[2].strip()
                                        break
                                    #end if
                                #end for
                                if value == '':
                                    value = temp[0][2].strip()
                                #end if
                            #end if
                        #end if
                        if name == '':
                            continue
                        #end if
                        fields.append({'type':'select','name':name,'value':value})
                    #end for
                #end if

                area_match = re.findall("<(\s*)textarea(.+?)>(.*?)<(\s*)/(\s*)textarea(\s*)>",row[2],re.I|re.DOTALL)
                if len(area_match) > 0:
                    for area_row in area_match:
                        name = ''
                        value = ''
                        temp = re.findall(r"name(\s*)=(\s*)('|\")(.+?)(\3)",area_row[1],re.I)
                        if len(temp) > 0:
                            name = temp[0][3].replace(' ','')
                        else:
                            temp = re.findall(r"name(\s*)=(\s*)(.+?)(\s|$)",area_row[1],re.I)
                            if len(temp) > 0:
                                name = temp[0][2]
                        #end if
                        value = area_row[2].strip()
                        if name == '':
                            continue
                        #end if
                        fields.append({'type':'textarea','name':name,'value':value})
                #end if

                #url=self.dirEndswithSlash(url)
                fullpath = self.changeUrl(url, action)
                if fullpath == "" or fullpath[0] == '#' or len(fullpath.split("?")) > 2 or fullpath.find('>') >= 0 or fullpath.find('<') >= 0 or fullpath.find('{') >= 0 or fullpath.find('}') >= 0 or fullpath.find('\\') >= 0 or fullpath.find('+') >= 0 or fullpath.find('|') >= 0 or fullpath.find(',') >=0 :
                    continue
                #end if
                parse = urlparse.urlparse(fullpath)
                if  parse[0] != 'http' and parse[0] != 'https':
                    continue
                #end if
                if parse[1].find(self.domain) < 0 or parse[2].find(self.base_path) != 0:
                    continue
                #end if
               
                if method != 'post':
                    paramslist = []
                    for f in fields:
                        paramslist.append(f['name']+'='+f['value'])
                    params = '&'.join(paramslist)

                    self.addUrl(fullpath+'?'+params,url)
                else:
                    patternExist = self.checkPostPattern(parse,fields)
                    if not patternExist:
                        params = self.changeCode(json.write(fields))
                        if check_exclude_url(self.exclude_url,url):
                            continue
                        #end if
                        self.write_url_log(fullpath, 'post', params, url)
                #end if
            #end for
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getForm:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id + ",url:" + url)
        #end try
    #end def

    def getList(self,url):
        try:
            for row in self.nomatch_type_list:
                if url.lower().find(row) > 0:
                    return []
                #end if
            #end for
            for row in self.uncontent_type_list:
                if url.lower().find(row) > 0:
                    return []
                #end if
            #end for
            if url.find("www.phpmyadmin.net") > 0 and url.find("token") > 0:
                return []
            #end if

            if self.specialDir(url) == False:
                return []

            list = []
            temp = []

            #url=self.dirEndswithSlash(url)
            res, content = self.requestUrl(url)
            if not url.endswith('/'):
                url=urllib2.quote(url,'%:/?=#&;,')
                if res.has_key('content-location') and res['content-location'].endswith('/'):
                    if res['content-location'][:-1] == url:
                        url = res['content-location']
                url = urllib2.unquote(url)

            if content != "":
                temp.extend(self.getUrlByFullPath(url, content))
                temp.extend(self.getUrlFromJs(url, content))
                temp.extend(self.getATag(url, content))
                temp.extend(self.getIframeSrc(url, content))
                temp.extend(self.getSwf(url,content))
                self.getForm(url, content)
            #end if

            for row in temp:
                if self.checklogout(row['url'], row['url_content']):
                    continue
                #end if
                row = row['url']
                if row.find('#') > 0:
                    row = row.split('#')[0]
                #end if
                row = self.html_parser.unescape(row).strip()
                if row == "" or row[0] == '#' or len(row.split("?")) > 2 or row.find('>') >= 0 or row.find('<') >= 0 or row.find('{') >= 0 or row.find('}') >= 0 or row.find('\\') >= 0 or row.find('+') >= 0 or row.find('|') >= 0 or row.find(',') >=0 :
                    continue
                #end if
                if row == "":
                    continue
                #end if
                row = self.changeUrl(url, row)
                if self.specialAction(row) == False:
                    continue
                #end if
                url_tuple = urlparse.urlparse(row)
                row_list = url_tuple[2].split('/')
                for i in range(10):
                    if len(row_list) > 2:
                        row_list = row_list[0:-1]
                        t = "%s://%s%s/" % (url_tuple[0],url_tuple[1],'/'.join(row_list))
                        if check_exclude_url(self.exclude_url,t):
                            continue
                        #end if
                        if t in list:
                            continue
                        #end if

                        list.append(t)
                    else:
                        break
                    #end if
                #end for
                if check_exclude_url(self.exclude_url,row):
                    continue
                #end if
                if row in list:
                    continue
                #end if
                
                list.append(row)
            #end for
            return list
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getList:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return []
        #end try
    #end def

    '''
    def getList(self,url):
        try:
            for row in self.nomatch_type_list:
                if url.lower().find(row) > 0:
                    return []
                #end if
            #end for

            list = []
            res, content = self.requestUrl(url)
            #print res,content
            if content != "":
                list.extend(self.getATag(url, content))
                list.extend(self.getIframeSrc(url, content))
                self.getForm(url, content)
            #end if

            return list
        except Exception,e:
            logging.getLogger().error("File:Spider.py, Spider.getList:" + str(e) + ",task id:" + self.task_id + ",domain id:" + self.domain_id)
            return []
        #end try
    #end try
    '''
#end class

def main(argv):
    try:
        dict = {}
        dict['domain_queue'] = argv['domain_queue']
        dict['task_id'] = str(argv['task_id'])
        dict['domain_id'] = str(argv['domain_id'])
        dict['domain'] = argv['domain']
        dict['scheme'] = argv['scheme']
        dict['ip'] = argv['ip']
        dict['title'] = argv['title']
        dict['maxnum'] = argv['web_url_count']
        dict['web_timeout'] = argv['web_timeout']
        dict['max_timeout_count'] = argv['max_timeout_count']
        dict['end_time'] = argv['end_time']
        dict['policy'] = argv['policy']
        dict['base_path'] = argv['base_path']
        dict['policy_detail'] = argv['policy_detail']
        dict['cookie_url'] = argv['cookie_url']
        dict['cookie'] = argv['cookie']
        dict['begin_path'] = argv['begin_path']
        dict['result'] = []
        dict['form_result'] = []
        dict['temp_queue'] = Queue()
        dict['pattern_dict'] = {}
        dict['html_patten'] = []
        #dict['downloadDir'] = "/var/webs/task_id%sdomain_id%s/" % (argv['task_id'],argv['domain_id'])
        dict['downloadDir'] = "/var/webs/task%s/" % (argv['task_id'])
        dict['nomatch_type_list'] = ['.mp3','.pdf','.png','.jpg','.gif','.rm','.asf','.exe','.mov','.ttf','.rmvb','.rtf','.ra','.mp4','.wma','.wmv','.xps','.doc','.docx','.txt','.zip','.rar','.mht','.msi','.flv','.xls','.nrg','.cd','.ppt','.ld2','.ocx','.url','.avi','.swf','.db','.bmp','.psd','.chm','.iso','.ape','.cue','.u32','.ucd','.dll','.ico','.pk','.lrc','.m4v','.cnn','.m3u','.tif','.mpeg','.srt','.chs','.cab','.xsl','.pps','.doc','.tar','.tgz','.bz','.gz','.mpg','.jpeg','.bmp']
        dict['uncontent_type_list'] = ['.mdb','.sql']
        dict['error_rule_list'] = [{'status':'404','keyword':u'<title>找不到该网页<title>'}]
        dict['rec'] = argv['rec']
        dict['same_url_pattern_count'] = 5
        dict['asset_scan_id'] = argv['asset_scan_id']
        dict['web_getdomain_enable'] = argv['web_getdomain_enable']
        dict['web_getdomain_timeout'] = argv['web_getdomain_timeout']
        dict['exclude_url'] = argv['exclude_url']
        scaner = Spider(dict)
        scaner.start()

    except Exception,e:
        logging.getLogger().error("File:Spider.py, main:" + str(e) + ",task id:" + str(argv['task_id']) + ",domain id:" + str(argv['domain_id']),",domain:" + argv['domain'])
    #end try
#end def



