#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import atexit
import logging
import thread
import threading
import time
from Queue import Queue
from lib.common import *
#from send_udp import send_udp_thread

class ScanHostMsgStop:
    def __init__(self):
        try:
            self.conn = ""
            self.cursor = ""     
        except Exception,e:
            logging.getLogger().error("File:ScanHostMsgStop.py, ScanHostMsgStop.__init__:" + str(e) + ",task id:115")
        #end try
    #end def
    
    def mysqlConnect(self):
        try:
            
            if self.conn == '' or self.cursor == '':
                self.conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
                self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
            #end if
            return True
        except Exception,e:
            self.conn = ''
            self.cursor = ''
            logging.getLogger().error("File:ScanHostMsgStop.py, ScanHostMsgStop.mysqlConnect:" + str(e) + ",task id:115")
            return False
        #end try
    #end def
    
    def mysqlClose(self):
        try:
            if self.conn != '' and self.cursor != '':
                self.cursor.close()
                self.conn.close()
            #end if
            self.conn = ''
            self.cursor = ''
            return True
        except Exception,e:
            self.conn = ''
            self.cursor = ''
            logging.getLogger().error("File:ScanHostMsgStop.py, ScanHostMsgStop.mysqlClose:" + str(e) + ",task id:115")
            return False
        #end try
    #end def
    
    def main(self):
        try:
            conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            
            sql = ""
            sql = "update hostmsg_task set `state` = '2'"       
            cursor.execute(sql)
            conn.commit()
            
            cursor.close()
            conn.close()
        except Exception,e:
            logging.getLogger().error("File:ScanHostMsgStop.py, ScanHostMsgStop.mian:" + str(e) + ",task id:115")
            return False
        #end try    
    #end def
#end class

if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    try:
         scanHostMsgStop = ScanHostMsgStop()
         scanHostMsgStop.main()
    except Exception,e:
        logging.getLogger().error("File:ScanHostMsgStop.py, __main__:" + str(e) + ",task id:115")
    #end try
#end if

