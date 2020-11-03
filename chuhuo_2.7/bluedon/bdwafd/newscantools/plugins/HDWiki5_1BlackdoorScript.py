#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
       
        expurl="%s%s"%(url,"style/default/admin/open.gif")
        expurl1="%s%s"%(url,"baike/style/default/admin/open.gif")
        expurl2="%s%s"%(url,"wiki/style/default/admin/open.gif ")
        #r,c=http.request(expurl)
        r,c=yx_httplib2_request(http,expurl)
        
        
        #print c
        if r['status']=='200' and c.find("<?php @eval")>=0:
            request = getRequest(expurl1)
            response = getResponse(response)
            if ob['isstart']=='1':
                list.append(getRecord(ob,expurl,ob['level'],detail+"验证性扫描结果：\n"+"在图片中发现php代码：<?php @eval",request,response))
            else:
                list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
        else:
            #r1,c1=http.request(expurl1)
            r1,c1=yx_httplib2_request(http,expurl1)
            if r1['status']=='200' and c1.find("<?php @eval")>=0:
                
                request = getRequest(expurl1)
                response = getResponse(response)
                if ob['isstart']=='1':
                    list.append(getRecord(ob,expurl1,ob['level'],detail+"验证性扫描结果：\n"+"在图片中发现php代码：<?php @eval",request,response))
                else:
                    list.append(getRecord(ob,expurl1,ob['level'],detail,request,response))
            else:
                #r2,c2=http.request(expurl2)
                r2,c2=yx_httplib2_request(http,expurl2)
                if r2['status']=='200' and c2.find("<?php @eval")>=0:
                
                    request = getRequest(expurl1)
                    response = getResponse(response)
                    if ob['isstart']=='1':
                        list.append(getRecord(ob,expurl1,ob['level'],detail+"验证性扫描结果：\n"+"在图片中发现php代码：<?php @eval",request,response))
                    else:
                        list.append(getRecord(ob,expurl1,ob['level'],detail,request,response))
                
    except Exception,e:
        logging.getLogger().error("File:hdwiki5.1blackdoorscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:hdwiki5.1blackdoorscript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def