#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import sys
import os
from lib.waf_netutil import *
from lib.waf_apache import *
from lib.waf_ssh import *

def set_dmi(ecc):
    """set_dmi function """
    logging.getLogger().debug( "enter set_dmi function")
    
    #---1: update apache
    
    # apache_add_ip(ecc.ip)

    # apache_add_ip(ecc.ipv6)

    #stop_apache()
    #start_apache()
    
    ssh_add(ecc.ip, ecc.netmask)
    stop_ssh()
    start_ssh()
    
    #---2: update ssh
#end def

def unset_dmi(ecc):
    """unset_dmi function """
    
    logging.getLogger().debug( "enter unset_dmi function")
    
    #---1: update apache
    
    # apache_del_ip(ecc.ip)
    # apache_del_ip(ecc.ipv6)
    #stop_apache()
    #start_apache()
    
    ssh_del(ecc.ip, ecc.netmask)
    stop_ssh()
    start_ssh()
    
    #---2: update ssh
#end def


if __name__ == "__main__":
  
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    

    eths = get_eth_config()
    
    reset_apache(eths)
    waf_popen('service apache2 recheck')
    reset_ssh(eths)
    
    print 1
    sys.exit(0)

 
#end if

