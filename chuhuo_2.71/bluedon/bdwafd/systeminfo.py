# -*- coding:utf8 -*-
#!/usr/bin/env python

import multiprocessing
import psutil
import socket
import struct
import threading
import collections
import datetime
import time
from sqlalchemy import and_, func
from sysinfo_tables import WafSessionManager
from db import (
    WafSysInfo, WafNicsFlow, WafNicSet,
    session_scope, fw_session_scope,
)
from fwdb import NetPort
from logging import getLogger
from sets import Set


# the netflow info of nics
nicflowinfo = collections.namedtuple(
    "nicflowinfo", "recvdbytes sentbytes recvdpkg sentpkg errin errout dropin dropout")
# the netratio info of nics
nicratioinfo = collections.namedtuple(
    "nicratioinfo", "recvd_total recvd_ratio sent_total sent_ratio")
# the general info of nics
nicstatusinfo = collections.namedtuple(
    "nicstatusinfo", "duplex speed ip submask gateway enabled linkstat bridge")


def getNicGatWay():
    """return a list whose element is a dick: nice_name:gatway"""
    nicgateway = []  # nicname:gateway
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[0] == 'Iface':
                continue
            if int(fields[3], 16) & 2:
                nicgateway.append({fields[0]: socket.inet_ntoa(
                    struct.pack("<L", int(fields[2], 16)))})
        return nicgateway


