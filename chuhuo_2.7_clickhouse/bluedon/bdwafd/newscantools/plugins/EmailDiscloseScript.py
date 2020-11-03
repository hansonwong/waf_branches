#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from lib.common import *

def run_url(http,ob,item):
    try:
        result = []
        
        if item['method'] != 'get':
            return []
        #end if
        #temp = item['url'].lower()
        #if temp.find(".css") >= 0 or temp.find(".js") >= 0:
        #    return []
        #end if
        
        url = item['url']
        if item['params'] != "":
            url = "%s?%s" % (url,item['params'])
        #end if
        email_type_list = ['@gmail.com','@163.com','@126.com','@sina.com','@yahoo.com.cn','@yahoo.cn','@tom.com','@hexun.com','@21cn.com','@sohu.com','@sogou.com','@qq.com','@56.com','@3126.com','@china.com','@139.com','@yahoo.com','@live.cn','@hotmail.com','@foxmail.com','@vip.sina.cn','@msn.com','@msn.cn','@263.net.cn','@263.net','@yeah.net','@yeah.com','@5ydns.com','@35.com','@zzy.cn','@net.cn','@xinnet.com']
        temp = getTopDomain(ob['domain'])
        if temp != False:
            email_type_list.append("@%s" % (temp))
        #end if
        
        output = []
        
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res and res.has_key('status') and res['status'] == '200':
            content_list = content.replace("\r\n","\n").split("\n")
            for item in content_list:
                for email in email_type_list:
                    email1 = email
                    email2 = email.replace("@","#")
                    if item.find(email1) > 0 or item.find(email2) > 0:
                        output.append(item)
                    #end if
                #end for
            #end for 
        #end if
        
        if (output and len(output) > 0) or re.search(r"[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+",content,re.I):
            request = getRequest(url)
            response = getResponse(res)
            detail = "检测到邮件信息，可能导致信息泄露。"
            output = ""
            result.append(getRecord(ob,url,ob['level'],detail,request,response,output))
        #end if
        
        return result
        
    except Exception,e:
        logging.getLogger().error("File:EmailDiscloseScript.py, run_url function :%s, task id:%s, scheme:%s, domain:%s, base_path:%s, url:%s" % (str(e),ob['task_id'],ob['scheme'],ob['domain'],ob['base_path'],item['url']))
        write_scan_log(ob['task_id'],ob['domain_id'],"File:EmailDiscloseScript.py, run_url function :%s, url:%s" % (str(e),item['url']))
        return []
    #end try    
#end def

