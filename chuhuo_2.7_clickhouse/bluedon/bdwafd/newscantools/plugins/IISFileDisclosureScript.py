#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u"IIS是由微软公司提供的基于运行Microsoft Windows的互联网基本服务。攻击者可以利用一个包含\"~\"的get请求,来让服务器上的文件和文件夹被泄漏。"
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "%2F*~1.*%2Fx.aspx"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '404':
            url = "%s://%s/" % (ob['scheme'],domain)
            url += "%2Fooxx*~1.*%2Fx.aspx"
            res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
            if res['status'] == '400':
                request = getRequest(url)
                response = getResponse(res)
                list.append(getRecord(ob,url,ob['level'],detail,request,response))
            #end if
        #end if
    except Exception,e:
        logging.getLogger().error("File:IISFileDisclosureScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:IISFileDisclosureScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def

