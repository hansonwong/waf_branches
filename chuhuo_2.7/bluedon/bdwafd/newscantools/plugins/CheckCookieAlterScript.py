#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_url(http,ob,item):
    try:
        result = []
        if item['method'] != 'get':
            return []
        #end if
        url = item['url']
        params = item['params']
        if params != "":
            url = "%s?%s" % (url,params)
        #end if
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res and res.has_key('status') and res['status'] == '200' and res.has_key('content-type') and res['content-type'] != '' and content.find("document.cookie") >= 0:
            list = content.replace("\r\n","\n").split("\n")
            for row in list:
                if row.find("document.cookie") < 0:
                    continue
                #end if
                match = re.findall(r"document.cookie(\s*)=",row,re.I)
                if match and len(match) > 0:
                    detail = "Cookie 是在客户端创建的。代码用于操纵站点的 cookie。可以将实施 cookie 逻辑的功能移至客户端（浏览器）。这样一来，攻击者就能发送其本无权发送的 cookie。"
                    request = getRequest(url)
                    response = getResponse(res)
                    result.append(getRecord(ob,url,ob['level'],detail,request,response,""))
                    break
                #end if
            #end for
        #end if
        
        return result
    except Exception,e:
        logging.getLogger().error("File:CheckCookieAlterScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CheckCookieAlterScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def

