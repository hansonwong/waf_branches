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
        url += "extmail/cgi/env.cgi"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('CGI/FCGI Envirement')>=0 and content.find('SCRIPT_NAME')>=0 and content.find('SERVER_NAME')>=0 and content.find('SERVER_ADMIN')>=0:
            request = getRequest(url)
            response = getResponse(res)
            contentlist = re.findall(r'<tr><td>(.*)</td><td>(.*)</td></tr>',content)
            if ob['isstart']=='1':
                acontent = ""
                for contentlist2 in contentlist:
                    bcontent = contentlist2[0]+':'+contentlist2[1]
                    acontent = acontent + bcontent + "\n"
                detail="验证性扫描结果：\n%s\n%s"%(acontent,detail)            
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:ExtMailInformationleakageScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:ExtMailInformationleakageScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def