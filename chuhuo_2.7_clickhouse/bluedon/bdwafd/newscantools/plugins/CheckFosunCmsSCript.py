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
        url += "customform/CustomFormJS.asp?CustomFormID=%27&FormStyleID=%27"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '500' and content.find('Microsoft JET Database Engine')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain']+ob['base_path'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:checkfosuncmsscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:checkfosuncmsscript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def