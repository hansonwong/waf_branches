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
        pathlist=['INSTALL','MAINTAINERS','.gitattributes','.htaccess','example.gitignore','README.txt','themes/README.txt','sites/README.txt','profiles/README.txt','modules/README.txt','core/CHANGELOG.txt','core/vendor/README.txt','.editorconfig','CHANGELOG.txt','COPYRIGHT.txt','INSTALL.mysql.txt','INSTALL.pgsql.txt','INSTALL.sqlite.txt','INSTALL.txt','MAINTAINERS.txt','UPGRADE.txt','themes/bartik/color/preview.js','sites/all/themes/README.txt','sites/all/modules/README.txt','scripts/test.script','modules/user/user.info','misc/ajax.js','themes/tests/README.txt','sites/all/README.txt','INSTALL','MAINTAINERS','.gitattributes','.htaccess','example.gitignore','/README.txt','.editorconfig','CHANGELOG.txt','COPYRIGHT.txt','INSTALL.mysql.txt','INSTALL.pgsql.txt','INSTALL.sqlite.txt','INSTALL.txt']
        for path in pathlist:			              
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("drupal")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindDrupalScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindDrupalScript.py, run_domain function :" + str(e))
        return result

