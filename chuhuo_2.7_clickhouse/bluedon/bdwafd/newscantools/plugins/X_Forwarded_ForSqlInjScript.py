#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
import json
import urlparse
import re
import urllib

def GetDatabaseError(data):
    
    try:
        if data.find("You have an error in your SQL syntax") >= 0:
            return True,"mysql","You have an error in your SQL syntax"
        if data.find("supplied argument is not a valid MySQL") >=0:
            return True,"mysql","supplied argument is not a valid MySQL"
        if data.find('Microsoft JET Database Engine')>=0:
            return True,"access","Microsoft JET Database Engine"
        if data.find('Microsoft OLE DB Provider for SQL Server')>=0:
            return True,"mssql","Microsoft OLE DB Provider for SQL Server"
        if data.find('System.Data.SqlClient.SqlException')>=0:
            return True,"mssql","System.Data.SqlClient.SqlException"
        if data.find('System.Data.SqlClient.SqlException')>=0:
            return True,"mssql","System.Data.SqlClient.SqlException"
        if data.find('System.Data.OleDb.OleDbException')>=0:
            return True,"mssql","System.Data.OleDb.OleDbException"
        if data.find("[Microsoft][ODBC Microsoft Access Driver]") >= 0:
            return True,"access","[Microsoft][ODBC Microsoft Access Driver]"
        if data.find("[Microsoft][ODBC SQL Server Driver]") >= 0:
            return True,"mssql","[Microsoft][ODBC SQL Server Driver]"
        if data.find("Microsoft OLE DB Provider for ODBC Drivers</font> <font size=\"2\" face=\"Arial\">error") >= 0:
            return True,"mssql","Microsoft OLE DB Provider for ODBC Drivers</font> <font size=\"2\" face=\"Arial\">error"
        if data.find("Microsoft OLE DB Provider for ODBC Drivers") >= 0:
            return True,"mssql","Microsoft OLE DB Provider for ODBC Drivers"
        if data.find("java.sql.SQLException: Syntax error or access violation") >= 0:
            return True,"oracle","java.sql.SQLException: Syntax error or access violation"
        if data.find("PostgreSQL query failed: ERROR: parser:") >= 0:
            return True,"PostgreSQL","PostgreSQL query failed: ERROR: parser:"
        if data.find("invalid input syntax for")>=0:
            return True,"PostgreSQL","invalid input syntax for"
        if data.find("XPathException") >= 0:
            return True,"XPath","XPathException"
        if data.find("supplied argument is not a valid ldap") >= 0:
            return True,"LDAP","supplied argument is not a valid ldap"
        if data.find("javax.naming.NameNotFoundException") >= 0:
            return True,"LDAP","javax.naming.NameNotFoundException"
        if data.find("DB2 SQL error:") >= 0:
            return True,"db2","DB2 SQL error:"
        if data.find('[IBM][JDBC Driver]')>=0:
            return True,"db2","[IBM][JDBC Driver]"
            
        if data.find("Dynamic SQL Error") >= 0:
            return True,"Interbase","Dynamic SQL Error"
        if data.find("Sybase message:") >= 0:
            return True,"sybase","Sybase message:"
        ora_test = re.search("ORA-[0-9]{4,}", data)
        if ora_test != None:
            return True,"oracle","ORA"
        return False,"",""
    except Exception,e:
        logging.getLogger().error("File:x0forwarded0forsqlinjection.py, GetDatabaseError:" + str(e)+"URL:"+self.url)
        return False,"",""
        

        
def run_url(http,ob,item):
    
    result = []
    detail=""
    domain=ob['domain']
    host_domain = ''
    try:
        isstart='0'#标志位为0表示不启动验证性扫描，反之启动验证性扫描 
#-------START 2014-10-16  yinkun -----
        tmp_url = urllib.unquote(item['url'])      
        parse=urlparse.urlparse(tmp_url)
        path=parse.path
        path=path.lower()
        host_domain = ''
        if checkIpv6(domain):
            host_domain = '[' + domain + ']'
        else:
            host_domain = domain
