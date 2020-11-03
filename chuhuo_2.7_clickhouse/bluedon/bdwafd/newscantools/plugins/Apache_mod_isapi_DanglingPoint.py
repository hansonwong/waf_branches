#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def getVersion(server): # only in Windows
    #Apache/2.2.6 (Win32)  
    try:
        if server.find('win32') < 0 and server.find('windows') < 0:
            return False
        big,middle,small = map(int,server.split(' ')[0].split('/')[1].strip().split('.'))
        if big == 2 and middle == 2 and small <=14:
            return True
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
        if res and res.has_key('server') and res['server'].lower().find('apache') >= 0 and getVersion(res['server'].lower()):
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail+"当前版本:"+res['server'].split(' ')[0].split('/')[1],request,response))
    except Exception,e:
        logging.getLogger().error("File:Apache_mod_isapi_DanglingPoint.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:Apache_mod_isapi_DanglingPoint.py, run_domain function :" + str(e))
    #end try

    return list
#end def
