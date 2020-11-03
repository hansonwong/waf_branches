#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
import re
import urllib

_xforwardedhost = None
def run_url(http,ob,item):
    result = []
    try:
        detail = u""
        url = urllib.unquote(item['url'])
        host = "evilXForwardedHost.com"
        header = {"X-Forwarded-Host": host,"Connection":"Keep-alive","User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5"}
#       res, content = http.request(url,headers=header)
        res, content = yx_httplib2_request(http,url,headers=header)
        if res and content.find(host) != -1:
            
            request = getRequest(url,headers=header)
            response = getResponse(res)
            result.append(getRecord(ob,item['url'],ob['level'],detail,request,response))
        #end if
    except Exception,e:
        logging.getLogger().error("File:HostHeaderAttack.py, run_url function :%s, task id:%s, scheme:%s, domain:%s, base_path:%s, url:%s" % (str(e),ob['task_id'],ob['scheme'],ob['domain'],ob['base_path'],item['url']))
        write_scan_log(ob['task_id'],ob['domain_id'],"File:HostHeaderAttack.py, run_url function :%s , url:%s" % (str(e),item['url']))
    #end try
    return result
#end def