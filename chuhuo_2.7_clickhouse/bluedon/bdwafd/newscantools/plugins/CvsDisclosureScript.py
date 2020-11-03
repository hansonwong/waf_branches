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
        url = "%sCVS/Entries" % (item['url'])
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200':
            if content.find('html') >= 0 and content.find('body') >= 0:
                return []
            #end if
            if content.find("////") > 0:
                detail = u"该路径泄露了CVS信息，可能导致源码泄露或者CVS服务器被攻击。"
                detail = detail.encode('utf8')
                request = getRequest(url,"GET")
                response = getResponse(res,"")
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
            #end if
        #end if
        
        return result
    except Exception,e:
        logging.getLogger().error("File:CvsDisclosureScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CvsDisclosureScript.py, run_url function :"+ str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def

