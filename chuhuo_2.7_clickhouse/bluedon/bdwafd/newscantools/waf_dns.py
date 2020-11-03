#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import sys

from lib.waf_netutil import *

NETCONFIG_DNS1 = "network_dns1"
NETCONFIG_DNS2 = "network_dns2"
NETCONFIG_IPV6_DNS1 = "network_ipv6_dns1"
NETCONFIG_IPV6_DNS2 = "network_ipv6_dns2"
RESLOVE_CONF   = "/etc"


def set_dns():
    """set_dns function """
    
    dns1 = get_config_value(NETCONFIG_DNS1)
    dns2 = get_config_value(NETCONFIG_DNS2)
    dns3 = get_config_value(NETCONFIG_IPV6_DNS1)
    dns4 = get_config_value(NETCONFIG_IPV6_DNS2)
    if dns1 or dns2 or dns3 or dns4:
        if dns1 != -1 or dns2 != -1 or dn3 != -1 or dns4 != -1:
            
            waf_popen("cat /dev/null > /etc/resolv.conf");
            
            if len(dns1) > 0:
                waf_popen("echo \"nameserver %s\n\" >> /etc/resolv.conf" % dns1)
            #end if
            
            if len(dns2) > 0:
                waf_popen("echo \"nameserver %s\n\" >> /etc/resolv.conf" % dns2)
            #end if
            if len(dns3) > 0:
                waf_popen("echo \"nameserver %s\n\" >> /etc/resolv.conf" % dns3)
            #end if
            if len(dns4) > 0:
                waf_popen("echo \"nameserver %s\n\" >> /etc/resolv.conf" % dns4)
            #end if
        #end if
    else:
        waf_popen("cat /dev/null > /etc/resolv.conf");
    #end if
    

   
#end def

if __name__ == "__main__":
    
  
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
   
    set_dns()
    print 1

#end if

