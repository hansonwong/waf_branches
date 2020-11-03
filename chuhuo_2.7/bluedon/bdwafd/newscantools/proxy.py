#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket, thread, select, re
import signal,sys
import MySQLdb
from lib.waf_netutil import *
import logging
from HostScan import db_manager
"""
host = "192.168.9.33"
user = "root"
passwd = "yxserver"
"""
__version__ = '0.1.0 Draft 1'
BUFLEN = 8192
VERSION = 'Python Proxy/'+__version__
HTTPVER = 'HTTP/1.1'

exclude_suffix = ["jpg", "gif", "png", "bmp", "jpeg", "xml", "css"]

#re.IGNORECASE = True
resp_pcre = re.compile(r"([hH][tT][tT][pP]\/1\.\d[\s\S]*?)\r\n\r\n")
resp_set_cookie_pcre = re.compile(r"[sS][eE][tT]-[Cc][oO][oO][kK][iI][eE]:([\s\S]*?)\r\n")
req_pcre = re.compile(r"[Cc][oO][oO][kK][iI][eE]:([\s\S]*?)\r\n")
url_pcre = re.compile(r"([hH][tT][tT][pP]s{0,1}:\/\/[\s\S]*?)\s")
domain_pcre = re.compile(r"([hH][tT][tT][pP]s{0,1}:\/\/[\s\S]*?)\/")

def update_cookie(domain, url, cookie):

    try:
        if url.split(".")[-1].lower() in exclude_suffix:
            return
        #end if
        domain = domain.strip()
        url    = url.strip()
        cookie = cookie.strip()
        id = 0
        cookie_dic = {}
        tmp_list = []
        
        I_or_U = True  #True: insert, False: update
        
        
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from cookie where url = %s"
        cur.execute(sql, (url))
        
        ret = cur.fetchone()
     
        if ret and ret["cookie"]:
            id = int(ret["id"])
            I_or_U = False
            
            c_str = ret["cookie"].strip()
            cookies = c_str.split(";")
        
            for c in cookies:
                c = c.strip()

                tokens = c.split("=", 1)
                
                # if len(tokens) != 2:
                #     print "get a error cookie:", c_str
                #     return
                if len(tokens) != 2:
                    continue
                #end if
                
                cookie_dic[tokens[0].strip()] = tokens[1].strip()

            #end for
        #end if
    
        cookies = cookie.split(";")
        
        for c in cookies:
            c = c.strip()
            tokens = c.split("=", 1)
            
            # if len(tokens) != 2: 
            #     print "get a error cookie"
            #     return 
            
            #modify by haiboyi@yxlink.com,cookie may contain Httponly
            if len(tokens) != 2:
                continue
            #end if
            cookie_dic[tokens[0].strip()] = tokens[1].strip()
        #end for
        
        
        
        for k in cookie_dic.keys():
            tmp_list.append(k + "=" + cookie_dic[k])
        #end for
        
        new_cookie_str = "; ".join(tmp_list)
        
        # print ']]]]]]]]]]]]]]]]]]]]]]]]]]]]]', new_cookie_str
        if I_or_U:
            sql  = "insert into cookie values(0, %s, %s, %s, now())"
            cur.execute(sql, (domain, url, new_cookie_str))
            conn.commit()
        else:
            sql  = "update cookie set `domain` = %s, `url` = %s, `cookie` = %s, `update_time` = now() where id = %s"
            cur.execute(sql, (domain, url, new_cookie_str, str(id)))
            conn.commit()
        #end if
    except Exception,e:
        print e
    #end try
#end def
        
    
    

