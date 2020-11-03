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
        pathlist=['robots.txt','install/testdata/hdwikitest.sql','js/api.js','js/editor/editor.js','js/hdeditor/hdeditor.min.js','js/hdeditor/skins/content.css','js/jqeditor/hdwiki.js','js/jqeditor/skins/content_default.css','plugins/hdapi/view/admin_hdapi.htm','plugins/mwimport/desc.xml','plugins/mwimport/view/admin_mwimport.htm','plugins/ucenter/view/admin_ucenter.htm','style/aoyun/hdwiki.css','style/default/admin/admin.css','style/default/desc.xml','view/default/admin_addlink.htm']
        for path in pathlist:			             
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("hdwiki")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindHdwikiScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindHdwikiScript.py, run_domain function :" + str(e))
        return result

