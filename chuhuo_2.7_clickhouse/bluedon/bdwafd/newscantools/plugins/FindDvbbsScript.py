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
        pathlist=['Admin/images/admin.js','admin/inc/admin.js','admin/left.htm','boke/CacheFile/System.config','boke/Script/Dv_form.js','boke/Skins/Default/xml/index.xslt','boke/Skins/dvskin/xml/index.xslt','Css/aqua/style.css','Css/cndw/pub_cndw.css','Css/gray/style.css','Css/green/pub_cndw_green.css','Css/red/style.css','Css/yellow/style.css','Data/sitemap_cache.xml','dv_edit/main.js','Dv_ForumNews/Temp_Dv_ForumNews.config','Dv_plus/IndivGroup/js/Dv_form.js','Dv_plus/IndivGroup/Skin/Dispbbs.xslt','Dv_plus/myspace/drag/space.js','Dv_plus/myspace/script/fuc_setting.xslt','images/manage/admin.js','images/post/DhtmlEdit.js','inc/Admin_transformxhml.xslt','inc/Templates/bbsinfo.xml','Plus_popwan/CacheFile/sn.config','Resource/Admin/pub_html1.htm','Resource/Classical/boardhelp_html4.htm','Resource/Format_Fuc.xslt','Resource/Template_1/boardhelp_html4.htm','Skins/aspsky_1.css','skins/classical.css','skins/myspace/default01/demo.htm']
        for path in pathlist:			       	          
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("dvbbs")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindDvbbsScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindDvbbsScript.py, run_domain function :" + str(e))
        return result

