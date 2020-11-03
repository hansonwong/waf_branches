#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    #www.sdbys.cn/module/download/downfile.jsp?filename=downfile.jsp&pathfile=module/download/downfile.jsp
    try:  
        result=[]                               
        detail=''
       
        domain=ob['domain']
        url="module/download/downfile.jsp?filename=downfile.jsp&pathfile=module/download/downfile.jsp"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        if content.find("import=\"jcms.blf")>=0:
            request = getRequest(geturl)
            response = getResponse(response)
            
            if ob['isstart']=='1':
                detail="验证性扫描结果：\n%s"%content
            result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:jcms2010downlaodfilescript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:jcms2010downlaodfilescript.py, run_domain function :" + str(e))
    return result

