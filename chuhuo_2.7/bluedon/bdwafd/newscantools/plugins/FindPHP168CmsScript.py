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
        pathlist=['readme.txt','ckeditor/plugins/gallery/plugin.js','install/','cms/install/index.html','ewebeditor/KindEditor.js','form/install/data.sql','hack/cnzz/template/menu.htm','help/main.html','images/dialog.css','js/util.js','plugin/qqconnect/bind.html','skin/admin/style.css','template/admin/ask/config.html']
        for path in pathlist:			            
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("php168")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindPHP168CmsScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindPHP168CmsScript.py, run_domain function :" + str(e))
        return result

