#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from lib.common import *

def run_url(http,ob,item):
    try:
        result = []
        
        if item['method'] != 'post':
            return []
        #end if
        
        refer = item['refer']
        params = json.read(item['params'])
        
        flag = False
        for row in params:
            if row['type'] == 'password':
                flag = True
            #end if
            if row['type'] in ['file','textarea']:
                return []
            #end if
        #end for
        
        if flag:
            res, content = requestUrl(http,refer,ob['task_id'],ob['domain_id'])
            if res and res.has_key('status') and res['status'] == '200':
                if res.has_key('cache-control') and res['cache-control'].find('no-cache') >= 0:
                    return []
                #end if
                if res.has_key('pragma') and res['pragma'].find('no-cache') >= 0:
                    return []
                #end if
                if res.has_key('expires') and res['expires'] == '0':
                    return []
                #end if
                match = re.findall(r"<(\s*)meta(\s+)http-equiv(\s*)=(\s*)('|\")(.+?)\5(\s+)content(\s*)=(\s*)('|\")(.+?)\10(\s*)/(\s*)>",content,re.I|re.DOTALL)
                if match and len(match) > 0:
                    for row in match:
                        type = row[5].lower().replace(" ","")
                        value = row[10].lower().replace(" ","")
                        if type == 'cache-control' and value.find('no-cache') >= 0:
                            return []
                        elif type == 'pragma' and value.find('no-cache') >= 0:
                            return []
                        elif type == 'expires' and value == '0':
                            return []
                        #end if
                    #end for
                #end if
                
                detail = "不建议让 Web 浏览器保存任何登录信息，因为当有漏洞存在时，可能会危及这个信息。"
                request = getRequest(refer)
                response = getResponse(res)
                output = ""
                result.append(getRecord(ob,refer,ob['level'],detail,request,response,output))
            #end if
        #end if
        
        return result
    except Exception,e:
        logging.getLogger().error("File:CheckCacheAdminPageScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CheckCacheAdminPageScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def

