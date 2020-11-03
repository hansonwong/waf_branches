#!/usr/bin/env python
#-*-encoding:UTF-8-*-

import sys

from lib.waf_netutil import *
from lib.common import *
eth_configs = []
user_routes = []
#----------------------------------------------------------------------
def set_default_route():
    """set_route function"""
    
    global eth_configs
    
    tablenum = 100
    
    #for ecc in eth_configs:
        
        #if ecc.enable == 1:
           
            #if ecc.work_mode == FIXED_MODE:
                ##TO DSI,we need set default route
                ##192.168.100.0/24 dev eth3  proto kernel  scope link  src 192.168.100.1
                
                #waf_popen("ip route add %s/%d proto kernel  scope link  dev %s" % 
                          #(get_subnet(ecc.ip, ecc.netmask), to_cidr(ecc.netmask), ecc.real_name))
                
            #elif ecc.work_mode == ROUTE_MODE:
                
                #waf_popen("echo \"%d    %s_rt\" >> /etc/iproute2/rt_tables" % (tablenum, ecc.real_name))             
                #waf_popen("ip route add default via %s dev %s table %s_rt" % (ecc.nexthop, ecc.real_name, ecc.real_name))
                #waf_popen("ip rule add dev %s lookup %s_rt" % (ecc.real_name, ecc.real_name))
                
                #tablenum = tablenum + 1
            #elif ecc.work_mode == NORMAL_MODE:
                #waf_popen("route add -net %s netmask %s dev %s" % (get_subnet(ecc.ip, ecc.netmask), ecc.netmask, ecc.real_name))

    ##end if
    
    #waf_popen("cat /dev/null > /etc/network/interfaces");
    
    f = file("/etc/network/interfaces", "w")
    
    #waf_popen("echo \"auto lo\" >>/etc/network/interfaces")
    #waf_popen("echo \"iface lo inet loopback\n\" >>/etc/network/interfaces")
    
    f.write("auto lo\n")
    f.write("iface lo inet loopback\n\n")
    
    allow_hotplug = []
            
    for ecc in eth_configs:
        
        if ecc.enable == 0:
            continue
        #end if
        
        
        
        if ecc.work_mode == ROUTE_MODE or ecc.work_mode == NORMAL_MODE or ecc.work_mode == FIXED_MODE:
            
            allow_hotplug.append(ecc.real_name)
            
            #waf_popen("echo \"auto %s\" >>/etc/network/interfaces" % ecc.real_name)
            #waf_popen("echo \"iface %s inet static\" >>/etc/network/interfaces" % ecc.real_name)
            #waf_popen("echo \"    address %s\" >>/etc/network/interfaces" % ecc.ip)
            #waf_popen("echo \"    netmask %s\n\" >>/etc/network/interfaces" % ecc.netmask)
            if not ecc.ip and not ecc.ipv6:
                continue
            f.write("auto %s\n" % ecc.real_name)
            if ecc.ip:
                f.write("iface %s inet static\n" % ecc.real_name)
                f.write("    address %s\n" % ecc.ip)
                f.write("    netmask %s\n\n" % ecc.netmask)
            if ecc.ipv6 and ':' in ecc.ipv6:
                f.write("iface %s inet6 static\n" % ecc.real_name)
                f.write("    address %s\n" % ecc.ipv6)
                f.write("    netmask %s\n\n" % ecc.ipv6_prefix)

        #end if
    #end for
    
    
        
    
    #for i in allow_hotplug:
    #waf_popen("echo \"allow-hotplug %s\" >>/etc/network/interfaces" % " ".join(allow_hotplug))
    
    f.write("allow-hotplug %s\n" % " ".join(allow_hotplug))
    f.close()
    
    waf_popen("/etc/init.d/networking restart")
    
    #for config scan interface,we need to delete dmi' routes
    #logging.getLogger().error("===========%d" % len(eth_configs))
    
    
    #ip route add $eth2net dev eth2  proto kernel  scope link  src $eth2ip table dmitable 
    #ip route add default via $eth2gw dev eth2 metric 10 table dmitable 
    #ip rule add from $eth2ip table dmitable
    
    for ecc in eth_configs:
        if ecc.enable == 0:
            continue
        #end if

        if ecc.work_mode == NORMAL_MODE :
            
            waf_popen("echo \"%d    %s_rt\" >> /etc/iproute2/rt_tables" % (tablenum, ecc.real_name))
            if ecc.ip:
                waf_popen("ip route add %s/%s dev %s  proto kernel  scope link  src %s table %s" 
                      % (get_subnet(ecc.ip, ecc.netmask), str(to_cidr(ecc.netmask)), ecc.real_name, ecc.ip, (ecc.real_name + "_rt")))
            
            if ecc.gateway and len(ecc.gateway) > 1:
                waf_popen("ip route add default via %s dev %s table %s " % (ecc.gateway, ecc.real_name, (ecc.real_name + "_rt")))
            if ecc.ipv6_gateway and ':' in ecc.ipv6_gateway:
                waf_popen("route -A inet6 add default gw %s dev %s " % (ecc.ipv6_gateway, ecc.real_name))
            #end if
            waf_popen("ip rule add from %s table %s" % (ecc.ip, (ecc.real_name + "_rt")))
            # print("ip rule add from %s table %s" % (ecc.ipv6, (ecc.real_name + "_rt")))
            tablenum = tablenum + 1
            pass
        #end if
    #end for
    
    route_eccs = []
    
    for ecc in eth_configs:
        
        if ecc.enable == 0:
            continue
        #end if
        if ecc.work_mode == ROUTE_MODE :
            waf_popen("echo \"%d    %s_rt\" >> /etc/iproute2/rt_tables" % (tablenum, ecc.real_name))             
            #waf_popen("ip route add default via %s dev %s table %s_rt" % (ecc.nexthop, ecc.real_name, ecc.real_name))
            #waf_popen("ip rule add dev %s lookup %s_rt" % (ecc.real_name, ecc.real_name))
            
            tablenum = tablenum + 1
            
            route_eccs.append(ecc)
        #end if
    #end for
    if len(route_eccs) == 2:
        
        waf_popen("ip route add default via %s dev %s table %s_rt" % (route_eccs[0].nexthop, route_eccs[1].real_name, route_eccs[0].real_name))
        waf_popen("ip rule add dev %s lookup %s_rt" % (route_eccs[0].real_name, route_eccs[0].real_name))
        
        waf_popen("ip route add default via %s dev %s table %s_rt" % (route_eccs[1].nexthop, route_eccs[0].real_name, route_eccs[1].real_name))
        waf_popen("ip rule add dev %s lookup %s_rt" % (route_eccs[1].real_name, route_eccs[1].real_name))
        
    #end if

    waf_popen("ip route flush cache")
    

