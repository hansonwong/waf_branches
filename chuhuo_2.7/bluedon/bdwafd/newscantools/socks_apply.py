#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import MySQLdb
import logging
from lib.common import *

class SocksApply:
    def __init__(self):
        try:
            self.conn = ""
            self.cursor = ""
        except Exception,e:
            logging.getLogger().error("init SocksApply Exception(SocksApply):" + str(e))
        #end try
    #end def
    
    def mysqlConnect(self):
        try:
            self.conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
            return True
        except Exception,e:
            logging.getLogger().error("mysql connect Exception(SocksApply):" + str(e))
            return False
        #end try
    #end def
    
    def mysqlClose(self):
        try:
            self.cursor.close()
            self.conn.close()
            return True
        except Exception,e:
            logging.getLogger().error("mysql close Exception(SocksApply):" + str(e))
            return False
        #end try
    #end def
    
    def main(self):
        try:
            if self.mysqlConnect():
                socks_ip = ''
                socks_port = ''
                self.cursor.execute("select `Value` from `config` where `Name` = 'socks_ip'")
                ret = self.cursor.fetchone()
                if ret and len(ret) > 0:
                    socks_ip = str(ret['Value'])
                #end if
                self.cursor.execute("select `Value` from `config` where `Name` = 'socks_port'")
                ret = self.cursor.fetchone()
                if ret and len(ret) > 0:
                    socks_port = str(ret['Value'])
                #end if
                self.cursor.execute("select `Value` from `config` where `Name` = 'socks_username'")
                ret = self.cursor.fetchone()
                if ret and len(ret) > 0:
                    socks_username = str(ret['Value'])
                #end if
                self.cursor.execute("select `Value` from `config` where `Name` = 'socks_password'")
                ret = self.cursor.fetchone()
                if ret and len(ret) > 0:
                    socks_password = str(ret['Value'])
                #end if
                self.mysqlClose()
            
                content = []
                f = file("/etc/proxychains.conf", "r+")
                lines = f.readlines()
                for line in lines:
                    if line.find("socks5") == 0 or line.find("socks4") == 0:
                        if socks_username == '' and socks_password == '':    
                            content.append("socks5 " + socks_ip + " " + socks_port + "\n")
                        else:
                            content.append("socks5 " + socks_ip + " " + socks_port + " '" + socks_username + "' '" + socks_password + "' \n")
                        #end if
                    else:
                        content.append(line)
                    #end if
                #end for
                f.close()
            
                f = file("/etc/proxychains.conf", "w+")
                f.writelines(content)
                f.close()
            #end if
        except Exception,e:
            logging.getLogger().error("main Exception(SocksApply):" + str(e))
        #end try
    #end def
#end class

if __name__ == '__main__':
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    try:
        sockapply = SocksApply()
        sockapply.main()
    except Exception,e:
        logging.getLogger().error("SocksApply Exception:" + str(e))
    #end try
#end if

