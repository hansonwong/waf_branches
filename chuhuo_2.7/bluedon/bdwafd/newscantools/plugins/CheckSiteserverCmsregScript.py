#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]                               
        detail=u''
        detail=detail.encode('utf8')
        domain=ob['domain']
        url1="UserCenter/register.aspx"
        url2="UserCenter/login.aspx"
        #http://www.esou.org.cn
        #http://www.yy-edu.net
        geturl1="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url1)
        geturl2="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url2)
        response1,content1=requestUrl(http,geturl1,ob['task_id'],ob['domain_id'])
        response2,content2=requestUrl(http,geturl2,ob['task_id'],ob['domain_id'])
        if response1.has_key("status") and response1['status']=='200' and content1.find("siteserver/validateCode2.aspx")>=0 and response2.has_key("status") and response2['status']=='200' and content2.find("siteserver/validateCode2.aspx")>=0:
            request = getRequest(geturl1)
            response = getResponse(response1)
            result.append(getRecord(ob,ob['scheme']+"://"+domain,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:checksiteserverregcms.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:checksiteserverregcms.py, run_domain function :" + str(e))
    return result

