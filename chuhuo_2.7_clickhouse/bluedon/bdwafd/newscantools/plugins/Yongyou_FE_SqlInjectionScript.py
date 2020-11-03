#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s/" % (ob['scheme'],ob['domain'])
        url += "common/codewidget.jsp?code=1%27"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '500' and (content.find('com.microsoft.sqlserver.jdbc.SQLServerException')>=0 or content.find('java.sql.SQLException')>=0):
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:Yongyou_FE_SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:Yongyou_FE_SqlInjectionScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
