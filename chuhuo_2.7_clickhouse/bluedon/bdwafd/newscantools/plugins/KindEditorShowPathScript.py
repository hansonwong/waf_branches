#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_url(http,ob,item):
    try:  
        result=[]                               
        detail=u''
        detail=detail.encode('utf8')
        path="/kindeditor/php/file_manager_json.php?path=/"
        url=item['url']
        if url[-1]=='/' and item['method']=='get':        
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("current_dir_path")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
        return result
    except Exception, e:
        logging.getLogger().error("File:KindEditorShowPathScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:KindEditorShowPathScript.py, run_domain function :" + str(e))
        return result

