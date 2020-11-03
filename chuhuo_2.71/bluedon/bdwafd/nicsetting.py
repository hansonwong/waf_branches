#!/usr/bin/env python
#-*-coding:utf-8-*-
import os
import json
import commands
import sys
from itertools import chain

import psutil
from IPy import IP
from MySQL import MySQL
from config import config

from systeminfo import getFormattedNicSetInfo,SystemInfo
from db import WafNicSet,WafRoute
from sysinfo_tables import WafSessionManager
from logging import getLogger

NIC_WORKMODE = {
    "route":      "10",
    "redundancy": "10",
    "virtual":    "10",
    "mirror":     "9",
    "bridge":     "8",
    "nat":        "11",
}

IPTABLES = '/usr/sbin/iptables'
IP6TABLES = '/usr/sbin/ip6tables'
NGINX_FILE = '/Data/apps/nginx/conf/ssl.conf'


def exchange_mask(mask):
    """
    转换子网掩码格式
    >>> exchange_mask('255.255.255.255')
    32
    >>> exchange_mask('255.255.255.0')
    24
    """

    if not '.' in mask: return mask
    mask_bin = ''.join([bin(int(i)) for i in mask.split('.')])
    return mask_bin.count('1')

def strmask_to_intv6(mask):
    if not ':' in mask: return mask
    mask_bin = ''.join([bin(int(i, 16)) for i in mask.split(':') if i])
    return mask_bin.count('1')

def ip_addr(ip_obj, device, is_add=True):
    """add or del ipaddress"""
    _map = {True: 'add', False: 'del'}
    ip_cmd = 'ip -{version:} addr {action:} {addr:} dev {device:}'
    status, output = commands.getstatusoutput(ip_cmd.format(version=ip_obj.version(),
                                                            action=_map[is_add],
                                                            addr=ip_obj.string,
                                                            device=device))
    if status:
        getLogger('main').warning('device `%s` ip config `%s` failed| %s', device, ip_obj.string, output)


class MyIP(IP):
    """自定义ip对象，用于储存ip地址和掩码"""
    def __init__(self, data, netmask):
        super(MyIP, self).__init__(data)
        self.addr = data
        self.int_mask = str(exchange_mask(netmask)) if self.version() == 4 else str(strmask_to_intv6(netmask))

    def __eq__(self, other):
        return super(MyIP, self).__eq__(other) and self.int_mask == other.int_mask

    def __repr__(self):
        return "MyIP('%s', '%s')" % (self.addr, self.int_mask)

    def __str__(self):
        return self.string

    @property
    def string(self):
        """输出192.168.1.1/24这种形式的的ip"""
        return '%s/%s' % (self.strNormal(1), self.int_mask)


class IfaceAddress(object):
    def __init__(self, portname):
        self.db = MySQL(config['db'])
        sqlstr = "SELECT * FROM waf.t_nicset WHERE nic='%s'"%portname
        self.db.query(sqlstr)
        data = self.db.fetchOneRow()
        self.sIPV4Address = data["ip"] or ""
        self.sIPV6Address = ""
        self.sPortName = portname
        self.sNetMask = data["mask"]
        self.sWorkMode = data["workpattern"]
        self.sIPV4NextJump = data["gateway"]
        self.iStatus = data["isstart"]
        self.all_ifaces = psutil.net_if_stats().keys()
        self.mode_num = NIC_WORKMODE.get(self.sWorkMode, '10')

    def __del__(self):
        self.db.close()

    def config(self):
        """配置"""
        if self.sPortName not in self.all_ifaces:
            getLogger('main').warning('iface no found in devices')
            return
        if str(self.iStatus) == '1':
            self.enable()
        elif str(self.iStatus) == '0':
            self.disable()

    def disable(self):
        """禁用"""
        os.popen("ifconfig %s down"%self.sPortName)
        self._clean_up()
        getLogger('main').info('iface `%s` down', self.sPortName)

    def enable(self):
        """启用"""
        os.popen("ifconfig %s up"%self.sPortName)
        self._clean_up()
        self._prepare_data()
        self._proc_workmode()
        self._proc_addresses()
        if self.sNetMask:
            ConfigRoute([self.sPortName, self.sIPV4Address, self.sNetMask, self.sIPV4NextJump])  # 启用网口时重配静态路由
        getLogger('main').info('iface `%s` del_ip: %s ===> add_ip: %s',
                               self.sPortName, self.old_ips, self.new_ips)

    def _prepare_data(self):
        """预处理一些数据，获得旧ip、待配置ip"""
        new_ips = set()
        for i in chain(self.sIPV4Address.split(','), self.sIPV6Address.split(',')):
            if i and i.strip():
                i = "%s/%s"%(i, self.sNetMask)
                i = i.strip().split('/')
                new_ips.add(MyIP(i[0], i[1]))
        old_ips = psutil.net_if_addrs()[self.sPortName]
        old_ips = {MyIP(i.address, i.netmask) for i in old_ips
                   if i.family in (2, 10) and '%' not in i.address}
        _same = new_ips & old_ips
        old_ips = old_ips - _same
        self.new_ips = new_ips
        self.old_ips = old_ips


    def _proc_addresses(self):
        """删除旧ip，添加新ip"""
        for i in self.old_ips:
            ip_addr(i, self.sPortName, is_add=False)
        for i in self.new_ips:
            ip_addr(i, self.sPortName, is_add=True)

    def _clean_up(self):
        #(TODO)peixu:待完善
        """清除iptable规则"""
        pass

    def _proc_workmode(self):
        """工作模式配置"""
        mode_cmd = '/home/ng_platform/bd_dpdk_warper/clients/port_config %s %s'
        status, output = commands.getstatusoutput(mode_cmd % (self.sPortName, self.mode_num))
        getLogger('main').info(mode_cmd, self.sPortName, self.mode_num)
        if status:
            getLogger('main').error(output)



