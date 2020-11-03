#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
import MySQLdb
import httplib2
import urlparse
import re
import logging
class DirTraversal:
    def __init__(self,http,ob,item):
        self.http=http
        self.ob=ob
        self.task_id=ob['task_id']
        self.domain_id=ob['domain_id']
        self.url_list_table="url_list_"+ob['task_id']
        self.web_timeout=ob['web_timeout']
        self.level=ob['level']
        self.url=item['url']
        #self.vuldict={}
    #end def
    def MysqlGetUrl(self):
        try:
            parse=urlparse.urlparse(self.url)
            urls=parse.path
            if urls=="" or urls=="/":
                return self.url
            urls=self.url.split("/")
            urls=urls[len(urls)-1]
            if urls=="" or urls.find(".")<0:
                return  self.url
            else:
                return False     
        except Exception,e:
            logging.getLogger().error("mysql MysqlGetUrl Exception(DirectoryTraversal.py):" + str(e))
            return False
        
    def CheckVul(self):
        try:
            result=[]
            geturl=self.MysqlGetUrl()
            if geturl:
                response,content=requestUrl(self.http,geturl,self.task_id,self.domain_id)
                code = findCode(content)
                content = changeCode(content,code)
                if content.find('转到父目录')>=0 or content.find('返回上一级目录')>=0 or  content.find('Directory Listing For')>=0 or content.find('Index of')>=0 or content.find("[To Parent Directory]")>=0:
                    detail=u"目录遍历漏洞是由于Web服务器设置不当导致的，攻击者可利用此漏洞查看Web目录下的文件及其文件夹，从而找到可攻击的文件。该漏洞一般被攻击者作为辅助攻击的手段之一。"
                    detail=detail.encode('utf8')
                    request=getRequest(geturl,'GET')
                    response=getResponse(response,"")
                    result.append(getRecord(self.ob,geturl,self.level,detail,request,response))
                #end if
                
                '''
                there = re.compile(r'char\s*set\s*=\s*UTF.{0,10}8',re.I)
                m=there.search(content)
                if m:  
                    if content.find('转到父目录')>=0 or content.find('返回上一级目录')>=0 or  content.find('Directory Listing For')>=0 or content.find('Index of')>=0:
                        detail=u"目录遍历漏洞是由于Web服务器设置不当导致的，攻击者可利用此漏洞查看Web目录下的文件及其文件夹，从而找到可攻击的文件。该漏洞一般被攻击者作为辅助攻击的手段之一。"
                        detail=detail.encode('utf8')
                        request=getRequest(geturl,'GET')
                        response=getResponse(response,"")
                        result.append(getRecord(self.ob,geturl,self.level,detail,request,response))
                else:
                    content=content.decode('gb2312').encode('utf8')
                    if content.find('转到父目录')>=0 or content.find('返回上一级目录')>=0 or  content.find('Directory Listing For')>=0 or content.find('Index of')>=0:
                        detail=u"目录遍历漏洞是由于Web服务器设置不当导致的，攻击者可利用此漏洞查看Web目录下的文件及其文件夹，从而找到可攻击的文件。该漏洞一般被攻击者作为辅助攻击的手段之一。"
                        detail=detail.encode('utf8')
                        request=getRequest(geturl,'GET')
                        response=getResponse(response,"")
                        result.append(getRecord(self.ob,geturl,self.level,detail,request,response))
                '''
            return result
        except Exception,e:
            logging.getLogger().error("File:DiretoryTraversal.py, CheckVul function :" + str(e) + ",task id:" + self.task_id + ", domain id:" + self.domain_id + ", url:" + geturl)
            return []
def run_url(http,ob,item):
    try:
            
        DirTraversa=DirTraversal(http,ob,item)
        vuls=DirTraversa.CheckVul()
        return vuls
    except Exception,e:
        logging.getLogger().error("File:DiretoryTraversal.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:DiretoryTraversal.py, run_url function :" + str(e))
        return []