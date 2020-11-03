#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
import re
import logging
import urlparse
import os
import logging
from lib.common import *


def GetDatabaseError(data):
        try:
            if data.find("You have an error in your SQL syntax") >= 0:
                return True
            if data.find("supplied argument is not a valid MySQL") >=0:
                return True
            if data.find('Microsoft JET Database Engine')>=0:
                return True
            if data.find('Microsoft OLE DB Provider for SQL Server')>=0:
                return True
            if data.find('System.Data.SqlClient.SqlException')>=0:
                return True
            if data.find('System.Data.SqlClient.SqlException')>=0:
                return True
            if data.find('System.Data.OleDb.OleDbException')>=0:
                return True   
            if data.find("[Microsoft][ODBC Microsoft Access Driver]") >= 0:
                return True
            if data.find("[Microsoft][ODBC SQL Server Driver]") >= 0:
                return True
            if data.find("Microsoft OLE DB Provider for ODBC Drivers</font> <font size=\"2\" face=\"Arial\">error") >= 0:
                return True
            if data.find("Microsoft OLE DB Provider for ODBC Drivers") >= 0:
                return True
            if data.find("java.sql.SQLException: Syntax error or access violation") >= 0:
                return True
            if data.find("PostgreSQL query failed: ERROR: parser:") >= 0:
                return True
            if data.find("XPathException") >= 0:
                return True
            if data.find("supplied argument is not a valid ldap") >= 0 or data.find("javax.naming.NameNotFoundException") >= 0:
                return True
            if data.find("DB2 SQL error:") >= 0 or data.find('[IBM][JDBC Driver]')>=0:
                return True
            if data.find("Dynamic SQL Error") >= 0:
                return True
            if data.find("Sybase message:") >= 0:
                return True
            ora_test = re.search("ORA-[0-9]{4,}", data)
            if ora_test != None:
                return True
            return False
        except Exception,e:
            logging.getLogger().error("File:CheckDatabaseErrorSCRIPT.py, FUNCITON:GetDatabaseError:" + str(e)+"URL:"+url)
            return False

def aduit(url,host):
        try:
            response,content=requestUrl(http,url+"%5C",ob['task_id'],ob['domain_id'])
            IsDatabaseError=GetDatabaseError(content)
            if IsDatabaseError==False:
                headers = {}
                getv=checkurl(url)
                if getv:
                    headers={"Host": host,"User-Agent":" Mozilla/5.0 (Windows NT 5.1; rv:14.0)\
                    Gecko/20100101 Firefox/14.0.1","Accept":" text/html,application/xhtml+xml,application/xml;q=0.9,\
                    */*;q=0.8","Accept-Language": "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3","Accept-Encoding":" gzip, \
                    deflate","Connection": "keep-alive","Cookie":getv+"%5C"}
#                   responsecookie,cotnentcookie=http.request(requesturl, "GET",'',headers)
                    responsecookie,cotnentcookie=yx_httplib2_request(http,requesturl, "GET",'',headers)
                    IsDatabaseError=GetDatabaseError(cotnentcookie)
            return IsDatabaseError
            #end if
        except Exception,e:
            logging.getLogger().error("File:SqlInjectionScript.py, SqlInjection.TestSql.three:" + str(e)+"URL:"+url)
            return False

def checkurl(url):
    try:
        
        
        r = urlparse.urlparse(url)
        getquery = r.query
        
        if getquery.find("&")>=0:
            getquerylist = getquery.split("&")
            
            return getquerylist[len(getquerylist)-1]
            
        else:
            return getquery
        #print "checkurl ending"
    #end def
    except Exception,e:
        logging.getLogger().error("File:CheckDatabaseErrorSCRIPT.py, funciton.checkurl:" + str(e)+"URL:"+url)
        return False

 
    
def run_url(http,ob,item):
    try:
        list = []
        if item['params'] == "":
            return list
        if item['params'].find("=")<0:
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
            host=urlparse.urlparse(item['url'])[1]
            params = changeParams(item['params'])
            for row in params:
                url = "%s?%s" % (item['url'],row)
                res=aduit(url,host)
                if res:
                    request=getRequest(url+"%5C",'GET')
                    response=getResponse(response,"")
                    self.ob['status']="1"
                    list.append(getRecord(ob,url,ob['level'],'',request,response))
        return list
    except Exception,e:
        logging.getLogger().error("File:CheckDatabaseErrorSCRIPT.py, funciton.run_url:" + str(e)+"URL:"+url)
        write_scan_log(ob['task_id'],ob['domain_id'],"File:CheckDatabaseErrorSCRIPT.py, funciton.run_url:" + str(e)+" url:"+url)
        return []
    