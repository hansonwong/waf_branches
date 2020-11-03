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
        pathlist=['robots.txt','admin/index.htm','ads/install/templates/ads-float.html','announce/install/templates/index.html','bill/install/mysql.sql','comment/include/js/comment.js','data/js/config.js','digg/install/templates/index.html','editor/js/editor.js','error_report/install/mysql.sql','formguide/install/templates/form_index.html','guestbook/install/templates/index.html','house/.htaccess','images/js/admin.js','install/cms_index.html','link/install/templates/index.html','mail/install/templates/sendmail.html','member/include/js/login.js','message/install/mysql.sql','module/info/include/mysql/phpcms_info.sql','mood/install/templates/header.html','order/install/templates/deliver.html','phpcms/templates/default/member/connect.html','phpcms/templates/default/wap/header.html','phpsso_server/statics/js/formvalidator.js','search/install/templates/index.html','space/images/js/space.js','special/type/dev.html','spider/uninstall/mysql.sql','stat/uninstall/mysql.sql','statics/js/cookie.js','templates/default/info/area.html','union/install/mysql.sql','video/install/templates/category.html','vote/install/templates/index.html','wenba/install/mysql.sql','yp/images/js/global.js']
        for path in pathlist:			            
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("phpcms")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindPHPCmsScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindPHPCmsScript.py, run_domain function :" + str(e))
        return result