#-------END--------------------------------------        
        if (path.find(".css")>=0 or path.find(".doc")>=0 or path.find(".txt")>=0 or path.find(".pdf")>=0 or path.find(".js")>=0) and path.find("jsp")<0:
            return result
        #end if
        
        if item['params']!='':    
            url="%s?%s"%(tmp_url,item['params'])
        else:
            url=tmp_url
        #end if
        
        headers={"Host":host_domain,"User-Agent":" Mozilla/5.0 (Windows NT 5.1; rv:14.0)\
                     Gecko/20100101 Firefox/14.0.1","Accept":" text/html,application/xhtml+xml,application/xml;q=0.9,\
                     */*;q=0.8","Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3","Accept-Encoding":" gzip, \
                     deflate","Connection": "keep-alive","X-Forwarded-For": "231.23.233.2'"}
        headers1={"Host":host_domain,"User-Agent":" Mozilla/5.0 (Windows NT 5.1; rv:14.0)\
                     Gecko/20100101 Firefox/14.0.1","Accept":" text/html,application/xhtml+xml,application/xml;q=0.9,\
                     */*;q=0.8","Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3","Accept-Encoding":" gzip, \
                     deflate","Connection": "keep-alive","X-Forwarded-For": "231.23.233.2"}
        
        if item['method']=='get':
            #response,content=http.request(url,'GET','',headers)
            #r,c=http.request(url,'GET','',headers1)
            response,content=yx_httplib2_request(http,url,'GET','',headers)
            r,c=yx_httplib2_request(http,url,'GET','',headers1)
            
            res1,res2,res3 = GetDatabaseError(content)
            res11,res22,res33 = GetDatabaseError(c)
            if res1 and response.has_key('status') and response['status'] == '500' and res11 == False:
                request = getRequest(url,"GET",headers,"")
                response = getResponse(response)
                output = "发现数据库错误信息：%s" % (res3)
                result.append(getRecord(ob,url,ob['level'],detail,request,response,output))
                '''
                if ob['isstart']=='1':
                    result.append(getRecord(ob,url,ob['level'],detail+"验证性扫描结果：\n"+"发现数据库错误信息："+GetDatabaseError(content)[2],request,response))
                else:
                    
                    result.append(getRecord(ob,url,ob['level'],detail,request,response))
                '''
            #end if 
        #end if
              
        if item['method']=='post':
            reject_key = ['__viewstate', 'ibtnenter.x', 'ibtnenter.y','password']
            ret=[]
            par=json.read(item['params'])
            for i in par:
                if i and len(i.keys()) > 0:
                    for k in i.keys():
                        if k == 'name':
                            if i[k].lower() not in reject_key:
                                ret.append(i[k]+"=1111")
                            #end if
                        #end if
                    #end for
                #end if
            #end for
            
            post_data= "&".join(ret)
            #r,c = http.request(url,'POST',post_data,headers1)
            #response,content = http.request(url,'POST',post_data,headers)
            r,c = yx_httplib2_request(http,url,'POST',post_data,headers1)
            response,content = yx_httplib2_request(http,url,'POST',post_data,headers)
            
            res1,res2,res3 = GetDatabaseError(content)
            res11,res22,res33 = GetDatabaseError(c)
            if res1 and response.has_key('status') and response['status'] == '500' and res11 == False:
                request = postRequest(url,"POST",headers,post_data)
                response = getResponse(response)
                output = "发现数据库错误信息：%s" % (res3)
                result.append(getRecord(ob,url,ob['level'],detail,request,response,output))
                
                '''
                if ob['isstart']=='1':
                    result.append(getRecord(ob,url,ob['level'],detail+"验证性扫描结果：\n"+"发现数据库错误信息："+GetDatabaseError(content)[2],request,response))
                else:
                    
                    result.append(getRecord(ob,url,ob['level'],detail,request,response))
                #result.append(getRecord(ob,url,ob['level'],detail,request,response))
                '''
            #end if 
        #end if
            
    except Exception, e:
        logging.getLogger().error("File:x-forwarded-for sqlinjectionscript.py, run_url function :" + str(e) + ",task id:" + ob['task_id'] + ",domain id:" + ob['domain_id'])
        write_scan_log(ob['task_id'],ob['domain_id'],"File:x-forwarded-for sqlinjectionscript.py, run_url function :" + str(e))
    return result

            