#end def

def del_dmi_routes():
    global eth_configs
    
    for ecc in eth_configs:
        #logging.getLogger().error(ecc.work_type)
        #if ecc.work_type.find("DMI") != -1 and ecc.work_type.find("NVS") == -1 :
        if int(ecc.work_mode) == 0 and ecc.work_type.find("NVS") == -1 :
            if len(ecc.ip) > 0:
                routes_str = "src %s" % ecc.ip
                
                lines = waf_popen("ip route list")
                
                for l in lines:
                    if l.find(routes_str) != -1:
                        #logging.getLogger().error( "ip route del %s" % l)
                        waf_popen("ip route del %s" % l)
                    #end if
                #end for
            #end if
                
        #end if
    #end for
#end def

def get_ipv6_net(ipv6,netmask):
    tmp_ip = ipv6_to_bin(ipv6)
    if tmp_ip == False:
        return False
    num_mask = int(netmask)
    if num_mask > 0 and num_mask < 129:
        a = 128 - num_mask
        if a == 0:
            return tmp_ip
        else:
            tmp_ip = tmp_ip[:num_mask]
            for i in range(a):
                tmp_ip += '0'
            return tmp_ip
    else:
        return False
    
def set_user_route():
    """set_user_route function"""
     
    
    re = user_routes
    print re
    for i in re:
        dest    = i["Dest"]
        netmask = i["Netmask"]
        gateway = i["Gateway"]
        iface   = get_real_name(i["Iface"])
        ip      = get_eth_ip(iface)

        Destv6    = i["Destv6"]
        Netmaskv6 = i["Netmaskv6"]
        Gatewayv6 = i["Gatewayv6"]
        ipv6      = get_eth_ipv6(iface)

        default = int(i["Default"])
        
        
        #set default route
        if default == 1:
            if (gateway and len(gateway) > 1) or (Gatewayv6 and ':' in Gatewayv6):
                if gateway and len(gateway) > 1:
                    waf_popen("ip route add default via %s dev %s" % (gateway, iface))
                if Gatewayv6 and ':' in Gatewayv6:
                    waf_popen("route -A inet6 add default gw %s dev %s"%(Gatewayv6, iface))
            
                continue
            #end if
        #end if`
        
        #set net route and host route
        
        if (not dest and not Destv6) or not iface:
            continue
        #end if
        
        if len(dest) > 1 and len(iface) > 1:
            
            if netmask and len(netmask) > 1:
                
                if get_subnet(dest, netmask) == dest:
                    
                    #net route
                    if gateway and len(gateway) > 1:
                        waf_popen("ip route add %s/%s dev %s via %s src %s " % (dest, to_cidr(netmask), iface, gateway, ip))
                        #waf_popen("route add -net %s netmask %s dev %s gw %s" % (dest, netmask, iface, gateway))
                    else:
                        waf_popen("ip route add %s/%s dev %s proto kernel  scope link src %s " % (dest, to_cidr(netmask), iface, ip))
                    #end if
                    
                    
                else:
                    #host route
                    if gateway and len(gateway) > 1:
                        waf_popen("ip route add %s dev %s via %s src %s " % (dest, iface, gateway, ip))
                    else:
                        waf_popen("ip route add %s dev %s proto kernel  scope link src %s " % (dest, iface, ip))
                    #end if
   
                #end if
            else:
                #waf_popen("ip route add %s dev scope link" % dest)
                pass
        #end if
        
        if len(Destv6) > 1 and len(iface) > 1:
            if Netmaskv6 and len(Netmaskv6) > 0 and len(Netmaskv6) <= 128:
                if get_ipv6_net(Destv6,Netmaskv6) == ipv6_to_bin(Destv6):
                    #net route
                    if Gatewayv6 and len(Gatewayv6) > 0:
                        waf_popen("ip -6 route add %s/%s dev %s via %s src  %s" % (Destv6, Netmaskv6, iface, Gatewayv6, ipv6))
                    else:
                        waf_popen("ip -6 route add %s/%s dev %s proto kernel  scope link src %s " % (Destv6, Netmaskv6, iface, ipv6))
                else:
                    #host route
                    if Gatewayv6 and len(Gatewayv6) > 0:
                        waf_popen("ip -6 route add %s dev %s gw %s src %s " % (Destv6, iface, Gatewayv6, ipv6))
                    else:
                        waf_popen("ip -6 route add %s dev %s proto kernel  scope link src %s " % (Destv6, iface, ipv6))

            else:
                pass

        #waf_popen("%s %s %s %s up" % (IFCONFIG, iface, ))
    #end for
    
