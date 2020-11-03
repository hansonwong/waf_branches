#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_url(http,ob,item):
    try:  
        result=[]
        if ob['site_type'] != 'aspx':
            return result
        url=item['url']
        if url[-1] !='/' or item['method'] !='get':
            return result
        if url.count('/') >5:
            return result
        detail=u''
        detail=detail.encode('utf8')
        pathlist=['Global.asax','Web.config','Admin/MasterPage/Default.Master','ashx/comment.ashx','en/Module/AboutDetail.ascx','Html_skin30/downclass_29_1.html','HtmlAspx/ascx/CreateOrder.ascx','Master/default.Master','Module/AboutDetail.ascx','T/skin01/enindex.html','T/skin05/about.html','Enrss.xml','Ch/Memberphoto.Asp','Html_skin30/enabout.html']
        for path in pathlist:			              
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("ljcms")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindLjcmsScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindLjcmsScript.py, run_domain function :" + str(e))
        return result

