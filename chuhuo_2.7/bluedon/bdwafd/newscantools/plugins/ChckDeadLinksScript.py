#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import httplib2
import urlparse
import re
def run_url(http,ob,item):
    try:
        result=[]
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
            response,content=requestUrl(http,item['url']+"?"+item['params'],ob['task_id'],ob['domain_id'])
            
            if response['status']!='200':
                request=getRequest(item['url']+"?"+item['params'],'GET')
                
                response=getResponse(response,"")
                
                result.append(getRecord(ob,item['url']+"?"+item['params'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:LocalFileIncludeScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:LocalFileIncludeScript.py, run_url function :" + str(e)+", url:"+item['url']+"?"+item['params'])
    #end try
    return result                    
                
                 
     
            
            
   
    