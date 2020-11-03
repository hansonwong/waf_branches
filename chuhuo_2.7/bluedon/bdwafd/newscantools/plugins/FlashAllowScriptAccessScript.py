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
        if res and res.has_key('status') and res['status'] == '200' and content.find('param') > 0 and (content.find('allowScriptAccess') > 0 or content.find('AllowScriptAccess') > 0):
            match = re.findall(r"<(\s*)param(\s+)name(\s*)=(\s*)('|\")allowscriptaccess\5(\s+)value(\s*)=(\s*)('|\")always\9(\s*)/(\s*)>",content,re.I|re.DOTALL)
            if match and len(match) > 0:
                detail = "Flash 显示程序接受 AllowScriptAccess 之类的对象参数。当父 SWF 装入子 SWF，并确定被装入的 SWF 与进行装入的 SWF 是否对 Web 页面脚本有相同的访问权时，会使用 AllowScriptAccess 参数。如果参数设为“always”，父项从任何域中装入的 SWF 都可能将脚本注入托管 Web 页面中。"
                request = getRequest(url)
                response = getResponse(res)
                output = "<param name=%sallowscriptaccess%s value=%salways%s />" % (match[0][4],match[0][4],match[0][8],match[0][8])
                result.append(getRecord(ob,url,ob['level'],detail,request,response,output))
            #end if
        #end if
        
        return result
    except Exception,e:
        logging.getLogger().error("File:FlashAllowScriptAccessScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FlashAllowScriptAccessScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def