def GetRouteInfo(nicname):
    """get default gateways"""
    gateways = []
    try:
        fileRoute = os.popen("route -n | grep \"" +nicname + "\"")
        #ip,gw,mask,nic
        for line in fileRoute:
            tmplist = line.strip().split()
            #ignore the defualt gateway
            if tmplist[0] == "0.0.0.0" and tmplist[2] == "0.0.0.0":
                continue
            if tmplist[3].upper() == "UG":
                tmpdic = {tmplist[-1]:(tmplist[0],tmplist[1],tmplist[2])}
                gateways.append(tmpdic)
    except:
        return gateways
    return gateways

def GetRouteAllInfo():
    """get all gateways"""
    gateways = []
    fileRoute = os.popen("/sbin/route -n")
    for line in fileRoute:
        tmplist = line.strip().split()
        if not tmplist[0][0].isdigit():
            continue
        #the tmpdic[nic][-1] is a flag whether a route is a default route
        #ip,gw,mask,nic,isdefault
        if tmplist[3].upper() == "UG":
            tmp = (tmplist[0],tmplist[1],tmplist[2],tmplist[-1],1)
            gateways.append(tmp)
        else:
            tmp = (tmplist[0],tmplist[1],tmplist[2],tmplist[-1],0)
            gateways.append(tmp)
    return gateways

def SetNicStatus(nicname,enabled):
    """ enabled=1:set nic up, otherwise set nic down"""
    upstr = "/sbin/ifconfig %s up" % nicname
    downstr = "/sbin/ifconfig %s down" % nicname
    ret = 0
    if enabled == 1:
        ret = os.system(upstr)
    else:
        ret = os.system(downstr)
    return ret

def GetNIP(ipstr,submaskstr):
    """ to get sub network address"""
    iplist = ipstr.split(".")
    sublist = submaskstr.split(".")
    subnet = []
    for i in range(0,len(iplist)):
        subnet.append(str(int(iplist[i]) & int(sublist[i])))

    return ".".join(subnet)

