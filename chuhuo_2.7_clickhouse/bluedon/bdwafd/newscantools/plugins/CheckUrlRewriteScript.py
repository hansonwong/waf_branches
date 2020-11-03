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

        rewrite_url = ''

        if params == '':
            return []
        else:
            temp = params.split('&')
            flag = False
            for row in temp:
                if row.find('=') > 0 and row.split('=')[1].lower().find('http://') == 0:
                    rewrite_url= row.split('=')[1]
                    flag = True
                    break
                #end if
            #end for
        #end if
        url = "%s?%s" % (url,params)

        title1 = ""
        title2 = ""

        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if res.has_key('status') == False or res['status'] != '200':
            return []
        #end if
        match = re.findall(r"<(\s*)title(\s*)>(.+?)<(\s*)/(\s*)title(\s*)>",content,re.I|re.DOTALL)
        if match and len(match) > 0:
            title1 = match[0][2]
        #end if

        res, content = requestUrl(http,rewrite_url,ob['task_id'],ob['domain_id'])
        if res.has_key('status') == False or res['status'] != '200':
            return []
        #end if
        match = re.findall(r"<(\s*)title(\s*)>(.+?)<(\s*)/(\s*)title(\s*)>",content,re.I|re.DOTALL)
        if match and len(match) > 0:
            title2 = match[0][2]
        #end if

        if title1 == title2 and title1 != '':
            detail = "发现 http 参数会保留 URL 值，且会导致 Web 应用程序将请求重定向到指定的 URL。攻击者可以将 URL 值改成指向恶意站点，从而顺利启用网络钓鱼欺骗并窃得用户凭证。"
            request = getRequest(url)
            response = getResponse(res)
            result.append(getRecord(ob,url,ob['level'],detail,request,response,""))

            return result
        else:
            return []
        #end if

    except Exception,e:
        logging.getLogger().error("File:CheckUrlRewriteScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CheckUrlRewriteScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try
#end def

