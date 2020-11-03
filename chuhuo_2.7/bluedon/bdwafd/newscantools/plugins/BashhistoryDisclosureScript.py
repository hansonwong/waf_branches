#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_url(http,ob,item):
    try:
        result = []
        if item['method'] != 'get' or item['url'][-1] != '/' or item['params'] != '':
            return []
        #end if
        url = "%s.bash_history" % (item['url'])
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res and res.has_key('status') and res.has_key('content-type') and res['status'] == '200' and res['content-type'].find("image") < 0:
            if content.find('html') >= 0 or content.find('body') >= 0 or content.find('HTML')>=0 or content.find("BODY")>=0:
                return []
            #end if
            if (content.find('cd') >= 0 or content.find('ls') >= 0) and content.find("<table")<0:
                match = re.findall(r"[^_=a-z0-9](cd|ls)[^_=a-z0-9]",content,re.I)
                if match and len(match) > 0:
                    detail = u"该路径泄露了Bash的指令信息，可能导致服务器被攻击。"
                    detail = detail.encode('utf8')
                    request = getRequest(url,"GET")
                    response = getResponse(res,"")
                    result.append(getRecord(ob,url,ob['level'],detail,request,response))
                #end if
            #end if
        #end if
        
        return result
    except Exception,e:
        logging.getLogger().error("File:BashhistoryDisclosureScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:BashhistoryDisclosureScript.py, run_url function :" + str(e)+", url:" + item['url'])
        return []
    #end try    
#end def



