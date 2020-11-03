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
        #if url.find('.php') < 0 and url.find('.aspx') < 0 and url.find('.asp') < 0 and url.find('.jsp') < 0 and url.find('.do') < 0:
            #return []
        #end if
        i = -1
        for row in ('.html','.php','.aspx','.asp','.jsp','.do','.htm'):
            i = url.find(row)
            if i != -1:
                break
        if i == -1:
            return result
        #end if
        begin,end = url[:i] ,url[i:]
        begin_split = begin.split("/")
        
        list = ['_','.','~','old']
        relist = ["%s/%s%s%s" % ("/".join(begin_split[0:-1]),row,begin_split[-1],end) for row in list]
        relist = valid_urls(ob['domain'], relist)
        if not relist:
            return result
        
        detail = "开发者往往会将脚本文件的备用版本留在虚拟根目录中，例如，开头是“Copy of”、“_”、“.”、“~”和“Old”的文件。当请求这些文件时，它们会显示在浏览器中。这些文件可能包含现有脚本的备用版本或旧版本。"
        keys=[u'点击F5进行刷新',u'网页不存在',u'页面不存在']
        for new_url in relist:
            #new_url = "%s/%s%s" % ("/".join(url.split("/")[0:-1]),row,url.split("/")[-1])   #url like 'index.php/login' will be wrong
            #new_url = "%s/%s%s%s" % ("/".join(begin_split[0:-1]),row,begin_split[-1],end)
            res, content = requestUrl(http,new_url,ob['task_id'],ob['domain_id'])
            if res and res.has_key('status') and res['status'] == '200' and res.has_key('content-type') and res['content-type'] != '':
                for key in keys:
                    if content.find(key.encode('gbk'))>=0 or content.find(key.encode('utf8'))>=0:
                        return []
                    #end if
                #end for
                request = getRequest(new_url)
                response = getResponse(res)
                output = ""
                result.append(getRecord(ob,new_url,ob['level'],detail,request,response,output))
            #end if
        #end for
        
        if len(result) > 1:
            return []
        else:
            return result
        #end if
        
    except Exception,e:
        logging.getLogger().error("File:CheckFileReplaceScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CheckFileReplaceScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def

