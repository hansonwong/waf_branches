#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    try:
        domain = ob['domain']
        base_path = ob['base_path']
    
        url = "%s://%s%s" % (ob['scheme'],domain,base_path)
        header = {"Host":domain,"Connection":"Keep-alive","Accept":"text/plain","user-agent":"Baiduspider,Sogou,baidu,Sosospider,Googlebot,FAST-WebCrawler,MSNBOT,Slurp","Referer":"http://www.baidu.com/"}
        #res1, content1 = http.request(url)
        res1, content1 = yx_httplib2_request(http,url)
        #res2, content2 = http.request(url,"GET","",header)
        res2, content2 = yx_httplib2_request(http,url,"GET","",header)
        
        if res1.has_key('status') and res2.has_key('status') and res1['status'] == '200' and res2['status'] == '200':
            len1 = 0
            if res1.has_key('content-length'):
                len1 = int(res1['content-length'])
            else:
                len1 = len(content1)
            #end if
            
            len2 = 0
            if res2.has_key('content-length'):
                len2 = int(res2['content-length'])
            else:
                len2 = len(content2)
            #end if
            
            output = ""
            title2 = ""
            flag = False
            if len1 > 5000 and len2 > 5000:
                if abs(len2-len1) > 10000:
                    match1 = re.findall(r"<(\s*)title(\s*)>(.+?)<(\s*)/(\s*)title(\s*)>",content1,re.I|re.DOTALL)
                    match2 = re.findall(r"<(\s*)title(\s*)>(.+?)<(\s*)/(\s*)title(\s*)>",content2,re.I|re.DOTALL)
                    if len(match1) > 0 and len(match2) > 0 and match1[0][2] != '' and match2[0][2] != '' and match1[0][2] != match2[0][2]:
                        code1 = findCode(content1)
                        title1 = changeCode(match1[0][2],code1)
                        code2 = findCode(content2)
                        title2 = changeCode(match2[0][2],code2)
                        output = "普通请求长度：%s，特殊请求长度：%s\n普通请求标题：%s，特殊请求标题：%s" % (str(len1),str(len2),title1,title2)
                        flag = True
                    #end if
                #end if
            #end if
            
            if flag:
                list = []
                detail = "该网站可能已经被劫持，网站可能已经被恶意攻击者利用。"
                request = getRequest(url,"GET",header,"")
                if len2 > 4000:
                    content2 = content2[0:4000]
                #end if
                response = getResponse(res1) + "\n" + content2 + "\n" + title2
                list.append(getRecord(ob,url,ob['level'],detail,request,response,output))
                return list
            #end if
        #end if
        
    except Exception,e:
        logging.getLogger().error("File:PageHijackScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:PageHijackScript.py, run_domain function :" + str(e))
    #end try
    
    return []
#end def




