#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = ""
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "group/search.php?sad=g&keyword=%cf'"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if content.find('Error sql:')>=0:
            request = getRequest(url,'GET')
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain']+ob['base_path'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:dedecms2007sqlinjection1script.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:dedecms2007sqlinjection1script.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def