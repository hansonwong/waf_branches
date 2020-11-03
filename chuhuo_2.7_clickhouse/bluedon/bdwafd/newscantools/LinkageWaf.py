#!/usr/bin/python
#-*-encoding:UTF-8-*-
import MySQLdb
import logging
import sys
import os
import json
from urllib import urlencode
from httplib import HTTPSConnection,CannotSendRequest,ImproperConnectionState

from lib.common import *

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)

def DEBUG(msg):
    logging.getLogger().info('File:LinkageWaf.py, %s' % (msg))
#end def

def WARN(msg):
    logging.getLogger().warn('File:LinkageWaf.py, %s' % (msg))
#end def

def ERROR(msg):
    logging.getLogger().error('File:LinkageWaf.py, %s' % (msg))
#end def

class LinkageWaf:
    def __init__(self,task_id,domain_id):
        try:
            self.task_id = str(task_id)
            self.domain_id = str(domain_id)
            self.enable = 0
            self.ip = None
            self.port = 443
            self.user = None
            self.pwd = None
            self.scheme = None
            self.domain = None
            #self.connection = None
            self.headers = {"Content-type":"application/x-www-form-urlencoded","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0'}
            
        except Exception,e:
            ERROR("LinkageWaf.__init__:%s, task_id:%s" % (str(e),str(task_id)))
        #end try
    #end def
    
    def init(self):
        try:
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            sql = "select Name, Value from config where Name in ('linkage_waf_enable','linkage_waf_ip','linkage_waf_user','linkage_waf_pwd')"
            cursor.execute(sql)
            res = cursor.fetchall()
            for row in res:
                if row['Name'] == 'linkage_waf_enable':
                    self.enable = str(row['Value'])
                elif row['Name'] == 'linkage_waf_ip':
                    self.ip = str(row['Value'])
                elif row['Name'] == 'linkage_waf_user':
                    self.user = str(row['Value'])
                elif row['Name'] == 'linkage_waf_pwd':
                    self.pwd = str(row['Value'])
                #end if
            #end for
            
            domain_list_table = "domain_list_%s" % (self.task_id)
            if table_exists(domain_list_table):
                sql = "select scheme, domain from %s where id = '%s'" % (domain_list_table,self.domain_id)
                cursor.execute(sql)
                res = cursor.fetchone()
                if res:
                    self.scheme = res['scheme']
                    self.domain = res['domain']
                #end if
            #end if
            filepath = sys_path("/www/yx.config.inc.php")
            f = file(filepath, "r+")
            lines = f.readlines()
            f.close()
            for row in lines:
                if row.find("feature_set") >= 0:
                    match = re.findall(r"feature_set = '([0-1,]+)'",row,re.I)
                    if match and len(match) > 0:
                        m = match[0].replace(",","")
                        if m[6] == '0':
                            self.enable = '0'
                        #end if
                    #end if
                    break
                #end if
            #end for
            
            return True
        except Exception,e:
            ERROR("LinkageWaf.init:%s, task_id:%s" % (str(e),str(self.task_id)))
            return False
        #end try
    #end def
    
    def _request(self, method, target, params):
        try:
            connection = None
            try:
                connection = HTTPSConnection(self.ip, self.port)
                connection.request(method, target, params, self.headers)
            except CannotSendRequest,ImproperConnectionState:
                connection = HTTPSConnection(self.ip, self.port)
                connection.request(method, target, params, self.headers)
            #end try
            
            res = connection.getresponse()
            header = res.getheaders()
            response = []
            while True:
                try:
                    tmp = res.read(1024*64)
                    if not tmp:
                        break
                    else:
                        response.append(tmp)
                except Exception, e1:
                    break
                #end if
            #end while
            response = ''.join(response)
            response = self.parse(response)
            
            try:
                connection.close()
            except Exception,e2:
                pass
            #end try
            
            return header,response
        except Exception,e:
            ERROR("LinkageWaf._request:%s, task_id:%s" % (str(e),self.task_id))
            return {},False
        #end try
    #end def
    
    def parse(self,response):
        try:
            res = None
            try:
                res = json.read(response)
            except Exception,e1:
                return {'success':False}
            #end try
            return res
        except Exception,e:
            ERROR("LinkageWaf.parse:%s, task_id:%s" % (str(e),self.task_id))
            return {'success':False}
        #end try
    #end def
    
    def login(self):
        try:
            params = urlencode({'module':'login','waf_username':self.user,'waf_password':self.pwd})
            header, response = self._request("POST", "/html/common/login/checklogin", params)
            
            session = None
            if response and response.has_key('success') and response['success'] and header and len(header) > 0:
                content = ""
                for i in range(len(header)):
                    n,v = header[i]
                    if n.find('set-cookie') >= 0:
                        content = v
                    #end if
                #end for
                
                match = re.findall(r"nvssession=([0-9a-z]+);",content,re.I)
                if match and len(match) > 0:
                    session = match[0]
                #end if  
            #end if
            
            if session == None:
                return False
            else:
                cookie = "wafsession=%s; loginName=webadmin; type=2; enhance=1; wtf=1; rpi_https=1; rpi_loadbalance=1; ddos_feature=1; tamper_db=1; connsetting=1; advprotect=1; timemgr=1; anticc=1; aclaccess=1; vlan=1; hasetting=1; scanleak=1; urlpattern=1; snmp=1; snmptrap=1; syslog=1; icp=1; antihotlink=1; antiscanning=1; protectedip=0; vulscanlog=1; csrfprotect=1; webshell=1; upgradeconfig=1" % (session)
                #cookie = "enhance=; apiconfig=0; firewallsetting=0; upgradesetting=0; max_port_thread_global=10; max_host_thread_global=20; max_web_thread_global=10; max_weak_thread_global=20; ip_range=*.*.*.*; ip_range_user=*.*.*.*; nvssession=%s; loginName=webadmin; type=2" % (session)
                self.headers['Cookie'] = cookie
                return True
            #end if
            
        except Exception,e:
            ERROR("LinkageWaf.login:%s, task_id:%s, ip:%s, user:%s, pwd:%s" % (str(e),self.task_id,self.ip,self.user,self.pwd))
            return False
        #end try
    #end if
    
    def requestUrls(self):
        try:
            url = "/html/getpages"
            params = urlencode({'waf_username':self.user,'waf_password':self.pwd,'scheme':self.scheme,'domain':self.domain})
            header, response = self._request("POST", url, params)
            
            return response
            
        except Exception,e:
            ERROR("LinkageWaf.requestUrls:%s, task_id:%s" % (str(e),self.task_id,self.ip,self.user,self.pwd))
            return None
        #end try
    #end def
    
    
    def main(self):
        try:
            if self.init() == False:
                return False
            #end if
            
            if self.enable == '0':
                return []
            #end if
            
            '''
            if self.login() == False:
                return False
            #end if
            '''
            
            response = self.requestUrls()
            if response is None:
                return False
            #end if
            
            urllist = []
            
            if response and response.has_key('result'):
                i = 0
                for row in response['result']:
                    if row and row.has_key('pageurl') and row.has_key('count') and row['count'] > 2:
                        url = row['pageurl']
                        if url in urllist:
                            continue
                        #end if
                        #i += 1
                        #print i,url
                        urllist.append(url)
                    #end if
                #end for
            #end if
            
            return urllist
        except Exception,e:
            ERROR("LinkageWaf.main:%s, task_id:%s" % (str(e),self.task_id))
            return False
        #end try
    #end def
    
#end class


if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    try:
        linkagewaf = LinkageWaf('11','1')
        lines = linkagewaf.main()
        for row in lines:
            print row
        #end for
        
        
    except Exception,e:
        ERROR("__main__:%s" % (str(e)))
    #end try
#end if




