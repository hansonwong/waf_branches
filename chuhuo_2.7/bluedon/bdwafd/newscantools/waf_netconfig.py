#!/usr/bin/env python
#-*-encoding:UTF-8-*-
import ConfigParser
import MySQLdb
import re
import time
import logging
import os
import sys
import subprocess

from lib.waf_netutil import *
from waf_dmi import set_dmi
from waf_dmi import unset_dmi
from waf_dsi import set_dsi
#from waf_ha  import get_ha_status


#-------------------global------------------------


eth_infos   = []
eth_configs = []


#############################################################################

#----------------------------------------------------------------------
def get_real_name(eth):
    """get_real_name function"""
    
    for i in eth_infos:
        if eth == i.name:
            return i.real_name
        #end if
    #end for
    
    return -1
#end def

#----------------------------------------------------------------------
def get_eth_ifenable(realname):
    """get_eth_ifenable function"""

    re = waf_popen("%s %s" % (IFCONFIG, realname))
    
    for i in re:
        if i.find("UP ") != -1:
            return 1
        #end if
    #end for
    
    return 0
    
#end def

#----------------------------------------------------------------------
def get_eth_workmode(realname):
    """get_eth_workmode function"""
    
    #---1: if working on bridge mode
    
    re = waf_popen("%s show" % BRCTL)
    
    for i in re:
        k = " ".join(i.split())
        ks = k.split(" ")
        
        if len(ks) != 0:
            if realname == ks[len(ks) - 1]:
                return BRIDGE_MODE
            #end if
        #end if
    #end for
    
    #---2: if working on route mode
    
    re = waf_popen("ip rule list")
    
    for i in re:
        if i.find(realname + " ") != -1:
            return ROUTE_MODE
        #end if
    #end for
    
    re = waf_popen("cat /etc/default/dhcp3-server")
    for i in re:
        if i.find(realname) != -1:
            return FIXED_MODE
        #end if
    #end for
    
    for i in re:
        if i.find(realname + " ") != -1:
            return ROUTE_MODE
        #end if
    #end for
    
    return NORMAL_MODE
        
    
    
#end def

#----------------------------------------------------------------------
def get_eth_worktype(realname, workmode):
    """get_eth_worktype function"""
    
    re = []

    if workmode == BRIDGE_MODE:
        return 0
    elif workmode == FIXED_MODE:
        
        tmpip = get_eth_ip(realname)
        if tmpip == -1:
            return ""
        else:
            re1 = waf_popen("cat /etc/apache2/ports.conf")
            
            for i in re1:
                if i.find(tmpip) != -1:
                    re2 = waf_popen("cat /etc/ssh/sshd_config")
                    for k in re2:
                        if k.find(tmpip) != -1:
                            return "DSI"
                        #end if
                    #end for
                #endif
            #end for
        #end if
        return ""
    
    
    elif workmode == ROUTE_MODE:
        return 0
    elif workmode == NORMAL_MODE:
        
        ethip = get_eth_ip(realname)
        
        if ethip == -1:
            return ""
        #end if
        
        d = waf_popen("cat /etc/apache2/ports.conf")
        
        for i in d:
            if i.find(ethip) != -1:
                re.append("DMI")
                break
            #end if
        #end for
        
        d = waf_popen("cat /etc/nginx/nginx.conf")
        
        if len(d) != 0:
        
            for i in d:
                if i.find(ethip) != -1:
                    re.append("RPI")
                    break
                #end if
            #end for
        #end if
                     
    #end if
    
    if len(re) == 0:
        return ""
    elif len(re) == 1:
        return re[0]
    else:
        return "|".join(re)
    
#end def


