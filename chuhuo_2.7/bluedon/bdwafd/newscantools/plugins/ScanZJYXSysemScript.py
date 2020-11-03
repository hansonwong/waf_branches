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
        url += "Government/Resources/program/logon.asp"
        #res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        header={'User-Agent':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; InfoPath.2; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'}
        #res,content=http.request(url,headers=header)
        res,content=yx_httplib2_request(http,url,headers=header)
        if res['status'] == '200' and content.find('<form action="logon.asp" method="post" name="LogonForm">')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:scanzjyxsystemscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:scanzjyxsystemscript.py, run_domain function :" + str(e))
    #end try

    return list
#end def