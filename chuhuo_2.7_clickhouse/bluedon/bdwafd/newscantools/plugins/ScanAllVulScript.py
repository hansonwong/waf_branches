#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import httplib2
#from urlparse import urlparse
from lib.fast_request import fast_request
from lib.common import *
import re


class ScanAllVul:
    
    
    def __init__(self,rule_obj,domain,RequestFile,ScanType,HttpType,ScanMatching,ob,connect_count):
        try:
            
#-------start 2014-10-14  yinkun 对IPv6地址做处理（添加"[]"）--------------
            self.domain = ''
            if checkIpv6(domain):
                self.domain = '[' + domain + ']'
            else:
                self.domain = domain
#-------end----------------------------------------------------------------
            self.rule_obj=rule_obj
#            print self.domain
            self.url="%s%s"%("http://",self.domain)#带http://的域名
#            print self.url
            if RequestFile[0]!='/':
                
                self.RequestFile="/%s"%(RequestFile)#请求的文件
            else:
                self.RequestFile="%s"%(RequestFile)
#            print self.RequestFile
            self.RequestUrl="%s%s"%(self.url,self.RequestFile)#最终要请求的url

            self.ScanType=ScanType
#            print self.ScanType
            self.HttpType=HttpType
#            print self.HttpType
            self.ScanMatching=str(ScanMatching)
#            print self.ScanMatching
            http=httplib2.Http()
            self.http=http
            self.Result=False
            self.req_method='HEAD'
            #self.no_code_count=0
            self.max_request=50
            self.no_code_count = 0
            self.ob=ob
            self.rec = ob["rec"]
            self.isForce = ob['isForce']
            self.web_speed = ob["web_speed"]
            self.web_minute_package_count = ob["web_minute_package_count"]
            self.ssl_enable = False
            if ob['scheme'] == 'https':
                self.ssl_enable = True
            self.connect_count=connect_count
        except Exception,e:
            print e
        #end try
    #end def





 
    def Check_WebStatus(self):#检测状态码是否需要继续执行
    
        IsRun=''

        try:
            fr = fast_request(self.domain, "/", self.rec, self.ob, self.ssl_enable)
            fr.connect()
            fr.req_url("/dfseoewioiewoiewoiewoijijoewoddsljkda.html", "HEAD", 512)
            fr.close()
            #print fr.code
            if fr.code == "200" :
                IsRun='0'
            else:
                IsRun='1'
            #end if 
        except Exception,e:
            logging.getLogger().error(" ScanVulScript.check_if_support_head" + str(e))
        return IsRun
        #end try
    #end def
       


            
    def Check_Response_Statuscode(self):#返回状态码识别
        '''
        根据状态码进行匹配
        '''
        try:
    
#            if self.check_if_support_head():
#                self.req_method = "HEAD"
#            else:
#                self.req_method = "GET"
            IsRun=self.Check_WebStatus()
            if IsRun=='0':
                return False
         
            if self.HttpType=='GET':#ISrun=''时也是跑返回状态码的
                if self.req_method == "HEAD":
                    #print "HEAD---Check_Response_Statuscode--%s"%(self.RequestFile)
                   
                    fr = fast_request(self.domain, '/', self.rec, self.ob, self.ssl_enable)
                    
                    
                    #if self.rec.err_out() and not self.isForce:
                        #return False,"",""
                    if fr.connectOK == False: 
                                   
                        fr.connect() 
                    
#                    if self.connect_count >= self.max_request:
#                        fr.close()
#                        fr.connect()
#                        self.connect_count= 0
#                        #end if
#                
#                    self.connect_count=self.connect_count+1
                    prev =time.time()
                    fr.req_url(self.RequestFile, self.req_method, 512)

                    #end if
                    fr.close()
                    self.connect_count=self.connect_count+1
            
                    if fr.code==self.ScanMatching:
                    
                        return True,fr.request_data, fr.response_data
                    else:
                        return False,"",""
                    #end if
                    if flowControl(self,time.time()-prev,self.rec,self.isForce,self.web_speed,self.web_minute_package_count,False):
                        return False,"",""
                    #end if
                else:
                    #print "get--Check_Response_Statuscode---%s"%(self.RequestFile)
                    fr = fast_request(self.domain, '/', self.rec, self.ob, self.ssl_enable)
                    #if self.rec.err_out() and not self.isForce:
                        #return False,"",""
                    if fr.connectOK == False: 
                                   
                        fr.connect() 