def SetNicIpInfo(nicname,ipstr,submaskstr):
    """ gatewayopt can be add or del"""
    #set nic ip first
    ret = 0
    if ipstr:
        strip = "/sbin/ifconfig %s %s netmask %s up" % (nicname,ipstr,submaskstr)
        ret = os.system(strip)
    else:
        ret = os.system("/sbin/ifconfig %s 0.0.0.0 up" % nicname)
    return ret
    # if gatewaystr:
    #     gateways = GetRouteInfo(nicname)
    #     #[{nic:(ip,gateway,netmask)}], ip must be a subnet ip
    #     subnet = GetNIP(ipstr,submaskstr)
    #     for nicn in gateways:
    #         tmpipinfo = nicn[nicname]
    #         if gatewayopt == "del":
    #             delstr = ""
    #             if gatewaystr == "0.0.0.0":
    #                 delstr = "/sbin/route del -net %s netmask %s dev %s" % ( tmpipinfo[0],tmpipinfo[2],nicname )
    #             else:
    #                 delstr = "/sbin/route del -net %s netmask %s gw %s" % ( tmpipinfo[0],tmpipinfo[2],tmpipinfo[1] )
    #             ret = os.system(delstr)
    #             if ret != 0:
    #                 getLogger('main').warning('delete gateway %s failed' % gatewaystr)
    #             continue
    #         if tmpipinfo[0] == ipstr and tmpipinfo[2] == subnet and tmpipinfo[1] == gatewaystr:
    #             continue
    #         routestr = ""
    #         if gatewaystr == "0.0.0.0":
    #             routestr = "/sbin/route %s -net %s netmask %s dev %s" % (gatewayopt,subnet,submaskstr,nicname )
    #         else:
    #             routestr = "/sbin/route %s -net %s netmask %s gw %s" % (gatewayopt,subnet,submaskstr,gatewaystr )
    #         ret = os.system(routestr)
    #         if ret != 0:
    #             getLogger('main').warning('add gateway %s failed' % gatewaystr)


#nics is a listt
def ConfigNic(nics):
    """
    nics: a list of nic names
    only set nic's ip and mask,except gateway
    """
    getLogger('main').info('ConfigNic Start')
    session = WafSessionManager()
    for nic in nics:
        ipinfo = session.GetNicIpSetInfo(nic)
        #(ip,mask,gateway,isstart)
        if nic in ipinfo:
            getLogger('main').info(ipinfo[nic][0])
            ##make sure nic is running
            #SetNicStatus(nic,1)
            SetNicIpInfo(nic,ipinfo[nic][0],ipinfo[nic][1])
            SetNicStatus(nic, ipinfo[nic][3])
        else:
            os.system("/sbin/ifconfig %s 0.0.0.0" % nic)
    getLogger('main').info('ConfigNic End')

# def ClearAllNic(nics=[]):
#     getLogger('main').info('ClearAllNic Start')
#     session = WafSessionManager()
#     ipinfos = session.GetAllNicIpSetInfo()
#     brgs = session.GetAllBridgeNameInfo()
#     for nic in ipinfos:
#         if nic in brgs:
#             #when set nic ,the brg may not exist,only set the brg's nic up
#             tmpbrginfo = session.GetBridgeInfo(nic)
#             tmpnics = tmpbrginfo[nic][0].split(",")
#             for tmpnic in tmpnics:
#                 SetNicStatus(tmpnic,1)
#             continue
#         tmpinfo = ipinfos[nic]
#         SetNicStatus(nic,1)
#         SetNicIpInfo(nic,tmpinfo[0],tmpinfo[1])
#     getLogger('main').info('ClearAllNic End')

def ConfigAllNic(nics=[]):
    """only used to restore the nic settings in database after being rebooted"""
    getLogger('main').info('ConfigAllNic Start')
    session = WafSessionManager()
    ipinfos = session.GetAllNicIpSetInfo()  # t_nicset dict
    #because the nic maybe a brg and the brg may not exist,ConfigNic should not be used
    #ConfigNic(ipinfos.keys())
    brgs = session.GetAllBridgeNameInfo()
    for nic in ipinfos:
        # print nic
        if nic in brgs:
            #when set nic ,the brg may not exist,only set the brg's nic up
            tmpbrginfo = session.GetBridgeInfo(nic)
            tmpnics = tmpbrginfo[nic][0].split(",")
            # print "www", tmpnics
            for tmpnic in tmpnics:
                SetNicStatus(tmpnic,1)
            continue
        tmpinfo = ipinfos[nic]
        # print "ddd", tmpinfo
		# to set nic in sys as database edit by ddjian
        SetNicStatus(nic,tmpinfo[3])
        if nic.find("vEth") != -1:
            IfaceAddress(nic).config()
        else:
            SetNicIpInfo(nic,tmpinfo[0],tmpinfo[1])
    getLogger('main').info('ConfigAllNic End')

def InitNicSetTable(clearfirst = True):
    """insert all the nic info to database"""
    import netifaces
    getLogger("main").info("refresh route table")
    sinfo   = SystemInfo()
    session = WafSessionManager()
    if clearfirst:
        session.ClearAllNicInfo()
    nicinfos = getFormattedNicSetInfo(sinfo)
    for nicname in nicinfos:
        nicinfos[nicname].lan_port = nicinfos[nicname].nic
        nicinfos[nicname].lan_type = 'common'
        nicinfos[nicname].mac = netifaces.ifaddresses(nicname)[netifaces.AF_LINK][0]['addr']
        session.AddNicInfo(nicinfos[nicname])

