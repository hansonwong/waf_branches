#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def run_url(http,ob,item):
    try:
        result = []
        if item['method'] != 'get':
            return []
        #end if
        if item['params'] != '':
            return []
        #end if
        if item['url'][-1] != '/':
            return []
        #end if
        
        url = item['url']
        
        list = ['upload.html','upload.htm']
        if ob['site_type'] == 'php':
            list.append('upload.php')
        elif ob['site_type'] == 'asp':
            list.append('upload.asp')
        elif ob['site_type'] == 'aspx':
            list.append('upload.aspx')
        elif ob['site_type'] == 'jsp':
            list.append('upload.jsp')
        else:
            list.extend(['upload.php','upload.asp','upload.aspx','upload.jsp'])
        #end if
        relist = ["%s%s" % (url,row) for row in list]
        relist = valid_urls(ob['domain'], relist)
        if not relist:
            return result

        detail = "在站点上检测到潜在的文件上传"
        for url in relist:
            #url = "%s%s" % (url,row)
            res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
            if res and res.has_key('status') and res['status'] == '200' and res.has_key('content-type') and res['content-type'] != '' and content != '' and content.find('input') >= 0 and content.find('file') >= 0 and content.find('type') >= 0:
                match = re.findall(r"<(\s*)input(\s+)type(\s*)=(\s*)('|\")file\5(.+?)>",content,re.I|re.DOTALL)
                if match and len(match) > 0:
                    request = getRequest(url)
                    response = getResponse(res)
                    output = "...<%sinput%stype%s=%s%sfile%s%s>..." % (match[0][0],match[0][1],match[0][2],match[0][3],match[0][4],match[0][4],match[0][5])
                    result.append(getRecord(ob,url,ob['level'],detail,request,response,output))
                #end if
            #end if
        #end for
        
        return result
    except Exception,e:
        logging.getLogger().error("File:CheckUploadFileScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CheckUploadFileScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def