#                    if self.connect_count >= self.max_request:
#                        fr.close()
#                        fr.connect()
#                        self.connect_count= 0
#                        #end if
#                
#                    self.connect_count=self.connect_count+1
                    prev =time.time()
                    fr.req_url(self.RequestFile, self.req_method, 512)
                    fr.close()
                    
                    if fr.code==self.ScanMatching:
                    
                        return True,fr.request_data, fr.response_data

                    else:
                        return False,"",""
                    #end if
                    if flowControl(self,time.time()-prev,self.rec,self.isForce,self.web_speed,self.web_minute_package_count,False):
                        return False,"",""
                    #end if
            else:
                #print "POST--Check_Response_Statuscode---%s"%(self.RequestFile)
                PostData,PostUrl=self.Get_postdata()
                if PostUrl!='':
                    #response,content=self.http.request(PostUrl,"POST",PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,PostUrl,"POST",PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    if response.has_key('status') and response['status']==str(self.ScanMatching):
                        
                        return True,"",response
                    else:
                        
                        return False,"",""
                else:
                    return  False,"",""
        except Exception,e:
                #print e
                return False,"",""
        #end try
    #end def
    
    


       
            
    def Check_Response_String(self):
        '''
        该函数是根据返回的字符串进行匹配
        
        '''
        if self.HttpType=='GET':
            print "get--Check_Response_String---%s"%(self.RequestFile)
            if self.RequestFile.find("@RFIURL")>=0:
                
                self.RequestFile=self.RequestFile.replace("@RFIURL", self.ob['rfi_url'])
                self.RequestUrl=self.RequestUrl.replace("@RFIURL", self.ob['rfi_url'])
            #r,c=self.http.request(self.RequestUrl)
            r,c=yx_httplib2_request(self.http,self.RequestUrl)
            if c.find(self.ScanMatching)>=0:
                return True,"",r
            else:
                return False,"",""

#        try:
#            if self.HttpType=='GET':
#                print "get--Check_Response_String---%s"%(self.RequestFile)
#           
#                if self.RequestFile.find("@RFIURL")>=0:
#                    self.RequestFile=self.RequestFile.replace("@RFIURL", self.ob['rfi_url'])
#                    self.RequestUrl=self.RequestUrl.replace("@RFIURL", self.ob['rfi_url'])
#                fr = fast_request(self.domain,'/', self.rec, self.ob, self.ssl_enable)
#                if self.rec.err_out():
#                    return False,"",""
#                if fr.connectOK == False:
#                    fr.connect()
##                if self.connect_count >= self.max_request:
##                    fr.close()
##                    fr.connect()
##                    self.connect_count= 0
##                #end if
##                
##                self.connect_count=self.connect_count+1
#                
#                recv_data = fr.req_url(self.RequestFile, "GET", 2048)
#                fr.close()
#                
#                
#                if self.ScanMatching=="@RFIURL_RESPONSE":
#                    self.ScanMatching=self.ob['rfi_keyword']
#                if (fr.code=='200' or fr.code=='500') and recv_data.find(self.ScanMatching)>=0:
#                    return True,fr.request_data, fr.response_data
#                else:
#                    return False,"",""
#                    
#            else:
#                print "POST--Check_Response_String---%s"%(self.RequestFile)
#
#                PostData,PostUrl=self.Get_postdata()
#                
#                if PostUrl!='':
#                    response,content=self.http.request(PostUrl,"POST",PostData,{"Content-Type":"application/x-www-form-urlencoded"})
#                    if response.has_key('status') and content.find(self.ScanMatching)>=0 and (response['status']=='200' or response['status']=='500'):
#                        return True,"",response
#                    else:
#                        return False,"",""
#                else:
#                    
#                    return False,"",""
#                    
#        except Exception,e:
#            logging.getLogger().error(" ScanVulScript.Check_Response_String" + str(e))
#            return False,"",""
#        #end tyr
#    #end def
        
        


    def Check_Response_Pcre(self):#返回正则识别
#        print "正则正则"
        try:
            if self.HttpType=='GET':
                fr = fast_request(self.domain, '/', self.rec, self.ob, self.ssl_enable)
                #if self.rec.err_out() and not self.isForce:
                    #return False,"",""
                if fr.connectOK == False:
                    fr.connect()
                    
