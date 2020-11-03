#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import sys

from waf_netutil import *


DHCPD_CONF      = "/etc/dhcp3/dhcpd.conf"
DHCP_ETH_CONF   = "/etc/default/dhcp3-server"

#----------------------------------------------------------------------
def update_dhcp_config(realname, subnet, netmask, begin, end, broadcast, routers):
    """update_dhcp_config function"""
    
    # update DHCPD_CONF

    
    #waf_popen("cat /dev/null > %s" % DHCPD_CONF)
    
    f = file(DHCPD_CONF, "w+")
    
    f.writelines("default-lease-time 600;\n")
    f.writelines("max-lease-time 7200;\n")
    f.writelines("authoritative;\n")
    f.writelines("log-facility local7;\n")
    f.writelines("subnet " + str(subnet) + " netmask " + str(netmask) + "{\n")
    f.writelines("range " + str(begin) + " " + str(end) + ";\n")
    f.writelines("option routers  " + str(routers) + ";\n")
    f.writelines("option broadcast-address " + str(broadcast) + ";\n")
    f.writelines("}\n")
    
    f.close()
    
    #waf_popen("cat /dev/null > %s" % DHCP_ETH_CONF)
    
    f = file(DHCP_ETH_CONF, "w+")
    f.writelines("INTERFACES=\"" + realname + "\"\n")
    
    f.close()
                 
#end def

#----------------------------------------------------------------------
def stop_dhcp():
    """stop_dhcp function"""
    
    waf_popen("service dhcp3-server stop")
#end def 

#----------------------------------------------------------------------
def start_dhcp():
    """start_dhcp function"""
    
    waf_popen("service dhcp3-server start")
#end def


    

    