def RefreshNicSetTable(isall = True): 	# add isall to refresh nicset if isstart is needed
    """
    func: update nicset in database
    """
    getLogger("main").info("refresh nicinfo table")
    sinfo   = SystemInfo()
    session = WafSessionManager()
    oldnicname = session.GetAllNicIpSetInfo()
    nicinfos = getFormattedNicSetInfo(sinfo)
    for nicname in nicinfos:
        if nicname in oldnicname:
            session.UpdateNicInfo(nicinfos[nicname], isall)


def InitRouteTable(clearfirst = True):
    """insert all the available route info to database"""
    getLogger("main").info("refresh route table")
    gateways = GetRouteAllInfo()
    session = WafSessionManager()
    if clearfirst:
        session.ClearAllRouteInfo()
    #print gateways
    for gtw in gateways:
        tmp = WafRoute()
        #ip,gw,mask,nic,isdefault
        tmp.dest = gtw[0]
        tmp.gateway = gtw[1]
        tmp.mask = gtw[2]
        tmp.nic=gtw[3]
        tmp.isdefault=gtw[4]
    #    print tmp
        session.AddRoute(tmp)

def ConfigRoute(args):
    getLogger('main').info('ConfigRoute Start')
    tuplist = []
    leng = len(args)
    i = 0
    pos = 0
    while i < leng/4:
        tupinfo = (args[pos],args[pos+1],args[pos+2],args[pos+3])
        tuplist.append(tupinfo)
        i += 1
        pos += 4
    session = WafSessionManager()
    #nic,ip,mask,gateway
    for rec in tuplist:
        infos = session.GetRouteInfo(rec[0],rec[1],rec[2],rec[3])
        rs = GetRouteAllInfo()
        subnet = GetNIP(rec[1],rec[2])
        if not infos:   #del
            delflag = False
            for r in rs:
                #ip,gw,mask,nic,isdefault
                if r[0] == rec[1] and r[1] == rec[3] and r[2] == rec[2] and r[3] == rec[0]:
                    delflag = True
                    break
                #no need for netmask
                if rec[1].split(".")[-1] != '0' and r[1] == rec[3] and r[3] == rec[0] and r[0] == rec[1]:
                    delflag = True
                    break
            if delflag:
                cmdstr = ""
                #ip is network ip
                if rec[1].split(".")[-1] == '0':
                    if rec[3]:
                        cmdstr = "/sbin/route del -net %s netmask %s gw %s dev %s" % (subnet,rec[2],rec[3],rec[0])
                    else:
                        cmdstr = "/sbin/route del -net %s netmask %s dev %s" % (subnet,rec[2],rec[0])
                    getLogger('main').warning('%s' % cmdstr)
                    if os.system(cmdstr) != 0:
                        getLogger('main').warning('Route %s del failed' % subnet)
                else:#ip is host ip
                    if rec[3] and rec[3] != "0.0.0.0":
                        cmdstr = "/sbin/route del -host %s gw %s dev %s" % (rec[1],rec[3],rec[0])
                    else:
                        cmdstr = "/sbin/route del -host %s dev %s" % (rec[1],rec[0])
                    getLogger('main').warning('%s' % cmdstr)
                    if os.system(cmdstr) != 0:
                        getLogger('main').warning('Route %s del failed' % rec[1])
        else:       #add
            if rec[1]:           #add a route
                addflag = True
                for r in rs:
                    #ip,gw,mask,nic,isdefault
                    if r[0] == rec[1] and r[1] == rec[3] and r[2] == rec[2] and r[3] == rec[0]:
                        addflag = False
                        break
                    #no need for netmask
                    if rec[1].split(".")[-1] != '0' and r[1] == rec[3] and r[3] == rec[0] and r[0] == rec[1]:
                        addflag = False
                        break
                if addflag:
                    #add the default route?
                    if rec[1] == "0.0.0.0" and rec[2] == "0.0.0.0" and rec[3] != "0.0.0.0":
                        cmdstr = "/sbin/route add default gw %s" % rec[3]
                        if os.system(cmdstr) != 0:
                            getLogger('main').info("route add default gwt failed")
                    else:
                        routestr = ""
                        if rec[1].split(".")[-1] == '0':#ip is a network ip
                            if rec[3] and rec[3] != "0.0.0.0":
                                routestr = "/sbin/route add -net %s netmask %s gw %s dev %s" % (subnet,rec[2],rec[3],rec[0])
                            else:
                                routestr = "/sbin/route add -net %s netmask %s dev %s" % (subnet,rec[2],rec[0] )
                            getLogger('main').warning('%s' % routestr)
                            if os.system(routestr) != 0:
                                getLogger('main').warning('add route %s failed' % subnet)
                        else:#ip is a host ip
                            if rec[3] and rec[3] != "0.0.0.0":
                                routestr = "/sbin/route add -host %s gw %s dev %s" % (rec[1],rec[3],rec[0])
                            else:
                                routestr = "/sbin/route add -host %s dev %s" % (rec[1],rec[0] )
                            getLogger('main').warning('%s' % routestr)
                            if os.system(routestr) != 0:
                                getLogger('main').warning('add route %s failed' % rec[1])

    getLogger('main').info('ConfigRoute End')

