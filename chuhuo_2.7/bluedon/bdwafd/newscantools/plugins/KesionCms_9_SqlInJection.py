#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = ""
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "item/?c-1,key-'.html"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if (content.find('Microsoft JET Database Engine')>=0 or content.find("Microsoft OLE DB Provider for SQL Server")>=0) and res['status']=='500':
            request = getRequest(url,'GET')
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:kesioncms_9_sqlinjection.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:kesioncms_9_sqlinjection.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def