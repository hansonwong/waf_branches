#!/usr/bin/env python
#-*-encoding:UTF-8-*-

####################################
#
#  author:kun yin
#  tutor:yuying xia
#  date:9/19/2014
#
####################################

from lib.common import vulscan_popen
from lib.common import init_log
from HostScan import db_manager
import logging
import os
import sys
import ConfigParser
import time
import fcntl

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)

APACHE_PORTS_CONF        = "/etc/apache2/ports.conf"
APACHE_CONFIG_TAG_BEGIN  = "<IfModule mod_ssl.c>"
APACHE_CONFIG_TAG_END    = "</IfModule>"
WAF_CONFIG   = "/etc/waf_nic.conf"

YES = 1
NO = 0

class Apache_ipv6(object):

    eth_ipv6 = []
    #example:[{'Name':xxx,'Ipv6':'XXX','Netmask':''},...]

    def __init__(self):
        try:
            self.eth_ipv6 = []
            db = db_manager()
            sql = 'select Name, Ipv6 , Netmaskv6 from net_config where type like "%DMI%"'
            res = db.get_all_item_from_db(sql)
            if res:            
                cfg = ConfigParser.RawConfigParser()
                cfg.readfp(open(WAF_CONFIG))

                for item in res:
                    eth_real_name = cfg.get("nicmaps",item.get('Name').strip()).replace('"','')
                    if None != item.get('Ipv6'):
                        self.eth_ipv6.append({'Name':eth_real_name,'Ipv6':item.get('Ipv6'),'Netmask':item.get('Netmaskv6')})
        except Exception, e:
            logging.getLogger().error("File:apache_IPv6.py __init__"+str(e))
  
    @staticmethod
    def is_mysql_start():
        try:
            lines = vulscan_popen("service mysql status")
            for line in lines:
                if line.find('MySQL is stopped') != -1:
                    return NO
                else:
                    return YES
        except Exception,e:
            logging.getLogger().error("File:apache_IPv6.py is_mysql_start()"+str(e))

    @staticmethod
    def start_mysql():
        try:
            vulscan_popen("service mysql start > /dev/null")
        except Exception,e:
            logging.getLogger().error("File:apache_IPv6.py start_mysql()"+str(e))

    @classmethod
    def is_dmi_interface_running(self,interface):
        try:
            return vulscan_popen("ifconfig %s | grep RUNNING" % interface)
        except Exception,e:
            logging.getLogger().error("File:apache_IPv6.py is_dmi_interface_running"+str(e))

    @classmethod
    def is_config_ipv6(self,interface,ipv6addr):
        try:
            return vulscan_popen("ifconfig %s | grep %s" % (interface,ipv6addr))    
        except Exception,e:
            logging.getLogger().error("File:apache_IPv6.py is_config_ipv6()"+str(e))

    @classmethod
    def config_eth_ipv6addr(self,interface,ip,netmask):
        try:
            return vulscan_popen("ifconfig %s add %s/%s" % (interface,ip,netmask))
        except Exception,e:
            logging.getLogger().error("File:apache_IPv6.py config_eth_ipv6addr()"+str(e))

    @classmethod
    def remove_line_from_apache(self,ip):
        try:
            res = NO
            if ip and len(ip) > 0:
                f = file(APACHE_PORTS_CONF, "rb+")
                fcntl.flock(f.fileno(),fcntl.LOCK_EX)
                lines = f.readlines()
                for line in lines:
                    if line.find(ip) != -1:
                        lines.remove(line)
                        res = YES
                
                f.seek(0,0)
                f.truncate()
                f.writelines(lines)
                f.close()

            return res
        
        except Exception, e:
            logging.getLogger().error("File:apache_IPv6.py remove_line_from_apache()"+str(e))

    @classmethod
    def add_line_to_apache(self,ip):
        try:
            first = 0
            if ip and len(ip) > 0:
                f = file(APACHE_PORTS_CONF, "r+")
                temp = []
                fcntl.flock(f.fileno(),fcntl.LOCK_EX)
                lines = f.readlines()
                insert_index = -1

                for line in lines:
                    if line.find(str(ip)) != -1:
                        f.close()
                        return NO
                    if line.find(APACHE_CONFIG_TAG_BEGIN) != -1:
                        insert_index = lines.index(line) + 1
                       
                    if line.find(APACHE_CONFIG_TAG_END) != -1:
                        if first == 0:
                            first = 1
                            b = lines.index(line)
                    temp.append(line)
                f.close()
                
                if insert_index == -1:
                    logging.getLogger().debug("apache_add_ip error: can not find insert index")
                    f.close()
                    return NO
                f = file(APACHE_PORTS_CONF, "w+")
                fcntl.flock(f.fileno(),fcntl.LOCK_EX)
                temp.insert(insert_index, "    Listen [" + ip + "]:443\n")
                
                f.writelines(temp)
                f.close()

                return YES        
        

        except Exception, e:
            logging.getLogger().error("File:apache_IPv6.py add_line_to_apache()"+str(e))

    @staticmethod
    def remove_all_ipv6addr_from_apache():
        try:
            res = NO
            temp = []
            tempfile = []
            f = file(APACHE_PORTS_CONF, "rb+")
            fcntl.flock(f.fileno(),fcntl.LOCK_EX)
            lines = f.readlines()
            for line in lines:
                if line.find(']:443') == -1:
                    temp.append(line)
                else:
                    res = YES
            f.seek(0,0)
            f.truncate()
            f.writelines(temp)
            f.close()
            return res
        except Exception,e:
            logging.getLogger().error("File:apache_IPv6.py remove_all_ipv6addr_from_apache"+str(e))

