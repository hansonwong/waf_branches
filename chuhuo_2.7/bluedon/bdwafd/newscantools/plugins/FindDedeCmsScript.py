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
        pathlist=['data/admin/allowurl.txt','data/index.html','data/js/index.html','data/mytag/index.html','data/sessions/index.html','data/textdata/index.html','dede/action/css_body.css','dede/css_body.css','dede/templets/article_coonepage_rule.htm','include/alert.htm','member/images/base.css','member/js/box.js','php/modpage/readme.txt','plus/sitemap.html','setup/license.html','special/index.html','templets/default/style/dedecms.css','company/template/default/search_list.htm']
        for path in pathlist:			       	           
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("dedecms")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindDedeCmsScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindDedeCmsScript.py, run_domain function :" + str(e))
        return result

