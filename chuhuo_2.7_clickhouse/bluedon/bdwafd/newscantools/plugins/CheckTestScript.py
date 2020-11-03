#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    result = []
    try:
        scheme = ob['scheme']
        domain = ob['domain']
        base_path = ob['base_path']

        list = ['test.html','test.htm','test.php','test.asp','test.aspx','test.do','test.cfm','test.cgi']

        count = 0
        for row in list:
            if checkFileTypeStatus(scheme,domain,base_path,row[4:],"HEAD") == False:
                continue
            url = "%s://%s%s%s" % (scheme,domain,base_path,row)
#           res, content = http.request(url,"HEAD")
            res, content = yx_httplib2_request(http,url,"HEAD")
            if res and res.has_key('status') and res['status'] == '200' and res.has_key('content-type') and res['content-type'] != '':
                detail = "检测到应用程序测试脚本 %s，可能包含敏感信息。" % (row)
                request = getRequest(url)
                response = getResponse(res)
                output = ""
                count += 1
                result.append(getRecord(ob,url,ob['level'],detail,request,response,output))
            #end if
        #end for

        if count >= 3:
            return []
        else:
            return result
        #end if

    except Exception,e:
        logging.getLogger().error("File:CheckTestScrit.py, run_domain function :%s, task id:%s, scheme:%s, domain:%s, base_path:%s" % (str(e),ob['task_id'],ob['scheme'],ob['domain'],ob['base_path']))
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CheckTestScrit.py, run_domain function :"+str(e))
    #end try

    return result
#end def



