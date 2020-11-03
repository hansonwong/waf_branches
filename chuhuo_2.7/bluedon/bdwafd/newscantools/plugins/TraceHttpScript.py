#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    try:
        scheme = ob['scheme']
        domain = ob['domain']
        base_path = ob['base_path']
    
        url = "%s://%s%s" % (scheme,domain,base_path)
        #res, content = http.request(url,"OPTIONS")
        res, content = yx_httplib2_request(http,url,"OPTIONS")
        
        list = []
        detail = u"该域名支持TRACE请求类型"
        detail = detail.encode("utf8")
        
        if res and res.has_key('status') and res['status'] == '200' and res.has_key('allow') and res['allow'].lower().find("trace") >= 0:
            request = getRequest(url,"OPTIONS")
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))

        else:
            traceurl = url + '<script>alert(333)</script>'
            #res, content = http.request(traceurl,'TRACE')
            res, content = yx_httplib2_request(http,traceurl,'TRACE')
            if res and res.has_key('status') and res['status'] == '200' and content.lower().find('alert(333)') >=0:
                request = getRequest(traceurl,"TRACE")
                response = getResponse(res)
                list.append(getRecord(ob,url,ob['level'],detail,request,response))
        #end if
        
        return list
    except Exception,e:
        logging.getLogger().error("File:TraceHttpScript.py, run_domain function :%s, task id:%s, scheme:%s, domain:%s, base_path:%s" % (str(e),ob['task_id'],ob['scheme'],ob['domain'],ob['base_path']))  
        write_scan_log(ob['task_id'],ob['domain_id'],"File:TraceHttpScript.py, run_domain function :"+str(e))      
    #end try
    
    return []
#end def



