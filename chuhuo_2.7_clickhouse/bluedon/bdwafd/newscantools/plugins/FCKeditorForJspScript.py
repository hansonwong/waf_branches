#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
#def MysqlGetUrl(self,url):
#    try:
#        
#        parse=urlparse.urlparse(url)
#        urls=parse.path
#        if urls=="" or urls=="/":
#            return self.url
#        urls=url.split("/")
#        urls=urls[len(urls)-1]
#        if urls=="" or urls.find(".")<0:
#            return  url
#        else:
#            return False      
#    except Exception,e:
#        logging.getLogger().error("mysql MysqlGetUrl Exception(FCKeditorForJspScript.py):" + str(e))
#        return False
def run_domain(http,ob):
    try:
        result=[]
        detail = u""
                                                
        detail = detail.encode('utf8')
        domain=ob['domain']
        url="FCKeditor/editor/filemanager/browser/default/connectors/jsp/connector?Command=GetFoldersAndFiles&Type=&CurrentFolder=%2F"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
        
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        if content.find("<Connector command=\"GetFoldersAndFiles\" resourceType=\"\">")>=0:
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
        else:
            url1="FCK/editor/filemanager/browser/default/connectors/jsp/connector?Command=GetFoldersAndFiles&Type=&CurrentFolder=%2F"
            geturl1="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url1)
            response1,content1=requestUrl(http,geturl1,ob['task_id'],ob['domain_id'])
            if content1.find("<Connector command=\"GetFoldersAndFiles\" resourceType=\"\">")>=0:
                request = getRequest(geturl)
                response = getResponse(response)
                result.append(getRecord(ob,geturl1,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:fckeditor from jsp dir script.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:fckeditor from jsp dir script.py, run_domain function :" + str(e))
    #end try
    return result

    