#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
import re

def run_url(http,ob,item):
    result = []
    try:
        if item['method'] != 'get':
            return []
        #end if      
        url = item['url']
        http.httlib2_set_follow_redirects(False)
        #res, content = http.request(url)
        res, content = yx_httplib2_request(http,url)
        if res and res.has_key('status') and res['status'] in ['301','302'] and re.search(r"<(\s*)form(.+?)>(.+?)<(\s*)/(\s*)form(\s*)>",content,re.I|re.DOTALL):
            detail = u""
            request = getRequest(url)
            response = getResponse(res)     
            result.append(getRecord(ob,url,ob['level'],detail,request,response))
        #end if
    except Exception,e:
        logging.getLogger().error("File:RedirectPageFoundFormScript.py, run_url function :%s, task id:%s, scheme:%s, domain:%s, base_path:%s, url:%s" % (str(e),ob['task_id'],ob['scheme'],ob['domain'],ob['base_path'],item['url']))
        write_scan_log(ob['task_id'],ob['domain_id'],"File:RedirectPageFoundFormScript.py, run_url function :%s, url:%s" % (str(e),item['url']))
    #end try
    http.httlib2_set_follow_redirects(True)
    return result
#end def