#end def

def read_user_routes():
    global host, user, passwd
     
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
        sql = "select * from user_route"
        cur.execute(sql)
        re = cur.fetchall()
        
        return re
    
    except Exception,e:
        
        logging.getLogger().debug("read_user_routesException:" + str(e))
        return -1
    return -1
#end def
        

def flush_routes():
    """flush_routes function"""

    #clear route list

    #waf_popen("ip route flush table all")
    
    
    
    ##del user route rule
    re = waf_popen("ip rule list")
    
    not_to_del = ["from all lookup local", "from all lookup main", "from all lookup default"]
    
    if len(re) > 0:
        
        for rule in re:
        
            if len(rule) > 0:        
                

                if rule.find(":") == -1:
                    continue
                #end if
                
                todel = rule.split(":", 2)[1].strip()
                if todel not in not_to_del:
                    waf_popen("ip rule del %s" % todel)
                else:
                    logging.getLogger().debug(todel)
                
                #end if
                
            #end if
        #end for
    #end if
    
    #del route table
    
    #waf_popen("cat /dev/null > /etc/iproute2/rt_tables");
    
    f = file("/etc/iproute2/rt_tables", "w")

    #255     local
    #254     main
    #253     default
    #0       unspec
    
    #waf_popen("echo \"255     local\" >> /etc/iproute2/rt_tables");
    #waf_popen("echo \"254     main\" >> /etc/iproute2/rt_tables");
    #waf_popen("echo \"253     default\" >> /etc/iproute2/rt_tables");
    #waf_popen("echo \"0       unspec\" >> /etc/iproute2/rt_tables");
    
    f.write("255    local\n")
    f.write("254    main\n")
    f.write("253    default\n")
    f.write("0      unspec\n")
    
    f.close()
#end def

if __name__ == "__main__":
    
    init_log(logging.ERROR, logging.ERROR, "/var/log/" + os.path.split(__file__)[1].split(".")[0] + ".log")
    
    eth_configs = get_eth_config()
    if eth_configs == -1:
        logging.getLogger().error("read eth configs error")
        
        sys.exit(0)
    #end if
    
    for eth in eth_configs:
        if eth.real_name == -1:
            logging.getLogger().error("error eth real name:%s" % eth.name)
        
            sys.exit(0)
        #end if
    #end for
    
    user_routes = read_user_routes()
    flush_routes()
    set_default_route()
    set_user_route()
    del_dmi_routes()
    waf_popen('sleep 5')
    waf_popen('service ssh restart')
    waf_popen('service apache restart')
    
    print "1"
    
#end if
   

