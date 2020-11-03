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
        pathlist=['install.sql','install.php','INSTALL.php','License.txt','ad.asp','admin.asp','collect.asp','counter.asp','create.asp','INSTALL.asp','link.asp','login.asp','webftp.asp','ad/index.asp','admin/Article/index.asp','admin/system/create.asp','admin/webftp/index.asp','api/alipay.php','block/core.class.php','dbquery/core.class.php','dbquery/language/zh-cn.xml','feedback/core.class.php','images/style.css','/inc/config.asp','language/zh-cn.xml','library/template.class.php','page/system/inc/fun.js','page/Tools/fun.asp','page/webftp/fun.asp','system/images/fun.js','system/js/jquery.kc.js','template/default.htm']
        for path in pathlist:			             
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("kingcms")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindKingCmsScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindKingCmsScript.py, run_domain function :" + str(e))
        return result

