#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_url(http,ob,item):
    try:  
        result=[] 
        if ob['site_type'] != 'php':
            return result
        url=item['url']
        if url[-1] !='/' or item['method'] !='get':
            return result
        if url.count('/') >5:
            return result 
        detail=u''
        detail=detail.encode('utf8')
        pathlist=['robots.txt','bbcode.js','newsfader.js','templates.cdb','u2upopup.js','admin/discuzfiles.md5','api/manyou/cloud_channel.htm','images/admincp/admincp.js','include/javascript/ajax.js','mspace/default/style.ini','plugins/manyou/discuz_plugin_manyou.xml','source/plugin/myapp/discuz_plugin_myapp.xml','static/js/admincp.js','template/default/common/common.css','uc_server/view/default/admin_frame_main.htm','bbcode.js','newsfader.js','templates.cdb','u2upopup.js','mspace/default1/style.ini','uc_server/view/default/admin_frame_main.htm']
        for path in pathlist:			       	            
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("discuz")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindDiscuzScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindDiscuzScript.py, run_domain function :" + str(e))
        return result

