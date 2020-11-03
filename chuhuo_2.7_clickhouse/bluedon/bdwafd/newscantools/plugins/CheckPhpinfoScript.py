#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_url(http,ob,item):
    try:
        result = []
        if item['method'] != 'get':
            return []
        #end if
        if item['params'] != '':
            return []
        #end if
        if item['url'][-1] != '/':
            return []
        #end if
        if ob['site_type'] in ['asp','aspx','jsp']:
            return []
        #end if
        
        url = "%sphpinfo.php" % (item['url'])
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res and res.has_key('status') and res['status'] == '200' and res.has_key('content-type') and res['content-type'] != '' and content.find('phpinfo.php?') >= 0:
            detail = "在 Web 站点上安装了缺省样本脚本或目录"
            output = ""
            request = getRequest(url)
            response = getResponse(res)
            result.append(getRecord(ob,url,ob['level'],detail,request,response,output))
        #end if
        
        return result
    except Exception,e:
        logging.getLogger().error("File:CheckPhpinfoScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CheckPhpinfoScript.py, run_url function :" + str(e) +", url:" + item['url'])
        return []
    #end try    
#end def