#                if self.connect_count >= self.max_request:
#                    fr.close()
#                    fr.connect()
#                    self.connect_count= 0
#                #end if
#                
#                self.connect_count=self.connect_count+1
                prev =time.time()
                recv_data = fr.req_url(self.RequestFile, "GET", 2048)
                fr.close()
               
                print "get--Check_Response_Pcre---%s"%(self.RequestFile)
                pcreobject = re.compile(self.ScanMatching,re.I)

                m=pcreobject.search(recv_data)
                if m and fr.code=='200':
                    return True,fr.request_data, fr.response_data
                else:
                    return False,"",""
                #end if
                if flowControl(self,time.time()-prev,self.rec,self.isForce,self.web_speed,self.web_minute_package_count,False):
                    return False,"",""
                #end if
            else:
                print "POST--Check_Response_Pcre---%s"%(self.RequestFile)
                print"POST正则匹配 ",self.RequestUrl,"vul_id:"+self.rule_obj['vul_id']  
                PostData,PostUrl=self.Get_postdata()
                if PostUrl!='':
                    #response,content=self.http.request(PostUrl,"POST",PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,PostUrl,"POST",PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                

                    pcreobject = re.compile(self.ScanMatching,re.I)
           
                    m=pcreobject.search(content)
                    if m:
                        return True,"",response
                    else:
                        return False,"",""
                else:
                    return  False,"",""
        except Exception,e:
            logging.getLogger().error(" ScanVulScript.Check_Response_Pcre" + str(e))
            return False,"",""
        #end try
    #end def
    
    
    

    
    def check_if_support_head(self):
        
        try:
            fr = fast_request(self.domain, "/", self.rec, self.ob, self.ssl_enable)
            fr.connect()
            fr.req_url("/", "HEAD", 512)
            fr.close()
            #print fr.code
            if fr.code == "200" or fr.code == "301" or fr.code == "302" or fr.code == "403":
                return True
            else:
                return False
            #end if 
        except Exception,e:
            logging.getLogger().error(" ScanVulScript.check_if_support_head" + str(e))
            return False
        #end try
    #end def
       

               
    def Get_postdata(self):
        PostData=''
        PostUrl=''
        try:
            parsed=urlparse(self.RequestUrl)
            PostData=parsed.query
            PostUrl="%s%s%s"%(parsed.scheme,parsed.netloc,parsed.path)
        except Exception,e:
            logging.getLogger().error(" ScanVulScript.Get_postdata" + str(e))
        return PostData,PostUrl
        #end tyr
    #end def
    
    

    def getheadrequest(self):
        if self.ob['cookie']!='':
            request_data = '%s %s HTTP/1.1\r\nHost: %s\r\nConnection:Keep-Alive\r\nCookie: %s\r\n\r\n' % (self.req_method, self.RequestFile, self.domain, self.ob['cookie'])
        else:
            request_data = '%s %s HTTP/1.1\r\nHost: %s\r\nConnection:Keep-Alive\r\n\r\n' % (self.req_method, self.RequestFile, self.domain)
        #end if
        return request_data
    #end def
    
    
    
    
    def Audit(self):
        try:
            if self.ScanType==1:
                self.Result,req,res=self.Check_Response_Statuscode()
                
            if self.ScanType==2:
                self.Result,req,res=self.Check_Response_String()
              

            if self.ScanType==3:
                
                self.Result,req,res=self.Check_Response_Pcre()
                
            if self.Result:

                if self.req_method=='HEAD':
                    request=self.getheadrequest()
                if self.req_method=='GET':
                    request=req
        
                response=res
                
                return getRecord_cgidb(self.rule_obj,self.ob,self.RequestUrl,self.rule_obj['level'],'',request,response)
            else:
            
                return ""
        except Exception,e:
            print self.Result
            logging.getLogger().error(" ScanVulScript.Audit" + str(e))
            return ''
        #end try
    #end def
        
        

        
def ScanAll(rule_obj,RequestFile,ScanType,HttpType,ScanMatching,ob,connect_count):
    '''
    rule_obj:存放所需数据的字典
    RequestFile：所请求的文件
    ScanType：   扫描类型 1：返回码 2：字符串 3：正则
    HttpType ：HTTP请求类型get? post?
    ScanMatching:  匹配字符串  ==状态码？字符串？正则？
    ob: 存放所需数据的字典
    '''

    try:
        
    
        
        
        return isvul
         
    except Exception,e:
        logging.getLogger().error(" ScanVulScript.ScanAll" + str(e))
        return ''
    #end try
#end try
            