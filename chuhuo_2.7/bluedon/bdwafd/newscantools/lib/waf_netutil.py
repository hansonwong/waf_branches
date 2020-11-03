#!/usr/bin/env python
#-*-encoding:UTF-8-*-
import ConfigParser
import MySQLdb
import re
import time
import logging
import logging.handlers
import os
import subprocess
import socket
import fcntl
import struct

BRCTL     = "/usr/sbin/brctl"
IFCONFIG  = "/sbin/ifconfig"
VCONFIG   = "/sbin/vconfig"

WAF_NIC_CONFIG        = "/etc/waf_nic.conf"
WAF_CONSTANT_CONFIG   = "/etc/waf_constant.rc"

sys_path = lambda relativePath: "%s/%s"%(os.getcwd(), relativePath)
WAF_CONFIG   = sys_path("waf.conf")

WAFBRIDGE  = "wafbridge"
VLANBRIDGE = "vlan_br"
BOND_NAME  = "bond"

MAX_ETH_NUM = 20

            
NORMAL_MODE = 0
FIXED_MODE = 1
BRIDGE_MODE = 2
ROUTE_MODE = 3

WORK_TYPE_DSI = "DSI"
WORK_TYPE_DMI = "DMI"
WORK_TYPE_RPI = "RPI"

FACILITY = {
	'kern': 0, 'user': 1, 'mail': 2, 'daemon': 3,
	'auth': 4, 'syslog': 5, 'lpr': 6, 'news': 7,
	'uucp': 8, 'cron': 9, 'authpriv': 10, 'ftp': 11,
	'local0': 16, 'local1': 17, 'local2': 18, 'local3': 19,
	'local4': 20, 'local5': 21, 'local6': 22, 'local7': 23,
}

LEVEL = {
	'emerg': 0, 'alert':1, 'crit': 2, 'err': 3,
	'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
}


#-------------------global------------------------

#host   = "192.168.9.30"#cfg.get("mysql","db_ip").replace('"','')
#user   = "root"#cfg.get("mysql","db_user").replace('"','')
#passwd = "yxserver"#cfg.get("mysql","db_passwd").replace('"','')

cfg    = ConfigParser.RawConfigParser()
cfg.readfp(open(WAF_CONFIG))
host   = cfg.get("mysql","db_ip").replace('"','')
user   = cfg.get("mysql","db_user").replace('"','')
passwd = cfg.get("mysql","db_passwd").replace('"','')
DEVID = "error_serial_num"

syslog_servers = []
try:
    conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
    
    cur = conn.cursor(MySQLdb.cursors.DictCursor)
    
    sql = "select * from license where Name = 'serial_num'" 
    cur.execute(sql)
    ret = cur.fetchone()
    
    if ret and len(ret["Value"]) > 1:
        DEVID = ret["Value"]
    #end if
    
    sql = "select * from config where Name = 'syslog_server1'" 
    cur.execute(sql)
    ret = cur.fetchone()
    
    if ret and len(ret["Value"]) > 1:
        tmpserver = ret["Value"]
        
        if len(tmpserver.split("|")) == 2:
            syslog_servers.append(tmpserver)
        #end if
    #end if
    
    sql = "select * from config where Name = 'syslog_server2'" 
    cur.execute(sql)
    ret = cur.fetchone()
    
    if ret and len(ret["Value"]) > 1:
        tmpserver = ret["Value"]
        
        if len(tmpserver.split("|")) == 2:
            syslog_servers.append(tmpserver)
        #end if
    #end if
    
    sql = "select * from config where Name = 'syslog_server3'" 
    cur.execute(sql)
    ret = cur.fetchone()
    
    if ret and len(ret["Value"]) > 1:
        tmpserver = ret["Value"]
        
        if len(tmpserver.split("|")) == 2:
            syslog_servers.append(tmpserver)
        #end if
    #end if

    conn.close()
 
except Exception,e:
    print e
#end

class dsi_info_class(object):
    """"""

    def __init__(self, subnet, netmask, begin, end):
        
        self.subnet  = subnet
        self.netmask = netmask
        self.begin   = begin
        self.end     = end
        
    #end def
    
