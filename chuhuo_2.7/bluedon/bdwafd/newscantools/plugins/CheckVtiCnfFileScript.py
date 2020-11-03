#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_url(http,ob,item):
    try:
        result = []
        if item['method'] != 'get':
            return []
        #end if
        url = item['url']
        params = item['params']
        if params != '':
            return []
        #end if
        if url.find('.htm') < 0:
            return []
        #end if
        if url[-1] == '/':
            return []
        #end if
        dir = '/'.join(url.split('/')[0:-1])
        filename = url.split('/')[-1]
        match = re.findall(r"([a-z]+)",filename,re.I)
        if match and len(match) > 0:
            pass
        else:
            return []
        #end if
        url = "%s/_vti_cnf/%s" % (dir,filename)
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res and res.has_key('status') and res['status'] == '200' and res.has_key('content-type') and res['content-type'] != '' and content.find('Microsoft FrontPage') >= 0:
            detail = "当安装 Microsoft FrontPage 服务器扩展时，安装会创建称为“_vti_cnf”的目录。对于 DIR 目录中的每个“filename.htm”，都会创建下列文件：/DIR/_vti_cnf/filename.htm，这个文件包含敏感的 FrontPage 发布信息。"
            request = getRequest(url)
            response = getResponse(res)
            result.append(getRecord(ob,url,ob['level'],detail,request,response,""))
        #end if
        
        return result
    except Exception,e:
        logging.getLogger().error("File:CheckVtiCnfFileScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CheckVtiCnfFileScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def

