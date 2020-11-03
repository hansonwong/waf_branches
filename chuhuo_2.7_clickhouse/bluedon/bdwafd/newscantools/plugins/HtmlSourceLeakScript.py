#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_url(http,ob,item):
    try:
        result = []
        if item['method'] != 'get':
            return []
        #end if
        url = item['url']
        
        if url.find('.html') < 0 and url.find('.htm') < 0 and url.find('.php') < 0 and url.find('.asp') < 0 and url.find('.aspx') < 0 and url.find('.jsp') < 0 and url.find('.do') < 0:
            return []
        #end if
        
        params = item['params']
        if params != "":
            url = "%s?%s" % (url,params)
        #end if
        detail = "发现HTML的注释信息，可能包含程序员的调试信息或者存在遗留的重要敏感信息。"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        request = getRequest(url)
        response = getResponse(res)
        if res and res.has_key('status') and res['status'] == '200' and content.find("<!--") >= 0 and content.find("-->") >= 0:
            match = re.findall(r"<!--(\s*)(.+?)(\s*)-->",content,re.I|re.DOTALL)
            if match and len(match) > 0:
                for row in match:
                    key = row[1]
                    if key != "":
                        m = re.findall(r"(\s+)(admin|username|password|passwd)(\s+)",key,re.I)
                        if m and len(m) > 0:
                            result.append(getRecord(ob,url,ob['level'],detail,request,response))
                            break
                        #end if

                        m = re.findall(r"(.+?)\.(asp|php|jsp|aspx|do|pl|txt|rar|zip|tar)",key,re.I)
                        if m and len(m) > 0:
                            result.append(getRecord(ob,url,ob['level'],detail,request,response))
                            break
                        #end if
                        
                        m = re.findall(r"(\s+)(http|https|ftp):\/\/",key,re.I)
                        if m and len(m) > 0:
                            result.append(getRecord(ob,url,ob['level'],detail,request,response))
                            break
                        #end if
                        
                        m = re.findall(r"(function|<%)",key,re.I)
                        if m and len(m) > 0:
                            result.append(getRecord(ob,url,ob['level'],detail,request,response))
                            break
                        #end if

                        m = re.findall(r"(\s+)([cdefgh]:\\)",key,re.I)
                        if m and len(m) > 0:
                            result.append(getRecord(ob,url,ob['level'],detail,request,response))
                            break
                        #end if
                    #end if
                #end for
            #end if
        #end if
        
        return result
    except Exception,e:
        logging.getLogger().error("File:HtmlSourceLeakScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:HtmlSourceLeakScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def