#end class


########################################################################

class eth_info_class(object):
    """eth_info_class"""

    #----------------------------------------------------------------------
    def __init__(self, name, real_name, mac):
        """eth_info_class Constructor"""
        
        self.name      = name
        self.real_name = real_name
        self.mac       = mac
        
    #end def
    def __repr__(self):
        return repr("name:%s "
                "real_name:%s "
                "mac:%s"%
                (
                self.name,
                self.real_name,
                self.mac,
                )
                )
    
#end class
    
########################################################################

class eth_config_class(object):
    """eth_config_class"""
    
    def __init__(self, name, real_name, work_mode, work_type, bridge_id, ip, netmask, nexthop, enable, gateway, ipv6, ipv6_gateway, ipv6_prefix):
        """eth_config_class Constructor"""
        
        self.name      = name
        self.real_name = real_name
        self.work_mode = int(work_mode)
        self.work_type = work_type
        self.bridge_id = int(bridge_id)
        self.ip        = ip
        self.netmask   = netmask
        self.nexthop   = nexthop
        self.gateway   = gateway

        #Add by xiayuying 2014-02-26 for dmi_ipv6 
        self.ipv6         = ipv6
        self.ipv6_gateway = ipv6_gateway
        self.ipv6_prefix  = ipv6_prefix
        #End
        
        
        self.enable    = int(enable)

    def __repr__(self):
        return repr("name:%s "
                "real_name:%s "
                "work_mode:%d "
                "work_type:%s "
                "bridge_id:%d "
                "ip:%s "
                "netmask:%s "
                "nexthop:%s "
                "gateway:%s "
                "ipv6:%s "
                "ipv6_gateway:%s "
                "ipv6_prefix:%s "%
                (
                self.name,
                self.real_name,
                self.work_mode,
                self.work_type,
                self.bridge_id,
                self.ip,
                self.netmask,
                self.nexthop,
                self.gateway,
                self.ipv6,
                self.ipv6_gateway,
                self.ipv6_prefix
                )
                )
        
    #end def

#end class

