#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *


def run_url(http,ob,item):
    detail=""
    detail=detail.encode('utf8')
    list=[]
    
    try:
        url=item['url']       
        if url.find(".gif")<0 and url.find(".jpg")<0:
            return list
        explist=['/c.php','%00.php']       
        for exp in explist:
            expurl="%s%s"%(item['url'],exp)
            #response, content = http.request(expurl)
            response, content = yx_httplib2_request(http,expurl)
            if response['status']=='200' and response['content-type']=='text/html':
                request = getRequest(expurl)
                response = getResponse(response)
                list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
                break
        return list

    except Exception,e:
        logging.getLogger().error("File:NginxParsingVulnerabilities.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:NginxParsingVulnerabilities.py, run_url function :" + str(e))            
        return list

