#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import urlparse
#http://neovante.com/
def run_url(http,ob,item):
   
    try:
        list = []

        isstart='0'
        responsedetail=''
        if item['params'] == "":

            return list
        if item['method'] == 'get' and item['params'].find("=")<0:

            return list
        #end if


        parse=urlparse.urlparse(item['url'])
        path=parse.path

        if path=="" or path=="/":

            return list
        path=path.lower()
        if path.find(".css")>=0 or path.find(".doc")>=0 or path.find(".txt")>=0 or path.find(".pdf")>=0:
            return list
        if item['method'] == 'get':



            url_list = []
            params = changeParams(item['params'])
            for row in params:
                url = "%s?%s" % (item['url'],row)
                url="%s'"%(url)
                #print "--===---============-"
                print url
                #print "--===---============-"
                res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
                if content.find("XPathException")>=0:
                    
                    request = getRequest(url)
                    response = getResponse(res)
                    list.append(getRecord(ob,url,ob['level'],"",request,response))
    except Exception,e:
        logging.getLogger().error("File:wordpresssqlinjectionscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
    #end try
    
    return list
                    
                