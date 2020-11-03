#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import httplib2
class Blindsqlclass:
    def __init__(self,http,url,ob):
        try:
            self.vuldict={}
            self.url=url
            self.http=httplib2.Http()
            self.responseinit,self.contentinit=yx_httplib2_request(self.http,self.url)
            self.leninit=len(self.contentinit)
            self.ob=ob
            #print self.leninit
            
        except Exception,e:
            print str(e)
            #return False
    
    def auditint(self,url):
        try:
            
            firststr="%20AnD%202121=2121"
            firsturl="%s%s"%(url,firststr)
            #print firsturl
            
#           response,content=self.http.request(firsturl)
            response,content = yx_httplib2_request(self.http,firsturl)
            #print content
            firstlen=len(content)
            
            secstr="%20AnD%202121=2122"
            securl="%s%s"%(url,secstr)
#            r,c=self.http.request(securl)
            r,c = yx_httplib2_request(self.http,securl)
            seclen=len(c)
            getkey=self.GetKey(c)
            if getkey:
                if content.find(getkey)>=0 and c.find(getkey)<0 and response['status']=='200' and (r['status']=='200' or r['status']=='500'):
                    if firstlen>seclen:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
            #END IF 
        except Exception,e:
            print str(e)
            return False
                
            

    def auditstr(self,url):
        try:
            
            firststr="%27AnD%272121%27=%272121"
            firsturl="%s%s"%(url,firststr)
            #print firsturl
            
            response,content=yx_httplib2_request(self.http,firsturl)
#            print content
            firstlen=len(content)
            
            secstr="%27AnD%272121%27=%272122"
            securl="%s%s"%(url,secstr)
            r,c=yx_httplib2_request(self.http,securl)
            seclen=len(c)
            getkey=self.GetKey(c)
            if getkey:
                if content.find(getkey)>=0 and c.find(getkey)<0 and response['status']=='200' and (r['status']=='200' or r['status']=='500'):
                    if  firstlen>seclen:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
            #END IF 
        except Exception,e:
            print str(e)
            return False
    def audit(self,url):
        
        detail=""
        try:
            
            if self.auditint(url):
                print "blind sqlinj for int type"
                request = getRequest("%s and 1=1"%(url))
                response = getResponse(self.responseinit)
                detail="此注入类型数字型盲注"
                self.vuldict = {'url':url,'detail':"存在注入的URL:%s\n此注入类型数字型盲注"%(url),'request':request,'response':response}
                return self.vuldict
            elif self.auditstr(url):
                detail="此注入类型字符型盲注"
                print "blind sqlinj for str type"
                request = getRequest("%s'and'1'='1"%(url))
                response = getResponse(self.responseinit)
                self.vuldict = {'url':url,'detail':"存在注入的URL:%s\n此注入类型字符型盲注"%(url),'request':request,'response':response}
                return self.vuldict
            else:
                print "dont find sqlinj"
                
        except Exception,e:
                print str(e)
        return self.vuldict
                
        
        
    
    
    def GetKey(self,contenterror):
            try:
                listkey=[]
                contentlist=self.contentinit.split("\r\n")
                for i in contentlist:
                    if contenterror.find(i)<0:
                        listkey.append(i)
                        if len(listkey)>=2:
                            return listkey[1]
                        if len(listkey)==1:
                            return listkey[0]
               
            except Exception,e:
                print str(e)
                return None
        #end def

def run_url(http,ob,item):
    res=[]
    try:
        list = []
        isstart='0'#标志位为0表示不启动验证性扫描，反之启动验证性扫描
        responsedetail=''
        if item['params'] == "":
            return list
        if item['method'] == 'get' and item['params'].find("=")<0:
            return list
        #end if
        parse=urlparse.urlparse(item['url'])
        path=parse.path
        if path=="" or path=="/":
            return list
        path=path.lower()
        if path.find(".css")>=0 or path.find(".doc")>=0 or path.find(".txt")>=0 or path.find(".pdf")>=0:
            return list
        if item['method'] == 'get':
            url_list = []
            params = changeParams(item['params'])
            for row in params:
                url = "%s?%s" % (item['url'],row)
                print url
                bindsql=Blindsqlclass(http,url,ob)
                print
                ret=bindsql.audit(url)
                if ret:
                    
                    res.append(getRecord(ob,url,ob['level'],ret['detail'],ret['request'],ret['response']))

        
    except Exception,e:
        print (str(e))
        write_scan_log(ob['task_id'],ob['domain_id'],"File:SqlBlindScript.py, run_url function :" + str(e) +", url:"+item['url'])
    return res        
            #end for
        #emd if

#if __name__=='__main__':
#    http=httplib2.Http()
#    url="http://demo.aisec.cn/demo/aisec/ajax_link.php?id=1"
#    bindsql=Blindsqlclass(http,url)
#    bindsql.audit()
    

        
        