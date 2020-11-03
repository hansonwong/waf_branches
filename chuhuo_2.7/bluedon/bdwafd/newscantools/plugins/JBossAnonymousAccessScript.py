#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u"JBoss是全世界开发者共同努力的成果，一个基于J2EE的开放源代码的应用服务器，JBoss允许匿名访问，攻击者可利用此执行远程代码，导致服务器直接被上传WebShell。"
        detail = detail.encode('utf8')
    
        url = "%s://%s/" % (ob['scheme'],ob['domain'])
        url += "jmx-console/HtmlAdaptor"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('MX Agent View') >= 0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
        else:
            url = "%s://%s:8080/" % (ob['scheme'],domain)
            url += "jmx-console/HtmlAdaptor"
            res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("MX Agent View") >= 0:
                request = getRequest(url)
                response = getResponse(res)
                list.append(getRecord(ob,url,ob['level'],detail,request,response))
            #end if
        #end if
    except Exception,e:
        logging.getLogger().error("File:JBossAnonymousAccessScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:JBossAnonymousAccessScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def




            
        
        
        
        
        