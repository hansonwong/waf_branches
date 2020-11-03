#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import string

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = ""

        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl1 = "data/admin/ver.txt"#201210
        expurl2 = "member/login.php"#index_do.php?fmdo=user&dopost=regnew
        expurl3 = "plus/feedback.php"
        geturl1 = "%s%s" % (url,expurl1)
        geturl2 = "%s%s" % (url,expurl2)
        geturl3 = "%s%s" % (url,expurl3)
        res, content = requestUrl(http,geturl1,ob['task_id'],ob['domain_id'])
        ver=content.strip()
        if len(content) < 7 or len(content)>20:
            return []
        #end if
        ver=ver[0:6]
        try:
            verdate = int(ver)
            #verdate=string.atoi(ver)
        except ValueError:
            return []

        if verdate<201210:
            r, c = requestUrl(http,geturl2,ob['task_id'],ob['domain_id'])
            if r['status']=='200' and content.find("member/index_do.php?fmdo=user&dopost=regnew")>=0:
                r1, c1 = requestUrl(http,geturl3,ob['task_id'],ob['domain_id'])
                if r1['status']=='200' and content.find("DedeCMS")>=0:


                    request = getRequest(geturl3)
                    response = getResponse(res)
                    list.append(getRecord(ob,ob['scheme']+"://"+ob['domain']+ob['base_path'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:dedecmsFeedbackSqlInjection.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:dedecmsFeedbackSqlInjection.py, run_domain function :" + str(e))
    #end try

    return list
#end def