def waf_popen(cmd):
    logging.getLogger().debug(cmd)
    return subprocess.Popen(cmd,shell=True,close_fds=True,bufsize=-1,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout.readlines()
#end def

def init_log(console_level, file_level, logfile):
    """init_log functionaa"""
    
    #logname = os.path.basename(__file__).split(".")[0]
    

    formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s')
 

    logging.getLogger().setLevel(0)
    
    console_log = logging.StreamHandler()
    console_log.setLevel(console_level)
    console_log.setFormatter(formatter)
    
    file_log = logging.handlers.RotatingFileHandler(logfile,maxBytes=1024*1024,backupCount=2)
    file_log.setLevel(file_level)
    file_log.setFormatter(formatter)
    
    
    logging.getLogger().addHandler(file_log)
    logging.getLogger().addHandler(console_log)
    
#end def

def get_real_name(name):
    acfg    = ConfigParser.RawConfigParser()
    acfg.readfp(open(WAF_NIC_CONFIG))

    eth  = "ETH"
    mac  = "MAC"
    nic_num = "NIC_NUM"
    
    sec = "nicmaps"
    
    try:
        tmp_realname = acfg.get(sec, name)
            
    except Exception,e:
        
        logging.getLogger().debug("get_real_name Exception, read eth info error:" + str(e))

        return -1
    return tmp_realname.replace('"','')
#end def

def get_config_value(name):
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')

        cur = conn.cursor(MySQLdb.cursors.DictCursor)
    
        sql = "select * from config where Name = '%s'" % name
        cur.execute(sql)
        re = cur.fetchone()
        conn.close()
        
        return re["Value"]
 
    except Exception,e:
        logging.getLogger().debug("get_config_value Exception:" + str(e))
        return -1

#end def

def get_eth_config(name = 0):
    """get_eth_config function"""
    
    global host, user, passwd
    
    if name != 0:
        
        try:
            conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
    
            cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
            sql = "select * from net_config"
            cur.execute(sql)
            re = cur.fetchall()
            
            for i in re:
                if i["Name"] == name:
                    tmp_name     = i["Name"]
                    tmp_enable   = int(i["Enable"])
                    tmp_workmode = i["WorkMode"]
                    tmp_worktype = (i["Type"])
                    tmp_bridgeid = 0
                    if not i["BridgeId"]:
                        pass
                    else:
                        tmp_bridgeid = int(i["BridgeId"])
                    #end if
                    tmp_ip       = i["Ip"]
                    tmp_netmask  = i["Netmask"]
                    tmp_nexthop  = i["NextHop"]
                    tmp_gateway  = i["Gateway"]
                    #Add by xiayuying 2014-02-26 for dmi_ipv6
                    tmp_ipv6         = i["Ipv6"]
                    tmp_ipv6_gateway = i["Gatewayv6"]
                    tmp_ipv6_prefix  = i["Netmaskv6"]
                    #End
                    #name, real_name, work_mode, work_type, bridge_id, ip, netmask, nexthop, enable)
                    
                     
                    
                    tmp_realname = get_real_name(tmp_name)
                    
                    tmp_ecc = eth_config_class(tmp_name,
                                               tmp_realname,
                                               tmp_workmode,
                                               tmp_worktype,
                                               tmp_bridgeid,
                                               tmp_ip,
                                               tmp_netmask,
                                               tmp_nexthop,
                                               tmp_enable,
                                               tmp_gateway,
                                               tmp_ipv6,
                                               tmp_ipv6_gateway,
                                               tmp_ipv6_prefix
                                               )
                    
                    return tmp_ecc
                #end if
            #end for
            
            conn.close()
        
        except Exception,e:
            logging.getLogger().debug("get_eth_config Exception:" + str(e))
            return -1
    else:
        ethconfigs = []
        
        try:
            conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
    
            cur = conn.cursor(MySQLdb.cursors.DictCursor)
        
            sql = "select * from net_config"
            cur.execute(sql)
            re = cur.fetchall()
            
            for i in re:
                tmp_name     = i["Name"]
                tmp_enable   = int(i["Enable"])
                tmp_workmode = i["WorkMode"]
                tmp_worktype = (i["Type"])
                tmp_bridgeid = 0
                if not i["BridgeId"]:
                    pass
                else:
                    tmp_bridgeid = int(i["BridgeId"])
                tmp_ip       = i["Ip"]
                tmp_netmask  = i["Netmask"]
                tmp_nexthop  = i["NextHop"]
                
                tmp_gateway  = i["Gateway"]

                #Add by xiayuying 2014-02-26 for dmi_ipv6
                tmp_ipv6         = i["Ipv6"]
                tmp_ipv6_gateway = i["Gatewayv6"]
                tmp_ipv6_prefix  = i["Netmaskv6"]
                #End
                #name, real_name, work_mode, work_type, bridge_id, ip, netmask, nexthop, enable)

                tmp_realname = get_real_name(tmp_name)
                
                tmp_ecc = eth_config_class(tmp_name,
                                           tmp_realname,
                                           tmp_workmode,
                                           tmp_worktype,
                                           tmp_bridgeid,
                                           tmp_ip,
                                           tmp_netmask,
                                           tmp_nexthop,
                                           tmp_enable,
                                           tmp_gateway,
                                           tmp_ipv6,
                                           tmp_ipv6_gateway,
                                           tmp_ipv6_prefix
                                           )
                
                ethconfigs.append(tmp_ecc)
            
            conn.close()
        
        except Exception,e:
            logging.getLogger().debug("get_eth_config Exception:" + str(e))
            return -1
        
        return ethconfigs
    #end if
        
#end def

########################################################################
class bridge_info_class(object):
    
    def __init__(self, name, eths):
        self.name = name
        self.eths = eths
        
        regex_wafbridge  = ur"^%s\d{1,4}$" % WAFBRIDGE
        regex_vlanbridge = ur"^%s\d{1,4}_\d{0,4}$" % VLANBRIDGE
        
        #vlan_br14_3
        
        if re.search(regex_wafbridge, name):
            
            self.id = int(name.split(WAFBRIDGE, 1)[1])
            self.br_type = 0
            self.vid = -1
            
        elif re.search(regex_vlanbridge, name):
            
            self.id = int(name.split(VLANBRIDGE, 1)[1].split("_")[0])
            self.br_type = 1
            self.vid = int(name.split(VLANBRIDGE, 1)[1].split("_")[1])
            
        #end if
         
    #end def  
    
#end class

########################################################################

class bond_info_class(object):
    """bond_info class"""
    
    def __init__(self, id, eths, bridge_id):
        
        self.id   = id
        self.name = BOND_NAME + str(id)
        self.eths = eths
        
        self.bid  = bridge_id
        
    #end def 
#end class

def get_eth_ip(realname):
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        re = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', realname[:15]))[20:24])
        
        return re
    
    except Exception,e:
        logging.getLogger().debug("get_eth_ip Exception,maybe it working on bridge mode .arg:" + realname + ",:" + str(e))
        
        return -1
#end def


def string2ipv6(s):
    try:
        ret = ''
        for i in range(len(s)/2):
            ret = ret + '\\x' + s[i*2] + s[i*2+1]
        exec("temp= '" + ret + "'")
        res = socket.inet_ntop(socket.AF_INET6, temp)
        return res

    except Exception, e:
        logging.getLogger().debug("string2ipv6:" + s + ",:" + str(e))
        return -1

def get_eth_ipv6(realname):
    try:
        fp = open('/proc/net/if_inet6', 'rb')
        lines = fp.readlines()
        fp.close()
        res = ''
        for line in lines:
            if realname in line:
                if line.find('fe80') != 0:
                    res = string2ipv6(line.split()[0])
        return res
    except Exception, e:
        logging.getLogger().error("get_eth_ipv6 Exception,maybe it working on bridge mode .arg:" + realname + ",:" + str(e))
        return -1

def get_eth_current_broadcast(realname):
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        re = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8919, struct.pack('256s', realname[:15]))[20:24])
        
        return re
    
    except Exception,e:
        logging.getLogger().debug("get_eth_broadcast Exception,arg:" + realname + ",:" + str(e))
        
        return -1
