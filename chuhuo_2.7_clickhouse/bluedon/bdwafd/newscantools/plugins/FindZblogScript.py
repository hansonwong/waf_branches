#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_url(http,ob,item):
    try:  
        result=[]
        if ob['site_type'] != 'asp':
            return result
        url=item['url']
        if url[-1] !='/' or item['method'] !='get':
            return result
        if url.count('/') >5:
            return result
        detail=u''
        detail=detail.encode('utf8')
        pathlist=['license.txt','PLUGIN/BackupDB/plugin.xml','PLUGIN/PingTool/plugin.xml','PLUGIN/PluginSapper/plugin.xml','SCRIPT/common.js','THEMES/default/TEMPLATE/catalog.html','THEMES/default/theme.xml','zb_system/DEFEND/default/footer.html','zb_system/DEFEND/thanks.html','zb_system/SCRIPT/common.js','zb_users/CACHE/updateinfo.txt','zb_users/PLUGIN/AppCentre/plugin.xml','zb_users/PLUGIN/FileManage/plugin.xml','zb_users/THEME/default/theme.xml','zb_users/THEME/HTML5CSS3/theme.xml','zb_users/THEME/metro/TEMPLATE/footer.html','zb_users/THEME/metro/theme.xml']
        for path in pathlist:			             
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("z-blog")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindZblogScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindZblogScript.py, run_domain function :" + str(e))
        return result