#----------------------------------------------------------------------
def init_eth_info():
    """init_eth_info function"""
    
    acfg    = ConfigParser.RawConfigParser()
    acfg.readfp(open(WAF_NIC_CONFIG))

    eth  = "ETH"
    mac  = "MAC"
    nic_num = "NIC_NUM"
    
    sec = "nicmaps"

    try:
        nic_num = int(acfg.get(sec, nic_num).replace('"',''))
        
    except Exception,e:
        
        logging.getLogger().debug("init_eth_info Exception, read nic num error:" + str(e))

        return -1
    
    try:
        for i in range(MAX_ETH_NUM):
            
            try:
            
                tmp_realname = acfg.get(sec, eth + str(i)).replace('"','')
                tmp_mac      = acfg.get(sec, eth + str(i) + "_" + mac).replace('"','')
                tmp_ethinfo = eth_info_class(eth + str(i), tmp_realname, tmp_mac)

                eth_infos.append(tmp_ethinfo)
                
            except Exception, e:
                pass
            #end try
       
    except Exception,e:
        
        logging.getLogger().debug("init_eth_info Exception, read eth info error:" + str(e))

        return -1
    #end try
    
    return eth_infos
    
#end def

#----------------------------------------------------------------------
def set_workmode(ecc):
    """set_workmode"""
    global INIT
    
    logging.getLogger().debug("enter func :set_workmode")

    if ecc.work_mode == BRIDGE_MODE:
        
        if get_ha_status() == "Suspending":
            pass
        else:
        
            from waf_bridge import set_bridge
            set_bridge(ecc) 
            
            if INIT == 0:
                waf_popen("/usr/bin/python /var/waf/waf_vlan.py start")
            #end if
        #end if
        
    elif ecc.work_mode == ROUTE_MODE:
        
        set_eth_ip(ecc.real_name, ecc.ip, ecc.netmask)
        
        waf_popen("echo 1 > /proc/sys/net/ipv4/ip_forward")
    
    elif ecc.work_mode == NORMAL_MODE:
        
        set_eth_ip(ecc.real_name, ecc.ip, ecc.netmask)
        
        if ecc.work_type.find("DMI") != -1:

            waf_popen("/usr/bin/python /var/waf/waf_dmi.py")
            
        elif ecc.work_type.find("RPI") != -1:
            waf_popen("/usr/bin/python /var/waf/waf_rpi.py reset")
        elif ecc.work_type.find("HA") != -1:
            pass
        #end if
        
        
        
    
    elif ecc.work_mode == FIXED_MODE:
        
        set_eth_ip(ecc.real_name, ecc.ip, ecc.netmask)
        
        set_dsi(ecc)
        
    #end if
    
     
    
    if INIT == 0:
        waf_popen("/usr/bin/python /var/waf/waf_iptables.py start")
        waf_popen("/usr/bin/python /var/waf/waf_routes.py")
    #end if
    
#end def

#----------------------------------------------------------------------
def del_workmode(ecc):
    """del_workmode"""
    
    try:
    
        logging.getLogger().debug("enter func :del_workmode")
        
        if ecc.work_mode == BRIDGE_MODE:
            
            if get_ha_status() == "Suspending":
                pass
            else:
            
                #from waf_bridge import del_bridge
                #del_bridge(ecc)
                waf_popen("/usr/bin/python /var/waf/waf_bridge.py stop")
                waf_popen("/usr/bin/python /var/waf/waf_bridge.py start")
            #end if
            
            
            
        elif ecc.work_mode == ROUTE_MODE:
            
            waf_popen("echo 0 > /proc/sys/net/ipv4/ip_forward")
        
        elif ecc.work_mode == NORMAL_MODE:
            
            #set_eth_ip(ecc.real_name, ecc.ip, ecc.netmask)
            
            if ecc.work_type.find("DMI") != -1:

                waf_popen("/usr/bin/python /var/waf/waf_dmi.py")
                
            elif ecc.work_type.find("RPI") != -1:
                
                waf_popen("/usr/bin/python /var/waf/waf_rpi.py reset")
                
            elif ecc.work_type.find("HA") != -1:
                pass
            #end if
        
        elif ecc.work_mode == FIXED_MODE:
            
            pass
        
        #end if
    except Exception,e:
        logging.getLogger().debug("del_workmode Exception:" + str(e))
        
        return -1
    #end try
        
    
