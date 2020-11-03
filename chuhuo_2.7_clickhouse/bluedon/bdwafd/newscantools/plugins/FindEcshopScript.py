#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_url(http,ob,item):
    try:  
        result=[]
        if ob['site_type'] != 'php':
            return result
        url=item['url']
        if url[-1] !='/' or item['method'] !='get':
            return result
        if url.count('/') >5:
            return result 
        detail=u''
        detail=detail.encode('utf8')
        pathlist=['install/','admin/ecshopfiles.md5','admin/help/zh_cn/database.xml','admin/js/validator.js','admin/templates/about_us.htm','alipay.html','data/cycle_image.xml','data/flashdata/default/cycle_image.xml','demo/js/check.js','demo/templates/faq_en_us_utf-8.htm','demo/zh_cn.sql','themes/default/library/member.lbi','themes/default/style.css','themes/default_old/activity.dwt','install/data/data_en_us.sql','install/data/demo/zh_cn.sql','install/js/transport.js','install/templates/license_en_us.htm','js/transport.js','mobile/templates/article.html','themes/Blueocean/exchange_goods.dwt','themes/Blueocean/library/comments.lbi','themes/default_old/library/comments.lbi','wap/templates/article.wml','widget/blog_sohu.xhtml']
        for path in pathlist:			       	           
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("ecshop")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindEcshopScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindEcshopScript.py, run_domain function :" + str(e))
        return result