class SystemInfo(threading.Thread):
    """It can acquire cpu%, disk space, memory, network flow info"""
    def __init__(self):
        super(SystemInfo, self).__init__()
        # network interface card ratio info
        self.nicratio = {}
        self.allnicratio = nicratioinfo(
            recvd_total=0, recvd_ratio=0, sent_total=0, sent_ratio=0)
        # mutex and main thread control
        self.event = threading.Event()
        self.exitflag = False

    def start(self):
        """ start the thread to compute the realtime transimit ratio of nics"""
        self.event.set()
        super(SystemInfo, self).start()

    def stop(self):
        """ stop the thread to compute the realtime transimit ratio of nics"""
        self.event.clear()
        self.exitflag = True
        self.join()

    def run(self):
        """ main thread to compute the transmit ratio of nics"""
        while True:
            try:
                if self.exitflag:
                    break
                if not self.event.is_set():
                    self.event.wait()
                time.sleep(1)
                netinfo = psutil.net_io_counters(True)
                for k in netinfo:
                    tmpratio = nicratioinfo(recvd_total=netinfo[k].bytes_recv,
                                            recvd_ratio=0,
                                            sent_total=netinfo[k].bytes_sent,
                                            sent_ratio=0)
                    if k not in self.nicratio:  # initialize self.nicratio
                        self.nicratio[k] = tmpratio
                    else:  # update self.nicratio
                        lastratio = self.nicratio[k]
                        tmp = nicratioinfo(recvd_total=tmpratio.recvd_total,
                                           recvd_ratio=int(tmpratio.recvd_total) - int(lastratio.recvd_total),
                                           sent_total=tmpratio.sent_total,
                                           sent_ratio=int(tmpratio.sent_total) - int(lastratio.sent_total))
                        self.nicratio[k] = tmp

                netflowTotal = psutil.net_io_counters()
                tmpratiototal = nicratioinfo(
                    recvd_total=netflowTotal.bytes_recv, recvd_ratio=0,
                    sent_total=netflowTotal.bytes_sent, sent_ratio=0)
                if self.allnicratio == ():  # initialize self.allnicratio
                    self.allnicratio = tmpratiototal
                else:  # update self.allnicratio
                    self.allnicratio = nicratioinfo(
                        recvd_total=tmpratiototal.recvd_total,
                        recvd_ratio=int(tmpratiototal.recvd_total) - int(self.allnicratio.recvd_total),
                        sent_total=tmpratiototal.sent_total,
                        sent_ratio=int(tmpratiototal.sent_total) - int(self.allnicratio.sent_total))
            except Exception, e:
                getLogger('main').exception(e)

    def getNicIps(self):
        """to get all nic's ip4 and ip6 addr and its relative mask"""
        import netifaces
        nics = netifaces.interfaces()
        # nicname:[{addr:netmask}]
        nicsaddr = {}
        for item in nics:
            adict = netifaces.ifaddresses(item)
            # define AF_INET         2       /* Internet IP Protocol         */
            # define AF_INET6        10      /* IP version 6                 */
            # define AF_PACKET       17      /* Packet family                */
            #{2:[{}],10:[{}]}
            iplist = []
            for key in adict:                           # a dict keys are:2,10,17,etc
                if key == 17 or key == 10:  # only ip4 concerned
                    continue
                tmplist = ()
                for innerdict in adict[key]:            # a list,means a nic has more than one ip
                    if "netmask" in innerdict and "addr" in innerdict:
                        # tmpaddr = innerdict["addr"].split(".")
                        # if tmpaddr[0] == "127":
                        #    continue
                        # print "addr:%s" % innerdict["addr"]
                        # tmplist=(innerdict["addr"],innerdict["netmask"])
                        if "br" in item:
                            if innerdict['broadcast'].split('.')[-1] == '255':
                                tmplist = (
                                    innerdict["addr"], innerdict["netmask"])
                        else:
                            tmplist = (innerdict["addr"], innerdict["netmask"])
                if tmplist:
                    iplist.append(tmplist)
            if iplist:
                nicsaddr[item] = iplist
        return nicsaddr

    # return all nics' enable info
    def getAllNicEnableInfo(self):
        """return a dict :nic_name:True/False, True means enabled, while False not"""
        import os
        import re
        # to get all nic device
        nicenabled = {}
        nicdev = []  # nicnames
        nicif = []  # nicnames

        fdev = open("/proc/net/dev")
        for line in fdev:
            if line.find(":") > 0:
                info = line.strip().split()
                if re.match(r'virbr.+', info[0][0:-1]):  # ignore virbr0,virbr0-nic
                    continue
                nicdev.append(info[0][0:-1])  # to strip ':'
        # to get the active nic
        fifconfig = os.popen("/sbin/ifconfig | grep \"^\\w\"")
        for line in fifconfig:
            info = line.strip().split()
            name, _, other = info[0].partition(':')
            # if info[0] == 'eth3:1':
                # continue
            if other:
                continue
            if re.match(r'virbr.+', name):  # ignore virbr0,virbr0-nic
                continue
            nicif.append(name)
            nicenabled[name] = True
        # set nic's disabled flag
        for item in nicdev:
            if item not in nicif:
                nicenabled[item] = False
        return nicenabled

    def getNicDuplex(self, allnics):
        """return a dict: nic_name:full/half"""
        import os
        nicduplex = {}
        for eth in allnics:
            nicmodstr = "/sbin/ethtool " + eth + " | grep -i duplex"
            fethtool = os.popen(nicmodstr)
            for line in fethtool:
                if line.upper().find("FULL"):
                    nicduplex[eth] = "full"
                else:
                    nicduplex[eth] = "half"
        return nicduplex

    def getNicSpeed(self, allnics):
        """return a dict: nic_name:speed (with unit)"""
        import os
        nicspeed = {}
        for eth in allnics:
            nicmodstr = "/sbin/ethtool " + eth + \
                " | grep -i speed | grep -o [0-9]*[0-9]"
            fethtool = os.popen(nicmodstr)
            for line in fethtool:
                nicspeed[eth] = line[0:-1]
        return nicspeed

    def getNicLinkStatus(self, allnics):
        """get nic's active status,1=linked,0=unlinked"""
        # 1:active,0:deactive
        import os
        niclink = {}
        for eth in allnics:
            nicmodstr = "/sbin/ethtool " + eth + " | grep -i \"link detected\""
            fethtool = os.popen(nicmodstr)
            for line in fethtool:
                if line.upper().find("YES") > 0:
                    niclink[eth] = int(1)
                    break
                else:
                    niclink[eth] = int(0)
                    break
        return niclink

    def getNicBridge(self, allniclist):
        """return a dict:nic_name:[bridge_name]"""
        import os
        nicbridge = {}
        nicbridgestr = "/sbin/brctl show"
        fethbridge = os.popen(nicbridgestr)
        bridgename = ''
        for line in fethbridge:
            bridge = line.strip().split()
            if len(bridge) != 1:
                bridgename = bridge[0]
            if bridge[-1] in allniclist:
                if bridge[-1] in nicbridge:  # not None
                    nicbridge[bridge[-1]].append(bridgename)
                else:
                    nicbridge[bridge[-1]] = [bridgename]
        return nicbridge

    def getNicStatus(self):
        """ to get general info of nics,like working mode,original speed,connecting state , bridge"""
        nicstat = {}
        nicsips = self.getNicIps()

        nicgateway = getNicGatWay()
        # all nic's enabled info
        allnicenabledinfo = self.getAllNicEnableInfo()

        # all nic list
        nicdev = allnicenabledinfo.keys()
        # to get nic's speed mode
        nicspeed = self.getNicSpeed(allnicenabledinfo)
        # to get nic duplex mode
        nicduplex = self.getNicDuplex(allnicenabledinfo)
        # get active stat
        niclink = self.getNicLinkStatus(allnicenabledinfo)

        # to get bridge info
        nicbridge = self.getNicBridge(nicdev)
        # reform info in nametuple nicstatusinfo
        for nicname in allnicenabledinfo:
            tmpip = []
            tmpmask = {}
            if nicname in nicsips:
                for li in nicsips[nicname]:  # li is a list cotain [ip4,netmask] and [ip6,netmask]
                    tmpip.append(li[0])
                    tmpmask[li[0]] = li[1]
            tmpgateway = ''
            for it in nicgateway:
                if nicname in it:
                    tmpgateway = it[nicname]
                    break
            tmpbridge = nicbridge.get(nicname, '')
            tmpduplex = nicduplex.get(nicname, '')
            tmpspeed = nicspeed.get(nicname, '')
            tmplink = niclink.get(nicname, int(0))
            nicstat[nicname] = nicstatusinfo(
                duplex=tmpduplex, speed=tmpspeed, ip=tmpip, submask=tmpmask,
                gateway=tmpgateway, enabled=allnicenabledinfo[nicname], linkstat=tmplink, bridge=tmpbridge)

        return nicstat


