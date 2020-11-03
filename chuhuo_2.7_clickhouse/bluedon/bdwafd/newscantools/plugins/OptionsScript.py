#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_domain(http,ob):
    try:
        domain = ob['domain']
        base_path = ob['base_path']
    
        url = "%s://%s%s" % (ob['scheme'],ob['domain'],ob['base_path'])
        #res, content = http.request(url,"OPTIONS")
        res, content = yx_httplib2_request(http,url,"OPTIONS")
        list = []
        methodlist=['PUT','PROPFIND','DELETE','MKCOL','LOCK','UNLOCK','PROPPATCH','SEARCH','COPY','MOVE']
        if res.has_key('status') and res['status'] == '200':
            temp = []
            if res.has_key('allow'):
                temp.extend(res['allow'].split(','))
            #end if
            '''
            if res.has_key('public'):
                temp.extend(res['public'].split(','))
            #end if
            '''
            for row in temp:
                row = row.strip()
                if row in methodlist and row not in list:
                    list.append(row)
                #end if
            #end for
            if len(list) > 0:
                url = "%s://%s%s" % (ob['scheme'],domain,base_path)
                detail = u'该域名危险的HTTP请求类型：'
                detail = detail.encode('utf-8')
                detail = "%s %s" % (detail,' , '.join(list))
                request = getRequest(url,"OPTIONS")
                response = getResponse(res)
                    
                list = []
                results=''
                if  ob['isstart']=='1':
                    results=audit(http,ob)
                if  results!='':
                    detail="%s\n%s%s"%(detail,"\n验证性扫描结果：\n文件写入成功，URL为：",results)
                list.append(getRecord(ob,url,ob['level'],detail,request,response))
                
                    
                    
                    
                    
                    
                    
                return list
            #end if
        #end if
    except Exception,e:
        logging.getLogger().error("File:OptionsScript.py, run_domain function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:OptionsScript.py, run_domain function :" + str(e))
    #end try
    
    return []
#end def
def audit(http,ob):
    try:
        
        url = "%s://%s/" % (ob['scheme'],ob['domain'])
        headers={"Host": ob['domain'],"User-Agent":" Mozilla/5.0 (Windows NT 5.1; rv:14.0)\
        Gecko/20100101 Firefox/14.0.1","Accept":" text/html,application/xhtml+xml,application/xml;q=0.9,\
        */*;q=0.8","Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3","Accept-Encoding":" gzip, \
        deflate","Connection": "keep-alive"}
        data="This is a test file created by NVS"
        #r,c=http.request("%s%s"%(url,"/nvs_puttestfile.txt"),"PUT",data,headers)
        #r1,c1=http.request("%s%s"%(url,"/nvs_puttestfile.txt"))
        r,c=yx_httplib2_request(http,"%s%s"%(url,"/nvs_puttestfile.txt"),"PUT",data,headers)
        r1,c1=yx_httplib2_request(http,"%s%s"%(url,"/nvs_puttestfile.txt"))
        if r1['status']=='200' and c1.find("This is a test file created by NVS")>=0:
            return "%s%s"%(url,"/nvs_puttestfile.txt")
        else:
            return ""
    except Exception,e:
        logging.getLogger().error("optionscript.audit"+str(e))
        return ""



