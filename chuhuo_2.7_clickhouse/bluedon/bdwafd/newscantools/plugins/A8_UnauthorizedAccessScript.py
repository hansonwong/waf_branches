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
        url += "seeyon/management/status.jsp"
#       res1, content1 = http.request(url)
        res1, content1 = yx_httplib2_request(http,url)
        cookie = ""
        if res1.has_key('set-cookie'):
            cookie = res1['set-cookie']
        #end if
       	headers = {'Cookie': cookie}
#       res, content = http.request(url,headers=headers)
        res, content = yx_httplib2_request(http,url,headers=headers)
#	    r,c=http.request(url,headers=headers)
        r,c=yx_httplib2_request(http,url,headers=headers)
        if r['status'] == '200' and c.find('DA8.datasource.properies.filepath=')>=0 and c.find('Djava.endorsed.dirs=')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:A8_UnauthorizedAccessScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:A8_UnauthorizedAccessScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
