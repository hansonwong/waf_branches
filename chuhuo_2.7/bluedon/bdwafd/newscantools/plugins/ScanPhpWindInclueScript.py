#!/usr/bin/python
# -*- coding: utf-8 -*-

LOCAL_DEBUG = True

import logging
import re
import os
import sys
import socket
import threading
import time
from lib.common import *
FLAG = "#d9Fa0j#"
from lib.fast_request import fast_request

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)

path_vul_file = sys_path("/vuls_db/vuldb_27_2")
#path_vul_file = "C:\\svn\\nvs_phase2\\scripts\\vuls_db_repo\\vuldb_1_2"

class check_page_thread(threading.Thread):
    def __init__(self, ob, domain, basedir, vuls):
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
        self.ssl_enable = False
        if ob['scheme'] == 'https':
            self.ssl_enable = True
        #end if
        
        self.ret = []
        self.total_check = 0
    #end def
    
    def run(self):
        
        global FLAG #"#d9Fa0j#"
        
        exec_time = time.time()
  
        need_check_content = []

        fr = fast_request(self.domain, self.basedir, self.rec, self.ob, self.ssl_enable)
        try:
            for v in self.vuls:
                #if self.rec.err_out() and not self.isForce:
                    #return
                #end if

                #fr.connect()
                vs = v.strip().split(FLAG)
                if len(vs) != 8:
                    continue
                #end if
                if vs[5] != "200" and vs[5] != "403":
                    need_check_content.append(v)
                    continue
                #end if   
                #fr.close()
            #end for
        except Exception, e:
            logging.getLogger().error("File:PathCheck.py, check_page_thread::run function :" + str(e) + ",task id:" + self.ob['task_id'] + ", check_path: " + vs[3])
            #end try
        #end if
        
        for v in need_check_content:
            try:
                #if self.rec.err_out() and not self.isForce:
                    #return
                #end if
                fr.connect()
                vs = v.strip().split("#d9Fa0j#")
                if len(vs) != 8:
                    continue
                #end if
                prev =time.time()
                recv_data = fr.req_url(vs[3], "GET", 2048)
               
                if fr.code == "200" and recv_data.find(vs[5]) != -1:
                    """
                    print "-------------------------------------------------"
                    print "http://" + self.domain + self.basedir + vs[3]
                    print "-------------------------------------------------"
                    print vs[6]
                    print "-------------------------------------------------"
                    print request_data
                    print "-------------------------------------------------"
                    print response_data
                    print "-------------------------------------------------"
                    """
                    self.ret.append(getRecord(self.ob, fr.url, vs[1], vs[6], fr.request_data, fr.response_data))
                #end if
                fr.close()
                if flowControl(self,time.time()-prev,self.rec,self.isForce,self.web_speed,self.web_minute_package_count,False):
                    return
                #end if
            except Exception, e:
                #print e
                logging.getLogger().error("File:PathCheck.py, check_page_thread::run function :" + str(e) + ",task id:" + self.ob['task_id'] + ", check_path: " + vs[3])
            #end try
        #end for
        
        exec_time = time.time() - exec_time
    #end def

def path_check_mgr(ob, domain, basedir, max_thread):
    
    try:
        
        f = open(path_vul_file, "r")
        
        lines = f.readlines()
        lines_num = len(lines)
        if lines_num < max_thread or lines_num < 200:
            max_thread = 1
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
        for i in thread_data:
            threads.append(check_page_thread(ob, domain, basedir, i))
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
        logging.getLogger().error("File:scanphpwindincludescript.py, path_check_mgr function :" + str(e) + ",task id:" + ob['task_id'] + ", domain:" + ob['domain'])
        return []
    #end try    
#end def

def run_domain(http,ob):
    t = time.time()
    try:     
        ret = path_check_mgr(ob, ob["domain"], ob["base_path"], ob["max_thread"])
        #print time.time() - t
        return ret
    except Exception,e:
        logging.getLogger().error("File:scanphpwindincludescript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ", domain: " + ob['domain'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:scanphpwindincludescript.py, run_domain function :" + str(e))
        return []
    #end try    
#end def

#if __name__ == '__main__':
#    t = time.time()
#    path_check_mgr(1, "192.168.9.176", "/", 10)
#    print time.time() - t
