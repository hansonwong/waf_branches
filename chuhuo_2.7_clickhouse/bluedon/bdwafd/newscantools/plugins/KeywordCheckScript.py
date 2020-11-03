#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
import sys
import os

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)

def run_url(http,ob,item):
    try:
        dic_file = sys_path("/www/dic/keyword_%s.dic" % (ob['user_id']))
        dic_list = []
        f = file(dic_file, "r+")
        lines = f.readlines()
        f.close()
        for line in lines:
            temp = line.replace("\r","").replace("\n","").strip()
            if temp == "":
                continue
            else:
                dic_list.append(temp)
            #end if
        #end for
        
        result = []
        if item['method'] == "get":
            if item['params'] != "":
                url = "%s?%s" % (item['url'],item['params'])
            else:
                url = item['url']
            #end if
            res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
            if content == "":
                return []
            #end if
            #print url
            if ob['content_code'].lower() != 'utf8' and ob['content_code'].lower() != 'utf-8' and ob['content_code'] != '':
                try:
                    content = content.decode(ob['content_code'].lower()).encode('utf8')
                except Exception,e1:
                    logging.getLogger().debug("File:KeywordCheckScript.py, run_url function :" + str(e1) + " , url : " + url)
                #end try
            #end if
            request = getRequest(url)
            response = getResponse(res)
            match_list = []
            for row in dic_list:
                try:
                    row = row.decode('utf8').encode('utf8')
                except Exception,e1:
                    logging.getLogger().debug("File:KeywordCheckScript.py, run_url function :" + str(e1))
                #end if
                if content.find(row) >= 0:
                    match_list.append(row)
                #end if    
            #end for
            if len(match_list) <= 0:
                return []
            #end if
            detail = "URL : %s ， 包含关键字：%s。" % (url,",".join(match_list))
            result.append(getRecord(ob,url,ob['level'],detail,request,response))
        #end if
        
        return result
    except Exception,e:
        logging.getLogger().error("File:KeywordCheckScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:KeywordCheckScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def

