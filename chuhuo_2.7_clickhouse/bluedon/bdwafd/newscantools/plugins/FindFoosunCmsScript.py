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
        pathlist=['Admin/Collect/vssver2.scc','Admin/FreeLabel/vssver2.scc','Admin/News/images/vssver2.scc','Admin/News/lib/vssver2.scc','Admin/PublicSite/vssver2.scc','Foosun/Admin/Mall/Mall_Factory.Asp','FS_Inc/vssver2.scc','FS_InterFace/vssver2.scc','Install/SQL/Value/site_param.sql','manage/collect/MasterPage_Site.master','Templets/pro/cms.htm','User/contr/lib/vssver2.scc','Users/All_User.Asp','Users/Mall/OrderPrint.Asp','xml/products/dotnetcmsversion.xml']
        for path in pathlist:			            
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("foosuncms")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindFoosunCmsScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindFoosunCmsScript.py, run_domain function :" + str(e))
        return result

