#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_url(http,ob,item):
    try:  
        result=[]
        if ob['site_type'] != 'asp':
            return result      
        url=item['url']
        if url[-1] !='/' or item['method'] !='get':
            return result
        if url.count('/') >5:
            return result        
        detail=u''
        detail=detail.encode('utf8')        
        pathlist=['install/','about/_notes/dwsync.xml','admin/_Style/_notes/dwsync.xml','apply/_notes/dwsync.xml','config/_notes/dwsync.xml','fckeditor/fckconfig.js','gbook/_notes/dwsync.xml','inc/_notes/dwsync.xml','plug/comment.html']
        for path in pathlist:			            
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("aspcms")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindAspCmsScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindAspCmsScript.py, run_domain function :" + str(e))
        return result

