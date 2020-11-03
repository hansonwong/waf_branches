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
        url="FCKeditor/editor/filemanager/browser/default/connectors/php/connector.php?Command=GetFoldersAndFiles&Type=File&CurrentFolder=%2F"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
        
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        if content.find("<Connector command=\"GetFoldersAndFiles\" resourceType=\"\">")>=0:
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
        else:
            url="admin/FCKeditor/editor/filemanager/browser/default/connectors/php/connector.php?Command=GetFoldersAndFiles&Type=File&CurrentFolder=%2F"
            geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
            response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if content.find("<Connector command=\"GetFoldersAndFiles\" resourceType=\"\">")>=0:
                request = getRequest(geturl)
                response = getResponse(response)
                result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
            else:
                url="manager/FCKeditor/editor/filemanager/browser/default/connectors/php/connector.php?Command=GetFoldersAndFiles&Type=File&CurrentFolder=%2F"
                geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
                response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
                if content.find("<Connector command=\"GetFoldersAndFiles\" resourceType=\"\">")>=0:
                    request = getRequest(geturl)
                    response = getResponse(response)
                    result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
                else:
                    url="manage/FCKeditor/editor/filemanager/browser/default/connectors/php/connector.php?Command=GetFoldersAndFiles&Type=File&CurrentFolder=%2F"
                    geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
                    response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
                    if content.find("<Connector command=\"GetFoldersAndFiles\" resourceType=\"\">")>=0:
                        request = getRequest(geturl)
                        response = getResponse(response)
                        result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
                        
    except Exception,e:
        logging.getLogger().error("File:fckeditor for php dir script.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:fckeditor for php dir script.py, run_domain function :" + str(e))
    #end try
    return result

    