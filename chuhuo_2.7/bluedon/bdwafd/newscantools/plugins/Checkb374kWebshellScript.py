#!/usr/bin/python
# -*- coding: utf-8 -*-
#code by lee
from lib.common import *
import sys
import os

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)

def run_url(http,ob,item):
    print "xxxxxxxxx"
    
    list=[]
    detail=""
    r=None
    try:
       
        #end if 
#        logging.getLogger().error(ip)
        
        filepath = sys_path("/www/dic/webshell_")
        r=open(filepath+ob['user_id']+".dic","r")
        
        webshelldic=r.readline().strip()
        
        if item['method'] == "get":
            
            if item['url'][-1] == '/':
                
                if item['params'] == "":
       
                    while webshelldic!="":
                       
                        url = "%s%s%s" % (item['url'],webshelldic,".php")
                        print "------------------"
                        print url
                        print "-----------------"
#                       response, content = http.request(url)
                        response, content = yx_httplib2_request(http,url)
                        if content.find('function tukar(lama,baru){ document.getElementById(lama')>=0 and response['status']!='404':
                            request = getRequest(url)
                            response = getResponse(response)
                            list.append(getRecord(ob,url,ob['level'],detail,request,response))
                        webshelldic=r.readline().strip()
        
        #end while

                
            
                
    except Exception,e:
        logging.getLogger().error("File:checkb374kwebshell.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:checkb374kwebshell.py, run_url function :" + str(e))
    #end try
    if r: r.close()
    return list

#ending
