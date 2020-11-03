#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import sys
from lib.waf_netutil import *
from lib.waf_dhcp import *
from lib.waf_apache import *
from lib.waf_ssh import *

CONFIG_DHCP_RANGE_START = "dhcp_range_start"
CONFIG_DHCP_RANGE_END   = "dhcp_range_end"

def set_dsi(ecc):
    """set_dsi function"""
    
    if ecc.work_type != WORK_TYPE_DSI:
        logging.getLogger().error("set_dsi error: work type isn't dsi")
        
        return -1
    #end if
    
    ip_start = get_config_value(CONFIG_DHCP_RANGE_START)
    ip_end   = get_config_value(CONFIG_DHCP_RANGE_END)
    
    broadcast = get_eth_broadcast(ecc.ip, ecc.netmask)
    routers   = ecc.ip
    netmask   = ecc.netmask
    
    subnet = get_subnet(ecc.ip, ecc.netmask)
    
    realname = ecc.real_name
    
    update_dhcp_config(realname, subnet, netmask, ip_start, ip_end, broadcast, routers)
    
    stop_dhcp()
    start_dhcp()
    check_apache()
    
#end def
def check_apache():
    try:
        res = waf_popen('service apache2 status')
        if 'NOT' in str(res):
            waf_popen('service apache2 restart')
    except Exception, e:
        logging.getLogger().error(str(e))
        
if __name__ == "__main__":
    
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    
    eccs = get_eth_config()
    
    if len(sys.argv) == 1:
    
        if eccs == -1:
            
            logging.getLogger().error("read eth configs error")
        
            print "-1"
            sys.exit(0)
        #end if
        
        for ecc in eccs:

            if ecc.work_mode == FIXED_MODE:

                
                set_dsi(ecc)
            #end if
        #end for
        
        reset_apache(eccs)
        reset_ssh(eccs)
        
        print 1
    
    elif len(sys.argv) == 2:
        
        ecc = get_eth_config(sys.argv[1])
    
        if ecc == -1:
            print "-1"
            sys.exit(0)
        #end if
        
        set_dsi(ecc)
        
        reset_apache(eccs)
        reset_ssh(eccs)
        
        print 1
    else:
        print "-1"
        sys.exit(0)
    #end if
    check_apache()
#end def