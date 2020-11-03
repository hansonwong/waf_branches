#!/usr/bin/python
# -*- coding: utf-8 -*-
#code by lee
from lib.common import *
import base64
import os
import sys

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)

def run_domain(http,ob):
    
    list=[] 

    try:
           
        ip = ob['domain']
    
        #end if 
#        logging.getLogger().error(ip)
        
        expurl="manager/html"
        
        filepath = sys_path("/www/dic/tomcatweakpwd_")
        r=open(filepath+ob['user_id']+".dic","r")
        
        weakpwd=r.readline().strip()
#        if ip.find(":")<0:
#            url = "%s://%s:8080%s%s" % (ob['scheme'],ip,ob['base_path'],expurl)
#        else:
        url = "%s://%s%s%s" % (ob['scheme'],ip,ob['base_path'],expurl)
        
        while weakpwd!="":
            
            if weakpwd.find("{NULL}"):
                
                weakpwd=weakpwd.replace("{NULL}","")
                
            #end if 
                
            headers={"Host": ip,"User-Agent":" Mozilla/4.0 (compatible; MSIE 6.0; Win32)",\
             "Accept":"text/html, */*","Cookie":"ASP.NET_SessionId=xjtshbayc4dkznhkmpwidtdt","Content-Type":"text/html","User-Agent": "Mozilla/3.0 (compatible; Indy Library)",\
             "Authorization": "Basic "+base64.b64encode(weakpwd)}
        
            try:
                
                #response, content = http.request(url,"GET",'',headers)
                response, content = yx_httplib2_request(http,url,"GET",'',headers)
                print response['status'],weakpwd,url
            except Exception,e:
                logging.getLogger().error("ScanWeakPwdForTomcat.py get request time out")
                
                weakpwd=r.readline().strip()
                
                continue
            
            #end try
            if response.has_key('status') and response['status']=='200' and content.find("<title>/manager</title>")>=0 and content.find("WoGo xServer")<0:
                
                request = getRequest(url,"GET",headers,"")
                
                response = getResponse(response)
                
                if weakpwd.split(":")[1]=="":
                    
                    weakpwd=weakpwd.split(":")[0]+":{NULL}"
                    
                #end if 
                
                detail=u"Apache Tomcat弱密码\n用户名：%s\n密码：%s"%(weakpwd.split(":")[0],weakpwd.split(":")[1])
                
                #write_weak_log(ob["task_id"], ob["task_name"], "http://"+ob['domain'], "Apache Tomcat", weakpwd.split(":",1)[0], weakpwd.split(":",1)[1])
                #modify by haiboyi
                write_weak_log(ob["task_id"], ob["task_name"], ob['ip'], "Apache Tomcat", weakpwd.split(":",1)[0], weakpwd.split(":",1)[1])
                
                list.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
            
            #end if
                
            weakpwd=r.readline().strip()
      
    #end while
                
    except Exception,e:
        
        logging.getLogger().error("File:ScanWeakPwdForTomcat.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:ScanWeakPwdForTomcat.py, run_domain function :" + str(e))
    #end try
    r.close()
    
    return list

#ending