def getNicFlowInfo():
    """ return a dict whose element is a nicflowinfo data,the key is the nic's name"""
    netflows = psutil.net_io_counters(True)
    # measured by byte
    tmp = {}
    for key in netflows:
        tmp[key] = nicflowinfo(
            recvdbytes=netflows[
                key].bytes_recv, sentbytes=netflows[key].bytes_sent,
            recvdpkg=netflows[
                key].packets_recv, sentpkg=netflows[key].packets_sent,
            errin=netflows[key].errin, errout=netflows[key].errout,
            dropin=netflows[key].dropin, dropout=netflows[key].dropout)
    return tmp


def getNicMacs():
    """ return a dict, whose key is the nic's name and the value is this nic's mac address"""
    import fcntl
    import socket
    import struct
    nicmacs = {}
    for key in psutil.net_io_counters(True):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', key[:15]))
        strmac = ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
        nicmacs[key] = strmac
    return nicmacs


def getFormattedNicFlowInfo(SystemInfoObj):
    infos = {}
    netflows = getNicFlowInfo()
    nicmacs = getNicMacs()

    allnicenabledinfo = SystemInfoObj.getAllNicEnableInfo()
    nicmodes = SystemInfoObj.getNicDuplex(allnicenabledinfo)
    niclinkstat = SystemInfoObj.getNicLinkStatus(allnicenabledinfo)
    ips = SystemInfoObj.getNicIps()

    nicbridge = SystemInfoObj.getNicBridge(allnicenabledinfo)
    bridges = []
    niclocals = []

    with fw_session_scope() as session:
        nic_to_lan = dict(session.query(NetPort.sPortName, NetPort.sLan).all())
    for nicname in nicbridge:
        if nicbridge[nicname]:
            for i in nicbridge[nicname]:  # nicbridge[nicname] is a list,eth2:[br0,br1,...]
                if not bridges or not i in bridges:
                    bridges.append(i)

    for nicn in allnicenabledinfo:
        if nicn in bridges:  # to hide bridge card flow info from nic flow info
            continue

        if nicn in ips:
            ipstr = ips[nicn][0][0]
            ipsplited = ipstr.split(".")
            if ipsplited[0] == "127":
                continue

        tmpmac = ""
        if nicn in nicmacs:
            tmpmac = nicmacs[nicn]
        else:
            if nicn.find(":"):
                tmpmac = nicn[:nicn.find(":")]
                if tmpmac in nicmacs:
                    tmpmac = nicmacs[tmpmac]

        tmpflow = netflows.get(nicn, nicflowinfo(recvdbytes=int(0), sentbytes=int(0),
                                        recvdpkg=int(0), sentpkg=int(0), errin=int(0),
                                        errout=int(0), dropin=int(0), dropout=int(0)))
        tmpmode = nicmodes.get(nicn, "auto")
        tmplink = niclinkstat.get(nicn, int(0))
        wn = WafNicsFlow(nic=nic_to_lan[nicn], mac=tmpmac, mode=tmpmode, status=tmplink,
                         rcv_pks=tmpflow.recvdpkg, snd_pks=tmpflow.sentpkg, 
                         rcv_bytes=tmpflow.recvdbytes, snd_bytes=tmpflow.sentbytes,
                         rcv_errs=tmpflow.errin, snd_errs=tmpflow.errout, 
                         rcv_losts=tmpflow.dropin, snd_losts=tmpflow.dropout,
                         time=time.strftime("%Y-%m", time.localtime()))
        infos[nicn] = wn
    return infos


