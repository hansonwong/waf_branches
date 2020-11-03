#!/usr/bin/python
# -*- coding: utf-8 -*-
import MySQLdb
import sys
import os
import logging
from lib.common import *
#from lib.waf_netutil import *

def ListUrl(DomainId):
    
    try:
        
        DomainId = str(DomainId)
        
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')

        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select Url from url_list where DomainId = '%s'" % DomainId
        
        #print sql
        cur.execute(sql)
        
        ret = cur.fetchall()
        
        if ret and len(ret) > 0:
            
            for row in ret:
                
                if row['Url'].find("http://") >= 0:

                    row['Url'] = row['Url'].replace("http://","")
                    
                    array = row['Url'].split("/")
                    
                    for i in range(len(array)):
                        
                        if i == (len(array) - 1):
                            
                            if array[i].find('?'):
                                
                                temp = array[i].split('?')
                                
                                array[i] = temp[0]
                                
                            #end if
                        #end if
                        
                        sql = "select count(Id) as c from `url_tree` where `Name` = '%s' and `Level` = '%d' and DomainId = '%s' " % (array[i],(i+1),DomainId)
                        
                        cur.execute(sql)
                        
                        ret2 = cur.fetchone()
                        
                        if ret2 and ret2['c'] <= 0:
                            
                            if i == 0:
                                
                                sql = "insert into url_tree(`Name`,`Level`,`ParentId`,`DomainId`) values ('%s','%d','%d','%s')" % (array[i],1,0,DomainId)
                            
                            else:
                                
                                ParentId = "" 
                               
                                sql = "select `Id` from `url_tree` where `Name` = '%s' and Level = '%d' " % (array[i-1],i)
                               
                                cur.execute(sql)
                               
                                ret2 = cur.fetchone()
                               
                                if ret2 and len(ret2) > 0:
                                   
                                    ParentId = ret2['Id']
                                    
                                else:
                                    
                                    continue
                                
                                #end if
                                
                                sql = "insert  into url_tree(`Name`,`Level`,`ParentId`,`DomainId`) values ('%s','%d','%d','%s') " % (array[i],(i+1),ParentId,DomainId)
    
                            #end if
                            
                            cur.execute(sql)
                            
                            conn.commit()
                            
                        #end if
                #end if
            #end for
        #end if
        
        conn.close()
        
    except Exception,e:
        
        logging.getLogger().error("ListUrl Exception(ListUrl):" + str(e))
    
    #end try
#end def

if __name__ == '__main__':
    
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    
    ListUrl(794)
    
#end if
    