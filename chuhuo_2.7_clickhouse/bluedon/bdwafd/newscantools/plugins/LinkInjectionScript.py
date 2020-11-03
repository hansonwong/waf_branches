#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from lib.common import *


def LinkInjectionCheck(http,ob,url):
    try:
        result = []
        if url == "":
            return result
        #end if
        expurl = "%s%s" % (url,"<iframe%20src=http://www.baidu.com></iframe>")
        res, content = requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        if res['status'] == '404' or len(content) <= 0:
            return result
        #end if
        flag, keyword = LinkGetKeyWord(content,"src=http://www.baidu.com></iframe>")
        if flag:
            detail = u"该URL可能会导致链接注入。测试链接为："
            detail = "%s%s%s" % (detail.encode('utf-8'),url,keyword)
            request = getRequest("%s%s" % (url,keyword))
            response = getResponse(res)
                
            result.append(getRecord(ob,url,ob['level'],detail,request,response)) 
        #end if
        return result
    except Exception,e:
        logging.getLogger().error("File:LinkInjectionScript.py, LinkInjectionCheck function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + url)
        return []
    #end try       
#end def
    

def run_url(http,ob,item):
    try:
        list = []
        if item['method'] != 'get' or item['params'] == '':
            return list
        #end if
        if checkUrlType(item['url']) == False:
            return list
        #end if
        params = changeParams(item['params'])
        for row in params:
            url = "%s?%s" % (item['url'],row)
            res = LinkInjectionCheck(http,ob,url)
            if len(res) > 0:
                list.extend(res)
            #end if
        #end for
        
        return list
    except Exception,e:
        logging.getLogger().error("File:LinkInjectionScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:LinkInjectionScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #ene  try
#end def


