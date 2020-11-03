#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import httplib2
import urlparse
import HTMLParser
import socket
import threading
import logging
import re
from lib.common import *
from plugins.lib.common import request_exception_counter
from plugins.lib.ex_httplib2 import *

class GetDomainThread(threading.Thread):
    def __init__(self, task_id, domain_queue):
        try:
            threading.Thread.__init__(self)
            self.conn = ""
            self.cursor = ""
            self.task_id = str(task_id)
            self.task_name = ''
            self.target = ''
            self.domain_queue = domain_queue
            self.web_timeout = 3
            self.web_getdomain_timeout = 120
            self.web_getdomain_policy = 1
            self.web_getdomain_enable = 1
            self.web_getdomain_state = 0
            self.user_id = '2'
            self.domain_ports = '80,81,8080'
            
            self.http = ""
            
            self.html_parser = HTMLParser.HTMLParser()
            
            self.ip_list = []
            
            self.asset_scan_id = 0

        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.__init__:" + str(e) + ",task id:" + str(task_id))
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
                    logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.mysqlConnect reconnect:" + str(e) + ",task id:" + str(self.task_id))
            #end if
            return True
        except Exception,e:
            self.conn = ''
            self.cursor = ''
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.mysqlConnect:" + str(e) + ",task id:" + str(self.task_id))
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
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.mysqlClose:" + str(e) + ",task id:" + str(self.task_id))
            return False
        #end try
    #end def
    
    def init(self):
        try:
            if self.mysqlConnect():
                sql = "select `task_name`,`asset_scan_id`,`web_target`,`web_timeout`,`web_getdomain_timeout`,`web_getdomain_policy`,`web_getdomain_state`,`web_getdomain_enable`,`user_id` from `task_manage`  where `id` = '%s'" % (self.task_id)
                self.cursor.execute(sql)
                self.conn.commit()
                res = self.cursor.fetchone()
                if res and len(res) > 0:
                    self.task_name = res['task_name']
                    self.target = res['web_target']
                    self.web_timeout = res['web_timeout']
                    self.web_getdomain_timeout = res['web_getdomain_timeout']
                    self.web_getdomain_policy = res['web_getdomain_policy']
                    self.web_getdomain_enable = res['web_getdomain_enable']
                    self.web_getdomain_state = res['web_getdomain_state']
                    self.user_id = str(res['user_id'])
                    self.http = httplib2.Http(timeout=self.web_getdomain_timeout)
                    self.http.follow_redirects = True
                    
                    self.asset_scan_id = res['asset_scan_id']
                    
                    
                    port_list = ['80','443']
                    sql = "select `Value` from `user_config` where `Name` = 'domain_ports' and `user_id` = '%s'" % (self.user_id)
                    self.cursor.execute(sql)
                    self.conn.commit()
                    res = self.cursor.fetchone()
                    if res and len(res) > 0:
                        #temp = res['Value'].split('|')
                        #port_list.extend(temp)
                        self.domain_ports = res['Value'].replace('|',',')
                    #end if
                    '''
                    f = file("/var/www/dic/tomcatweakpwd_port_%s.dic" % (self.user_id), "r+")
                    lines = f.readlines()
                    f.close()
                    for row in lines:
                        temp = row.replace("\r","").replace("\n","").replace(" ","").split('|')
                        port_list.extend(temp)
                    #end for
                    self.domain_ports = self.combinePorts(port_list)
                    '''
                    
                    return True
                else:
                    logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.init  : get config error ,task id:" + str(self.task_id))
                    return False
                #end if
            else:
                logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.init  : mysql connect error ,task id:" + str(self.task_id))
                return False
            #end if
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.init:" + str(e) + ",task id:" + str(self.task_id))
        #end try
    #end def
    
    def combinePorts(self,port_list):
        try:
            temp = []
            for port in port_list:
                if port == "":
                    continue
                #end if
                if port.find('-') > 0:
                    port_start = int(port.split('-')[0])
                    port_end = int(port.split('-')[1])
                    if port_start > 65535 or port_start < 1:
                        continue
                    #end if
                    if port_end > 65535 or port_end < 1:
                        continue
                    #end if
                    if port_start > port_end:
                        t = port_end
                        port_end = port_start
                        port_start = t
                    #end if
                    for i in range(port_start,port_end+1):
                        if i in temp:
                            continue
                        else:
                            temp.append(i)
                        #end if
                    #end for
                else:
                    port = int(port)
                    if port > 65535 or port < 1:
                        continue
                    #end if
                    if port in temp:
                        temp.append(port)
                    #end if
                #end if
            #end for
            
            for i in range(0,len(temp)-1):
                for j in range(i+1,len(temp)):
                    if temp[i] > temp[j]:
                        t = temp[j]
                        temp[j] = temp[i]
                        temp[i] = t
                    #end if
                #end for
            #end for
            
            list = []
            t = []
            for i in range(temp):
                if len(t) > 0:
                    t.append(str(i))
                else:
                    if i == int(t[len(t)-1])+1:
                        t.append(str(i))
                    else:
                        if len(t) > 1:
                            list.append("%s-%s" % (t[0],t[len(t)-1]))
                        else:
                            list.append(t[0])
                        #end if
                        t = [str(i)]
                    #end if
                #end if
            #end for
            if len(t) > 1:
                list.append("%s-%s" % (t[0],t[len(t)-1]))
            elif len(t) == 1:
                list.append(t[0])
            #end if
            
            return ','.join(list)
            
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.combinePorts:" + str(e) + ",task id:" + str(self.task_id))
            return ''
        #end try
    #end def
    
    def endGetDomain(self):
        try:
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            
            sql = "update `task_manage` set `web_getdomain_state` = '1' where `id` = '%s'" % (self.task_id)
            cursor.execute(sql)
            conn.commit()
            
            cursor.close()
            conn.close()
            
            '''
            if self.mysqlConnect():
                
                sql = "update `task_manage` set `web_getdomain_state` = '1' where `id` = '%s'" % (self.task_id)
                self.cursor.execute(sql)
                self.conn.commit()
            else:
                logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.endGetDomain: mysql connect error ,task id:" + str(self.task_id))
            #end if
            '''
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.endGetDomain:" + str(e) + ",task id:" + str(self.task_id))
        #end try
    #end def
    
    def insertDomain(self,ob):
        try:
            domain_id = 0
            scheme = "http"
            cookie_url = ""
            begin_path = ""

            if ob.has_key("scheme"):
                scheme = ob["scheme"]
            #end if
            if ob.has_key("cookie_url"):
                cookie_url = ob["cookie_url"]
            #end if
            if ob['ip'] == "":
                return
            #end if
            if ob.has_key("begin_path"):
                begin_path = ob["begin_path"]
            #end if
            exclude_url = ""
            if ob.has_key("exclude_url"):
                exclude_url = ob["exclude_url"]
            #end if
