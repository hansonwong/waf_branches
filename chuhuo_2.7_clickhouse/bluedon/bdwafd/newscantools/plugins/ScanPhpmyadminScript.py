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
        phpmyadminUrl=["phpMyAdmin/index.php","phpmyadmin/index.php","pma/index.php"]
        for exp in phpmyadminUrl:
            expurl= "%s%s"%(url,exp)
            res,content=requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
            if res['status']=='200' and content.find('<title>phpMyAdmin')>=0:
                request=getRequest(expurl)
                response=getResponse(res)
                list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
                break
        '''
        expurl= "%s%s"%(url,"/phpMyAdmin/index.php")
        expurl1="%s%s"%(url,"/pma/index.php")
        res, content = requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('<title>phpMyAdmin')>=0:
            request = getRequest(expurl)
            response = getResponse(res)
            list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
        else:
            res, content = requestUrl(http,expurl1,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find('<title>phpMyAdmin')>=0:
                request = getRequest(expurl1)
                response = getResponse(res)
                list.append(getRecord(ob,expurl1,ob['level'],detail,request,response))
       '''

    except Exception,e:
        logging.getLogger().error("File:scanphpmyadminscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:scanphpmyadminscript.py, run_domain function :" + str(e))
    #end try

    return list
#end def