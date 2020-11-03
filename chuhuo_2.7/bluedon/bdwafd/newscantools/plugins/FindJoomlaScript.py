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
        pathlist=['htaccess.txt','CONTRIBUTING.md','phpunit.xml.dist','robots.txt','joomla.xml','README.txt','robots.txt.dist','web.config.txt','installation/CHANGELOG','administrator/components/com_login/login.xml','components/com_mailto/views/sent/metadata.xml','components/com_wrapper/wrapper.xml','installation/language/en-GB/en-GB.ini','installation/language/en-US/en-US.ini','installation/language/zh-CN/zh-CN.ini','installation/template/js/installation.js','language/en-GB/en-GB.com_contact.ini','libraries/joomla/filesystem/meta/language/en-GB/en-GB.lib_joomla_filesystem_patcher.ini','libraries/joomla/html/language/en-GB/en-GB.jhtmldate.ini','media/com_finder/js/indexer.js','media/com_joomlaupdate/default.js','media/editors/tinymce/templates/template_list.js','media/jui/css/chosen.css','modules/mod_banners/mod_banners.xml','plugins/authentication/joomla/joomla.xml','templates/atomic/css/template.css']
        for path in pathlist:			             
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("joomla")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindJoomlaScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindJoomlaScript.py, run_domain function :" + str(e))
        return result