#-------START 2014-10-15  yinkun -------------------------
            domain = ''
            if checkIpv6(ob['domain']):
                domain = easyIpv6(ob['domain'].lower())
                domain = '[' + domain + ']'
            else:
                domain = ob['domain']
#-------END------------------------------------------------

            base_path = ob['base_path']    
            
            flag,scheme,domain,base_path = getRedirect("%s://%s%s" % (scheme,domain,base_path))
            
            #if flag == False:
                #return
            #end if
            
            if scheme != 'http' and scheme != 'https':
                scheme = 'http'
            #end if

#-------START 2014-10-15 yinkun  修改下一行，防止过滤掉ipv6地址
            if domain == "" or (domain.find(".") <= 0 and domain.find(":") <= 0):
                return
            #end if
            
            if self.mysqlConnect():
                sql = ""
                if self.asset_scan_id > 0:
                    sql = "select count(*) as c from domain_list_%s where `domain` = '%s' and `scheme` = '%s' and `ip` = '%s' and `base_path` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,domain,scheme,ob['ip'],base_path,self.asset_scan_id)
                else:
                    sql = "select count(*) as c from domain_list_%s where `domain` = '%s' and `scheme` = '%s' and `ip` = '%s' and `base_path` = '%s'" % (self.task_id,domain,scheme,ob['ip'],base_path)
                #end if
                self.cursor.execute(sql)
                self.conn.commit()
                res = self.cursor.fetchone()
                if res and len(res) > 0 and res['c'] > 0:
                    return
                else:
                    #Fix BUG #2092
                    if not base_path:
                        base_path = '/'
                    #end if
                    sql = "insert into domain_list_" + self.task_id + " (`task_id`,`task_name`,`scheme`,`domain`,`ip`,`state`,`spider_state`,`progress`,`title`,`base_path`,`policy`,`policy_detail`,`service_type`,`site_type`,`database_type`,`start_time`,`end_time`,`cookie_url`,`begin_path`,`asset_scan_id`, `exclude_url`) values (%s,%s,%s,%s,%s,'0','0','',%s,%s,%s,%s,'','','',%s,%s,%s,%s,%s,%s) "
                    start_time = '1970-01-02 00:00:00'
                    end_time = '1970-01-02 00:00:00'
                    self.cursor.execute(sql,(self.task_id,self.task_name,scheme,domain.lower(),ob['ip'].lower(),ob['title'],base_path,ob['policy'],ob['policy_detail'],start_time,end_time,cookie_url,begin_path,self.asset_scan_id,exclude_url))
                    self.conn.commit()
                    sql = "select LAST_INSERT_ID() as domain_id"
                    self.cursor.execute(sql)
                    self.conn.commit()
                    res = self.cursor.fetchone()
                    if res and len(res) > 0 and res['domain_id'] > 0:
                        domain_id = res['domain_id']
                        self.domain_queue.put(str(domain_id))
                        
                        sql = ""
                        if self.asset_scan_id > 0:
                            sql = "select count(*) as c from hostmsg_%s where `ip` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,ob['ip'],self.asset_scan_id)
                        else:
                            sql = "select count(*) as c from hostmsg_%s where ip = '%s'" % (self.task_id,ob['ip'])
                        #end if
                        self.cursor.execute(sql)
                        self.conn.commit()
                        res = self.cursor.fetchone()
                        if res and len(res) > 0 and res['c'] == 0:
                            current_time = time.strftime("%Y-%m-%d %X",time.localtime())
                            sql = "insert into hostmsg_%s (`task_id`,`task_name`,`ip`,`state`,`port_state`,`host_state`,`web_state`,`weak_state`,`start_time`,`asset_scan_id`) values ('%s','','%s','1','0','0','0','0','%s','%s')" % (self.task_id,self.task_id,ob['ip'],current_time,self.asset_scan_id)
                            self.cursor.execute(sql)
                            self.conn.commit()
                            sql = "update `task_manage` set `host_state` = '0',`weak_state` = '0',`port_state` = '0' where `id` = '%s'" % (self.task_id)
                            self.cursor.execute(sql)
                            self.conn.commit()
                        #end if
                        
                        logging.getLogger().debug("File:GetDomainThread.py, GetDomainThread.insertDomain:insert into domain_list success,task id:" + self.task_id + ",ip:" + ob['ip'] + ",domain:" + ob['domain'])
                    #end if
                #end if
            else:
                logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.insertDomain:mysql connect error,task id:" + self.task_id + ",ip:" + ob['ip'] + ",domain:" + ob['domain'])
            #end if
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.insertDomain:" + str(e) + ",task id:" + self.task_id + ",ip:" + ob['ip'] + ",domain:" + ob['domain'])
        #end try
    #end def
    
    def getDomainPolicy_1(self,ip):
        try:
            flag = False
            url = "http://cn.bing.com/search?q=ip%3A"+ip+"&qs=n&form=QBRE&pq=ip%3A"+ip+"&sc=0-0&sp=-1&sk="
            res, content = self.http.request(url)
            match = re.findall(r"<h3><a href=\"(.+?)\" target=\"_blank\" h=\"(.+?)\">(.+?)</a></h3>",content,re.I)
            if match and len(match) > 0:
                for row in match:
                    temp = urlparse.urlparse(row[0])
                    domain = temp[1]
                    title = row[2]
                    
                    self.insertDomain(domain, ip, title, '')
                    flag = True
                #end for
            #end if
            match = re.findall(r"<div class=\"sb_pag\"><h4>分页</h4><ul>(.+?)</ul></div>",content,re.I)
            if match and len(match) > 0:
                content = match[0]
                if content.find('下一页') > 0:
                    temp = content.split('<li>')
                    if len(temp) > 1:
                        content = temp[-1]
                        for temp_row in temp:
                            match = re.findall(r"<a href=\"(.+?)\" h=\"(.+?)\">([0-9]+)</a>",temp_row,re.I)
                            if match and len(match) > 0:
                                url = "http://cn.bing.com%s" % (match[0][0])
                                url = self.html_parser.unescape(url)
                                res, content = self.http.request(insertDomain)
                                match = re.findall(r"<h3><a href=\"(.+?)\" target=\"_blank\" h=\"(.+?)\">(.+?)</a></h3>",content,re.I)
                                if match and len(match) > 0:
                                    for row in match:
                                        temp = urlparse.urlparse(row[0])
                                        domain = temp[1]
                                        title = row[2]
                                        ob = {'domain':domain,'scheme':'http','ip':ip,'title':title,'base_path':'/','policy':'1','policy_detail':'','cookie_url':'','exclude_url':''}
                                        self.insertDomain(ob)
                                        flag = True
                                    #end for
                                #end if
                            #end if
                        #end for
                    #end if
                #end if
            #end if
            if flag == False:
                ob = {'domain':ip,'scheme':'http','ip':ip,'title':'','base_path':'/','policy':'1','policy_detail':'','cookie_url':'','exclude_url':''}
                self.insertDomain(ob)
            #end if
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.getDomainPolicy_1:" + str(e) + ",task id:" + str(self.task_id) + ",ip:" + ip)
        #end try
    #end def
    
    def getDomainPolicy_2(self,ip):
        try:
            if checkIpv6(ip):
                return False
            #end if
            domain_id = 0
            url = "http://query.yxlink.com/dns.py?action=cha&ip=%s" % (ip)
            res, content = self.http.request(url)
            lines = content.split("<br>")
            count_i = 0
            for line in lines:
                if len(line.split("#")) == 2:
                    ob = {'domain':line.split("#") [0],'scheme':'http','ip':ip,'title':line.split("#") [1],'base_path':'/','policy':'5','policy_detail':'','cookie_url':'','exclude_url':''}
                    self.insertDomain(ob)
                    count_i += 1
                #end if
            #end for
            if count_i <= 0:
                return False
                #ob = {'domain':ip,'scheme':'http','ip':ip,'title':'','base_path':'/','policy':'1','policy_detail':'','exclude_url':''}
                #self.insertDomain(ob)
            else:
                return True
            #end if
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.getDomainPolicy_2:" + str(e) + ",task id:" + str(self.task_id) + ",ip:" + ip)
            return False
        #end try
    #end def
    
    def updateWebState(self,ip):
        try:
            if self.mysqlConnect():
                sql = ""
                if self.asset_scan_id > 0:
                    sql = "update hostmsg_%s set `web_state` = '1' where `ip` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,ip,self.asset_scan_id)
                else:
                    sql = "update hostmsg_%s set `web_state` = '1' where `ip` = '%s'" % (self.task_id,ip)
                #end if
                self.cursor.execute(sql)
                self.conn.commit()
            #end if
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.updateWebState:" + str(e) + ",task id:" + self.task_id + ",ip:" + ip)
        #end try
    #end def
    
    def updateHostmsg(self,ip):
        try:
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            
            sql = ""
            if self.asset_scan_id > 0:
                sql = "select `state` from hostmsg_%s where `ip` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,ip,self.asset_scan_id)
            else:
                sql = "select `state` from hostmsg_%s where `ip` = '%s'" % (self.task_id,ip)
            #end if
            cursor.execute(sql)
            conn.commit()
            res = cursor.fetchone()
            if res and res['state'] == 1:
                cursor.close()
                conn.close()
            else:
                sql = ""
                if self.asset_scan_id > 0:
                    sql = "update hostmsg_%s set `state` = '1' , `port_state` = '0' , `host_state` = '0' , `web_state` = '0' , `weak_state` = '0' where `ip` = '%s' and `asset_scan_id` = '%s'" % (self.task_id,ip,self.asset_scan_id)
                else:
                    sql = "update hostmsg_%s set `state` = '1' , `port_state` = '0' , `host_state` = '0' , `web_state` = '0' , `weak_state` = '0' where `ip` = '%s'" % (self.task_id,ip)
                #end if
                cursor.execute(sql)
                conn.commit()
                sql = "update `task_manage` set `host_state` = '0' , `web_state` = '0' , `weak_state` = '0' , `port_state` = '0' where `id` = '%s'" % (self.task_id)
                cursor.execute(sql)
                conn.commit()
                cursor.close()
                conn.close()
            #end if 
            
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.updateHostmsg:" + str(e) + ",task id:" + self.task_id + ",ip:" + ip)
        #end try
    #end def
    
    def getDomainByPort(self,ip):
        web_service = False
        default_port = False

        ipv6_flag = False
        if checkIpv6(ip):
            ipv6_flag = True
        #end if
        
        try:
            iface = getIfaceByRoute(ip)
            #http = httplib2.Http(timeout=5,disable_ssl_certificate_validation=True)
            rec = request_exception_counter(100)
            rec.domain = ip
            http = ex_httplib2(rec)
            http.httlib2_set_follow_redirects(False)
            http.httlib2_set_timout(30)
            
            '''
            if iface == "":
                cmd = "/usr/bin/nmap -sS %s -p %s --host-timeout %ss -P0" % (ip,self.domain_ports,self.web_getdomain_timeout)
            else:
                cmd = "/usr/bin/nmap -sS %s -p %s --host-timeout %ss -P0 -e %s" % (ip,self.domain_ports,self.web_getdomain_timeout,iface)  
            #end if
            '''
            cmd_type = ""
            if ipv6_flag:
                cmd_type = " -6"
            #end if
            port_timeout = 60
            if not ipv6_flag:
                if iface == "":
                    cmd = "/usr/bin/nmap -sS %s -p %s --host-timeout %ss -P0" % (self.domain_ports,port_timeout)
                else:
                    cmd = "/usr/bin/nmap -sS %s -p %s --host-timeout %ss -P0 -e %s" % (ip,self.domain_ports,port_timeout,iface)  
                #end if
            
            else:
                if iface == "":
                    cmd = "/usr/bin/nmap -6  %s -p %s --host-timeout %ss -P0" % (ip,self.domain_ports,port_timeout)
                else:
                    cmd = "/usr/bin/nmap -6  %s -p %s --host-timeout %ss -P0 -e %s" % (ip,self.domain_ports,port_timeout,iface)


            lines = vulscan_popen(cmd)
            for line in lines:
                if line.find('open') > 0 and line.find('/tcp') > 0 and line.find('http') > 0:
                    port = line.split('/')[0]
                    if port == '80':
                        web_service = True
                        default_port = True
                        continue
                    elif port == '443':
                        web_service = True
                        try:
                            '''
                            url = "https://%s/" % (ip)
                            res, content = http.request(url)
                            if res and res.has_key('status') and res['status'] == '200' and content and content.find('body') > 0 and content.find('html') > 0:
                                domain = ip
                                ob = {'domain':domain,'scheme':'https','ip':ip,'title':'','base_path':'/','policy':'1','policy_detail':'','cookie_url':''}
                                self.insertDomain(ob)
                            #end if
                            '''
                            domain = ip
                            if ipv6_flag:
                                domain = "[%s]" % (ip)
                            #end if

                            ob = {'domain':domain,'scheme':'https','ip':ip,'title':'','base_path':'/','policy':'5','policy_detail':'','cookie_url':'','exclude_url':''}
                            self.insertDomain(ob)
                        except Exception,e:
                            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.getDomainByPort:not support https service : " + str(e))
                        #end if
                    else:
                        try:
                            '''
                            url = "http://%s:%s/" % (ip,port)
                            res, content = http.request(url)
                            if res and res.has_key('status') and res['status'] == '200' and content and content.find('body') > 0 and content.find('html') > 0:
                                web_service = True
                                domain = "%s:%s" % (ip,port)
                                ob = {'domain':domain,'scheme':'http','ip':ip,'title':'','base_path':'/','policy':'1','policy_detail':'','cookie_url':''}
                                self.insertDomain(ob)
                            #end if
                            '''
                            web_service = True
                            domain = "%s:%s" % (ip,port)
                            if ipv6_flag:
                                domain = "[%s]:%s" % (ip,port)
                            #end if
                            ob = {'domain':domain,'scheme':'http','ip':ip,'title':'','base_path':'/','policy':'5','policy_detail':'','cookie_url':'','exclude_url':''}
                            self.insertDomain(ob)
                        except Exception,e:
                            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.getDomainByPort:not support http service : " + str(e))
                        #end try
                    #end if
                #end if
            #end for
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.getDomainByPort:" + str(e) + ",task id:" + self.task_id + ",ip:" + ip)
        #end try
        
        return web_service,default_port
    #end def
    
    def getDomainMain(self,ip):
        try:
            web_service,default_port = self.getDomainByPort(ip)
            
            if web_service:
                
                self.updateHostmsg(ip)
                
                #判断是否为内网地址
                tmp = ip.split(".")
                if len(tmp) == 4:
                    if int(tmp[0]) == 10 or (int(tmp[0]) == 172 and int(tmp[1]) >= 16 and int(tmp[1]) <= 31) or (int(tmp[0]) == 192 and int(tmp[1]) == 168) and default_port:
                        ob = {'domain':ip,'scheme':'http','ip':ip,'title':'','base_path':'/','policy':'1','policy_detail':'','cookie_url':'','exclude_url':''}
                        self.insertDomain(ob)
                        return
                    #end if
                #end if
                
                #域名反查
                if self.web_getdomain_enable == 1:
                    #开启域名反查
                    success = False
                    '''
                    if self.web_getdomain_policy == 1:
                        success = self.getDomainPolicy_1(ip)
                    elif self.web_getdomain_policy == 2:
                        success = self.getDomainPolicy_2(ip)
                    #end if
                    '''
                    success = self.getDomainPolicy_2(ip)
                    if success:
                        return
                    #end if
                #end if
                
                #不开启域名反查或者域名反查为空
                if default_port:
                    domain = ip
                    if checkIpv6(ip):
                        domain = "[%s]" % (ip)
                    #end if
                    ob = {'domain':domain,'scheme':'http','ip':ip,'title':'','base_path':'/','policy':'5','policy_detail':'','cookie_url':'','exclude_url':''}
                    self.insertDomain(ob)
                #end if
            else:
                self.updateWebState(ip)
            #end if
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.getDomainMain:" + str(e) + ",task id:" + str(self.task_id) + ",ip:" + ip + ",web_getdomain_policy:" + str(self.web_getdomain_policy))
        #end try
    #end def
    
    def ifIpAlive(self,ip):
        try:
            try:
                sk = ''
                if checkIpv6(ip):
                    sk = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                else:
                    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #end if
                sk.settimeout(self.web_timeout)
                sk.connect((ip,80))
                sk.close()
                return True
            except Exception,e1:
                sk.close()
                logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.ifIpAlive:" + str(e1) + ",task id:" + self.task_id + ",ip:"+ip)
                return False
            #end try
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.ifIpAlive:" + str(e) + ",task id:" + self.task_id + ",ip:"+ip)
            return False
        #end try
    #end def
    
    '''
    def ip2int (self,ip):
        try:
            return struct.unpack("!I",socket.inet_aton(ip))[0]
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.ip2int:" + str(e) + ",task id:" + str(self.task_id) + ",ip:"+str(ip))
            return ''  
        #end try
    #end def
    
    def int2ip (self,i):
        try:
            return socket.inet_ntoa(struct.pack("!I",i))
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.int2ip:" + str(e) + ",task id:" + str(self.task_id) + ",i:"+str(i))
            return '' 
        #end try
    #end def
    
    def get_ip_by_host(self,domain):
        try:
            ip = socket.gethostbyname(domain)
            return ip
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.get_ip_by_host:" + str(e) + ",task id:" + str(self.task_id) + ", domain:" + str(domain))
            return ''
        #end try
    #end def
    '''
    
        
    def run(self):
        try:
            logging.getLogger().debug("File:GetDomainThread.py, GetDomainThread.run: function start ,task id:" + self.task_id)
            
            #获取上一次未扫描完成的域名
            initOk = self.init()
            if initOk and self.mysqlConnect():
                sql = ""
                if self.asset_scan_id > 0:
                    sql = "select `id` from domain_list_%s where `state` <> '1' and asset_scan_id = '%s'" % (self.task_id,str(self.asset_scan_id))
                else:
                    sql = "select `id` from domain_list_%s where `state` <> '1'" % (self.task_id)
                #end if
                self.cursor.execute(sql)
                self.conn.commit()
                res = self.cursor.fetchall()
                if res and len(res) > 0:
                    for row in res:
                        self.domain_queue.put(str(row['id']))
                    #end for
                #end if
            else:
                logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.run: mysql connect close ,task id:" + self.task_id)
            #end if
            
            #判断域名获取是否成功，如果未成功的话，继续获取域名，将不存在库里的域名插入数据库
            if initOk and self.web_getdomain_state == 0:
                #如果获取域名未完成
                #判断域名
                target_list = self.target.split(",")
                for row in target_list:
                    try:
                        #check simple ipv4 or simple ipv6
                        ipv4_enable = checkIpv4(row)
                        ipv6_enable = checkIpv6(row)
                        if ipv4_enable or ipv6_enable:
                            ip_full = row
                            if ipv6_enable:
                                ip_full = fullIpv6(row)
                                row = easyIpv6(ip_full)
                            #end if
                            if ip_full in self.ip_list:
                                continue
                            else:
                                self.ip_list.append(ip_full)
                                self.getDomainMain(row)
                            #end if
                            continue
                        #end if

                        #check ipv4 range or ipv6 range
                        ipv4_range_enable = checkIpv4Range(row)
                        ipv6_range_enable = checkIpv6Range(row)
                        if ipv4_range_enable or ipv6_range_enable:
                            temp = row.split("-")
                            temp_list = []
                            if ipv6_range_enable:
                                if checkIpv6(temp[1]):
                                    temp_list = getIpv6Range(temp[0].lower(), temp[1].lower())
                                else:
                                    last_colon_index = 0
                                    url_end = ''
                                    for i in range(len(temp[0])):
                                        if temp[0][i] == ':':
                                            last_colon_index = i
                                    url_end = temp[0][:last_colon_index+1] + temp[1]
                                    temp_list = getIpv6Range(temp[0].lower(), url_end.lower())
                            else:
                                temp_list = getIpv4Range(temp[0],temp[1])
                            #end if
                            for temp_item in temp_list:
                                ip_full = temp_item
                                if checkIpv6(temp_item):
                                    ip_full = fullIpv6(temp_item)
                                    temp_item = easyIpv6(ip_full)
                                #end if
                                if ip_full in self.ip_list:
                                    continue
                                else:
                                    self.ip_list.append(ip_full)
                                    self.getDomainMain(temp_item)
                                #end if
                            #end for
                            continue
                        #end if

                        ob = None
                        if row.find("#") >= 0:
                            temp = row.split("#")
                            ob = {}
                            if len(temp) > 3:
                                ob['scheme'] = temp[3]
                            else:
                                ob['scheme'] = 'http'
                            #end if
                            parse = urlparse.urlparse("%s://%s" %(ob['scheme'],temp[0]))
                            ob['domain'] = parse[1].lower()
                            if checkIpv6(ob['domain']):
                                ob['domain'] = easyIpv6(ob['domain'])
                                ob['domain'] = "[%s]" % (ob['domain'])
                            #end if
                            ob['begin_path'] = '' if parse[2] == '/' or parse[2] == '' else parse.geturl()                            
