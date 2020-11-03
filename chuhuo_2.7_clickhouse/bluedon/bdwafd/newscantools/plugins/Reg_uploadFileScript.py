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
        detail=u''
        detail=detail.encode('utf8')
        path="reg_upload.asp"
        geturl="%s%s"%(url,path)
        res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('<form name="form" method="post" action="upfile.asp" enctype="multipart/form-data" >')>=0:
            request = getRequest(geturl)
            response = getResponse(res)
            result.append(getRecord(ob,url,ob['level'],detail,request,response))
        return result
    except Exception, e:
        logging.getLogger().error("File:Reg_uploadFileScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:Reg_uploadFileScript.py, run_domain function :" + str(e))
        return result

