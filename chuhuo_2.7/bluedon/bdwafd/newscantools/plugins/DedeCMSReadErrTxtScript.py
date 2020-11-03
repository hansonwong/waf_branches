#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u"漏洞原因：文件/data/mysql_error_trace.inc记录mysql查询错误，如果有后台查询出现错误，则会暴露后台路径。\n\n\
                                                   临时解决办法：\n打开 /include/dedesql.class.php，搜 mysql_error_trace ，把 mysql_error_trace.inc 更名成 mysql_error_任意字符.inc\n\
                                                 然后登录ftp，转到 /data/ 目录，把 mysql_error_trace.inc 更名成 mysql_error_任意字符.inc （请注意两处文件名对应）。"
        detail = detail.encode('utf8')
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "data/mysql_error_trace.inc"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('<?php  exit();') >= 0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:dedecmsreaderrtxt.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:dedecmsreaderrtxt.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def




            
        
        
        
        
        