#end def

def get_eth_broadcast(ip, mask):
    import ipcalc

    net = ipcalc.Network(ip, to_cidr(mask))
    return net.broadcast()
#end def

def get_eth_mask(realname):
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        re = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x891b, struct.pack('256s', realname[:15]))[20:24])
        
        return re
    
    except Exception,e:
        logging.getLogger().debug("get_eth_mask Exception:" + str(e))
        
        return -1
#end def

def get_eth_prefix(realname):
    try:
        fp = open('/proc/net/if_inet6', 'rb')
        lines = fp.readlines()
        fp.close()
        res = ''
        for line in lines:
            if realname in line:
                if line.find('fe80') != 0:
                    res = int(line.split()[2], 16)
        return res
    except Exception, e:
        logging.getLogger().error("get_eth_prefix Exception:" + realname + ",:" + str(e))
        return -1

def get_bridge_id(realname):
    
    r = waf_popen("%s show" % BRCTL)
    
    current_br = ""
    
    for i in r:
        k = " ".join(i.split())
        ks = k.split(" ")

        if len(ks) >0:

            regex = ur"^%s\d{1,4}$" % WAFBRIDGE
                
            if re.search(regex, ks[0]):
                current_br = ks[0]
            #end if
        
            if ks[len(ks) - 1] == realname:
                
                if len(current_br) > 0:
                    
                    r = current_br.split(WAFBRIDGE)
                    
                    if len(r) == 2:
                        return r[1]
                    #end if
                #end if
            #end if
        #end if

    #end for
    return -1
#end def

#----------------------------------------------------------------------
def enable_eth(realname):
    """enable_eth function"""
    waf_popen("%s %s up" % (IFCONFIG, realname))
#end def

#----------------------------------------------------------------------
def disable_eth(realname):
    """disable_eth function"""
    
    waf_popen("%s %s -promisc down" % (IFCONFIG, realname))
#end def
    
#----------------------------------------------------------------------
def set_eth_ip(realname, ip, netmask):
    """set_eth_ip function"""
    
    waf_popen("%s %s %s netmask %s -promisc up" % (IFCONFIG, realname, ip, netmask))
