#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urllib
import urllib2
import re
import socket
import struct
import time
import MySQLdb
import logging
from lib.common import *

class VpnManage:
    
    def __init__(self,type):
        
        try:
            
            self.type = str(type)
            
            self.conn = ""

            self.cursor = ""
            
            self.main()
            
        except Exception,e:
            
            logging.getLogger().error("__init__(VpnManage) exception:" + str(e))
            
        #end try
    #end def
    
    def mysqlConnect(self):
        
        try:
        
            self.conn = MySQLdb.connect(host, user, passwd , db = database, charset = "utf8")
        
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
            
        except Exception,e:
            
            logging.getLogger().error("mysql connect Exception(VpnManage):" + str(e))
            
        #end try            
    #end def
    
    def mysqlClose(self):
        
        try:
        
            self.cursor.close()
        
            self.conn.close()
            
        except Exception,e:
            
            logging.getLogger().error("mysql close Exception(VpnManage):" + str(e))
            
        #end try          
    #end def
    
    def vpn_on(self):
        
        try:
            
            vpn_ip = get_config_value("vpn_ip").encode('utf-8')
            
            vpn_username = get_config_value("vpn_username").encode('utf-8')
            
            vpn_password = get_config_value("vpn_password").encode('utf-8')
            
            lines = "# written by pptpsetup\n"
        
            lines += "pty \"pptp " + vpn_ip + " --nolaunchpppd\" \n"
        
            lines += "name " + vpn_username + "\n"
        
            lines += "remotename friddy\n"
            
            lines += "persist\n"
        
            lines += "defaultroute\n"
            
            lines += "replacedefaultroute\n"
        
            lines += "file /etc/ppp/options.pptp\n"
        
            lines += "ipparam friddy\n"
    
            f = file("/etc/ppp/peers/friddy", "w+")
    
            f.writelines(lines)
    
            f.close()
        
            lines = vpn_username + " friddy \"" + vpn_password + "\" * \n"
        
            f = file("/etc/ppp/chap-secrets", "w+")
    
            f.writelines(lines)
    
            f.close()
        
            os.system("pon friddy")
            
        except Exception,e:
            
            logging.getLogger().error("vpn_on Exception(VpnManage):" + str(e))        
        
        #end try
    #end def
    
    def vpn_off(self):
    
        try:
            
            os.system("poff friddy")
            
        except Exception,e:
            
            logging.getLogger().error("vpn_off Exception(VpnManage):" + str(e))
        
        #end try
    #end def
    
    def vpn_state(self):
        
        try:
            
            msg = vulscan_popen("ifconfig ppp0")
            
            lines = ""
            
            if msg and len(msg) > 0:
                
                for line in msg:
                    
                    lines += line
                    
                #end for
            #end if
            
            f = file("/var/www/tmp/vpn_state", "w+")
    
            f.writelines(lines)
    
            f.close()
            
        except Exception,e:

            logging.getLogger().error("vpn_state Exception(VpnManage):" + str(e))
            
        #end try
    #end def
    
    def main(self):
        
        try:
            
            if self.type == '1':
                
                self.vpn_on()
                #logging.getLogger().error("run vpn on") 
                
            elif self.type == '2':
                
                self.vpn_off()
                vulscan_popen("/usr/bin/python /var/waf/waf_routes.py")
                #logging.getLogger().error("run vpn off")
                
            elif self.type == '3':
                
                self.vpn_state()
                #logging.getLogger().error("run vpn off")
            
            #end if
            
        except Exception,e:
            
            logging.getLogger().error("main Exception(VpnManage):" + str(e))
        
        #end try
    #end def
#end class


if __name__ == '__main__':
    
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    
    try:
        
        type = str(sys.argv[1])
        
        vpnManage = VpnManage(type)
        
    except Exception,e:
        
        logging.getLogger().error("__name__ Exception(VpnManage):" + str(e))   
    
    #end try
#end __main__
