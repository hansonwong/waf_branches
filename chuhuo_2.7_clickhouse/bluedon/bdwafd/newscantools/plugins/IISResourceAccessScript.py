#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import re
from lib.common import *

def run_url(http,ob,item):
    try:
        result = []
        if item['method'] != 'get':
            return []
        #end if
        '''
        url = ""
        if item['params'] == "":
            url = item['url']
        else:
            url = "%s?%s" % (item['url'],item['params'])
        #end if
        '''
        url = item['url']
        if url.find('.asp') < 0 and url.find('.aspx') < 0:
            return []
        #end if
        headers = {}
        headers['Cookie'] = "ASPSESSIONIDCSCDSCSS=LDMJENIAIBHHKKGHOKAPHFPB"
        headers['Accept'] = "*/*"
        headers['Accept-Language'] = "en-US"
        headers['User-Agent'] = "Mozilla/4.0 (compatible; MSIE 6.0; Win32)"
        headers['Host'] = ob['domain']
        headers['Referer'] = "http://%s/" % (ob['domain'])
        headers['Translate'] = "f"
        headers['Content-Type'] = "application/x-www-form-urlencoded"
        #res, content = http.request(url, 'GET', body = '', headers = headers)
        res, content = yx_httplib2_request(http,url, 'GET', body = '', headers = headers)
        if res['status'] == '200':
            match = re.findall(r"<%(.+?)%>",content,re.I|re.DOTALL)
            if match and len(match) > 1:
                headers2 = {}
                headers2['Cookie'] = "ASPSESSIONIDCSCDSCSS=LDMJENIAIBHHKKGHOKAPHFPB"
                headers2['Accept'] = "*/*"
                headers2['Accept-Language'] = "en-US"
                headers2['User-Agent'] = "Mozilla/4.0 (compatible; MSIE 6.0; Win32)"
                headers2['Host'] = ob['domain']
                headers2['Referer'] = "http://%s/" % (ob['domain'])
                headers2['Translate'] = "f"
                headers2['Content-Type'] = "application/x-www-form-urlencoded"
                request = getRequest(url,"GET",headers2,"")
                response = getResponse(res,"")
                detail = u"该网站的IIS服务器开启了脚本资源访问，将导致网站的源码泄露，建议管理员进入IIS管理器关闭脚本资源访问功能。"
                detail = detail.encode('utf8')
                
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
            #end if
        #end if
        
        return result
    except Exception,e:
        logging.getLogger().error("File:IISResourceAccessScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:IISResourceAccessScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def
