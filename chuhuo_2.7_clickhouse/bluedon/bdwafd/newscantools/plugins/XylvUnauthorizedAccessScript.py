﻿#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]                               
        detail=u''
        detail=detail.encode('utf8')
        domain=ob['domain']
        #url="/celive/js/include.php?cmseasylive=1111&departmentid=0"
        url="admin/index1.asp"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        if content.find("cs.asp?action=tops")>=0 and response['status']=='200':
            request = getRequest(geturl)
            #request = getRequest(geturl1)
            response = getResponse(response)
            result.append(getRecord(ob,ob['scheme']+"://"+domain,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:XYLVUnauthorizedaccessSCRIPT.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:XYLVUnauthorizedaccessSCRIPT.py, run_domain function :" + str(e))
    return result