#end def

def get_current_eth_config(name):
    """get_eth_config function"""
    
    try:
    
        tmp_realname = get_real_name(name)
        
        ifenable = get_eth_ifenable(tmp_realname)
        
        if ifenable == 0:
            return eth_config_class(name,
                                   tmp_realname,
                                   0,
                                   0,
                                   0,
                                   0,
                                   0,
                                   "",
                                   0,
                                   "",
                                   "",
                                   "",
                                   ""
                                   )
        #end if
        

        tmp_workmode = get_eth_workmode(tmp_realname)
        tmp_worktype = get_eth_worktype(tmp_realname, tmp_workmode)
        tmp_ip       = get_eth_ip(tmp_realname)
        tmp_netmask  = get_eth_mask(tmp_realname)
        tmp_bridgeid = 0

        if tmp_workmode == BRIDGE_MODE:
            tmp_bridgeid = get_bridge_id(tmp_realname)
            
            if tmp_bridgeid == -1:
                logging.getLogger().debug("get_bridge_id error:")
                return -1
            #end if
        #end if
        
        tmp_ipv6 = get_eth_ipv6(tmp_realname)
        tmp_ipv6_gateway = ""
        tmp_ipv6_prefix = get_eth_prefix(tmp_realname)

        tmp_ecc = eth_config_class(name,
                                   tmp_realname,
                                   tmp_workmode,
                                   tmp_worktype,
                                   tmp_bridgeid,
                                   tmp_ip,
                                   tmp_netmask,
                                   "",
                                   ifenable,
                                   "",
                                   tmp_ipv6,
                                   tmp_ipv6_gateway,
                                   tmp_ipv6_prefix
                                   )
        return tmp_ecc
    
    except Exception,e:
        logging.getLogger().debug("get_eth_config,name=%s Exception:%s" %(name, str(e)))
        
        return -1
    #end try
    
    
    
#end def

