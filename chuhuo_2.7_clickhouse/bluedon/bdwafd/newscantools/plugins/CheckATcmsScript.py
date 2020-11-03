#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl= "User/images/css/css.css"
        expurl1="Plus/gg/js/ad_dialog.js"
        geturl="%s%s"%(url,expurl)
        geturl1="%s%s"%(url,expurl1)
        res, content = requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and (content.find('.ACT_btn {')>=0 or content.find("border-right:1px solid #BCBCBCborder-bottom:1px solid #BCBCBC;    border-left:2px solid #FEFEFE;")>=0):
            request = getRequest(geturl)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"//"+ob['domain']+ob['base_path'],ob['level'],detail,request,response))
        else:
            res1, content1 = requestUrl(http,geturl1,ob['task_id'],ob['domain_id'])
            if res1['status']=="200" and content1.find("var over=false,down=false,divleft,divtop,n;")>=0:
                request = getRequest(geturl1)
                response = getResponse(res1)
                list.append(getRecord(ob,ob['scheme']+"://"+ob['domain']+ob['base_path'],ob['level'],detail,request,response))
                
    except Exception,e:
        logging.getLogger().error("File:checkatcmsSCRIPT.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:checkatcmsSCRIPT.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def