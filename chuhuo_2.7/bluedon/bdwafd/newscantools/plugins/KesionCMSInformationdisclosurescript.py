#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]                               
        detail=u''
        detail=detail.encode('utf8')
        domain=ob['domain']
        url="plus/Ajaxs.asp?action=GetRelativeItem&Key=%25"
        url1="user/reg/regajax.asp?action=getcityoption&province=%25"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
        geturl1="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url1)       
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
#        content=content.decode('gb2312').encode('utf8')
        if content.find("Microsoft VBScript")>=0 and content.find("800a000d")>=0:
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
        else:
            response,content=requestUrl(http,geturl1,ob['task_id'],ob['domain_id'])
            if content.find("Microsoft VBScript")>=0 and content.find("800a000d")>=0:
                request = getRequest(geturl1)
                response = getResponse(response)
                result.append(getRecord(ob,geturl1,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:kesionCMSinformationdisclosorce.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:kesionCMSinformationdisclosorce.py, run_domain function :" + str(e))
    return result