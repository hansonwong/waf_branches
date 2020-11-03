#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_url(http,ob,item):
    try:
        result = []
        
        if item['method'] != 'get':
            return []
        #end if
        if item['params'] != '':
            return []
        #end if
        if item['url'][-1] != "/":
            return []
        #end if
        
        url = item['url']
        #res, content = http.request(url,"OPTIONS")
        res, content = yx_httplib2_request(http,url,"OPTIONS")
        if res and res.has_key('status') and res['status'] in ['200','403'] and ((res.has_key('allow') and res['allow'].lower().find("put") >= 0) or (res.has_key('public') and res['public'].lower().find('put') >= 0)):
            detail = "该目录支持PUT请求，可能导致网站被上传木马，导致网站被破坏和泄露。"
            request = getRequest(url,"OPTIONS")
            response = getResponse(res)
            
            put_url = "%snvs_test.txt" % (url)
            #http.request(put_url,"PUT","nvs__test")
            yx_httplib2_request(http,put_url,"PUT","nvs__test")
            #res, content = http.request(put_url)
            res, content = yx_httplib2_request(http,put_url)
            if res and res.has_key('status') and res['status'] == '200' and content.find('nvs__test') >= 0:
                output = "请求URL：%s 将返回字符串：nvs__test" % (put_url)
                result.append(getRecord(ob,url,ob['level'],detail,request,response,output))
            #end if
        #end if
        
        return result
        
    except Exception,e:
        logging.getLogger().error("File:PutHttpScript.py, run_url function :%s, task id:%s, scheme:%s, domain:%s, base_path:%s, url:%s" % (str(e),ob['task_id'],ob['scheme'],ob['domain'],ob['base_path'],item['url']))
        write_scan_log(ob['task_id'],ob['domain_id'],"File:PutHttpScript.py, run_url function :%s, url:%s" % (str(e),item['url']))
        return []
    #end try    
#end def



