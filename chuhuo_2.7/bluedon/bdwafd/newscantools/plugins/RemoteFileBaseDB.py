#!/usr/bin/python
# -*- coding: utf-8 -*-

LOCAL_DEBUG = True

import logging
import re
import sys
import os
import socket
import threading
import time
import httplib2
from lib.common import *
#FLAG = "#d9Fa0j#"
from lib.fast_request import fast_request
from lib.ex_httplib2 import *
import Queue

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)

filename = "RemoteFileBaseDB.py"
path_vul_file = sys_path("/vuls_db/vuldb_12")
#path_vul_file = "C:\\svn\\nvs_phase2\\scripts\\vuls_db_repo\\vuldb_12"

class check_page_thread(threading.Thread):
    def __init__(self, http, ob, domain, basedir, vuls, exp_queue):
        threading.Thread.__init__(self)
        self.ob = ob
        self.domain = domain
        self.connect_domain = domain
        self.basedir = basedir[0:len(basedir) - 1]
        self.vuls = vuls
        self.req_method = ""
        self.rec = ob["rec"]
        self.isForce = ob['isForce']
        self.web_speed = ob["web_speed"]
        self.web_minute_package_count = ob["web_minute_package_count"]
        self.http = http
        self.scheme = ob["scheme"]
        
        self.ret = []
        self.total_check = 0
        self.continuous_id = []
        
        self.exp_queue = exp_queue
        
        self.error_len_range = range(-2, 0)
        self.rfi_url = self.ob["rfi_url"]
        self.rfi_keyword = self.ob["rfi_keyword"].encode('utf8')
 
    #end def
    
    def handle_result(self, url, factor, detail, request_data, response_data):
        self.ret.append(getRecord(self.ob, url, factor, detail, request_data, response_data))
        #self.ret.append(url)
        #self.continuous_id.append(self.total_check)
        #print "find:", url
      
    #end def

    def run(self):
    
        global FLAG #"#d9Fa0j#"

        exec_time = time.time()
        http = ex_httplib2(self.ob["rec"])
        http.httlib2_set_follow_redirects(False)
        http.httlib2_set_timout(self.ob["web_timeout"])
        
        for v in self.vuls:
            if len(self.ret) > 5:
                self.ret = []
                logging.getLogger().error("File:%s, too many match urls, task id:%s, domain:%s" % (filename,self.ob['task_id'],str(self.domain)))
                return
            #end if
            
            #if self.rec.err_out() and not self.isForce:
                #return
            #end if
   
            try:        
                vs = v.strip().split(FLAG)
                if len(vs) != 8:
                    continue
                #end if
                #print url
                url = self.scheme + "://" + self.domain + self.basedir[0:len(self.basedir) - 1] + vs[3].replace("@RFIURL", self.rfi_url)
                #print url
                prev =time.time()
                #res, content = http.request(url)
                res, content = yx_httplib2_request(http,url)
                self.total_check = self.total_check + 1

                if res and res.has_key('status') and res['status'] in ['200','500'] and content.find(self.rfi_keyword) != -1: # or fr.code.find("403") != -1:
                    #print url
                    request = getRequest(url,'GET')
                    response = getResponse(res,"")
                    self.handle_result(url, vs[1], vs[6], request, response)
 
                #end if
                if flowControl(self,time.time()-prev,self.rec,self.isForce,self.web_speed,self.web_minute_package_count,False):
                    return
                #end if
                
            except Exception, e:
                logging.getLogger().error("File:RemoteFileBaseDB.py, check_page_thread::run function :" + str(e) + ",task id:" + self.ob['task_id'] + ", check_path: " + vs[3] + ",domain:" + str(self.domain))
           
            #end try
        #end for
  
        
        exec_time = time.time() - exec_time
    #end def

def path_check_mgr(http, ob, domain, basedir, max_thread):
    
    try:
        
        f = open(path_vul_file, "r")
        
        lines = f.readlines()
        lines_num = len(lines)
        if lines_num < max_thread or lines_num < 200:
            max_thread = 1
        #end if
        if max_thread > 4:
            max_thread = 4
        #end if

        thread_data = []
        
        thread_vul_num = lines_num / max_thread
        for i in range(0, max_thread):
            tmp = []
            
            for c in range(0, thread_vul_num):
                tmp.append(lines.pop())
            #end for
            
            thread_data.append(tmp)
        #end for
        
        thread_data[max_thread - 1] = thread_data[max_thread - 1] + lines

        threads = []
        exp_queue = Queue.Queue()
        for i in thread_data:
            threads.append(check_page_thread(http, ob, domain, basedir, i, exp_queue))
        #end for
        
        for t in threads:
            t.start()
        #end for
        
        for t in threads:
            t.join()
        #end for 
        
        total_check = 0
        for t in threads:
            total_check = total_check + t.total_check
        #end for
        
        ret = []
        
        for t in threads:
            ret = t.ret + ret
        #end for
        #print total_check
        return ret
        
        
    except Exception,e:
        #print e
        logging.getLogger().error("File:RemoteFileBaseDB.py, path_check_mgr function :" + str(e) + ",task id:" + ob['task_id'] + ", domain:" + ob['domain'])
        return []
    #end try    
#end def

def run_domain(http,ob):
    t = time.time()
    try:     
        ret = path_check_mgr(http, ob, ob["domain"], ob["base_path"], ob["max_thread"])
        #print time.time() - t
        if ret and len(ret) > 4:
            return []
        else:
            return ret
        #end if
        
        return ret
    except Exception,e:
        logging.getLogger().error("File:RemoteFileBaseDB.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ", domain: " + ob['domain'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:RemoteFileBaseDB.py, run_domain function :" + str(e))
        return []
    #end try    
#end def

if __name__ == '__main__':
    t = time.time()
    #www.vooioov.com
    #192.168.9.176
    http = httplib2.Http(timeout=5)
    path_check_mgr(http, 1, "192.168.9.109", "/", 10)
    print time.time() - t
