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
from lib.common import *
#FLAG = "#d9Fa0j#"
from lib.fast_request import fast_request
import Queue

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)

filename = "PhpCheckScript.py"
path_vul_file = sys_path("/vuls_db/vuldb_8")
#path_vul_file = "C:\\svn\\nvs_phase2\\scripts\\vuls_db_repo\\vuldb_8"
len_dic = {}

def del_continuous(data, continuous_id, max_continuous):
    ifcontinuous = False
    if max_continuous < 1:
        return ifcontinuous, data
    ret = data
    count = 0
    to_dels = []
    to_del = []
    if len(continuous_id) >= max_continuous:
        for i in range(1, len(continuous_id)):
            #print continuous_id[i-1], continuous_id[i]
            
            if continuous_id[i] - continuous_id[i - 1] == 1:
                count = count + 1
                if i-1 not in to_del:
                    to_del.append(i-1)
                if i not in to_del:
                    to_del.append(i)
                #print to_del
            else:
                if count >= max_continuous:
                    to_dels.append(to_del)
                #end if
                to_del = []
                count = 0
            #end if
        #end for
        if count >= max_continuous:
            to_dels.append(to_del)
        #end if
    #end if
    #print to_dels
    
    if len(to_dels) > 0:
        ifcontinuous = True
    
    #del data:
    to_del_data = []
    for td in to_dels:
        for d in td:
            to_del_data.append(ret[d])
        #end for
    #end for
    
    for d in to_del_data:
        ret.remove(d)
    #del continuous_id:
    to_del_data = []
    for td in to_dels:
        for d in td:
            to_del_data.append(continuous_id[d])
        #end for
    #end for
    for d in to_del_data:
        continuous_id.remove(d)
    #del continuous_id:
    return ifcontinuous, ret, continuous_id
#end def

