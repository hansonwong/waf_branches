#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = ""
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "index.php?ac=search&at=list&att[a]=nvs"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if content.find('ESPCMS SQL Error')>=0 and res['status']!='404':
            request = getRequest(url,'GET')
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:EspcmssearchSqlinjectionsCRIPT.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:EspcmssearchSqlinjectionsCRIPT.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def