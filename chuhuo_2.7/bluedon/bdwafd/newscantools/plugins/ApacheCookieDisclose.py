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
        header={"Host":domain,"Connection":"Keep-alive","User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5","cookie":"nvscan:"+"nvscan"*3000}
#       res, content = http.request(url,headers=header)
        res, content = yx_httplib2_request(http,url,headers=header)
        if res['status'] == '400' and content.find('nvscan'*5) > 0:
            request = getRequest(url,headers=header)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:ApacheCookieDisclose.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:ApacheCookieDisclose.py, run_domain function :" + str(e))
    #end try
    return list
#end def