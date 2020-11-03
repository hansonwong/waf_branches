#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import httplib2
from lib.fast_request import fast_request
from lib.ex_httplib2 import *
from lib.common import *


class ScanCommon:
    def __init__(self,ob):
        try:
            self.ob = ob
            self.http = ex_httplib2(ob['rec'], ob['cookie'])
            self.http.httlib2_set_follow_redirects(False)
            self.http.httlib2_set_timout(ob['web_timeout'])
            
        except Exception,e:
            logging.getLogger().error("File:ScanCommonScript.py, ScanCommon.__init__:" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        #end try
    #end def
    
    def fixUrl(self,base_path,url):
        try:
            if url == "":
                return "%s" % (base_path)
            #end if
            if url[0] == '/':
                if url == '/':
                    return "%s" % (base_path)
                else:
                    return "%s%s" % (base_path,url[1:])
                #end if
            else:
                return "%s%s" % (base_path,url)
            #end if
        except Exception,e:
            logging.getLogger().error("File:ScanCommonScript.py, ScanCommon.fixUrl:" + str(e) + ",task id:" + self.ob['task_id'] + ",domain id:" + self.ob['domain_id'])
            return "%s%s" % (base_path,url)
        #end try
    #end def
    
    def getFullUrl(self,scheme,domain,base_path,url):
        try:
#-----start yinkun 2014-10-14  对IPv6地址做处理----------------------
            url_domain = ''
            if checkIpv6(domain):
                url_domain = '[' + domain + ']'
            else:
                url_domain = domain
#-----end-------------------------------------------------------------
            if url == "":
                return "%s://%s%s" % (scheme,url_domain,base_path)
            #end if
            if url[0] == '/':
                if url == '/':
                    return "%s://%s%s" % (scheme,url_domain,base_path)
                else:
                    return "%s://%s%s%s" % (scheme,url_domain,base_path,url[1:])
                #end if
            else:
                return "%s://%s%s%s" % (scheme,url_domain,base_path,url)
            #end if
        except Exception,e:
            logging.getLogger().error("File:ScanCommonScript.py, ScanCommon.getFullUrl:" + str(e) + ",task id:" + self.ob['task_id'] + ",domain id:" + self.ob['domain_id'])
            return "%s://%s%s%s" % (scheme,domain,base_path,url)
        #end try
    #end def
    
    def checkUrl(self,url,method):
        try:
            if url[-1] == '/':
                k = "web_dir1_status_for_%s_enable" % (method.lower())
                if self.ob[k] == '0':
                    return False
                #end if
            elif url.lower().find(".") >= 0:
                list = ['cgi','cfm','php','aspx','asp','html','inc','txt','jsp','xml','mdb','sql','nsf','bak','htx','rar','zip','pm','htm','pl','ini','cnf','htpasswd','cfg','exe','conf','dll','bas','dat','log','listprint','snp','cobalt','db','pwd','ida','idq','htw','btr','box','vts','htr','idc','do']
                for row in list:
                    if url.lower().find(".%s" % (row)) >= 0 and self.ob["web_%s_status_for_%s_enable" % (row,method.lower())] == '0':
                        return False
                    #end if
                #end for
                k = "web_dir2_status_for_%s_enable" % (method.lower())
                if self.ob[k] == '0':
                    return False
                #end if
                k = "web_html_status_for_%s_enable" % (method.lower())
                if self.ob[k] == '0':
                    return False
                #end if
            else:
                k = "web_dir2_status_for_%s_enable" % (method.lower())
                if self.ob[k] == '0':
                    return False
                #end if
            #end if
            
            return True
        except Exception,e:
            logging.getLogger().error("File:ScanCommonScript.py, ScanCommon.checkUrl:%s,task id:%s,domain id:%s,url:%s,method:%s" % (str(e),self.ob['task_id'],self.ob['domain_id'],url,method))
            return True
        #end try
    #end def
    
    def matchStatus(self,rule_obj):
        result = []
        try:
            fullurl = self.getFullUrl(self.ob['scheme'], self.ob['domain'], self.ob['base_path'], rule_obj['url'])
            if rule_obj['method'].lower() == 'get':
                #判断是否可以根据状态判断
                if self.ob['web_head_request_enable'] == '1':
                    if self.checkUrl(rule_obj['url'], "HEAD") == False:
                        return []
                    #end if
                else:
                    if self.checkUrl(rule_obj['url'], "GET") == False:
                        return []
                    #end if
                #end if
                
                if self.ob['web_head_request_enable'] == '1':
 #                  res, content = self.http.request(fullurl,"HEAD")
                    res, content = yx_httplib2_request(self.http,fullurl,"HEAD");
                else:
 #                  res, content = self.http.request(fullurl,"GET")
                    res, content = yx_httplib2_request(self.http,fullurl,"GET");
                #end if
                if res and res.has_key('status') and res['status'] == rule_obj['response'] and res.has_key('content-type') and res['content-type'] != "":
                    if res['status'] == '200':
                        content_length = 0
                        if res.has_key('content-length'):
                            content_length = int(res['content-length'])
                        else:
                            if content:
                                content_length = len(content)
                            else:
                                return []
                            #end if
                        #end if
                        if content_length in self.ob['len_404']:
                            return []
                        #end if
                        if content_length >= self.ob['web_404_len_range_min'] and content_length <= self.ob['web_404_len_range_max']:
                            return []
                        #end if
                    #end if
                    
                    '''
                    if res['status'] == '200' and res.has_key('content-length') and int(res['content-length']) in self.ob['len_404'] and int(res['content-length']) != 0:
                        return []
                    #end if
                    '''
                    
                    if self.ob['web_head_request_enable'] == '1':
#                       res1, content1 = self.http.request(fullurl,"GET")
                        res1, content1 = yx_httplib2_request(self.http,fullurl)
                        if res1 and res1.has_key('status') and res1['status'] == rule_obj['response'] and res1.has_key('content-type') and res1['content-type'] != "" and content1.find('http://www.safedog.cn/') < 0:
                            pass
                        else:
                            return []
                        #end if
                    #end if
                    request = ""
                    if self.ob['web_head_request_enable'] == '1':
                        request = getRequest(fullurl,"HEAD")
                    else:
                        request = getRequest(fullurl,"GET")
                    #end if
                    response = getResponse(res)
                    result.append(getRecord_cgidb(rule_obj,self.ob,fullurl,rule_obj['level'],"",request,response))
                #end if
                
                return result
                
                '''
                url = self.fixUrl(self.ob['base_path'], rule_obj['url'])
                fr = fast_request(self.ob['domain'], '/', self.ob['rec'], self.ob, self.ob['ssl_enable'])
                if self.ob['rec'].err_out():
                    return result
                #end if
                if fr.connectOK == False:                    
                    fr.connect() 
                #end if
                #判断是否支持head请求
                if self.ob['web_head_request_enable'] == '1':
                    #在支持head请求的情况下发送head请求
                    fr.req_url(url, 'HEAD', 512)
                else:
                    #在不支持head请求的情况下发送get请求
                    fr.req_url(url, 'GET', 512)
                #end if
                fr.close()
                if fr.code == rule_obj['response']:
                    #result.append(getRecord(self.ob,url,rule_obj['level'],rule_obj['detail'],fr.request_data,fr.response_data))
                    result.append(getRecord_cgidb(rule_obj,self.ob,fullurl,rule_obj['level'],"",fr.request_data,fr.response_data))
                    return result
                else:
                    return result
                #end if
                '''
            elif rule_obj['method'].lower() == 'post':
                return result
                '''
                PostData,PostUrl=self.Get_postdata()
                if PostUrl!='':
                    response,content=self.http.request(PostUrl,"POST",PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    if response.has_key('status') and response['status']==str(self.ScanMatching):
                        
                        return True,"",response
                    else:
                        
                        return False,"",""
                else:
                    return  False,"",""
                '''
            else:
                return result
            #end if
        except Exception,e:
            print rule_obj['url']
            logging.getLogger().error("File:ScanCommonScript.py, ScanCommon.matchStatus:" + str(e) + ",task id:" + self.ob['task_id'] + ",domain id:" + self.ob['domain_id'])
            return result
        #end try
    #end def
    
    def matchString(self,rule_obj):
        result = []
        try:
            #匹配字符串
            url = self.getFullUrl(self.ob['scheme'], self.ob['domain'], self.ob['base_path'], rule_obj['url'])
            if url.find("@RFIURL") >= 0:
                url = url.replace("@RFIURL",self.ob['rfi_url'])
            #end if
            method = rule_obj['method'].lower()
            if method == 'get':
#               res, content = self.http.request(url)
                res, content = yx_httplib2_request(self.http,url)
                if res and res.has_key('status') and res['status'] in ['200','500'] and content.find(rule_obj['response']) >= 0 and res.has_key('content-type') and res['content-type'] != "" and content.find('http://www.safedog.cn/') < 0:
                    if res['status'] == '200':
                        content_length = 0
                        if res.has_key('content-length'):
                            content_length = int(res['content-length'])
                        else:
                            if content:
                                content_length = len(content)
                            else:
                                return []
                            #end if
                        #end if
                        if content_length in self.ob['len_404']:
                            return []
                        #end if
                        if content_length >= self.ob['web_404_len_range_min'] and content_length <= self.ob['web_404_len_range_max']:
                            return []
                        #end if
                    #end if
                    
                    request = getRequest(url)
                    response = getResponse(res)
                    #result.append(getRecord(self.ob,url,rule_obj['level'],rule_obj['detail'],request,response))
                    result.append(getRecord_cgidb(rule_obj,self.ob,url,rule_obj['level'],"",request,response))
                #end if
            elif method == 'post':
                '''
                PostData,PostUrl=self.Get_postdata()
                if PostUrl!='':
                    response,content=self.http.request(PostUrl,"POST",PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    pcreobject = re.compile(self.ScanMatching,re.I)
                    m=pcreobject.search(content)
                    if m:
                        return True,"",response
                    else:
                        return False,"",""
                else:
                    return  False,"",""
                #end if
                '''
                return []
            else:
                return []
            #end if
        except Exception,e:
            logging.getLogger().error("File:ScanCommonScript.py, ScanCommon.matchString:" + str(e) + ",task id:" + self.ob['task_id'] + ",domain id:" + self.ob['domain_id'])
        #end try
        return result
    #end def
    
    def matchRegular(self,rule_obj):
        result = []
        try:
            #匹配正则表达式
            url = self.getFullUrl(self.ob['scheme'], self.ob['domain'], self.ob['base_path'], rule_obj['url'])
            if url.find("@RFIURL") >= 0:
                url = url.replace("@RFIURL",self.ob['rfi_url'])
            #end if
            method = rule_obj['method'].lower()
            if method == 'get':
                #res, content = self.http.request(url)
                res, content = yx_httplib2_request(self.http,url)
                if res and res.has_key('status') and res['status'] in ['200','500'] and res.has_key('content-type') and res['content-type'] != "" and content.find('http://www.safedog.cn/') < 0:
                    if res['status'] == '200':
                        content_length = 0
                        if res.has_key('content-length'):
                            content_length = int(res['content-length'])
                        else:
                            if content:
                                content_length = len(content)
                            else:
                                return []
                            #end if
                        #end if
                        if content_length in self.ob['len_404']:
                            return []
                        #end if
                        if content_length >= self.ob['web_404_len_range_min'] and content_length <= self.ob['web_404_len_range_max']:
                            return []
                        #end if
                    #end if
                    
                    pcre_obj = re.compile(rule_obj['response'],re.I)
                    match = pcre_obj.search(content)
                    if match:
                        request = getRequest(url)
                        response = getResponse(res)
                        result.append(getRecord_cgidb(rule_obj,self.ob,url,rule_obj['level'],"",request,response))
                    #end if
                #end if
            elif method == 'post':
                return []
            else:
                return []
            #end if
        except Exception,e:
            logging.getLogger().error("File:ScanCommonScript.py, ScanCommon.matchRegular:" + str(e) + ",task id:" + self.ob['task_id'] + ",domain id:" + self.ob['domain_id'])
        #end try
        return result
    #end def
    
    def start(self,rule_obj):
        try:
            result = []
            url = rule_obj['url']
            if url and len(url) > 2 and url[0:2] == "/?":
                return []
            #end if
            if url.find("../") != -1 or url.find("..\\") != -1:
                return []
            #end if
            
            if rule_obj['response_type'] == 1:
                #匹配状态码
                result = self.matchStatus(rule_obj)
            elif rule_obj['response_type'] == 2:
                #匹配字符串
                result = self.matchString(rule_obj)
            elif rule_obj['response_type'] == 3:
                #匹配正则表达式
                result = self.matchRegular(rule_obj)
            #end if
            
            if len(result) > 0:
                self.ob['find_vul_count'] += 1
            else:
                self.ob['find_vul_count'] -= 1
                if self.ob['find_vul_count'] < 0:
                    self.ob['find_vul_count'] = 0
                #end if
            #end if
            
            return result
            
        except Exception,e:
            logging.getLogger().error("File:ScanCommonScript.py, ScanCommon.start:" + str(e) + ",task id:" + self.ob['task_id'] + ",domain id:" + self.ob['domain_id'])
            write_scan_log(ob['task_id'],ob['domain_id'],"File:ScanCommonScript.py, ScanCommon.start:" + str(e))
            return []
        #end try
    #end def
#end class