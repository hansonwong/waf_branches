#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import re

def run_url(http,ob,item):
    print "--==--==-==--==-===----"
    print ob['isstart']
    print "--==--==-==--==-===----"
    detail=""
    list=[]
    try:
        url=item['url'].lower()
       
        if url.find(".action")<0 and url.find(".do")<0:
            return []

        exp="?debug=command&expression=%22nvs_test%22"
        
        expurl="%s%s"%(item['url'],exp)
#        print expurl
        print "==============="
        #response, content = http.request(expurl)
        response, content = yx_httplib2_request(http,expurl)
#        print content
        if content.find("nvs_test")>=0 and response['status']=='200' and content.find("<html")<0:
            request = getRequest(expurl)
            response = getResponse(response)
            list.append(getRecord(ob,item['url'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:structs2_s2_008script.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:structs2_s2_008script.py, run_url function :" + str(e))
    #end try
    
    return list