def check_all_ipv6addr(mydict):
    try:
        temp_ipv6 = []
        temp_file = []
        a = -1
        b = -1
        res = 0
        for dic in mydict:
            temp_ipv6.append(dic['Ipv6'])
 
        f = file(APACHE_PORTS_CONF, "rb+")
        fcntl.flock(f.fileno(),fcntl.LOCK_EX)
        lines = f.readlines()

        for line in lines:
            if line.find("]:443") != -1:
                a = line.find("[")
                b = line.find("]")
                temp_ip = line[a+1:b]
                if temp_ip in temp_ipv6:
                    temp_file.append(line)
                else:
                    res = 1
            else:
                temp_file.append(line)
            
        f.seek(0,0)
        f.truncate()
        f.writelines(temp_file)
        f.close()
            
        return res
    except Exception,e:
            logging.getLogger().error("File:apache_IPv6.py check_all_ipv6addr "+str(e))

# If retutn 1,imply /etc/apache2/ports.conf is modified,should restart apache
def main():
    try:
        mysql_start_times = 2
        res = 0
        while mysql_start_times > 0:
            if  Apache_ipv6.is_mysql_start() == NO:
                Apache_ipv6.start_mysql()
                mysql_start_times -= 1
                continue
            else:
                break
        else:
            res = Apache_ipv6.remove_all_ipv6addr_from_apache()
            return res
        my_apache = Apache_ipv6()
        if not len(my_apache.eth_ipv6):
            res = my_apache.remove_all_ipv6addr_from_apache()
            return res
        else:
            for dic in my_apache.eth_ipv6:
                if my_apache.is_dmi_interface_running(dic['Name']):
                    if not my_apache.is_config_ipv6(dic['Name'],dic['Ipv6']):
                        if my_apache.config_eth_ipv6addr(str(dic['Name']),str(dic['Ipv6']),str(dic['Netmask'])):
                            if my_apache.remove_line_from_apache(str(dic['Ipv6'])):
                                res = 1
                            logging.getLogger().error("File:apache_IPv6.py config_eth_ipv6addr failure")
                            continue
                    if my_apache.add_line_to_apache(str(dic['Ipv6'])):
                        res = 1
                          
                else:
                    if my_apache.remove_line_from_apache(str(dic['Ipv6'])):
                        res = 1

            if check_all_ipv6addr(my_apache.eth_ipv6):
                res = 1            

            return res          

    except Exception,e:
        logging.getLogger().error("File:apache_IPv6.py main()"+str(e))



if __name__ == '__main__':
    logfilepath = sys_path('/log/')
    init_log(logging.ERROR,logging.ERROR,logfilepath+os.path.split(__file__)[1].split(".")[0]+".log")
    res = main()
    if 1 == res:
         print "sholid restart apache"
         exit(0)
    else:
         print "needn't resatrt apache"
         exit(1)
