#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_url(http,ob,item):
    try:
        result = []
        if item['method'] != 'post':
            return []
        #end if
        
        parse = urlparse.urlparse(item['url'])
        params = item['params']
        
        if params.find("{\"type\":\"text\"") >= 0 and params.find("{\"type\":\"password\"") >= 0 and parse[0] == 'http': 
            url = item['refer']
            request = getRequest(url)
            res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
            response = getResponse(res)
            detail = "检测到登陆表单，但是没有使用https。"
            result.append(getRecord(ob,url,ob['level'],detail,request,response))
            
            return result
        else:
            return []
        #end if
    except Exception,e:
        logging.getLogger().error("File:JieMiDengLuScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:JieMiDengLuScript.py, run_url function :" + str(e))
        return []
    #end try    
#end def

