#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import sys

from lib.waf_netutil import *

NTP_SERVER_1 = "ntp_server1"
NTP_SERVER_2 = "ntp_server2"
NTP_SERVER_3 = "ntp_server3"

NTP_CONF_FILE = "/etc/ntp.conf"

if __name__ == "__main__":
    
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    
    ntp1 = get_config_value(NTP_SERVER_1)
    ntp2 = get_config_value(NTP_SERVER_2)
    ntp3 = get_config_value(NTP_SERVER_3)
    
    ntps = []
    
    if ntp1 and len(ntp1) > 0:
        ntps.append(ntp1)
        
    if ntp2 and len(ntp2) > 0:
        ntps.append(ntp2)
        
    if ntp3 and len(ntp3) > 0:
        ntps.append(ntp3)
        
    if len(ntps) > 0:
        f = file(NTP_CONF_FILE, "r+")
        
        lines = f.readlines()
        
        f.close()
        
        todel = []
        
        for l in lines:
            
           
            if l.strip().split(" ")[0] == "server":
                todel.append(l)
            #end if
            
            #restrict
            
            if l.strip().split(" ")[0] == "restrict":
                todel.append(l)
            #end if
        #end for
        
        for l in todel:
            lines.remove(l)
        #end for
        
        lines.append("restrict default ignore\n")
        
        for add in ntps:
            lines.append("server " + add + "\n")
        #end for
        
        f = file(NTP_CONF_FILE, "w+")

        f.writelines(lines)
            
        f.close()
        
        waf_popen("service ntp stop")
        
        #waf_popen("ntp -u %s" % ntps[0])
        
        waf_popen("service ntp start")
    #end if
        
#end if
                
    
    