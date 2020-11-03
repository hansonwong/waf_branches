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
        pathlist=['license.txt','adminsoft/control/connected.php','adminsoft/control/sqlmanage.php','adminsoft/include/admin_language_cn.php','adminsoft/js/control.js','install/dbmysql/db.sql','install/dbmysql/demodb.sql','install/lan_inc.php','install/sys_inc.php','install/templates/step.html','public/class_dbmysql.php','templates/wap/cn/public/footer.html','templates/wap/en/public/footer.html']
        for path in pathlist:			             
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("espcms")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindEspCmsScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindEspCmsScript.py, run_domain function :" + str(e))
        return result

