#!/usr/bin/python
# -*- coding: utf-8 -*-

import httplib2
import threading
import time
import socket
import re
from common import checkIpv6

#from common import request_exception_counter

"""
class request_exception_counter(object):
  
    def __init__(self):
        self.mutex = threading.Lock()
        
        self.timeout_err  = 0
        self.other_err    = 0
        self.success      = 0
        
        self.init_time    = time.time()
    #end def
    
    def add_timeout_err(self):
        self.mutex.acquire()
        self.timeout_err = self.timeout_err + 1 
        self.mutex.release()
    #end def
    
    def add_other_err(self):
        self.mutex.acquire()
        self.other_err = self.other_err + 1 
        self.mutex.release()
    #end def
    
    def add_success(self):
        self.mutex.acquire()
        self.success = self.success + 1 
        self.mutex.release()
    #end def
    
    def dump_info(self):
        return str("timeout:%d, other:%d, success:%d, time:%ds" \
                    % (self.timeout_err, self.other_err, self.success, time.time() - self.init_time))
    #end def
    
    def get_err_count(self):
        self.mutex.acquire()
        ret = (self.timeout_err + self.other_err) - self.success
        self.mutex.release()
        
        return ret
    #end def
#end class

"""


class ex_http_exception(Exception):
    def __init__(self, time_out_err, other_err, success, cost_time):
        
        self.time_out_err = time_out_err
        self.other_err    = other_err
        self.success      = success
        self.cost_time    = cost_time
        
    def __str__(self):
        return str("timeout:%d, other:%d, success:%d, time:%ds" \
                    % (self.time_out_err, self.other_err, self.success, self.cost_time))
#end class

class ex_httplib2(object):
    def __init__(self, rec, cookie = None):
        self.http = httplib2.Http(disable_ssl_certificate_validation=True)
        self.rec = rec
        
        if cookie and len(cookie) > 0:
            self.cookie = cookie
        else:
            self.cookie = None
        #end if
    #end def
    
    def httlib2_set_timout(self, a):
        self.http.timeout = a
    #end def
    
    def httlib2_set_follow_redirects(self, a):
        self.http.follow_redirects = a
    #end def
    
    def handle_timout_exp(self):
        self.rec.add_timeout_err()
    #end def
    
    def handle_other_err(self):
        self.rec.add_other_err()
    #end def
    
    def handle_success(self):
        self.rec.add_success()
        
    #end def
        
    def request(self, url, method="GET", body=None, headers=None):
        if headers is None:
            headers = {"Accept-Encoding":"identity"}
            #"Content-Type":"application/x-www-form-urlencoded"
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            headers["Accept-Encoding"] = "identity"
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        #end if
        
        if self.cookie:
            headers["Cookie"] = self.cookie
        #end if

#-------START 2014-10-15 yinkun-------
        a = url.find("[")
        b = url.find("]")
        if a >=0 and b >=0:
            host_domain = url[a+1:b]
            if checkIpv6(host_domain):
                headers["Host"] = '[' + host_domain + ']'
#--------------------------------------
        
        try:
            response, content = self.http.request(url, method, body, headers)
            self.handle_success()
            return (response, content)
   
        except socket.timeout,e:
            self.handle_timout_exp()
            raise
            
        except Exception,e:
            self.handle_other_err()
            raise
            
        #end try
    #end def
#end class




if __name__ == '__main__':
    rec = request_exception_counter()
    a = ex_httplib2(rec)
    a.httlib2_set_follow_redirects(False)
    a.httlib2_set_timout(2)

    for i in range (1):
        try:
            print 1
            resp, data = a.request("http://192.168.9.195", "POST", "AA=AA")
            print resp
        except ex_http_exception, e:
            print "===="
            print e
        except Exception, e:
            print "-----"
            print e
    #print rec.dump_info()