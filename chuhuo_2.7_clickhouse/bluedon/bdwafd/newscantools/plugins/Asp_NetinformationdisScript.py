#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import urlparse
import re
def Getkey(url):
    try:
        
    
        parse=urlparse.urlparse(url)
        urls=parse.path
        if urls=="" or urls=="/":
            return url
        #end if 
        urls=url.split("/")
        urls=urls[len(urls)-1]
        if urls=="" or urls.find(".")<0:
            return  url
        else:
            return ""    
        #end if  
    except Exception,e:
        logging.getLogger().error(" ASPnetinformaitondis.getkey() Exception(aspnetinformationdis.py):" + str(e))
        return ""
    #end if 
def run_url(http,ob,item):
    try:
        result=[]
        url=item['url']
        detail=''
        r,c=requestUrl(http,item['url'],ob['task_id'],ob['domain_id'])
        if r and r.has_key('x-powered-by') and r['x-powered-by']=='ASP.NET':
            expurl="/~nvs.aspx"
            
            
            geturl=Getkey(url)
            if geturl!="":
                gettrueurl="%s%s"%(geturl,expurl)
                response,content=requestUrl(http,gettrueurl,ob['task_id'],ob['domain_id'])
                m=re.search(r'([a-zA-Z]:\\)(.{0,25}\\)',content)
                if m:
                    if ob['isstart']=='1':
                        detail="%s验证性扫描结果：\n网站绝对路径：%s"%(detail,m.group(0))
                    request=getRequest(gettrueurl,'GET')
                
                    response=getResponse(response,"")
                
                    result.append(getRecord(ob,url,ob['level'],detail,request,response))
                #end if 
            #end if 
        else:
            return result
        #end if
    except Exception,e:
        logging.getLogger().error("File:aspnetinformationdis.py, run_url function :" + str(e) +",url:"+url+ ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:aspnetinformationdis.py, run_url function :%s , url:%s" % (str(e),url))
    #end try
    return result      
                