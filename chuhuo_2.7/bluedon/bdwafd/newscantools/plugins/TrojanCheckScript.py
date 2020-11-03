#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *

def checkCssTrojan(url,content):
    try:
        detail = ""
        if content.find('document') < 0 and content.find('write') < 0 and content.find('writeln') < 0:
            return False,""
        #end if
        match = re.findall(r"document\.(write|writeln)\((.+?)\)",content,re.I|re.DOTALL)
        if match and len(match) > 0:
            for row in match:
                detail += "document.%s(%s)\n" % (row[0],row[1])
            #end for
            return True,detail
        #end if
    except Exception,e:
        logging.getLogger().error("File:TrojanCheckScript.py, checkCssTrojan function :" + str(e) + ", url:" + url)
    #end try
    return False,""
#end def

def checkJsTrojan(url,content):
    try:
        detail = ""
        content = content.lower().replace("\r\n","\n")
        list = content.split("\n")
        for row in list:
            '''
            if row.find('eval(') >= 0 or row.find('execute(') >= 0:
                detail += "%s\n" % (row)
                continue
            #end if
            '''
            if row.find("\\x69\\x66\\x72\\x61\\x6d\\x65") >= 0 or row.find('\\x49\\x46\\x52\\x41\\x4d\\x45') >= 0:
                detail += "%s\n" % (row)
                continue
            #end if
            if row.find("\\x68\\x74\\x74\\x70") >= 0 or row.find('\\x48\\x54\\x54\\x50') >= 0:
                detail += "%s\n" % (row)
                continue
            #end if
            
            '''
            if (row.find('document.write') >= 0 or row.find('document.writeln') >= 0) and row.find('iframe') >= 0:
                detail += "%s\n" % (row)
                continue
            #end if
            '''
            
            '''
            if row.find('window.open') >= 0:
                detail += "%s\n" % (row)
                continue
            #end if
            '''
                
        #end for
        if detail != "":
            return True,detail
        #end if
    except Exception,e:
        logging.getLogger().error("File:TrojanCheckScript.py, checkJsTrojan function :" + str(e) + ", url:" + url)
    #end try
    return False,""
#end def

def checkHtmlTrojan(url,content):
    try:
        detail = ""
        
        if content.find('iframe') > 0 or content.find('IFRAME') > 0:
            match = re.findall(r"<(\s*)iframe(.+?)>",content,re.I)
            if match and len(match) > 0:
                for row in match:
                    temp = row[1].replace("\"","").replace("'","")
                    '''
                    if temp.lower().find('width') > 0 and temp.lower().find('height') > 0:
                        match1 = re.findall(r"(\s+)width(\s*)=(\s*)0",temp,re.I)
                        match2 = re.findall(r"(\s+)height(\s*)=(\s*)0",temp,re.I)
                        if len(match1) > 0 and len(match2) > 0:
                            detail += "<iframe %s></iframe>\n" % (row[1])
                            continue
                        #end if
                    #end if
                    '''
                    if temp.find("\\x69\\x66\\x72\\x61\\x6d\\x65") >= 0 or temp.find('\\x49\\x46\\x52\\x41\\x4d\\x45') >= 0:
                        detail += "%s\n" % (row)
                        continue
                    #end if
                    if temp.find("\\x68\\x74\\x74\\x70") >= 0 or temp.find('\\x48\\x54\\x54\\x50') >= 0:
                        detail += "%s\n" % (row)
                        continue
                    #end if
                #end for
            #end if
        #end if
        
        
        if content.find('script') > 0 or content.find('SCRIPT') > 0:
            match = re.findall(r"<(\s*)script(.+?)>(.+?)<(\s*)/(\s*)script(\s*)>",content,re.I|re.DOTALL)
            if match and len(match) > 0:
                for row in match:
                    flag, keyword = checkJsTrojan(url,row[2])
                    if flag:
                        detail += keyword
                    #end if
                #end for
            #end if
        #end if
        
        '''
        if content.find('style') > 0 or content.find('STYLE') > 0:
            match = re.findall(r"<(\s*)style(\s*)>(.+?)<(\s*)/(\s*)style(\s*)>",content,re.I|re.DOTALL)
            if match and len(match) > 0:
                for row in match:
                    flag, keyword = checkCssTrojan(url,row[2])
                    if flag:
                        detail += keyword
                    #end if
                #end for
            #end if
        #end if
        '''
        
        if content.find('jscript.encode') >= 0 and (content.find('script') >= 0 or content.find('SCRIPT') >= 0):
            match = re.findall(r"<(\s*)script(.+?)>(\s*)<(\s*)/(\s*)script(\s*)>",content,re.I|re.DOTALL)
            if match and len(match) > 0: 
                for row in match:
                    temp = row[1].lower()
                    if temp.find('jscript.encode') >= 0:
                        detail += "<script%s></script>\n" % (row[1])
                    #end if
                #end for
            #end if
        #end if
        
        if detail != "":
            return True,detail
        #end if
        
    except Exception,e:
        logging.getLogger().error("File:TrojanCheckScript.py, checkHtmlTrojan function :" + str(e) + ", url:" + url)
    #end try
    return False,""
#end def

def run_url(http,ob,item):
    try:
        return []
        result = []
        if item['method'] != 'get':
            return []
        #end if
        parse = urlparse.urlparse(item['url'])
        if len(parse[2].split('/')) >= 3 and item['url'][-1] == '/':
            return []
        #end if
        
        url = ""
        if item['params'] == "":
            url = item['url']
        else:
            url = "%s?%s" % (item['url'],item['params'])
        #end if
        #请求页面内容
        res, content = requestUrl(http,url,ob['task_id'],ob['domain_id'])
        if content == "":
            return []
        #end if
        if res.has_key('content-location') and res['content-location'] == url:
            flag = False
            keyword = ""
            url_type = item['url'].split('.')[-1]
            if url_type == 'css':
                #flag, keyword = checkCssTrojan(url,content)
                pass
            elif url_type == 'js':
                flag, keyword = checkJsTrojan(url,content)
            else:
                flag, keyword = checkHtmlTrojan(url,content)
            #end if     
            if flag:
                detail = "在URL : %s 中发现疑似木马信息，请详细查看，内容为：\n %s 附近的源码" % (url, keyword)
                request = getRequest(url)
                response = getResponse(res)
                result.append(getRecord(ob,url,ob['level'],detail,request,response))
            #end if
            return result
        else:
            return []
        #end if
    except Exception,e:
        logging.getLogger().error("File:TrojanCheckScript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'] + ", url:" + item['url'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:TrojanCheckScript.py, run_url function :" + str(e)+ ", url:" + item['url'])
        return []
    #end try    
#end def

