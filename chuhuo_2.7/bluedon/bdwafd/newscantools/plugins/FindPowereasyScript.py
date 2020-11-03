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
        pathlist=['License.txt','Web.config','rss.xsl','RSS.xsl','JS/checklogin.js','Temp/ajaxnote.txt','User/PopCalendar.js','xml/xml.xsl','Admin/MasterPage.master','API/Request.xml','App_GlobalResources/CacheResources.resx','Config/AjaxHandler.config','Controls/AttachFieldControl.ascx','Admin/Common/HelpLinks.xml','Admin/JS/AdminIndex.js','Controls/Company/Company.ascx','Database/SiteWeaver.sql','Editor/Lable/PE_Annouce.htm','Editor/plugins/pastefromword/dialogs/pastefromword.js','Install/Demo/Demo.sql','Install/NeedCheckDllList.config','Language/Gb2312.xml','Skin/OceanStar/default.css','Skin/OceanStar/user/default.css','Space/Template/sealove/index.xsl','Template/Default/Skin/default.css','Template/Default/Skin/user/default.css','User/Accessories/AvatarUploadHandler.ashx','wap/Language/Gb2312.xml','WebServices/CategoryService.asmx']
        for path in pathlist:			             
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("powereasy")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindPowereasyScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindPowereasyScript.py, run_domain function :" + str(e))
        return result

