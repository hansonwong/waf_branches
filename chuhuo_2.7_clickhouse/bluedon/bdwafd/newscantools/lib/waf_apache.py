#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import sys
import types

from waf_netutil import *


APACHE_PORTS_CONF        = "/etc/apache2/ports.conf"
APACHE_CONFIG_TAG_BEGIN  = "<IfModule mod_ssl.c>"
APACHE_CONFIG_TAG_END    = "</IfModule>"


#----------------------------------------------------------------------
def apache_add_ip(ip):
    """apache_add_ip function"""
    
    # update DHCPD_CONF
    
    if ip and len(ip) > 0:
    
        f = file(APACHE_PORTS_CONF, "r+")
        
        lines = f.readlines()
        
        insert_index = -1
        
        a = 0
        b = 0
        
        for line in lines:
            
            if line.find(APACHE_CONFIG_TAG_BEGIN) != -1:
                insert_index = lines.index(line) + 1
                
                a = lines.index(line)
            #end fi
        
            if line.find(APACHE_CONFIG_TAG_END) != -1:
                b = lines.index(line)
            #end if
 
        #end for
        
        f.close()
        
        #Fix BUG #2261
        for i in range(a, b+1):
            #Fix BUG#
            if lines[i].find(ip) != -1:
                return
            #end if
        #end for
                
        
        
        
        if insert_index == -1:
            logging.getLogger().debug("apache_add_ip error: can not find insert index")
            return -1
        
        f = file(APACHE_PORTS_CONF, "w+")
        
        lines.insert(insert_index, "    Listen " + ip + ":443\n")
        
        f.writelines(lines)
                    
        f.close()
    #end if
                 
#end def

#----------------------------------------------------------------------
def apache_del_ip(ip):
    """apache_del_ip function"""
    
    if ip and len(ip) > 0:
    
        # update DHCPD_CONF
        
        f = file(APACHE_PORTS_CONF, "r+")
        
        lines = f.readlines()
        
        for line in lines:
            
            if line.find(ip) != -1:
                lines.remove(line)
                
            #end if      
            
        #end for
        
        f.close()
        
        f = file(APACHE_PORTS_CONF, "w+")
        
        f.writelines(lines)
                    
        f.close()
    #end if
#end def

#----------------------------------------------------------------------
def apache_clear_ip():
    """apache_clear_ip function"""
    
    f = file(APACHE_PORTS_CONF, "r+")
        
    lines = f.readlines()
    
    a = -1
    b = -1
    
    for line in lines:
        
        if line.find(APACHE_CONFIG_TAG_BEGIN) != -1:
            a = lines.index(line)
        #end if
        
        if line.find(APACHE_CONFIG_TAG_END) != -1:
            b = lines.index(line)
        #end if    
        
    #end for
    
    f.close()
    
    if a != -1 and b != -1:
        dellines = []
        
        for i in range(a + 1, b):
            
            #if lines[i].find("127.0.0.1") == -1:
            dellines.append(lines[i])
            #end if
            
        #end for
        
        for i in dellines:
            lines.remove(i)
        #end for
    
        
    
    f = file(APACHE_PORTS_CONF, "w+")
    
    f.writelines(lines)
                
    f.close()
#end def 

#----------------------------------------------------------------------
def stop_apache():
    """stop_dhcp function"""
    
    waf_popen("service apache2 stop")
#end def 

#----------------------------------------------------------------------
def start_apache():
    """start_dhcp function"""
    waf_popen("service apache2 restart")
    waf_popen("service apache2 recheck")
#end def

#----------------------------------------------------------------------
def reset_apache(eccs):
    """reset_apache function"""
    
    if type(eccs) is not types.ListType:
        return
    #end if
    
    apache_clear_ip()
    
    apache_add_ip("127.0.0.1")
    
    for ecc in eccs:
        if ecc.enable == 1:
            if ecc.work_mode == NORMAL_MODE or ecc.work_mode == FIXED_MODE:
                
                if ecc.work_type.find("DMI") != -1 or ecc.work_type.find("DSI") != -1:
                    apache_add_ip(ecc.ip)
                
                #end if 
                
            #end if
        #end if
    #end for
    stop_apache()
    start_apache()
            
#end def





    

    