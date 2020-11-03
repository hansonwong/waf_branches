#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from lib.common import *


def checkWebShell(content,site_type):
    try:
        if content and len(content) < 5000 and content.find('form') > 0 and content.find('input') > 0:
            #if site_type == 'php' or site_type == 'jsp':
                form_content = ""
                other_content = ""
                if content.find('body') > 0:
                    match = re.findall(r"<(\s*)body(.*?)>(.*?)<(\s*)form(.+?)>(.+?)<(\s*)/(\s*)form(\s*)>(.*?)<(\s*)/(\s*)body(\s*)>",content,re.I|re.DOTALL)
                    if len(match) == 1:
                        form_content = match[0][5]
                        other_content = match[0][2] + match[0][9]
                else:
                    match = re.findall(r"(\s*)(.*?)(\s*)<(\s*)form(.+?)>(.+?)<(\s*)/(\s*)form(\s*)>(\s*)(.*?)(\s*)",content,re.I|re.DOTALL)
                    if len(match) == 1:
                        form_content = match[0][5]
                        other_content = match[0][1] + match[0][10]

                match = re.findall(r"<(\s*)input(.+?)type(\s*)=(\s*)(\"|')?(text|password)(\5)?(.+?)>",form_content,re.I|re.DOTALL)

                if match and len(other_content) < 50:
                    return True


            #elif site_type =='asp' or site_type == 'aspx':
                match = re.findall(r"<(\s*)input(.+?)type(\s*)=(\s*)(\"|')?(text|password)(\5)?(.+?)>",content,re.I|re.DOTALL)
                if match:
                    if content.find('window.onerror=killErrors;function yesok(){if (confirm') > 0 and content.find('top.hideform.FName.value += "||||"+DName;}else if(FAction==') > 0:
                        return True
        #end if (content <5000)
        else:
            if re.search(r"[^0-9.](10|172|192)\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])[^0-9.]",content,re.DOTALL) and re.search(r"<(\s*)input(.*?)type(\s*)=(\s*)(\"|')?(file|text)(\5)?(.+?)>",content) and re.search(r"[rwx-]{9}",content,re.I):
                return True

        return False
    except Exception,e:
        logging.getLogger().error("File:WehShellCheckScript.py, checkWebShell function :" + str(e))
        return False
    #end try
#end def

def run_url(http,ob,item):
    try:
        url = item['url']
        if not url.endswith('/'):
            return []


        dic_file = "/var/www/dic/webshell_%s.dic" % (ob['user_id'])
        dic_list = []
        f = file(dic_file, "r+")
        lines = f.readlines()
        f.close()
        for row in lines:
            dic_list.append(row.replace(" ","").replace("\r","").replace("\n",""))
        #end for

        webshell_dic = []
        if ob['site_type'] == 'php':
            for row in dic_list:
                webshell_dic.append("%s.php" % (row))
            #end for
        elif ob['site_type'] == 'asp':
            for row in dic_list:
                webshell_dic.append("%s.asp" % (row))
                webshell_dic.append("%s.aspx" % (row))
                webshell_dic.append("%s.cer" % (row))
                webshell_dic.append("%s.asa" % (row))
            #end for
        elif ob['site_type'] == 'aspx':
            for row in dic_list:
                webshell_dic.append("%s.asp" % (row))
                webshell_dic.append("%s.aspx" % (row))
                webshell_dic.append("%s.cer" % (row))
                webshell_dic.append("%s.asa" % (row))
        elif ob['site_type'] == 'jsp':
            for row in dic_list:
                webshell_dic.append("%s.jsp" % (row))
            #end for
        #end if
        #
        webshell_dic = ["%s%s" % (url,row) for row in webshell_dic]
        webshell_dic = valid_urls(ob['domain'], webshell_dic)
        if not webshell_dic:
            return []

        result = []
        detail = "URL：{url} 疑似为一个WebShell，请详细检查！"

        '''
        if item['method'] == "post" and item['params'] != "":
            params = json.read(item['params'])
            if len(params) == 1 and params[0]['type'] == "password":
                res, content = requestUrl(http,item['refer'],ob['task_id'],ob['domain_id'])
                request = getRequest(item['refer'])
                response = getResponse(res)
                result.append(getRecord(ob,item['refer'],ob['level'],detail.replace("{url}", item['refer']),request,response))
            #end if
        #end if
        '''

        if item['method'] == "get":
            if item['url'][-1] == '/':
                if item['params'] == "":
                    match_list = webshell_dic
                    for url in match_list:
                        #url = "%s%s" % (item['url'],row)
                        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
                        if content and checkWebShell(content,ob['site_type']) and res['status']=='200':
                            request = getRequest(url)
                            response = getResponse(res)
                            result.append(getRecord(ob,url,ob['level'],detail.replace("{url}", url),request,response))
                        #end if
                    #end for
                #end if
#            else:
#                if item['url'].find('php') > 0 or item['url'].find('jsp') > 0 or item['url'].find('asp') > 0 or item['url'].find('aspx') > 0 or item['url'].find('cer') > 0 or item['url'].find('asa') > 0:
#                    url = ""
#                    if item['params'] != "":
#                        url = "%s?%s" % (item['url'],item['params'])
#                    else:
#                        url = item['url']
#                    #end if
#                    res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
#                    if content and checkWebShell(content,ob['site_type']):
#                        request = getRequest(url)
#                        response = getResponse(res)
#                        result.append(getRecord(ob,url,ob['level'],detail.replace("{url}", url),request,response))
#                    #end if
                #end if
                '''
                if item['url'].find('asp;') > 0 or item['url'].find('aspx;') > 0 or item['url'].find('cer;') > 0 or item['url'].find('asa;') > 0:
                    url = ""
                    if item['params'] != "":
                        url = "%s?%s" % (item['url'],item['params'])
                    else:
                        url = item['url']
                    #end if
                    res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
                    request = getRequest(url)
                    response = getResponse(res)
                    result.append(getRecord(ob,url,ob['level'],detail.replace("{url}", url),request,response))
                else:
                    url = ""
                    if item['params'] != "":
                        url = "%s?%s" % (item['url'],item['params'])
                    else:
                        url = item['url']
                    #end if
                    #print url
                    res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
                    if content and checkWebShell(content):
                        request = getRequest(url)
                        response = getResponse(res)
                        result.append(getRecord(ob,url,ob['level'],detail.replace("{url}", url),request,response))
                    #end if
                #end if
                '''
            #end if
        #end if

        return result
    except Exception,e:
        logging.getLogger().error("File:WehShellCheckScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        return []
    #end try
#end def



