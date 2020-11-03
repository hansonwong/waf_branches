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
        pathlist=['robots.txt','d/file/index.html','d/file/p/index.html','d/js/acmsd/index.html','d/js/class/index.html','d/js/js/hotnews.js','d/js/pic/index.html','d/js/vote/index.html','d/txt/index.html','e/admin/adminstyle/1/page/about.htm','e/admin/ecmseditor/images/blank.html','e/admin/ecmseditor/infoeditor/epage/images/blank.html','e/admin/user/data/certpage.txt','e/data/ecmseditor/images/blank.html','e/data/fc/index.html','e/data/html/cjhtml.txt','e/data/template/gbooktemp.txt','e/data/tmp/cj/index.html','e/extend/index.html','e/install/data/empirecms.com.sql','e/tasks/index.html','e/tool/feedback/temp/test.txt','html/index.html','html/sp/index.html','install/data/empiredown.com.sql','s/index.html','search/index.html','t/index.html']
        for path in pathlist:			             
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("empirecms")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindEmpireCmsScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindEmpireCmsScript.py, run_domain function :" + str(e))
        return result

