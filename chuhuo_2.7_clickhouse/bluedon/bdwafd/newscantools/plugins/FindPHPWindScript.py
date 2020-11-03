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
        pathlist=['licence.txt','robots.txt','recommend.html','wind.sql','AUTHORS','humans.txt','LICENSE','wind/readme','wind/http/mime/mime','conf/md5sum','admin/safefiles.md5','api/agent.html','apps/diary/template/m_diary_bottom.htm','apps/groups/template/m_header.htm','apps/stopic/template/stopic.htm','apps/weibo/template/m_weibo_bottom.htm','connexion/template/custom_weibo_template.htm','data/lang/zh_cn.js','hack/app/info.xml','html/js/index.html','js/magic.js','lang/wind/admin/admin.htm','m/template/footer.htm','mode/area/js/adminview.js','phpwind/lang/wind/admin/admin.htm','phpwind/licence.txt','res/css/admin_layout.css','src/extensions/demo/Manifest.xml','src/extensions/demo/resource/editorApp.js','styles/english/template/admin_english/admin.htm','template/config/admin/config_run.htm','themes/forum/default/css/dev/forum.css','u/themes/default/footer.htm','windid/res/css/admin_layout.css','windid/res/js/dev/pages/admin/auth_manage.js','windid/res/js/dev/wind.js']
        for path in pathlist:			            
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("phpwind")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindPHPWindScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindPHPWindScript.py, run_domain function :" + str(e))
        return result

