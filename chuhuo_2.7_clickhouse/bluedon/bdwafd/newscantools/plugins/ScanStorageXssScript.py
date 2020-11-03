#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
import json
import urlparse
import re
       
def run_url(http,ob,item):
    
    result = []
    detail=""
    domain=ob['domain']
    try:
        isstart='0'
        parse=urlparse.urlparse(item['url'])
        path=parse.path
        path=path.lower()
        if (path.find(".css")>=0 or path.find(".doc")>=0 or path.find(".txt")>=0 or path.find(".pdf")>=0 or path.find(".js")>=0)and path.find("jsp")<0:
            
            return result
        if item['params']!='':
            
            url="%s?%s"%(item['url'],item['params'])
        else:
            url=item['url']
        #end if 
        if item['method']=='get':
            #response,content=http.request(url)
            response,content=yx_httplib2_request(http,url)
            m = re.search(r"<script>alert\((\d{1,10})\)",content,re.I)
            if m:
                request = getRequest(url,"GET")
                
                response = getResponse(response)
                
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
            #END IF 
        #END IF 
            
    except Exception, e:
        logging.getLogger().error("File:scanstoragexsscript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:scanstoragexsscript.py, run_url function :" + str(e))
    return result

            