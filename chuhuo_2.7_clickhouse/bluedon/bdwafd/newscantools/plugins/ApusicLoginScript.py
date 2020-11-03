#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
       
        expurl="%s%s"%(url,"admin/login.jsp")
        
        res, content = requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('action="j_security_check"')>=0 and content.find('name="j_username"')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:ApuicLoginScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:ApuicLoginScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def