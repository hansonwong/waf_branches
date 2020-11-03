#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    result = []
    try:
        scheme = ob['scheme']
        domain = ob['domain']
        base_path = ob['base_path']
    
        url = "%s://%s%s%s" % (scheme,domain,base_path,"robots.txt")
#       res, content = http.request(url)
        res, content = yx_httplib2_request(http,url)
        
        if res and res.has_key('status') and res['status'] == '200' and res.has_key('content-type') and res['content-type'] != '' and content != "":
            content_low = content.lower()
            if content_low.find('user-agent') >= 0 or content_low.find('disallow') >= 0:
                detail = "Web 服务器或应用程序服务器是以不安全的方式配置。"
                request = getRequest(url)
                response = getResponse(res)
                if len(content) > 200:
                    output = "%s......" % (content[0:200])
                else:
                    output = content
                #end if
                result.append(getRecord(ob,url,ob['level'],detail,request,response,output))
            #end if
        #end if
        
    except Exception,e:
        logging.getLogger().error("File:CheckRobotsScript.py, run_domain function :%s, task id:%s, scheme:%s, domain:%s, base_path:%s" % (str(e),ob['task_id'],ob['scheme'],ob['domain'],ob['base_path']))   
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CheckRobotsScript.py, run_domain function :"+str(e))     
    #end try
    
    return result
#end def