#end def

def set_eth_ipv6(realname, ipv6, ipv6_prefix):

#    waf_popen("%s %s del %s" % (IFCONFIG, realname, ipv6))
    line = ''
    lines = waf_popen("ifconfig %s | grep 'inet6 addr' | grep 'Scope:Global' | awk '{print $3}'" % (realname))
    for line in lines:
        waf_popen("%s %s del %s" % (IFCONFIG, realname, line))
#       print line
    waf_popen("%s %s add %s/%s -promisc up" % (IFCONFIG, realname, ipv6, ipv6_prefix))

#----------------------------------------------------------------------
def ip2int(ip):
    """ip2int function"""
    
    ip_items = ip.split('.')
    ip_int = 0
    
    for item in ip_items:
        ip_int = ip_int * 256 + int(item)

    return ip_int
#end def

#----------------------------------------------------------------------
def int2ip(ip_int):
    """int2ip function"""
    
    ip_items = ['0','0','0','0']
    
    for i in range(0,4):
        ip_items[3-i] = str(ip_int % 256)
        ip_int = int((int(ip_int) - int(ip_items[3-i])) / 256) 

    seq = '.'
    ip = seq.join(ip_items)

    return ip
#end def
    
#----------------------------------------------------------------------
def get_subnet(ip, netmask):
    """get_subnet function"""
    
    total = 256 ** 4

    ip_int = ip2int(ip)
    
    subnet_int = total - ip2int(netmask)
    net_int = int(ip_int / subnet_int) * subnet_int
    
    return int2ip(net_int)
#end def

def to_cidr(mask):
    """to_cidr function"""
    
    a = mask.split(".")

    if len(a) != 4:
        return 0

    cidr = 0
    
    tmplist = [0, 128, 192, 224, 240, 248, 252, 254, 255]

    for i in a:
    
        tmp = int(i)
        
        if tmp in tmplist:
            
            cidr = cidr + tmplist.index(tmp)
            
        else:
            return 0
        #end if
    #end for
    
    return cidr
#end def

def vconfig_add(eth, vid):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        fcntl.ioctl(s.fileno(), 0x8983, struct.pack("i24sih",0, eth, vid, 0))
        
    
    
    except Exception,e:
        logging.getLogger().debug("vconfig_add Exception," + str(e))
    #end try
#end def

def checkIpv6(ipv6_addr):
    try:
        addr= socket.inet_pton(socket.AF_INET6, ipv6_addr)
    except socket.error:
        return False
    else:
        return True

import base64

VUL_SYSLOG_HEADER = "NVSCAN_VULSCAN:%s#NVSCANSPLIT#" % (DEVID)

def syslog_raw(message, level=LEVEL['notice'], facility=FACILITY['daemon'],host='127.0.0.1', port=514):
    
    """
    Send syslog UDP packet to given host and port.
    """
    sock = ''
    if checkIpv6(host):
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = '<%d>%s' % (level + facility*8, message)
    sock.sendto(data, (host, port))
    sock.close()
		
#end def

def syslog(message):
    
    try:
        for s in syslog_servers:
            tmpip = s.split("|")[0]
            tmpport = int(s.split("|")[1])
            syslog_raw(message, host = tmpip, port = tmpport)        
        #end for
    except Exception,e:
        logging.getLogger().error("syslog Exception:" + str(e))
    #end try
#end def

def syslog_vul_begin(task_id, name):
    try:
        
        data = VUL_SYSLOG_HEADER + \
             (str(task_id)) + "#NVSCANSPLIT#" + \
             (name.decode("utf8"))+ "#NVSCANSPLIT#" + \
             ("0") + "#NVSCANSPLIT#" + \
             ("BEGIN")
        
        syslog(data.encode("utf8"))
    except Exception,e:
        #print e
        logging.getLogger().error("syslog_vul_begin Exception:" + str(e))
    #end try
#end def