class check_page_thread(threading.Thread):
    def __init__(self, ob, domain, basedir, vuls, exp_queue):
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
        self.continuous_id = []
        
        self.max_request = 50
        self.no_code_count = 0
        
        self.exp_queue = exp_queue
        
        self.error_len_range = range(-2, 0)
 
    #end def
    
    def check_if_support_head(self):
        fr = fast_request(self.domain, self.basedir, self.rec, self.ob, self.ssl_enable)
        fr.connect()
        fr.req_url("/", "HEAD", 512)
        fr.close()
        #print fr.code
        if fr.code == "200" or fr.code == "301" or fr.code == "302" or fr.code == "403":
            return True
        #end if
        
        return False
    #end if
    
    def get_error_page_len(self):
        fr = fast_request(self.domain, self.basedir, self.rec, self.ob, self.ssl_enable)
        fr.connect()
        
        fr.req_url("/ffffffffffffffffffffffff12121212121212121222222222222222222ffffffffffffffffffffffffffffffffffffff", self.req_method, 512)
        long_len = fr.ret_len
        
        fr.req_url("/zz", self.req_method, 512)
        short_len = fr.ret_len 
        
        if fr.code == "200":
            if long_len == short_len:
                self.error_len_range = range(short_len, short_len + 1)
            #end if
            
            if long_len > short_len:
                self.error_len_range = range(short_len, long_len + 1)
            else:
                self.error_len_range = range(long_len, short_len + 1)
            #end if
        #end if
    #end def
    
    '''
    def handle_result(self, url, factor, detail, request_data, response_data):
        self.ret.append(getRecord(self.ob, url, factor, detail, request_data, response_data))
        #self.ret.append(url)
        
        self.continuous_id.append(self.total_check)

        continuous,ret,continuous_id  = del_continuous(self.ret, self.continuous_id, 3)
        if continuous:
            self.ret = ret
            self.continuous_id = continuous_id
        #end if
        return continuous
    #end def
    '''
    
    def handle_result(self, url, factor, detail, request_data, response_data, len = 0):
        #self.ret.append(getRecord(self.ob, url, factor, detail, request_data, response_data))
        self.ret.append({'vul':getRecord(self.ob, url, factor, detail, request_data, response_data),'len':len})
        if len_dic.has_key(len):
            len_dic[len] += 1
        else:
            len_dic[len] = 1
        #end if
        
        self.continuous_id.append(self.total_check)

        continuous,ret,continuous_id  = del_continuous(self.ret, self.continuous_id, 3)
        if continuous:
            self.ret = ret
            self.continuous_id = continuous_id
        #end if
        return continuous
    #end def

    def run(self):
    
        global FLAG #"#d9Fa0j#"
        
        if self.check_if_support_head():
            self.req_method = "HEAD"
        else:
            self.req_method = "GET"
        #end if
        
        if checkErrorFileStatus(self.ob['scheme'],self.ob['domain'],self.ob['base_path'],".php",self.req_method) == False:
            return
        #end if
        
        self.get_error_page_len()
      
        #print self.req_method
        exec_time = time.time()
        need_check_content = []
        

        if self.req_method == "HEAD":
            fr = fast_request(self.domain, self.basedir, self.rec, self.ob, self.ssl_enable)

            count = 0
            for v in self.vuls:
                if len(self.ret) > 20:
                    self.ret = []
                    logging.getLogger().error("File:%s, too many match urls, task id:%s, domain:%s" % (filename,self.ob['task_id'],str(self.domain)))
                    return
                #end if
                
                #if self.rec.err_out() and not self.isForce:
                    #return
                #end if
                
                try:             
                    if fr.connectOK == False:               
                        fr.connect()                     
                    #end if
 
                    vs = v.strip().split(FLAG)
                    if len(vs) != 8:
                        continue
                    #end if
                    
                    if vs[5] != "200" and vs[5] != "403":
                        
                        need_check_content.append(v)
                        continue
                    #end if
             
                    if vs[3][0:2] == "/?" or vs[3].find("../") != -1 or vs[3].find("..\\") != -1:
                        continue
                    #end if
                    
                    if count >= self.max_request:
                        fr.close()
                        fr.connect()
                        count = 0
                    #end if
                    
                    count = count + 1
                    prev =time.time()
                    recv_data = fr.req_url(vs[3], self.req_method, 512)

                    if fr.code == "":
                        self.no_code_count = self.no_code_count + 1
                        if self.no_code_count > 50:
                            self.max_request = 1
                        #end if
                        fr.close()
                        fr.connect()
                        recv_data = fr.req_url(vs[3], self.req_method, 512)
                    #end if
                    
                    self.total_check = self.total_check + 1
                    
                    if fr.ret_len == 0:
                        continue
                    #end if
                    
                    if fr.code.find(vs[5]) != -1: # or fr.code.find("403") != -1:
                        """
                        print "-------------------------------------------------"
                        print "http://" + self.domain + self.basedir + vs[3]
                        print "-------------------------------------------------"
                        print vs[6]
                        print "-------------------------------------------------"
                        print fr.request_data
                        print "-------------------------------------------------"
                        print fr.response_data
                        print "-------------------------------------------------"
                        """
                        if fr.ret_len not in self.error_len_range:
                            if self.handle_result(fr.url, vs[1], vs[6], fr.request_data, fr.response_data, fr.ret_len) == True:
                                return
                            #end if
                        #end if
                    #end if
                    if flowControl(self,time.time()-prev,self.rec,self.isForce,self.web_speed,self.web_minute_package_count,False):
                        return
                    #end if
                    
                except Exception, e:                   
                    logging.getLogger().error("File:" + filename + ",  check_page_thread::run function :" + str(e) + ",task id:" + self.ob['task_id'] + ", check_path: " + vs[3] + ",domain:" + str(self.domain))
                #end try
            #end for
            
            fr.close()
        elif self.req_method == "GET":
            fr = fast_request(self.domain, self.basedir, self.rec, self.ob, self.ssl_enable)
            for v in self.vuls:
                if len(self.ret) > 20:
                    self.ret = []
                    logging.getLogger().error("File:%s, too many match urls, task id:%s, domain:%s" % (filename,self.ob['task_id'],str(self.domain)))
                    return
                #end if
                
                #if self.rec.err_out() and not self.isForce:
                    #return
                #end if

                try:
                    if fr.connectOK == False:
                        fr.connect()
                    #end if
                    vs = v.strip().split(FLAG)
                    
                    if len(vs) != 8:
                        continue
                    #end if
                    
                    if vs[5] != "200" and vs[5] != "403":
                        need_check_content.append(v)
                        continue
                    #end if
                    
                    if vs[3][0:2] == "/?" or vs[3].find("../") != -1 or vs[3].find("..\\") != -1:
                        continue
                    #end if
                    
                    request_data = '%s %s HTTP/1.1\r\nHost: %s\r\n\r\n' % (self.req_method, self.basedir + vs[3], self.domain)
                    prev =time.time()     
                    recv_data = fr.req_url(vs[3], self.req_method, 512)
                    
                    self.total_check = self.total_check + 1
                    
                    if fr.ret_len == 0:
                        continue
                    #end if

                    if fr.code.find(vs[5]) != -1: # or fr.code.find("403") != -1:
                        """
                        print "-------------------------------------------------"
                        print "http://" + self.domain + self.basedir + vs[3]
                        print "-------------------------------------------------"
                        print vs[6]
                        print "-------------------------------------------------"
                        print fr.request_data
                        print "-------------------------------------------------"
                        print fr.response_data
                        print "-------------------------------------------------"
                        """
                        if fr.ret_len not in self.error_len_range:
                            if self.handle_result(fr.url, vs[1], vs[6], fr.request_data, fr.response_data, fr.ret_len) == True:
                                return
                            #end if
                        #end if     
                    #end if
                    fr.close()
                    if flowControl(self,time.time()-prev,self.rec,self.isForce,self.web_speed,self.web_minute_package_count,False):
                        return
                    #end if                 
                except Exception, e:    
                    logging.getLogger().error("File:" + filename + ", check_page_thread::run function :" + str(e) + ",task id:" + self.ob['task_id'] + ", check_path: " + vs[3] + ",domain:" + str(self.domain))
                #end try
            #end for
            
        #end if
        
        for v in need_check_content:
            try:
                if len(self.ret) > 20:
                    self.ret = []
                    logging.getLogger().error("File:%s, too many match urls, task id:%s, domain:%s" % (filename,self.ob['task_id'],str(self.domain)))
                    return
                #end if
                
                #if self.rec.err_out() and not self.isForce:
                    #return
                #end if
                if fr.connectOK == False:
                    fr.connect()
                #end if
                vs = v.strip().split("#d9Fa0j#")
                if len(vs) != 8:
                    continue
                #end if
                prev =time.time()
                recv_data = fr.req_url(vs[3], "GET", 2048)
                self.total_check = self.total_check + 1
                
                if fr.ret_len == 0:
                    continue
                #end if
                
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
                    if fr.ret_len not in self.error_len_range:
                        if self.handle_result(fr.url, vs[1], vs[6], fr.request_data, fr.response_data, fr.ret_len) == True:
                            return
                #end if
                fr.close()
                if flowControl(self,time.time()-prev,self.rec,self.isForce,self.web_speed,self.web_minute_package_count,False):
                    return
                #end if                
            except Exception, e:
                #print e
                logging.getLogger().error("File:" + filename + ", check_page_thread::run function :" + str(e) + ",task id:" + self.ob['task_id'] + ", check_path: " + vs[3] + ",domain:" + str(self.domain))
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
        if max_thread > 4:
            max_thread = 4
        #end if
        #max_thread = 1
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
            threads.append(check_page_thread(ob, domain, basedir, i, exp_queue))
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
        #print "total find:",len(ret)
        return ret
       
    except Exception,e:
        logging.getLogger().error("File:" + filename + ", path_check_mgr function :" + str(e) + ",task id:" + ob['task_id'] + ", domain:" + ob['domain'])
        return []
    #end try    
#end def

def run_domain(http,ob):
    t = time.time()
    try:     
        ret = path_check_mgr(ob, ob["domain"], ob["base_path"], ob["max_thread"])
        if len(ob['len_404']) > 10:
            pass
        else:
            for k in len_dic.keys():
                if len_dic[k] > 1:
                    if k in ob['len_404']:
                        pass
                    else:
                        ob['len_404'].append(k)
                    #end if
                #end if 
            #end for
        #end if
        
        list = []
        for row in ret:
            if row['len'] not in ob['len_404']:
                list.append(row['vul'])
            #end if
        #end for
        
        if list and len(list) > 30:
            return []
        else:
            return list
        #end if
        
        #return ret
    except Exception,e:
        logging.getLogger().error("File:" + filename + ", run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ", domain: " + ob['domain'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:" + filename + ", run_domain function :" + str(e))
        return []
    #end try    
#end def

if __name__ == '__main__':
    t = time.time()
    #www.vooioov.com
    #192.168.9.176
    path_check_mgr(None, "119.147.51.146", "/", 10)
    #print time.time() - t
