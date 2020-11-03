#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
import MySQLdb
import logging
from lib.common import *

class MailManage:
    
    def __init__(self,taskId):
        
        try:
            
            self.taskId = str(taskId)
            
            self.conn = ""

            self.cursor = ""
            
            self.mail_from = ""
            
            self.mail_to = ""
            
            self.smtp_server = ""
            
            self.smtp_port = ""
            
            self.user = ""
            
            self.passwd = ""
            
            self.taskName = ""
            
            self.main()
            
        except Exception,e:
            
            logging.getLogger().error("__init__(MailManage) exception:" + str(e))
            
        #end try
    #end def

    def mysqlConnect(self):
        
        try:
        
            self.conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
            
        except Exception,e:
            
            logging.getLogger().error("mysql connect Exception(MailManage):" + str(e))
            
        #end try            
    #end def
    
    def mysqlClose(self):
        
        try:
        
            self.cursor.close()
        
            self.conn.close()
            
        except Exception,e:
            
            logging.getLogger().error("mysql close Exception(MailManage):" + str(e))
            
        #end try          
    #end def
    
    def getEmailConfig(self):
        
        try:
            
            self.mail_from = get_config_value("email_from")
            
            self.mail_to = get_config_value("email_send_to")
            
            self.smtp_server = get_config_value("email_smtp")
            
            self.smtp_port = get_config_value("email_smtp_port")
            
            self.user = get_config_value("email_account")
            
            self.passwd = get_config_value("email_pass")
            
            self.mysqlConnect()
            
            self.cursor.execute("select Name from task_list where Id = '" + self.taskId + "' ")
            
            ret = self.cursor.fetchone()
            
            if ret and len(ret) > 0:
                
                self.taskName = ret['Name'].encode('utf-8')
                
            #end if
            
            self.mysqlClose()
            
        except Exception,e:

            logging.getLogger().error("getEmailConfig Exception(MailManage):" + str(e))
            
        #end try
        
    #end def
    
    def sendMail(self):
        
        try:
            
            html = ""
            
            title = ""
            
            temp = u"任务："
            
            html = temp.encode('utf-8') + self.taskName
            
            temp = u" ，已扫描完成"
            
            html += temp.encode('utf-8')
            
            temp = u"漏洞扫描系统"
            
            title = "Web" + temp.encode('utf-8')
            
            msg = MIMEMultipart()
            
            body = MIMEText(html, 'html', 'utf-8')
            
            msg.attach(body)
            
            msg['to'] = self.mail_to
            
            msg['from'] = self.mail_from
            
            msg['subject'] = title + "," + time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
            
            try:
        
                smtp = smtplib.SMTP(self.smtp_server + ":" + str(self.smtp_port))
        
                smtp.login(self.user, self.passwd)
                
                smtp.sendmail(msg['from'], msg['to'], msg.as_string())
                
                smtp.close()
            
            except Exception, e1:
                
                logging.getLogger().error("send_report error(MailManage):" + str(e1))
            
            #end try
            
        except Exception,e:
            
            logging.getLogger().error("sendMail Exception(MailManage):" + str(e))
            
        #end try
    #end def
    
    def main(self):
        
        try:
            
            self.getEmailConfig()
            
            self.sendMail()
            
        except Exception,e:
            
            logging.getLogger().error("main Exception(MailManage):" + str(e))
        
        #end try
    #end def
    
#end class





    
