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
        pathlist=['robots.txt','license.txt','readme.txt','help.txt','readme.html','readme.htm','wp-admin/css/colors-classic.css','wp-admin/js/media-upload.dev.js','wp-content/plugins/akismet/akismet.js','wp-content/themes/classic/rtl.css','wp-content/themes/twentyeleven/readme.txt','wp-content/themes/twentyten/style.css','wp-includes/css/buttons.css','wp-includes/js/scriptaculous/wp-scriptaculous.js','wp-includes/js/tinymce/langs/wp-langs-en.js','wp-includes/js/tinymce/wp-tinymce.js','wp-includes/wlwmanifest.xml']
        for path in pathlist:			              
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("wordpress")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindWordPressScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindWordPressScript.py, run_domain function :" + str(e))
        return result

