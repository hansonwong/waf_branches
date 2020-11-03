#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import httplib2
import urlparse

def Getkey(url):
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
                return ""     
    except Exception,e:
            logging.getLogger().error(" check74cmsloginscript.getkey() Exception(DirectoryTraversal.py):" + str(e))
            return ""
def run_url(http,ob,item):
    try:
        result=[]
        expurl="/admin/admin_login.php"
        detail=u''
        url=item['url']
        geturl=Getkey(url)
        #logging.getLogger().error("geturl"+geturl)
        if geturl!="":
            gettrueurl="%s%s"%(geturl,expurl)
            response,content=requestUrl(http,gettrueurl,ob['task_id'],ob['domain_id'])
#            content=content.decode("gb2312").encode("utf8")
#            logging.getLogger().error( content)
            if (content.find("74CMS")>=0 or content.find("74cms")>=0 or content.find("Powered by 74CMS")>=0) and response['status']=='200':
                

                request=getRequest(gettrueurl,'GET')
                
                response=getResponse(response,"")
                
                result.append(getRecord(ob,gettrueurl,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:check74cmsloginscript.py, run_url function :" + str(e) +",url:"+url+ ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:check74cmsloginscript.py, run_url function :" + str(e) +",url:"+url)
    #end try
    return result      
            