#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
def run_url(http,ob,item):
    list = []
    detail = u''
    try:
        if item['method']=='get':
           
            if item['params'].lower().find("user-space")>=0:
                print item['url']
                expurl="%s/%s\\"%(item['url'],item['params'])
                print expurl
                res, content = requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        #print content
                if content.find('MySQL Query Error')>=0:
                    request = getRequest(expurl)
                    response = getResponse(res)
                    list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:hdwikiv5_1sqlinjection.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:hdwikiv5_1sqlinjection.py, run_url function :" + str(e)+", url: %s/%s\\"%(item['url'],item['params']))
    #end try
    
    return list
#end def 