########################################################################

 
if __name__ == "__main__":
    
    global INIT
    INIT = 0

    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    
    if len(sys.argv) == 3:
        if sys.argv[2] == "init":
            INIT = 1
        #end if
    #end if
    
    if len(sys.argv) == 1:
        init_eth_info()
        for i in eth_infos:
            waf_popen("/usr/bin/python /var/waf/waf_netconfig.py %s init" % i.name)
        #end 
        #waf_popen("/usr/bin/python /var/waf/waf_bonding.py")
        waf_popen("/usr/bin/python /var/waf/waf_vlan.py start")
        waf_popen("/usr/bin/python /var/waf/waf_iptables.py start")
        waf_popen("/usr/bin/python /var/waf/waf_routes.py")
        
        # print 1
        sys.exit(0)
    #end if
   
    if len(sys.argv) > 3:
        # print "-1"
        sys.exit(0)
    #end if
    
    if (sys.argv[1]) == "route_setup":
        waf_popen("python waf_routes.py")
        sys.exit(0)
    #end if
    
    if (sys.argv[1]) == "dmi_setup":
        waf_popen("python waf_dmi.py")
        sys.exit(0)
    #end if
    
    if (sys.argv[1]) == "dsi_setup":
        waf_popen("python waf_dsi.py")
        sys.exit(0)
    #end if
     

    init_eth_info()
    
    current_ecc = get_current_eth_config(sys.argv[1])
    
    logging.getLogger().debug( "current name: " + str(current_ecc.name))
    logging.getLogger().debug( "current realname: " + str(current_ecc.real_name))
    logging.getLogger().debug( "current workmode: " + str(current_ecc.work_mode))
    logging.getLogger().debug( "current worktype: " + str(current_ecc.work_type))
    logging.getLogger().debug( "current enable: " + str(current_ecc.enable))
    logging.getLogger().debug( "current bridge_id: " + str(current_ecc.bridge_id))
    logging.getLogger().debug( "current ip: " + str(current_ecc.ip))
    logging.getLogger().debug( "current netmask: " + str(current_ecc.netmask))
    
    
    if current_ecc == -1:
        #print "-1"
        sys.exit(0)
    #end if
    
    eth_configs = get_eth_config()
    
    for eth in eth_configs:
        if eth.real_name == -1:
            logging.getLogger().error("error eth real name:%s" % eth.name)
            print -1
            sys.exit(0)
        #end if
    #end for
    
    new_ecc = 0
    
    for i in eth_configs:

        if i.name == current_ecc.name:
            new_ecc = i
        #end if
    #end for
    
    if new_ecc == 0:
        #print "-1"
        sys.exit(0)
    #end if
    
    logging.getLogger().debug( "new name: " + str(new_ecc.name))
    logging.getLogger().debug( "new realname: " + str(new_ecc.real_name))
    logging.getLogger().debug( "new workmode: " + str(new_ecc.work_mode))
    logging.getLogger().debug( "new worktype: " + str(new_ecc.work_type))
    logging.getLogger().debug( "new enable: " + str(new_ecc.enable))
    logging.getLogger().debug( "new bridge_id: " + str(new_ecc.bridge_id))
    logging.getLogger().debug( "new ip: " + str(new_ecc.ip))
    logging.getLogger().debug( "new netmask: " + str(new_ecc.netmask))
    
    #***********************************************************
    #   1:check enable flag
    #***********************************************************
    
    if current_ecc.enable == 0 and new_ecc.enable == 0:
        #print 1
        sys.exit(0)
    #end if
    
    if current_ecc.enable == 0 and new_ecc.enable == 1:

        enable_eth(current_ecc.real_name)
        
        set_workmode(new_ecc)
        
        #print 1
        sys.exit(0)
    
    #end if
    
    if current_ecc.enable == 1 and new_ecc.enable == 0:

        del_workmode(current_ecc)
        
        disable_eth(current_ecc.real_name)
        
        waf_popen("/usr/bin/python /var/waf/waf_iptables.py start")
        
        #print 1
        sys.exit(0)
    
    #end if
    
    
    
    #***********************************************************
    #   2:check workmode
    #***********************************************************
            
    if new_ecc.work_mode != current_ecc.work_mode:
        
        del_workmode(current_ecc)
        set_workmode(new_ecc)
        
        #print 1
        sys.exit(0)
        
    #***********************************************************
    #   3:check bridge id
    #***********************************************************
        
    if new_ecc.work_mode == BRIDGE_MODE and new_ecc.bridge_id != current_ecc.bridge_id:
        del_workmode(current_ecc)
        set_workmode(new_ecc)
        
        waf_popen("/usr/bin/python /var/waf/waf_vlan.py start")
        
        #print 1
        sys.exit(0)
        
        
    #end if
    
    
    #***********************************************************
    #   4:check work_type,ip and netmask
    #***********************************************************
    
    if new_ecc.work_mode == NORMAL_MODE:

        
        set_eth_ip(new_ecc.real_name, new_ecc.ip, new_ecc.netmask)
        
        set_eth_ipv6(new_ecc.real_name, new_ecc.ipv6, new_ecc.ipv6_prefix)

        old_worktype = current_ecc.work_type
        new_worktype = new_ecc.work_type.encode("utf8")
        
        olds = []
        news = []
        
        if old_worktype or new_worktype:
            
            to_del    = []
            to_add    = []
            to_modify = []
          
            if not old_worktype and new_worktype:

                to_add = new_worktype.split("|")
            
            elif not new_worktype and old_worktype:
                to_del = old_worktype.split("|")
                
            else: 
                if old_worktype != new_worktype:
                    
                    olds = old_worktype.split("|")
                    news = new_worktype.split("|")
                    
                    logging.getLogger().debug((olds))
                    logging.getLogger().debug((news))
                    
                    
                    for o in olds:
                        if o not in news:
                            
                            to_del.append(o)
                        #end if
                    #end for
                    
                    for n in news:
                        if n not in olds:
                            
                            to_add.append(n)
                        #end if
                    #end for
                    
                    if new_ecc.ip != current_ecc.ip or new_ecc.netmask != current_ecc.netmask or new_ecc.ipv6 != current_ecc.ipv6 or new_ecc.ipv6_prefix != current_ecc.ipv6_prefix:
                        for i in news:
                            if i in olds:
                                to_modify.append(i)
                            #end if
                        #end for
                    #end if
                elif old_worktype == new_worktype:
                    
                    if new_ecc.ip != current_ecc.ip or new_ecc.netmask != current_ecc.netmask or new_ecc.ipv6 != current_ecc.ipv6 or new_ecc.ipv6_prefix != current_ecc.ipv6_prefix:
                        to_modify = new_worktype.split("|")
                    #end if
                #end if

            #end if
    
            for i in to_del:
                if i == WORK_TYPE_DMI:

                    waf_popen("/usr/bin/python /var/waf/waf_dmi.py")
                    
                elif i == WORK_TYPE_RPI:
                    waf_popen("/usr/bin/python /var/waf/waf_rpi.py reset")
                
                #end if
            #end for
                
            for i in to_add:
                if i == WORK_TYPE_DMI:
                    
                    waf_popen("/usr/bin/python /var/waf/waf_dmi.py")
                    
                elif i == WORK_TYPE_RPI:
                    waf_popen("/usr/bin/python /var/waf/waf_rpi.py reset")
                #end if
            #end for
            
            for i in to_modify:
                if i == WORK_TYPE_DMI:
                    
                    waf_popen("/usr/bin/python /var/waf/waf_dmi.py")
                    
                elif i == WORK_TYPE_RPI:
                    
                    waf_popen("/usr/bin/python /var/waf/waf_rpi.py reset")
                #end if
            #end for
                
        #end if
    elif new_ecc.work_mode == ROUTE_MODE:
        if new_ecc.ip != current_ecc.ip or new_ecc.netmask != current_ecc.netmask:
            set_eth_ip(new_ecc.real_name, new_ecc.ip, new_ecc.netmask)
        #end if
    elif new_ecc.work_mode == FIXED_MODE:
        
        if new_ecc.ip != current_ecc.ip or new_ecc.netmask != current_ecc.netmask:
            set_eth_ip(new_ecc.real_name, new_ecc.ip, new_ecc.netmask)

            waf_popen("/usr/bin/python /var/waf/waf_dsi.py")
        #end if
        
        if new_ecc.work_type != current_ecc.work_type:
            waf_popen("/usr/bin/python /var/waf/waf_dsi.py")
        #end if
    #end if
    if len(sys.argv) == 2:
        
        #***********************************************************
        #   5:set for bondings
        #***********************************************************
        
        waf_popen("/usr/bin/python /var/waf/waf_bonding.py")
        
        
        #***********************************************************
        #   6:update iptables
        #***********************************************************
        
        waf_popen("/usr/bin/python /var/waf/waf_iptables.py start")
        
        #***********************************************************
        #   7:update routes
        #***********************************************************
        
        waf_popen("/usr/bin/python /var/waf/waf_routes.py")
        
        #***********************************************************
        #   8:flow control
        #***********************************************************
        
        waf_popen("/usr/bin/python /var/waf/waf_flowcontrol.py")
        waf_popen("/usr/bin/python /var/waf/waf_dmi.py")

    #end if
    if new_ecc.work_mode == NORMAL_MODE:
        set_eth_ipv6(new_ecc.real_name, new_ecc.ipv6, new_ecc.ipv6_prefix)

    sys.exit(0)
    
#end if



