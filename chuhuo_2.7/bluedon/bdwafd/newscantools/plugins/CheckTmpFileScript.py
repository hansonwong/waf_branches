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
        if url.find('.php') < 0 and url.find('.asp') < 0 and url.find('.aspx') < 0 and url.find('.jsp') < 0 and url.find('.do') < 0:
            return []
        #end if
        
        detail = "Web 服务器通常没有这些文件扩展名的特定处理程序。 如果攻击者请求这类文件，文件内容会直接发送到浏览器。"
        list = ['.bak','.sav','.old','~']
        relist = ["%s%s" % (url,row) for row in list]
        relist = valid_urls(ob['domain'], relist)
        if not relist:
            return result
        for new_url in relist:
            #new_url = "%s%s" % (url,row)
            res, content = requestUrl(http,new_url,ob['task_id'],ob['domain_id'])
            if res and res.has_key('status') and res['status'] == '200' and res.has_key('content-type') and res['content-type'] != '' and content.find("<%") >= 0:
                request = getRequest(new_url)
                response = getResponse(res)
                result.append(getRecord(ob,new_url,ob['level'],detail,request,response))
            #end if
        #end for
        
        if len(result) >= 2:
            return []
        else:
            return result
        #end if
        
        return result
    except Exception,e:
        logging.getLogger().error("File:CheckTmpFileScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CheckTmpFileScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def

