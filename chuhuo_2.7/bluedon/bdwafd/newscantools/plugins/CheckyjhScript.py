#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
        urltest = "%s://%s%s%s" % (ob['scheme'],ob['domain'],ob['base_path'],"UserFiles/1.asp;1(1).jpg")
        urltestFile = "%s://%s%s%s" % (ob['scheme'],ob['domain'],ob['base_path'],"UserFiles/File/1.asp;1(1).jpg")
        urltestImage = "%s://%s%s%s" % (ob['scheme'],ob['domain'],ob['base_path'],"UserFiles/Image/1.asp;1(1).jpg")
        
        r, c = requestUrl(http,urltest,ob['task_id'],ob['domain_id'])
        r1, c1 = requestUrl(http,urltestFile,ob['task_id'],ob['domain_id'])
        r2, c2 = requestUrl(http,urltestImage,ob['task_id'],ob['domain_id'])
        if r['status']=='500' and (c.lower().find("execute request")>=0 or c.lower().find("GIF89a")>=0):
            request = getRequest(urltest)
            response = getResponse(r)
            list.append(getRecord(ob,urltest,ob['level'],detail,request,response))
        if r['status']=='200' and (c.lower().find("eval request")>=0 or c.lower().find('execute request')>=0):
            request = getRequest(urltest)
            response = getResponse(r)
            list.append(getRecord(ob,urltest,ob['level'],detail,request,response))
#------------------------userfiles------------------------------------------------------
        if r1['status']=='500' and (c1.lower().find("execute request")>=0 or c1.lower().find("GIF89a")>=0):
            request = getRequest(urltestFile)
            response = getResponse(r1)
            list.append(getRecord(ob,urltestFile,ob['level'],detail,request,response))
        if r1['status']=='200' and (c1.lower().find("eval request")>=0 or c1.lower().find('execute request')>=0):
            request = getRequest(urltestFile)
            response = getResponse(r1)
            list.append(getRecord(ob,urltestFile,ob['level'],detail,request,response))
#------------------------file------------------------------------------------------
        if r2['status']=='500' and (c2.lower().find("execute request")>=0 or c2.lower().find("GIF89a")>=0):
            request = getRequest(urltestImage)
            response = getResponse(r2)
            list.append(getRecord(ob,urltestImage,ob['level'],detail,request,response))
        if r2['status']=='200' and (c2.lower().find("eval request")>=0 or c2.lower().find('execute request')>=0):
            request = getRequest(urltestImage)
            response = getResponse(r2)
            list.append(getRecord(ob,urltestImage,ob['level'],detail,request,response))
#------------------------Image------------------------------------------------------
    except Exception,e:
        logging.getLogger().error("File:checkyjhscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:checkyjhscript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
        
        
        

        