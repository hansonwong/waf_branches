#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def getVersion(server):
    #'nginx/0.6.36'
    try:
        big,middle,small = map(int,server.split('/')[-1].strip().split('.'))
        if big > 0:
            return False
        if (middle == 5 and small < 38) or (middle == 6 and small < 39) or (middle == 7 and small < 62) or (middle == 8 and small < 15):
            return True
        else:
            return False
    except:
        return False
    #end try
#end def


def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u'该漏洞通过版本信息判断，可能存在误报。\n'
        detail = detail.encode('utf8')

        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res and res.has_key('server') and res['server'].lower().find('nginx') >= 0 and getVersion(res['server']):
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail+"当前版本:"+res['server'].split('/')[-1],request,response))
    except Exception,e:
        logging.getLogger().error("File:NginxBufferUnderflowScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:NginxBufferUnderflowScript.py, run_domain function :" + str(e))
    #end try

    return list
#end def