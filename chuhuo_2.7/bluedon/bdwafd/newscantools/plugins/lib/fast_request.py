#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import ssl
import re
import time
from common import checkIpv6


class fast_request(object):
    def __init__(self, domain, basedir, rec, ob, en_ssl = False):
        
        """
        domain: www.test.com
                www.test.com:81
                192.168.1.1
                192.168.1.1:81
                
        basedir: /
                /a/
        """
        
        self.domain = domain
        if checkIpv6(domain):
            self.domain = '[' + domain + ']'
        self.connect_domain = domain
        self.basedir = basedir[0:len(basedir) - 1]
       
        self.en_ssl = en_ssl
        self.ob = ob
        self.cookie = self.ob["cookie"]
        
        self.rec = rec
        
        self.port = 0
#--------- yinkun  2014-10-13      增加对含IPv6地址的域名处理  start------------- 
#example [fd80::89] or [fd80::89]:80         
        if domain and domain.find("[") >=0  and domain.find("]") >=0:
            a = domain.find("[")
            b = domain.find("]")
            self.connect_domain = domain[a+1:b]

            if len(domain.split("]:")) ==2:
                self.port  = int(domain.split("]:")[1])
            elif len(domain.split("]:")) ==1:
                if self.en_ssl:
                    self.port = 443
                else:
                    self.port = 80
#------------------------------------end-----------------------------------------
        elif domain and len(domain.split(":")) == 2:
            self.connect_domain = domain.split(":")[0]
            self.port   = int(domain.split(":")[1])
        elif domain and len(domain.split(":")) == 1:
            if self.en_ssl:
                self.port = 443
            else:
                self.port = 80
        #end if
        
        self.request_data = ""
        self.response_data = ""
        self.url  = ""
        self.code = ""
        self.ret_len = -1

        self.connectOK = False
        
    #end def
    
    def connect(self):
        
        try:
            ip_type = 4
            res = socket.getaddrinfo(self.connect_domain, None)
            if res and len(res) > 0:
                if checkIpv6(res[0][4][0]):
                    ip_type = 6
                else:
                    ip_type = 4
            else:
                print "connect getaddrinfo() error to ip error"

            socket.setdefaulttimeout(5)

            self.s = ''
            if ip_type == 4:
                if self.en_ssl:
                    self.s = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
                
                else:
                    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #end if
            else:
                if self.en_ssl:
                    self.s = ssl.wrap_socket(socket.socket(socket.AF_INET6, socket.SOCK_STREAM))
                
                else:
                    self.s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                #end if
            
            self.s.connect((self.connect_domain, self.port))
            
        except socket.timeout,e:
            self.connectOK = False
            if self.rec:
                self.rec.add_timeout_err()
            raise
        except Exception, e:
            self.connectOK = False
            if self.rec:
                self.rec.add_other_err()
            raise
        #end try
        self.connectOK = True
        
    #end def
    
    def close(self):
        self.s.close()
        self.connectOK = False
    #end def
        
    
    def req_url(self, url, req_method, max_len):
        
        
        try:
            self.url = ""
            self.request_data = ""
            self.response_data = ""
            self.code = ""
            self.ret_len = -1
            
            if self.cookie and len(self.cookie) > 0:
                self.request_data = '%s %s HTTP/1.1\r\nHost: %s\r\nConnection:Keep-Alive\r\nCookie: %s\r\n\r\n' % (req_method, self.basedir + url, self.domain, self.cookie)
            else:
                self.request_data = '%s %s HTTP/1.1\r\nHost: %s\r\nConnection:Keep-Alive\r\n\r\n' % (req_method, self.basedir + url, self.domain)
            #end if
            #t = time.time()
            try:
                self.s.send(self.request_data)
                recv_data = self.s.recv(max_len)
            except Exception, e:
                self.connectOK = False
                raise
            #end try
            #print time.time() - t
            self.response_data = recv_data.split("\r\n\r\n")[0]
            
            if self.en_ssl:
                self.url = "https://%s%s%s" % (self.domain, self.basedir, url)
            else:
                self.url = "http://%s%s%s" % (self.domain, self.basedir, url)
            #end if
            first_line = recv_data.split("\r\n")[0]
            p = re.compile(r"^HTTP/\d\.\d")
            if len(p.findall(first_line)) == 1:
                self.code = first_line.split(" ")[1]
#                print "^^^^^^^^^^^^^^^^^^^^^^^^"
#                print self.code
#                print self.basedir
#                print "^^^^^^^^^^^^^^^^^^^^^^^^"
            #end if
            
            p = re.compile(r"(?i)Content-Length: (\d+)")
            
            tmp = p.findall(self.response_data)
            if len(tmp) == 1:
                
                self.ret_len = int(tmp[0])
            else:
                #print "=====rerrrrr"
                #print recv_data
                pass
                    
            #end if
            #print self.ret_len 
            
            
            tmp_datas = recv_data.split("\r\n\r\n")
            tmp_datas.remove(tmp_datas[0])
            if self.rec:
                self.rec.add_success()
            return "".join(tmp_datas)
        except socket.timeout,e:
            if self.rec:
                self.rec.add_timeout_err()
            raise
        except Exception, e:
            if self.rec:
                self.rec.add_other_err()
            raise
        return ""
    #end def
#end class

if __name__ == '__main__':
   
    a = fast_request("sms.139life.com", "/", False)
    a.connect()
   
    #print a.req_url("/1", "HEAD")
    for i in range(100):
        a.req_url("/database/new.mdb", "HEAD", 4096)   
        print a.code
   
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("www.tompda.com", 80))
    s.send("GET / HTTP/1.1\r\nHost: www.tompda.com\r\n\r\n")
    print s.recv(100)
    print socket.SHUT_RDWR
    s.shutdown(socket.SHUT_RDWR)
    print s.recv(100)
    s.close()
    """