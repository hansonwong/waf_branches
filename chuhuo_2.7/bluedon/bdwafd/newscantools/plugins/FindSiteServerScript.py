#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_url(http,ob,item):
    try:  
        result=[]
        if ob['site_type'] != 'asp' or ob['site_type'] != 'aspx':
            return result
        url=item['url']
        if url[-1] !='/' or item['method'] !='get':
            return result
        if url.count('/') >5:
            return result
        detail=u''
        detail=detail.encode('utf8')
        pathlist=['robots.txt','Web.config','LiveServer/Configuration/UrlRewrite.config','LiveServer/Inc/html_head.inc','SiteFiles/bairong/SqlScripts/cms.sql','SiteFiles/bairong/TextEditor/ckeditor/plugins/nextpage/plugin.js','SiteFiles/bairong/TextEditor/eWebEditor/language/zh-cn.js','SiteFiles/bairong/TextEditor/eWebEditor/style/coolblue.js','SiteServer/CMS/vssver2.scc','SiteServer/Inc/html_head.inc','SiteServer/Installer/EULA.html','SiteServer/Installer/readme/problem/1.html','SiteServer/Installer/SqlScripts/liveserver.sql','SiteServer/Services/AdministratorService.asmx','SiteServer/Themes/Language/en.xml','SiteServer/Themes/Skins/Skin-DirectoryTree.ascx','SiteServer/UserCenter/Skins/Skin-Footer.ascx','UserCenter/Inc/script.js']
        for path in pathlist:			          
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("siteserver")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindSiteServerScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindSiteServerScript.py, run_domain function :" + str(e))
        return result

