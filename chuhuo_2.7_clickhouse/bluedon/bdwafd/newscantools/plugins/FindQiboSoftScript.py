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
        pathlist=['install/','a_d/install/data.sql','admin/template/article_more/config.htm','admin/template/blend/set.htm','admin/template/center/config.htm','admin/template/cutimg/cutimg.htm','admin/template/foot.htm','admin/template/fu_sort/editsort.htm','admin/template/html/set.htm','admin/template/label/article.htm','admin/template/label/maketpl/1.htm','admin/template/module/make.htm','admin/template/mysql/into.htm','admin/template/sort/editsort.htm','form/admin/template/label/form.htm','guestbook/admin/template/label/guestbook.htm','hack/cnzz/template/ask.htm','hack/gather/template/addrulesql.htm','hack/upgrade/template/get.htm','member/template/blue/foot.htm','member/template/default/homepage.htm','template/default/cutimg.htm','template/special/showsp2.htm','wap/template/foot.htm']
        for path in pathlist:			             
            geturl="%s%s"%(url,path)
            res,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find("qiboSoft")>=0:
                request = getRequest(geturl)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
                break
        return result
    except Exception, e:
        logging.getLogger().error("File:FindQiboSoftScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:FindQiboSoftScript.py, run_domain function :" + str(e))
        return result