def getFormattedNicSetInfo(SystemInfoObj):
    tmpdic = {}
    allnicenabledinfo = SystemInfoObj.getAllNicEnableInfo()
    nicdev = allnicenabledinfo.keys()
    nicips = SystemInfoObj.getNicIps()
    nicbridge = SystemInfoObj.getNicBridge(nicdev)
    bridges = []
    niclocals = []
    for nicname in nicbridge:
        if nicbridge[nicname]:
            for i in nicbridge[nicname]:  # nicbridge[nicname] is a list,eth2:[br0,br1,...]
                if not bridges or not i in bridges:
                    bridges.append(i)
    for nicname in nicips:
        ipstr = nicips[nicname][0][0]
        ipsplited = ipstr.split(".")
        if ipsplited[0] == "127":
            niclocals.append(nicname)
    nicinfos = SystemInfoObj.getNicStatus()

    for nicname in nicinfos:
        # do not show local nic in nicset table
        # if nicname in bridges or nicname in niclocals:
        if nicname in niclocals:
            continue

        tmpinfo = nicinfos[nicname]
        # duplex speed ip submask gateway enabled linkstat bridge
        tmpenable = int(0)
        if tmpinfo.enabled:
            tmpenable = int(1)
        tmplink = tmpinfo.linkstat
        tmpip = ""
        if tmpinfo.ip:
            if tmpinfo.ip[0]:
                tmpip = tmpinfo.ip[0]

        tmpmask = tmpinfo.submask.get(tmpip, "")
        tmpbridge = ",".join(tmpinfo.bridge)
        ns = WafNicSet(
            nic=nicname, ip=tmpip, mask=tmpmask, gateway=tmpinfo.gateway,
            isstart=tmpenable, islink=tmplink, workmode=tmpinfo.duplex, desc="", brgname=tmpbridge)
        tmpdic[nicname] = ns

    return tmpdic


class SystemInfoThread(threading.Thread):
    def __init__(self):
        super(SystemInfoThread, self).__init__(name=self.__class__.__name__)
        self.sinfo = SystemInfo()
        self.event = threading.Event()

    def start(self):
        getLogger('main').debug(self.__class__.__name__+ ' starting...')
        super(SystemInfoThread, self).start()
        getLogger('main').info(self.__class__.__name__+ ' started.')

    def stop(self):
        getLogger('main').debug(self.__class__.__name__+ ' Exiting...')
        self.event.set()
        self.join()
        getLogger('main').info(self.__class__.__name__+ ' Exited.')

    def mergeNetFlowInfo(self, oldinfo, newinfo):
        keys = oldinfo.keys() + newinfo.keys()
        keyset = Set(keys)
        tmp = {}
        for key in keyset:
            old = oldinfo.get(key, [0, 0])  # recv,sent
            new = newinfo.get(key, [0, 0])
            tmplist = []
            for i in range(0, len(old)):
                subvalue = new[i] - old[i]
                if int(subvalue) < 0:
                    subvalue = 0
                tmplist.append(subvalue)
            tmp[key] = tmplist
        return tmp

    def getsysinfo(self):
        mem = psutil.virtual_memory()
        parts = psutil.disk_partitions()
        total, used = 0, 0
        for part in parts:
            disk = psutil.disk_usage(part.mountpoint)
            total += int(disk.total)
            used += int(disk.used)
        return WafSysInfo(id=1,
                          time=time.mktime(time.localtime()),
                          cpu_ratio=psutil.cpu_percent(),
                          total_mem=mem.total / 1024 / 1024,
                          used_mem=(mem.used - mem.cached - mem.buffers) / 1024 / 1024,
                          total_disk = total / 1024 / 1024,
                          used_disk = used / 1024 / 1024)

    def proc(self):
        with session_scope() as session:
            cur_date = time.strftime("%Y-%m", time.localtime())
            for info in getFormattedNicFlowInfo(self.sinfo).values():
                q = session.query(WafNicsFlow).filter(and_(WafNicsFlow.nic==info.nic,
                                                       WafNicsFlow.time==cur_date))
                if q.first():
                    for k, v in info.__dict__.iteritems():
                        if k in ('rcv_pks', 'snd_pks', 'rcv_bytes', 'snd_bytes', 
                                'rcv_errs', 'snd_errs', 'rcv_losts', 'snd_losts'):
                            data = session.query(func.sum(getattr(WafNicsFlow, k))).filter(and_(
                                        WafNicsFlow.nic==info.nic, WafNicsFlow.time<cur_date)).one()
                            if data[0] and info.__dict__[k] > data[0]:
                                info.__dict__[k] = info.__dict__[k] - data[0]
                    info.__dict__.pop('_sa_instance_state')
                    q.update(info.__dict__)
                else:
                    session.add(info)


    def run(self):
        while 1:
            try:
                time.sleep(3600)
                if self.event.isSet():
                    return
                self.proc()
            except Exception, e:
                getLogger('main').exception(e)


if __name__ == '__main__':
    SystemInfoThread().proc() 
