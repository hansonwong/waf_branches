#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from lib.common import *

def run_url(http,ob,item):
    try:
        result = []
        if item['method'] != 'get':
            return []
        #end if
        url = item['url']
        if url.lower().find(".js")>=0 and url.lower().find(".jsp")<0:
            return []
        if item['params'] != '':
            url = "%s?%s" % (url,item['params'])
        #end if
        if checkUrlType(item['url']) == False or item['url'][-1] == '/':
            return []
        #end if
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res.has_key('status') and res['status'] != '200':
            return []
        #end if
        
        if len(content) <= 0:
            return []
        #end if
        match = re.findall(r"<(\s*)form(\s+)(.+?)>(.+?)<(\s*)/(\s*)form(\s*)>",content,re.I|re.DOTALL)
        if match and len(match) > 0:
            for row in match:
                value = row[2].lower()
                if value.find("enctype") < 0 or value.find("multipart/form-data") < 0:
                    continue
                #end if
                match2 = re.findall(r"type=(\"|')file\1",row[3],re.I)
                if match2 and len(match2) > 0:
                    detail = u"该URL中包含上传点，可能会包含上传漏洞并且被黑客利用。"
                    detail = detail.encode('utf-8')
                    request = getRequest(url)
                    response = getResponse(res)

                    result.append(getRecord(ob,url,ob['level'],detail,request,response))
                #end if
            #end for
        #end if
        
        return result
    
    except Exception,e:
        logging.getLogger().error("File:UploadFindScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:UploadFindScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def


