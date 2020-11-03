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
        url += "jcms/m_5_5/m_5_5_3/import_style.jsp"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('<head><link href="/jcms/css/thickbox.css" type=text/css')>=0 and content.find('var ext = GetFileExtension( thisobj.value );')>=0 and content.find('if(  ext=="xml" )')>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:JCMS_ArbitraryFileUploadScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:JCMS_ArbitraryFileUploadScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def