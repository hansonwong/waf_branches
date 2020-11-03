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
            logging.getLogger().error("mysql MysqlGetUrl Exception(DirectoryTraversal.py):" + str(e))
            return ""
def run_url(http,ob,item):
    try:
        result=[]
        expurl="/admin/adduser.asp"
        expurl1="/adduser1.asp"
        detail=u''
        url=item['url']
        geturl=Getkey(url)
        #logging.getLogger().error("geturl"+geturl)
        if geturl!="":
            gettrueurl="%s%s"%(geturl,expurl)
            gettrueurl1="%s%s"%(geturl,expurl1)
            response,content=requestUrl(http,gettrueurl,ob['task_id'],ob['domain_id'])
#            content=content.decode("gb2312").encode("utf8")
            #logging.getLogger().error( content)
            if (content.find("document.FrmAddLink.username.value.indexOf")>=0 or content.find("<body onload=\"javascript:window.close()\"></body>")>=0)and response['status']!='404':

                request=getRequest(gettrueurl,'GET')

                response=getResponse(response,"")

                result.append(getRecord(ob,gettrueurl,ob['level'],detail,request,response))
            else:
                response,content=requestUrl(http,gettrueurl1,ob['task_id'],ob['domain_id'])
#            content=content.decode("gb2312").encode("utf8")
            #logging.getLogger().error( content)
                if (content.find("document.FrmAddLink.username.value.indexOf")>=0 or content.find("<body onload=\"javascript:window.close()\"></body>")>=0) and response['status']!='404':

                    request=getRequest(gettrueurl1,'GET')

                    response=getResponse(response,"")

                    result.append(getRecord(ob,gettrueurl1,ob['level'],detail,request,response))


    except Exception,e:
        logging.getLogger().error("File:CheckCyyJsCRIPT.py, run_url function :" + str(e) +",url:"+url+ ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CheckCyyJsCRIPT.py, run_url function :" + str(e))
    #end try
    return result
