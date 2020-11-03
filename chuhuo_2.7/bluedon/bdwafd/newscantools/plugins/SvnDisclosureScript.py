#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import re
from lib.common import *

def run_url(http,ob,item):
    try:
        result = []
        if item['method'] != 'get' or item['url'][-1] != '/' or item['params'] != '':
            return []
        #end if
        url = "%s.svn/entries" % (item['url'])
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res and res.has_key('status') and res['status'] == '200' and res.has_key('content-type') and res['content-type'] != '':
            if content.find('<html>') >= 0 or content.find('<body>') >= 0 or content.find('<head>') >= 0 or content.find('<table ') >= 0 or content.find('<p>') >= 0 or content.find('<table>') >= 0 or content.find('<TABLE>') >= 0:
                return []
            #end if
            match = re.findall(r"(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])",content,re.I)
            if len(match) > 0 or content.find('svn') > 0:
                detail = u"该路径泄露了SVN信息，可能导致源码泄露或者SVN服务器被攻击。"
                detail = detail.encode('utf8')
                request = getRequest(url,"GET")
                response = getResponse(res,"")
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
            #end if
        #end if
        
        return result
    except Exception,e:
        logging.getLogger().error("File:SvnDisclosureScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:SvnDisclosureScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def

