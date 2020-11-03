#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import time
import json
import urllib

from lib.common import *
def get_post_request(url, post_data):

    if url.find("http://") != -1:
            d = url.replace("http://", "").split("/")[0]
            tmpurl =  url.replace("http://" + url.replace("http://", "").split("/")[0], "")
            if len(tmpurl) == 0:
                tmpurl = "/"
    elif url.find("https://") != -1:

        d = url.replace("https://", "").split("/")[0]
        tmpurl =  url.replace("https://" + url.replace("https://", "").split("/")[0], "")
        if len(tmpurl) == 0:
            tmpurl = "/"
    else:
        return ""
    #end if

    try:

        content = "POST" + " " + tmpurl + "  HTTP/1.1" + "\n"
        content += "Host: " + d + "\n"
        content += "Connection: Keep-alive" + "\n"
        content += "Accept: text/plain" + "\n"
        content += "Content-Length: %d" % int(len(post_data)) + "\n"
        content += "User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5" + "\n\n"
        content += post_data
        return content
    except Exception,e:
        print e
        return ""
    #end try
#end def

def GetXssCheck(http,ob,url):
    try:
        result = []
        if url == "":
            return result
        #end if
        res, content = requestUrl(http,url+"<script>alert(133)</script>",ob['task_id'],ob['domain_id'])
        if res and res.has_key('status') and res['status'] == '200' and res.has_key('content-type') and res['content-type'] != '' and content != "":
            flag, keyword = XssGetKeyWord(content,"<script>alert(133)</script>")
            if flag:
                detail = "%s%s" % (url,keyword)
                r,c=requestUrl(http,detail,ob['task_id'],ob['domain_id'])
                if c.find("<script>alert(133)</script>")<0:
                    detail = "%s%s" % (url,"<script>alert(133)</script>")
                request = getRequest(detail)
                response = getResponse(res)

                result.append(getRecord(ob,url+"<script>alert(133)</script>",ob['level'],detail,request,response))
            #end if
        #end if
        return result
    except Exception,e:
        logging.getLogger().error("File:XssScript.py, GetXssCheck function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + url)
        return []
    #end try
#end def


def run_url(http,ob,item):

    resultlist=[]

    try:
        tmp_url = urllib.unquote(item['url'])
        if item['params'] == "":
            return resultlist
        #end if
        if checkUrlType(tmp_url) == False:
            return resultlist
        #end if
        if item['method'] == 'get':

            url_list = []
            params = changeParams(item['params'])
            for row in params:
                url = "%s?%s" % (tmp_url,row)
                res = GetXssCheck(http,ob,url)
                if len(res) > 0:
                    resultlist.extend(res)
                #end if
            #end for
        elif item['method'] == 'post':
            print item['params']

            ret=[]

            #a=[{"type":"text","name":"user_","value":""},{"type":"password","name":"password","value":""},{"type":"text","name":"carid","value":""}]
            reject_key = ['__viewstate', 'ibtnenter.x', 'ibtnenter.y']
            par=json.read(item['params'])#字符串转成成list
            for i in par:#list

                #logging.getLogger().error(i)

                if i and len(i) > 0:

                    for k in i.keys():

                        if k=='name':

                            if i[k].lower() not in reject_key:

                                ret.append(i[k]+"=1111")

            post_data= "&".join(ret)
            #logging.getLogger().error(post_data)
            params = changeParams(post_data)
            response = ""
            request = ""
            for post_Data in params:
#                logging.getLogger().error("============================")
#                logging.getLogger().error(post_data)
                post_T_Data= post_Data+"<ScRiPt>alert(133)</ScRiPt>"
                print "*"*30
                print post_T_Data
                print "*"*30
                headers = {"Content-Type":"application/x-www-form-urlencoded"}
                #res,content = http.request(tmp_url, 'POST', post_T_Data, headers=headers)
                res,content = yx_httplib2_request(http,tmp_url, 'POST', post_T_Data, headers=headers)
                if res['status']=='404' or len(content) <= 0:
                    return []
                flag1, keyword1 = XssGetKeyWord(content,"<ScRiPt>alert(133)</ScRiPt>")
#                logging.getLogger().error("xxxxxxxxxxxxxxxxxxxxx")
#                logging.getLogger().error(flag1)
#                logging.getLogger().error(keyword1)
                if flag1:
#                    logging.getLogger().error("**************************")
#                    logging.getLogger().error(keyword1)
#Fix BUG #2348
                    #r,c = http.request(tmp_url, 'POST', post_Data+keyword1, headers=headers)
                    r,c = yx_httplib2_request(http,tmp_url, 'POST', post_Data+keyword1, headers=headers)
                    if c.find("<script>alert(133)</script>")<0:
                        keyword1="<script>alert(133)</script>"

                    detail = "漏洞参数："+post_Data+keyword1
                    request = get_post_request(tmp_url,post_Data+keyword1)
                    response = getResponse(res)
                    resultlist.append(getRecord(ob,tmp_url,ob['level'],detail,request,response))
            #end if


        #end if
    except Exception,e:
        logging.getLogger().error("File:XssScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:XssScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #ene  try

    if len(resultlist) > 1:
        tmpdetail = ""
        for r in resultlist:
            tmpdetail = tmpdetail + r["detail"] + "\n"
            #tmpdetail = tmpdetail +  "f"
        #end for

        ret = []
        url = tmp_url
        # if item['params'] == '':
        #     url = item['url']
        # else:
        #     url = "%s?%s" % (item['url'],item['params'])
        if item['method'] == 'get':
            url = "%s?%s" % (tmp_url,item['params'])
        #end if
        ret.append(getRecord(ob, url,ob['level'],tmpdetail,resultlist[0]["request"],resultlist[0]["response"]))
        resultlist = ret
    #end if

    return resultlist
#end def



