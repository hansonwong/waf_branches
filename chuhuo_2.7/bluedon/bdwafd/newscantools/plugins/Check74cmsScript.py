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
            logging.getLogger().error(" check74cmsscript.getkey() Exception(DirectoryTraversal.py):" + str(e))
            return ""

def Setflag(newflag):
    global flag
    flag=newflag

def run_url(http,ob,item):
    try:
        result=[]
        expurl="/admin/admin_login.php"
        expurl1="/admin/css/common.css"
        detail=u''
        url=item['url']
        geturl=Getkey(url)
        #logging.getLogger().error("geturl"+geturl)
        if geturl!="":
            gettrueurl="%s%s"%(geturl,expurl)
            gettrueurl1="%s%s"%(geturl,expurl1)
            response,content=requestUrl(http,gettrueurl,ob['task_id'],ob['domain_id'])
            response1,content1=requestUrl(http,gettrueurl1,ob['task_id'],ob['domain_id'])
#            content=content.decode("gb2312").encode("utf8")
#            logging.getLogger().error( content)
            flag=0
            if ((content.find("74CMS")>=0 or content.find("74cms")>=0 or content.find("Powered by 74CMS")>=0) and response['status']=='200' )or(content1.find(".admin_left_box  li a {color: #666666;text-decoration:none;background-image: url(../images/admin_left_li.gif)")>=0 and response1['status']=='200' and Setflag(2)):

                if flag==2:
                    request=getRequest(gettrueurl1,'GET')
                
                    response=getResponse(response1,"")
                    gettrueurl=gettrueurl1
                else:
                    request=getRequest(gettrueurl,'GET')
                    response=getResponse(response,"")

                
                result.append(getRecord(ob,gettrueurl,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:Check74cmsScript.py, run_url function :" + str(e) +",url:"+url+ ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:Check74cmsScript.py, run_url function :" + str(e) +",url:"+url)
    #end try
    return result      
            