#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]                               
        detail=""
        detail=detail.encode('utf8')
        domain=ob['domain']
        expurl1="%s://%s%sWebResource.axd?d=nvs_test"%(ob['scheme'],domain,ob['base_path'])#
        expurl2="%s://%s%sWebResource.axd?d="%(ob['scheme'],domain,ob['base_path'])
        response,content=requestUrl(http,expurl1,ob['task_id'],ob['domain_id'])#500
        response1,content=requestUrl(http,expurl2,ob['task_id'],ob['domain_id'])#404
        if response['status']=='500' and response1['status']=='404':
            
            request = getRequest(expurl1)
            response = getResponse(response)
            result.append(getRecord(ob,expurl1,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:modoer1_0sqlinjectionscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:paddingoracleattack.py, run_domain function :" + str(e))
    return result