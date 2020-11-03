#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *


def run_url(http,ob,item):
    try:
        result=[]
        if ob['rfi_url']=='':
            return result
        url=item['url']
        detail=u''
        detail=detail.encode('utf8')
        parse=urlparse.urlparse(url)
        path=parse.path
        if path=="" or path=="/":
            return result
       
        if item['params'] == "":
            return result
    #end if
        if item['method'] == 'get':
            query=""
            response1,content1=requestUrl(http,item['url']+"?"+item['params'],ob['task_id'],ob['domain_id'])
            if item['params'].find("&")>=0:
                
                params= item['params'].split("&")
                
                #logging.getLogger().error(item['url']+"?"+item['params'])
                #logging.getLogger().error(content1)
                #logging.getLogger().error("="*100)
                for i in range(0,len(params)):
                    #logging.getLogger().error(i)
                    query=""
                    for j in range(1,len(params)+1):
                        query=params[len(params)-i-j]+"&"+query
                        #logging.getLogger().error(query)
                    key=query[0:query.rfind("=")]  
                    geturl = "%s?%s" % (item['url'],key)
            else:
                geturl=item['url']+"?"+item['params']
                if geturl.find("=")>=0:
                    geturl=geturl.split("=")[0]
                    #logging.getLogger().error(geturl)
                else:
                    return result
                
                #logging.getLogger
            gettrueurl="%s=%s"%(geturl,ob['rfi_url'])
            response,content=requestUrl(http,gettrueurl,ob['task_id'],ob['domain_id'])
            response1,content1=requestUrl(http,url,ob['task_id'],ob['domain_id'])
            if content.find(ob['rfi_keyword'].encode('utf8'))>=0 and content1.find(ob['rfi_keyword'].encode('utf8'))<0:
                request=getRequest(gettrueurl,'GET')
                response=getResponse(response,"")
                result.append(getRecord(ob,gettrueurl,ob['level'],detail,request,response))
            else:
                gettrueurl="%s=%s%%00"%(geturl,ob['rfi_url'])
                response,content=requestUrl(http,gettrueurl,ob['task_id'],ob['domain_id'])
                response1,content1=requestUrl(http,url,ob['task_id'],ob['domain_id'])
                if content.find(ob['rfi_keyword'].encode('utf8'))>=0 and content1.find(ob['rfi_keyword'].encode('utf8'))<0:
                    request=getRequest(gettrueurl,'GET')
                    response=getResponse(response,"")
                    result.append(getRecord(ob,gettrueurl,ob['level'],detail,request,response))
                   
    except Exception,e:
        logging.getLogger().error("File:RmoteFileIncludeScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:RmoteFileIncludeScript.py, run_url function :" + str(e))
    #end try
    return result                    
                
                 
            
            
            
   
    