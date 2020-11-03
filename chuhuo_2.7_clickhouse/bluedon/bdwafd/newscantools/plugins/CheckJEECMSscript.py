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
        expurl= "jeeadmin/jeecms/login.do"#3.x
        expurl1="login/Jeecms.do"#2.x
        geturl="%s%s"%(url,expurl)
        geturl1="%s%s"%(url,expurl1)
        http.httlib2_set_follow_redirects(True)
        res, content = requestUrl(http,geturl,ob['task_id'],ob['domain_id'])

        if res['status'] == '200' and content.find('jeecms')>=0 and content.find('/jeeadmin/jeecms/login.do') < 0 and content.find('%2fjeeadmin%2fjeecms%2flogin.do') < 0:
            request = getRequest(geturl)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain']+ob['base_path'],ob['level'],detail,request,response))
        else:
            res, content = requestUrl(http,geturl1,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find('new JCore.CheckCode($(\'#checkCode\'),\'/CheckCode.svl\')')>=0:
                request = getRequest(geturl1)
                response = getResponse(res)
                list.append(getRecord(ob,ob['scheme']+"://"+ob['domain']+ob['base_path'],ob['level'],detail,request,response))
        http.httlib2_set_follow_redirects(False)
    except Exception,e:
        logging.getLogger().error("File:chejeecmsscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        http.httlib2_set_follow_redirects(False)
        write_scan_log(ob['task_id'],ob['domain_id'],"File:chejeecmsscript.py, run_domain function :" + str(e))
    #end try

    return list
#end def