#---------------yinkun-----------------------------------
                            if len(temp)>5 and temp[4] != '':      #配置了真实IP                      
                                ob['ip'] = temp[4]
                            else:
                                tmp_ip = domainToip(ob['domain'])
                                if tmp_ip == False:
                                    continue
                                else:
                                    ob['ip'] = tmp_ip
                                #end if
                            #end if
#---------------end--------------------------------------------                            
                            if len(temp) > 5:
                                ob['exclude_url'] = temp[5]
                            else:
                                ob['exclude_url'] = ''
                            #end if
                            ob['title'] = ''
                            ob['base_path'] = ''
                            ob['policy'] = temp[1]
                            ob['policy_detail'] = ''
                            ob['cookie_url'] = ''
                            if ob['policy'] == '3':
                                policy_detail = temp[2].split('|')
                                for r in policy_detail:
                                    ob['base_path'] = r
                                    self.insertDomain(ob)
                                #end for
                            elif ob['policy'] == '6':
                                ob['policy_detail'] = temp[2].split('|')[0]
                                ob['cookie_url'] = temp[2].split('|')[1]
                                
                                t = urlparse.urlparse(ob['policy_detail'])
                                t_tuple = (ob['scheme'],t[1],t[2],t[3],t[4],t[5])
                                ob['policy_detail'] = urlparse.urlunparse(t_tuple)
                                
                                self.insertDomain(ob)
                            else:
                                ob['policy_detail'] = temp[2]
                                self.insertDomain(ob)
                            #end if
                        else:
                            ob = {}
                            ob['domain'] = row
                            ob['scheme'] = 'http'
