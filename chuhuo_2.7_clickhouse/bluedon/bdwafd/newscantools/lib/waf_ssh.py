#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import sys
import types

from waf_netutil import *


HOSTS_ALLOW_CONFIG = "/etc/hosts.allow"
SSHD_CONFIG = "/etc/ssh/sshd_config"
# SSHD_CONFIG = "/root//sshd_config"

#----------------------------------------------------------------------
def clear_ssh_ip():
    """clear_ssh_ip function"""
    
    f = file(SSHD_CONFIG, "r+")
    lines = f.readlines()
    
    todel = []
        
    for line in lines:
        if line.find("ListenAddress") != -1:
            todel.append(line)
        #end for
    #end for
    
    for delline in todel:
        lines.remove(delline)
    
    f.close()
    f = file(SSHD_CONFIG, "w+")

    f.writelines(lines)
            
    f.close()
#end def


#----------------------------------------------------------------------
def ssh_add(ip, netmask):
    """ssh_add function"""
    
    #----update sshd.config
    
    #ListenAddress 192.168.100.1
    
    if ip and len(ip) > 0:
    
        f = file(SSHD_CONFIG, "r+")
        
        lines = f.readlines()
        
        insert_index = -1
        
        for line in lines:
            if line.find("Port 22") != -1:
                insert_index = lines.index(line) + 1
            #end for
        #end for
        if insert_index != -1:
            if ':' in ip:
                lines.insert(insert_index, "ListenAddress [" + ip + "]\n")
            else:
                lines.insert(insert_index, "ListenAddress " + ip + "\n")
        else:
            logging.getLogger().debug( "ssh_add error ,can not find str[ListenAddress]")
        #end if
        
        f.close()
        
        f = file(SSHD_CONFIG, "w+")
    
        f.writelines(lines)
                
        f.close()
    #end if
        
        
        
    
    ##----update hosts.allow
    
    #subnet = get_subnet(ip, netmask)
    
    #tokens = subnet.split(".")
    
    #for i in range(len(tokens)):
        #if tokens[i] == "0" and i != (len(tokens) - 1):
            
            #if tokens[i + 1] == "0":
                #tokens[i] = "*"
        ##end if
        
        #if i == (len(tokens) - 1):
            #tokens[i] = "*"
        ##end if
    ##end for
    
    #ipstr = ".".join(tokens)
    
    #if ip and len(ip) > 0:
    
        #f = file(HOSTS_ALLOW_CONFIG, "r+")
        
        #lines = f.readlines()
        
        #insert_index = -1
        
        #for line in lines:
                     
            #if line.find(ipstr) != -1:
                #f.close()
                #return 1
            ##end if      
            
        ##end for
        
        #f.close()
        
        #waf_popen("echo \"sshd:%s\" >> %s" % (ipstr, HOSTS_ALLOW_CONFIG))
    ##end if
                 
#end def

#----------------------------------------------------------------------
def ssh_del(ip, netmask):
    """ssh_del function"""
    
    #----update sshd.config
    
    #ListenAddress 192.168.100.1
    
    if ip and len(ip) > 0:
    
        f = file(SSHD_CONFIG, "r+")
        
        lines = f.readlines()
        
        for line in lines:
            if line.find(ip) != -1:
                lines.remove(line)
            #end for
        #end for
        
        f.close()
        
        f = file(SSHD_CONFIG, "w+")
    
        f.writelines(lines)
                
        f.close()
    #end if
    
    subnet = get_subnet(ip, netmask)
    
    tokens = subnet.split(".")
    
    for i in range(len(tokens)):
        print i
        if tokens[i] == "0" and i != (len(tokens) - 1):
            
            if tokens[i + 1] == "0":
                tokens[i] = "*"
        #end if
        
        if i == (len(tokens) - 1):
            tokens[i] = "*"
        #end if
    #end for
    
    ipstr = ".".join(tokens)
        
    f = file(HOSTS_ALLOW_CONFIG, "r+")
    
    lines = f.readlines()
    
    for line in lines:
        
        if line.find(ipstr) != -1:
            lines.remove(line)
            
        #end if      
        
    #end for
    
    f.close()
    
    f = file(HOSTS_ALLOW_CONFIG, "w+")
    
    f.writelines(lines)
                
    f.close()

#end def


#----------------------------------------------------------------------
def stop_ssh():
    """stop_ssh function"""
    
    waf_popen("service ssh stop")
#end def 

#----------------------------------------------------------------------
def start_ssh():
    """start_ssh function"""
    
    waf_popen("service ssh start")
#end def

#----------------------------------------------------------------------
def reset_ssh(eccs):
    """reset_ssh function"""
    if type(eccs) is not types.ListType:
        return
    #end if
    
    clear_ssh_ip()

    ssh_add("127.0.0.1", "255.0.0.0")
    
    for ecc in eccs:
        if ecc.enable == 1:
        
            if ecc.work_mode == NORMAL_MODE or ecc.work_mode == FIXED_MODE:
                
                if ecc.work_type.find("DMI") != -1 or ecc.work_type.find("DSI") != -1:
                    ssh_add(ecc.ip, ecc.netmask)
                    if ecc.ipv6 and ':' in ecc.ipv6:
                        ssh_add(ecc.ipv6, ecc.ipv6_prefix)
                
                #end if 
                
            #end if
        #end if
    #end for
    stop_ssh()
    start_ssh()
            
#end def

    

    