#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import re
from lib.common import *

def run_url(http,ob,item):
    try:
        result = []
        if item['method'] != 'post' or item['params'] == '':
            return []
        #end if

        from FormWeakPasswordCheck import FormWeakPasswordCheck

        c = FormWeakPasswordCheck(http,ob['user_id'])
        u,p,res,params = c.check(item["url"], item['params'])
        if u and p:
            detail = u"检测到WEB弱密码：\n用户名：%s\n密码：%s" % (u, p)
            detail = detail.encode('utf8')
            request = postRequest(item['url'],'POST',{},params)
            response = getResponse(res)
            result.append(getRecord(ob,item["url"],ob['level'],detail,request,response))
        #end if
        
        return result
    except Exception,e:
        
        logging.getLogger().error("File:FormWeakPwdCheck.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FormWeakPwdCheck.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def



