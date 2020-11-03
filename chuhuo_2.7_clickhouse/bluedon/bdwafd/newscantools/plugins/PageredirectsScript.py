#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import httplib2
import urlparse


def run_url(http,ob,item):
    try:     
        result=[]
        expurl="http://www.baidu.com"
        url=item['url']
        detail=u''
        detail=detail.encode('utf8')
        parse=urlparse.urlparse(url)
        path=parse.path
        if path=="" or path=="/":
            return result
        
        #end if 
        if item['params'] == "":
            return result
        #end if
        if item['method'] == 'get':
            query=""
            if item['params'].find("&")>=0:
                params= item['params'].split("&")
                for i in range(0,len(params)):
                    query=""
                    for j in range(1,len(params)):
                        query=params[len(params)-i-j]+"&"+query
    
                    key=query[0:query.rfind("=")]
                    geturl = "%s?%s" % (item['url'],key)
                    #end for
                #end for
                    
            else:
                geturl=item['url']+"?"+item['params']
                if geturl.find("=")>=0:
                    geturl=geturl.split("=")[0]  
                else:
                    return result
                #end if  
            #end if 
            gettrueurl="%s=%s"%(geturl,expurl)
            response,content=requestUrl(http,gettrueurl,ob['task_id'],ob['domain_id'])
#            logging.getLogger().error(response)
#            logging.getLogger().error(content)
            if response.has_key('location') and response['location']=="http://www.baidu.com":
                request=getRequest(gettrueurl,'GET')
                response=getResponse(response,"")
                #print"dd"
                #result.append(getRecord(ob,url,ob['level'],detail,request,response))
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:pageredirectsscript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:pageredirectsscript.py, run_url function :" + str(e))
    #end try
    return result