#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *


def run_domain(http,ob):
    result = []
    try:
        scheme = ob['scheme']
        domain = ob['domain']
        base_path = ob['base_path']
    
        url1 = "%s://%s%s%s" % (scheme,domain,base_path,"register.txt")
        url2 = "%s://%s%s%s" % (scheme,domain,base_path,"registration.txt")
#       res1, content1 = http.request(url1)
#       res2, content2 = http.request(url2)
        res1, content1 = yx_httplib2_request(http,url1)
        res2, content2 = yx_httplib2_request(http,url2)


        detail = "特定应用程序可能以直接明确的名称来存储敏感注册表信息，攻击者很容易猜测及检索这些名称"
        keys=[u'点击F5进行刷新',u'网页不存在',u'页面不存在',u'Authorization Required']
        if res1 and res1.has_key('status') and res1['status'] == '200' and res1.has_key('content-type') and res1['content-type'] != '' and content1 != '':
            for key in keys:
                if (content1.find('<html') >= 0 and content1.find('<head>') >= 0) or (content1.find(key.encode('gbk'))>=0 or content1.find(key.encode('utf8'))>=0) :
                    return []
                #end if
            #end for
            request = getRequest(url1)
            response = getResponse(res1)
            if len(content1) > 200:
                output = "%s......" % (content1[0:200])
            else:
                output = content1
            #end if
            result.append(getRecord(ob,url1,ob['level'],detail,request,response,output))
            
            return result
        #end if
        
        if res2 and res2.has_key('status') and res2['status'] == '200' and res2.has_key('content-type') and res2['content-type'] != '' and content2 != '':
            for key in keys:
                if (content2.find('<html') >= 0 and content2.find('<head>') >= 0) or (content2.find(key.encode('gbk'))>=0 or content2.find(key.encode('utf8'))>=0) :
                    return []
                #end if
            #end for
            request = getRequest(url2)
            response = getResponse(res2)
            if len(content2) > 200:
                output = "%s......" % (content2[0:200])
            else:
                output = content2
            #end if
            result.append(getRecord(ob,url2,ob['level'],detail,request,response,output))
            
            return result
        #end if
        
    except Exception,e:
        logging.getLogger().error("File:CheckRegisterScript.py, run_domain function :%s, task id:%s, scheme:%s, domain:%s, base_path:%s" % (str(e),ob['task_id'],ob['scheme'],ob['domain'],ob['base_path'])) 
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CheckRegisterScript.py, run_domain function :"+str(e))       
    #end try
    
    return result
#end def



