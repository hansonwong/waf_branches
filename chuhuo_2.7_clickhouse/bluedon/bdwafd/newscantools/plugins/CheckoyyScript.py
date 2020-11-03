#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]                               
        detail=u''
        detail=detail.encode('utf8')
        domain=ob['domain']
        url="otype.asp?classid=1"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        if content.find("include/data.js")>=0 and response['status']=='200':
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,ob['scheme']+"://"+domain+ob['base_path'],ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:checkoyyscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:checkoyyscript.py, run_domain function :" + str(e))
    return result

