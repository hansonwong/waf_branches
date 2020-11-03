#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import sys
from lib.waf_netutil import *

CONFIG_FLOW_CONTROL_ENABLE = "flowcontrol_enable"
CONFIG_FLOW_CONTROL_VALUE  = "flowcontrol_value"

WONDERSHAPER = "/usr/sbin/wondershaper"

if __name__ == "__main__":
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    
    eths = get_eth_config()
    
    for eth in eths:
        cmd = WONDERSHAPER + " clear "+ eth.real_name
        waf_popen(cmd)
    #end for
    
    if int(get_config_value(CONFIG_FLOW_CONTROL_ENABLE)) == 1:
        lists = get_config_value(CONFIG_FLOW_CONTROL_VALUE)
        
        if lists != -1:
            if len(lists) > 0:
                print lists.split("|")
                for tmp in lists.split("|"):
                    print tmp.split("#")
                    if len(tmp.split("#")) == 2:
                        #print tmp.split("#")[0],
                        #print tmp.split("#")[1]
                        cmd = WONDERSHAPER + " " + get_real_name(tmp.split("#")[0]) + " " + str(tmp.split("#")[1]) + " " + tmp.split("#")[1]
                        waf_popen(cmd)
                    #end if
                #end for
            #end if
        #end if
    #end if
        
#end if