def ConfigAllRoute():
    getLogger('main').info('ConfigAllRoute Start')
    session = WafSessionManager()
    infos = session.GetAllRouteInfo()
    for info in infos:
        if info.dest:           #add a route
            addflag = True
            rs = GetRouteAllInfo()
            for r in rs:
                #ip,gw,mask,nic,isdefault
                if r[0] == info.dest and r[1] == info.gateway and r[2] == info.mask and r[3] == info.nic:
                    addflag = False
                    break
                #no need for netmask
                if info.dest.split(".")[-1] != '0' and r[1] == info.gateway and r[3] == info.nic and r[0] == info.dest:
                    addflag = False
                    break
            if addflag:
                #add the default route?
                routestr = ""
                if info.dest == "0.0.0.0" and info.mask == "0.0.0.0" and info.gateway != "0.0.0.0":
                    routestr = "/sbin/route add default gw %s" % info.gateway
                    if os.system(routestr) != 0:
                        getLogger('main').info("route add default gwt failed")
                else:
                    subnet = GetNIP(info.dest,info.mask)
                    if info.gateway.split(".")[-1] == '0':#ip is a network ip
                        if info.gateway and info.gateway != "0.0.0.0":
                            routestr = "/sbin/route add -net %s netmask %s gw %s dev %s" % (subnet,info.mask,info.gateway,info.nic)
                        else:
                            routestr = "/sbin/route add -net %s netmask %s dev %s" % (subnet,info.mask,info.nic )
                        getLogger('main').warning('%s' % routestr)
                        if os.system(routestr) != 0:
                            getLogger('main').warning('add route %s failed' % subnet)
                    else:#ip is a host ip
                        if info.gateway and info.gateway != "0.0.0.0":
                            # routestr = "/sbin/route add -host %s gw %s dev %s" % (info.dest,info.gateway,info.nic)
                            routestr="/sbin/route add -net %s netmask %s gw %s dev %s"%(info.dest,info.mask,info.gateway,info.nic)
                        else:
                            routestr = "/sbin/route add -host %s dev %s" % (info.dest,info.nic )
                        getLogger('main').warning('%s' % routestr)
                        if os.system(routestr) != 0:
                            getLogger('main').warning('add route %s failed' % info.dest)
    getLogger('main').info('ConfigAllRoute End')

def RecoverSysRoute():
    """
    func: delete all route except default route and route in admin nic
    """
    getLogger('main').info('Delete Route When Changing Deploy Type')
    session = WafSessionManager()
    deAdminNic = session.GetDefaultAdminNic()
    # Get system route records except default route and the route in admin nic
    info = os.popen("route -n|grep -v 'Kernel'|grep -v 'Destination'|grep -v '%s'" % deAdminNic).readlines()
    if info:
        for line in info:
            tmplist = line.split()
            cmdstr = "/sbin/route del -net %s netmask %s dev %s" %(tmplist[0], tmplist[2],tmplist[-1])
            if os.system(cmdstr) != 0:
                getLogger('main').warning('Delete Non-default Route Failed! %s in %s' % (tmplist[0], tmplist[-1]))
    getLogger('main').info('Delete Route When Changing Deploy Type finished.')

if __name__=="__main__":
    #ConfigAllNic()
    InitNicSetTable()
    #ConfigAllRoute()
    #InitRouteTable()
