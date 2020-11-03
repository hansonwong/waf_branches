#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def getVersion(server):
    #server='PHP/5.2.5' / 'server': 'Apache/2.2.6 (Win32) PHP/5.2.5'
    try:
        big,middle,small = map(int,server.split(' ')[-1].split('/')[1].strip().split('.'))
        if big == 5 and ((middle == 2 and small <=17) or (middle == 3 and small <=5)):
            return True
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
        if res.has_key('x-powered-by') and res['x-powered-by'].lower().find('php') >= 0 and getVersion(res['x-powered-by']):
            server = res['x-powered-by']
        elif res.has_key('server') and res['server'].lower().find('php') >= 0 and getVersion(res['server']):
            server = res['server']
        else:
            return list
        request = getRequest(url)
        response = getResponse(res)
        list.append(getRecord(ob,url,ob['level'],detail+"当前版本:"+server.split(' ')[-1].split('/')[1],request,response))
    except Exception,e:
        logging.getLogger().error("File:PhpParseString2float.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:PhpParseString2float.py, run_domain function :" + str(e))
    #end try

    return list
#end def

def test():
    import httplib2
    http=httplib2.Http()
    res,content=http.request("http://www.roong-aroon.ac.th")
    print res,content

test()