class ConnectionHandler:
    def __init__(self, connection, address, timeout):
        
        
        try:
            self.now_url = ""
            self.now_domain = ""
            self.client = connection
            self.client_buffer = ''
            self.timeout = timeout
            self.method, self.path, self.protocol = self.get_base_header()
            if self.method=='CONNECT':
                self.method_CONNECT()
            elif self.method in ('OPTIONS', 'GET', 'HEAD', 'POST', 'PUT',
                                 'DELETE', 'TRACE'):
                self.method_others()
            self.client.close()
            #self.target.close()
        except Exception, e:
            self.client.close()
            self.target.close()
        #end try

    def get_base_header(self):
        while 1:
            self.client_buffer += self.client.recv(BUFLEN)
            end = self.client_buffer.find('\n')
            if end!=-1:
                break
        print '====%s'%self.client_buffer[:end]#debug
        
        domain = domain_pcre.findall(self.client_buffer[:end])
        url    = url_pcre.findall(self.client_buffer[:end]) 
        
        if domain and len(domain) == 1 and url and len(url) == 1:
            print "domain:",domain[0]
            print "url:", url[0]
            
            self.now_domain = domain[0]
            self.now_url    = url[0]
        data = (self.client_buffer[:end+1]).split()
        self.client_buffer = self.client_buffer[end+1:]
        return data

    def method_CONNECT(self):
        self._connect_target(self.path)
        #print ">>>>>>>>",
        #print self.path
        self.client.send(HTTPVER+' 200 Connection established\n'+
                         'Proxy-agent: %s\n\n'%VERSION)
        self.client_buffer = ''
        self._read_write()        

    def method_others(self):
        self.path = self.path[7:]
        i = self.path.find('/')
        host = self.path[:i]        
        path = self.path[i:]
        self._connect_target(host)
        self.target.send('%s %s %s\n'%(self.method, path, self.protocol)+
                         self.client_buffer)

        req_cookie =  req_pcre.findall(self.client_buffer)
        if req_cookie and len(req_cookie) == 1:
            print "req_cookie", req_cookie[0]
            
            update_cookie(self.now_domain, self.now_url, req_cookie[0])
        #end if
        self.client_buffer = ''
        self._read_write()

    def _connect_target(self, host):
        _host = ''
        _port = ''
        if '[' in host and ']' in host:
            _host = host[host.find('[')+1:host.find(']')] 
            _port = host[host.find(']'):]
            if ':' in _port:
                _port = int(_port[_port.find(':')+1:])
            else:
                _port = 80 
            self.target = socket.socket(socket.AF_INET6)
            self.target.connect((_host,80))
        else:
            i = host.find(':')
            if i!=-1:
                _port = int(host[i+1:])
                _host = host[:i]
            else:
                port = 80
            (soc_family, _, _, _, address) = socket.getaddrinfo(host, port)[0]
            self.target = socket.socket(soc_family)
            self.target.connect(address)

    def _read_write(self):
        time_out_max = self.timeout/3
        socs = [self.client, self.target]
        count = 0
        while 1:
            count += 1
            (recv, _, error) = select.select(socs, [], socs, 3)
            if error:
                break
            if recv:
                for in_ in recv:
                    
                    data = in_.recv(BUFLEN)
                    resp = resp_pcre.findall(data)
                    if resp and len(resp) == 1:
                        #print "resp_cookie", resp_cookie[0]
                        
                        resp_cookie = resp_set_cookie_pcre.findall(resp[0])
                        
                        if resp_cookie and len(resp_cookie) == 1:
                            print "resp_cookie", resp_cookie[0]
                            update_cookie(self.now_domain, self.now_url, resp_cookie[0])
                        #end if
                    #end if
                    
                    if in_ is self.client:
                        out = self.target
                    else:
                        out = self.client
                    if data:
                        out.send(data)
                        count = 0
            if count == time_out_max:
                break
            


    

def single_process( a, b):
    print "fffff"
    #self.client.close()
    #self.target.close()
    
    soc.close()

    sys.exit(0)
def start_server(host='', port=8080, IPv6=False, timeout=60,
                  handler=ConnectionHandler):
    global soc
    db = db_manager()
    res = db.get_one_item_from_db('select value from config where Name="httpproxy_flag"')
    if res and res.get('value') == '1':
        print 'ipv6'
        soc = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        print 'ipv4'
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.bind((host, port))
    print "Serving on %s:%d."%(host, port)#debug
    soc.listen(0)
    while 1:
        thread.start_new_thread(handler, soc.accept()+(timeout,))
        


if __name__ == '__main__':
    
    
    #url_pcre = re.compile(r"([hH][tT][tT][pP]s{0,1}:\/\/[\s\S]*?)\s")
    #a = "https://www.ff.com/ffsdf/fa.asp "
    #print  url_pcre.findall(a)
    #sys.exit(0)
    
    
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    signal.signal(signal.SIGTERM,single_process) 
    signal.signal(signal.SIGINT,single_process)
    #signal.signal(signal.SIGBREAK,single_process) 
    
    #a = "GET http://p4-hj3xl6yh5bfne-fp23etf3b6mfc25l-244171-i2-v6exp3-v4.metric.gstatic.com/v6exp3/6.gif HTTP/1.1"
    #print domain_pcre.findall(a)
    
    #print "fff"
    #update_cookie("www.test1.com", "www.test1.com/aa.php", "xx3=x2222x")
    
    #a = " uc1"
    #print a.split("=", 1)
    #sys.exit(0)
    try:
        ifen = get_config_value("httpproxy_enable")
        port = get_config_value("httpproxy_port")
        ifen = 1
        if ifen and int(ifen) == 1:
            if port:
                start_server(port = int(port))
            #end if
        #end if

    except Exception, e:
        logging.getLogger().error("File:proxy.py main:" + str(e))
    #end try
    

    
