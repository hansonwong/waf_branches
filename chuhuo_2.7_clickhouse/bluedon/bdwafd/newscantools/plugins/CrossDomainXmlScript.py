#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *


def run_domain(http,ob):
    result = []
    try:
        scheme = ob['scheme']
        domain = ob['domain']
        base_path = ob['base_path']
    
        url = "%s://%s%s%s" % (scheme,domain,base_path,"crossdomain.xml")
#       res, content = http.request(url)
        res, content = yx_httplib2_request(http,url)
        
        if res and res.has_key('status') and res['status'] == '200':
            #<allow-access-from domain="*" to-ports="*" secure="false"/>
            match = re.findall(r"<(\s*)allow-access-from(\s+)domain(\s*)=(\s*)(\"|')(.+?)\5(.*?)/(\s*)>",content,re.I|re.DOTALL)
            if match and len(match) > 0:
                for row in match:
                    keyword = row[5].replace(" ","")
                    if keyword == "*":
                        detail = "发现网站的配置文件crossdomain.xml中开启了允许访问的域为任意域的功能，可能导致网站存在危险。"
                        request = getRequest(url)
                        response = getResponse(res)
                        output = "<%sallow-access-from%sdomain%s=%s%s%s%s%s/%s>" % (row[0],row[1],row[2],row[3],row[4],row[5],row[4],row[6],row[7])
                        result.append(getRecord(ob,url,ob['level'],detail,request,response,output))
                        
                        return result
                    #end if
                #end for
            #end if
        #end if
        
    except Exception,e:
        logging.getLogger().error("File:CrossDomainXml.py, run_domain function :%s, task id:%s, scheme:%s, domain:%s, base_path:%s" % (str(e),ob['task_id'],ob['scheme'],ob['domain'],ob['base_path']))     
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CrossDomainXml.py, run_domain function :"+str(e)) 
    #end try
    
    return result
#end def