#---------------yinkun-----------------------------------                            
                            tmp_ip = domainToip(ob['domain'])
                            if tmp_ip == False:
                                continue
                            else:
                                ob['ip'] = tmp_ip
#---------------end--------------------------------------------                               
                            ob['title'] = ''
                            ob['base_path'] = '/'
                            ob['policy'] = '1'
                            ob['policy_detail'] = ''
                            ob['cookie_url'] = ''
                            ob['begin_path'] = ''
                            ob['exclude_url'] = ''
                            self.insertDomain(ob)
                        #end if

                        #域名反查
                        if self.web_getdomain_enable and ob and ob.has_key('ip') and checkIpv4(ob['ip']) and ob['ip'] not in self.ip_list and ob.has_key('domain'):
                            self.ip_list.append(ob['ip'])
                            getDomainPolicy(self,self.http,ob['ip'],ob['domain'],ob['policy'])
                        #end if

                    except Exception,e:
                        logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.startDomainScan:" + str(e) + ",task id:" + self.task_id)
                    #end if
                #end for
            #end if
            #self.domain_queue.put('null')
            self.endGetDomain()
        except Exception,e:
            logging.getLogger().error("File:GetDomainThread.py, GetDomainThread.startDomainScan:" + str(e) + ",task id:" + self.task_id)
            #self.domain_queue.put('null')
            self.endGetDomain()
        #end try
    #end def
#end class
