#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_url(http,ob,item):
    list = []
    #print "*"*1000
    try:
        url = item['url']
        detail = ''    
        expurl="%s%s"%(url,"%20")
        res, content = requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        #print content
        if content.find("<?php")>=0 and content.find("?>")>=0:
            request = getRequest(expurl)
            response = getResponse(res)
            list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
            if ob['isstart']=='1':
                detail="验证性扫描结果：\n%s"%content
    except Exception,e:
        logging.getLogger().error("File:nginxnullstringscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:nginxnullstringscript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def 