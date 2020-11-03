#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import sys
from lib.waf_netutil import *

if __name__ == "__main__":
    
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    
    eccs = get_eth_config()
    

    for ecc in eccs:

        if ecc.work_type and type(ecc.work_type) == type(u"test"):
            if ecc.work_type.find("DMI") != -1:

                re = waf_popen("/var/waf/ethtool " + ecc.real_name)
                
                for i in re:
                    if i.find("Link detected") != -1:
                        if i.find("yes") != -1:
                            print -1
                            sys.exit(-1)
                        #end if
                    #end if
                #end for
            #end if
                                    
        #end if
    #end for
    
    sys.exit(0)
    
#end if