def syslog_vul_end(task_id, name):
    try:
        data = VUL_SYSLOG_HEADER + \
             (str(task_id)) + "#NVSCANSPLIT#" + \
             (name.decode("utf8"))+ "#NVSCANSPLIT#" + \
             ("0") + "#NVSCANSPLIT#" + \
             ("END")
        syslog(data.encode("utf8"))
    except Exception,e:
        logging.getLogger().error("syslog_vul_end Exception:" + str(e))
    #end try
#end def

def syslog_host_vul(task_id, name, ip, port, proto, host_vul_name, family, factor, refurl):
    
    if factor == "C":
        factor = "紧急"
    elif factor == "H":
        factor = "高危"
    elif factor == "M":
        factor = "中危"
    elif factor == "L":
        factor = "低危"
    elif factor == "I":
        factor = "信息"
    else:
        factor = ""
    #endif
    if task_id is None:
        task_id = ""
    if name is None:
        name = ""
    if ip is None:
        ip = ""
    if port is None:
        port = ""
    if proto is None:
        proto = ""
    if host_vul_name is None:
        host_vul_name = ""
    if family is None:
        family = ""
    if refurl is None:
        refurl = ""
    
    
    try:
        """
        data = VUL_SYSLOG_HEADER + \
             "".join(base64.encodestring(str(task_id)).split("\n")) + "#" + \
             "".join(base64.encodestring(name).split("\n")) + "#" + \
             "".join(base64.encodestring("1").split("\n")) + "#" + \
             "".join(base64.encodestring(ip).split("\n")) + "#" + \
             "".join(base64.encodestring(port).split("\n")) + "#" + \
             "".join(base64.encodestring(proto).split("\n")) + "#" + \
             "".join(base64.encodestring(host_vul_name).split("\n")) + "#" + \
             "".join(base64.encodestring(host_vul_desc).split("\n")) + "#" + \
             "".join(base64.encodestring(host_vul_ref).split("\n")) + "#" + \
             "".join(base64.encodestring(factor).split("\n")) + "#" + \
             "".join(base64.encodestring(family).split("\n"))
        """
        
        data = VUL_SYSLOG_HEADER + \
             ((str(task_id))) + "#NVSCANSPLIT#" + \
             ((name)).decode("utf8") + "#NVSCANSPLIT#" + \
             (("1")) + "#NVSCANSPLIT#" + \
             ((ip)) + "#NVSCANSPLIT#" + \
             ((port)) + "#NVSCANSPLIT#" + \
             ((proto)) + "#NVSCANSPLIT#" +\
             ((host_vul_name)).decode("utf8") + "#NVSCANSPLIT#" + \
             ((family)).decode("utf8") + "#NVSCANSPLIT#" + \
             ((factor)).decode("utf8")+ "#NVSCANSPLIT#" + \
             refurl
        
    
        syslog(data.encode("utf8"))
    except Exception,e:
        logging.getLogger().error("syslog_host_vul Exception:" + str(e))
    #end try
#end def

def syslog_weak_vul(task_id, name, ip, pass_type, user, passwd):
    try:
        data = VUL_SYSLOG_HEADER + \
             (task_id) + "#NVSCANSPLIT#" + \
             (name.decode("utf8")) + "#NVSCANSPLIT#" + \
             ("3") + "#NVSCANSPLIT#" + \
             (ip) + "#NVSCANSPLIT#" + \
             (pass_type.decode("utf8")) + "#NVSCANSPLIT#" + \
             (user.decode("utf8")) + "#NVSCANSPLIT#" + \
             (passwd.decode("utf8"))
        syslog(data.encode("utf8"))
    except Exception,e:
        logging.getLogger().error("syslog_weak_vul Exception:" + str(e))
    #end try
#end def

def is_set_ipv6():
    try:
        conn = MySQLdb.connect(host,user,passwd,db='waf_hw',charset='utf8')
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from net_config"
        cur.execute(sql)
        res = cur.fetchall()
        print res
        if res:
            for item in res:
                if item.get('Ip_v6') and item.get('Ip_v6').strip()  and int(item.get('Enable')) == 1:
                    return True
        return False

    except Exception, e:
        logging.getLogger().error("is_set_ipv6 Exception:" + str(e))
        return False
