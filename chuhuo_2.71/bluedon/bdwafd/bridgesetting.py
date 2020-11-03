#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
from sets import Set
from logging import getLogger
from db import WafBridge
from sysinfo_tables import WafSessionManager
from nicsetting import ConfigNic, InitNicSetTable, SetNicStatus, RefreshNicSetTable
from nginx import NginxController


def GetBridgeNics():
    bridges = {}
    bridgename = ''
    tmpnics = []
    bridgeconf = GetBridgeInfoFromConf()
    bridgestr = "/sbin/brctl show"
    fbridge = os.popen(bridgestr)
    for line in fbridge:
        brg = line.strip().split()
        if brg and re.match(r'virbr', brg[0]):
            continue
        if len(brg) > 4:  # ignore first line
            continue
        elif len(brg) == 3:     # delete invalid bridge
            if brg[0] not in bridgeconf: 
                os.system('/sbin/ifconfig ' + brg[0] + ' down')
                os.system('/sbin/brctl delbr ' + brg[0])
            continue
        elif len(brg) == 4:
            if tmpnics and bridgename:
                bridges[bridgename] = tmpnics
            tmpnics = []
            bridgename = brg[0]
            # reserve the eth0:stp info
            tmpnics.append((brg[-1], brg[2]))
        else:
            # another inetface in a bridge
            tmpnics.append(brg[-1])
        if tmpnics:
            bridges[bridgename] = tmpnics
    return bridges


def GetBridgeInfoFromConf():
    """
    get bridge from waf_bridge.conf
    """
    bridges = {}
    with open('/usr/local/bluedon/www/cache/waf_bridge.conf', 'r') as f:
        for line in f.readlines():
            bridgeInfo = line.strip().split()  # br0 vEth0,vEth1 num
            if len(bridgeInfo) == 3:
                bridges[bridgeInfo[0]] = [bridgeInfo[1]]
    return bridges


def GetBridgeStpInfo(brgname):
    # get bridge's stp info of brgname,not all bridges'
    bridges = {}
    bridgestr = "/sbin/brctl showstp \"" + brgname + "\""
    fbridge = os.popen(bridgestr)
    bridgename = ""
    tmpnics = []
    tmp = {}
    for line in fbridge:
        brginfo = line.strip().split()
        if len(brginfo) == 1:
            if brginfo[0] != brgname:
                if tmp and bridgename == brgname:
                    bridges[brgname] = tmp
                    break
                if tmp and brginfo[0] != "flags":
                    tmp = {}
                continue
            bridgename = brgname
        if bridgename == brgname:
            tmpstr = ""
            for num in brginfo:
                try:
                    tmpint = int(float(num))
                    # print "tmpstr:",tmpstr
                    tmp[tmpstr] = tmpint
                    break
                except ValueError:
                    tmpstr += num
    # print "bridges:",bridges
    return bridges


def SetStpOnOff(brgname, brgnics, brgset):
    ret = int(0)
    tmpnics = brgnics.get(brgname, [])
    if tmpnics:
        brginfo = brgset.get(brgname, ())
        if tmpnics[0][1].lower() == "yes":
            if brginfo and brginfo[2] != int(1):
                configstr = "/sbin/brctl stp \"" + brgname + "\" off"
                ret = os.system(configstr)
                if ret == int(0):
                    getLogger("main").info(
                        "set bridge: " + brgname + " stp off")
                else:
                    getLogger("main").info(
                        "set bridge: " + brgname + " stp off failed")
                    return ret
        else:
            if brginfo and brginfo[2] != int(0):
                configstr = "/sbin/brctl stp \"" + brgname + "\" on"
                ret = os.system(configstr)
                if ret == int(0):
                    getLogger("main").info(
                        "set bridge: " + brgname + " stp on")
                else:
                    getLogger("main").info(
                        "set bridge: " + brgname + " stp on failed")
                    return ret
    return ret


def UpdateBridgeNic(brgname, brgnics, brgset):
    tmplistdel = []
    tmplistadd = []
    brgniclist = brgnics.get(brgname, [])
    ret = int(0)
    if brgniclist:
        brgniclist = [brgniclist[0][0]] + brgniclist[1:]
        brgnicset = Set(brgniclist)
        brgsetlist = brgset[brgname][0].strip().split(",")
        brgsett = Set(brgsetlist)
        tmplistdel = brgnicset - brgsett
        tmplistadd = brgsett - brgnicset

    if tmplistadd:
        addstr = " ".join(tmplistadd)
        ret = os.system("/sbin/brctl addif " + brgname + " " + addstr)
        if ret == int(0):
            getLogger("main").info("added bridge eths")
        else:
            getLogger("main").info("added bridge eths failed")
            return ret

    if tmplistdel:
        delstr = " ".join(tmplistdel)
        ret = os.system("/sbin/brctl delif " + brgname + " " + delstr)
        if ret == int(0):
            getLogger("main").info("deleted bridge eths")
        else:
            getLogger("main").info("deleted bridge eths failed")
            return ret
    return ret


def SetBridgeStpInfo(brgname, brgstps, brgset):
    ret = int(0)
    # set ageing time?
    ageing = brgstps[brgname].get("ageingtime", int(0))
    # print "ageingtime:",ageing," str:",str(ageing)," set:",brgset[brgname][1]
    if brgset[brgname][1] != ageing:
        ret = os.system(
            "/sbin/brctl setageing " + brgname + " " + str(brgset[brgname][1]))
        if ret == int(0):
            getLogger("main").info("ageing time setted")
        else:
            getLogger("main").info("ageing time set failed")
            return ret
    # set maxage?
    age = brgstps[brgname].get("maxage", int(0))
    # print "maxage:",age," str:",str(age)," set:",brgset[brgname][4]
    if brgset[brgname][4] != age:
        ret = os.system(
            "/sbin/brctl setmaxage " + brgname + " " + str(brgset[brgname][4]))
        if ret == int(0):
            getLogger("main").info("max age setted")
        else:
            getLogger("main").info("max age set failed")
            return ret
    # set forwarddelay?
    fwdd = brgstps[brgname].get("forwarddelay", int(0))
    # print "fwdd:",fwdd," str:",str(fwdd)," set:",brgset[brgname][3]
    if brgset[brgname][3] != fwdd:
        ret = os.system(
            "/sbin/brctl setfd " + brgname + " " + str(brgset[brgname][3]))
        if ret == int(0):
            getLogger("main").info("forward delay setted")
        else:
            getLogger("main").info("forward delay set failed")
            return ret
    # set hello time?
    hello = brgstps[brgname].get("hellotime", int(0))
    # print "hellotime:",hello," str:",str(hello)," set:",brgset[brgname][5]
    if brgset[brgname][5] != hello:
        ret = os.system(
            "/sbin/brctl sethello " + brgname + " " + str(brgset[brgname][5]))
        if ret == int(0):
            getLogger("main").info("hello time setted")
        else:
            getLogger("main").info("hello time set failed")
            return ret
    return ret


def InitBridgeTable():
    brgnics = GetBridgeNics()
    sess = WafSessionManager()
    # sess.ClearAllBridge()
    for brg in brgnics:
        brgniclist = []
        stpflag = "no"
        i = 0
        for nictuple in brgnics[brg]:
            if i == 0:
                brgniclist.append(nictuple[0])
                stpflag = nictuple[1]
                i += 1
            else:
                brgniclist.append(nictuple)

        stps = GetBridgeStpInfo(brg)
        tmpbrg = WafBridge()
        tmpbrg.name = brg
        tmpbrg.nics = ",".join(brgniclist)
        stp = stps.get(brg, {})
        if stp:
            tmpbrg.ageingtime = stp["ageingtime"]
            tmpbrg.forwarddelay = stp["forwarddelay"]
            tmpbrg.hellotime = stp["hellotime"]
            tmpbrg.maxage = stp["maxage"]
        tmpbrg.level = 32767
        # print stpflag
        if stpflag == "no" or stpflag == "off":
            tmpbrg.stp = 0
        else:
            tmpbrg.stp = 1

        # print tmpbrg
        sess.AddBridge(tmpbrg)


# brgnames is a list
def ConfigBridge(brgnames, reboot=False):
    return
    # session = WafSessionManager()
    #(nics,agengtime,stp,forwarddelay,maxage,hellotime,level)

    # add by suntus start
    # NginxController().restart()
    if not reboot:
        os.system('killall -9 bdwaf')
        os.system('/usr/local/bluedon/bdwaf/sbin/bdwaf')
    # add by suntus end

    brgset = GetBridgeInfoFromConf()
    ret = 0
    for brgname in brgnames:
        # brgset = session.GetBridgeInfo(brgname)
        brgnics = GetBridgeNics()
        # brgstps = {}
        # if brgnics:
        #    brgstps = GetBridgeStpInfo(brgname)
        configstr = ""
        ret = int(0)
        # del bridge?
        if not brgset.get(brgname, {}):
            configstr = "/sbin/ifconfig %s down" % brgname
            ret = os.system(configstr)
            configstr = "/sbin/brctl delbr %s" % brgname
            ret = os.system(configstr)
            if ret != 0:
                getLogger("main").info("delete bridge: " + brgname + " failed")
            # ui have forbidden user modifying the bridge's name,so when deleting a brige,
            # there is no need to add other bridges in database
            # InitNicSetTable()
            RefreshNicSetTable(False)
            return ret
        else:  # add bridge
            if not brgnics.get(brgname, []):  # exist now?
                # configstr = "/sbin/brctl addbr \"" + brgname + "\""
                sys_brs = os.popen("brctl show | grep br | awk '{print $1}'").readlines()
                tmp_brgname = '%s\n' % brgname 
                if tmp_brgname not in sys_brs:
                    configstr = "/sbin/brctl addbr \"%s\"" % brgname
                    ret = os.system(configstr)

                brgniclist = brgset[brgname][0].strip().split(",")
                for nic in brgniclist:
                    os.system('/sbin/ifconfig %s up' % nic)
                brgnicstr = " ".join(brgniclist)
                configstr = "/sbin/brctl addif %s %s" % (brgname, brgnicstr)
                ret = os.system(configstr)

                if ret == 0:
                    # enable bridgs's nic
                    for brgnic in brgniclist:
                        SetNicStatus(brgnic, 1)
                    brgnics = GetBridgeNics()
                    # make sure bridge is running
                    cmdstr = "/sbin/ifconfig %s up" % brgname
                    ret = os.system(cmdstr)
                    if ret != 0:
                        getLogger("main").info("set %s up failed" % brgname)
                else:
                    # make sure bridge is running
                    cmdstr = "/sbin/ifconfig %s up" % brgname
                    ret = os.system(cmdstr)
                    if ret != 0:
                        getLogger("main").info(
                            "add bridge: " + brgname + " failed")
                    return ret
        # do something when modifed or after being added
        # update bridge's eths
        ret = UpdateBridgeNic(brgname, brgnics, brgset)
        if ret != 0:
            return ret
        #tmplist = [brgname]
        #ConfigNic(tmplist)
        """
        #set stp?
        ret = SetStpOnOff(brgname,brgnics,brgset)
        if ret != int(0):
            return ret
        #set stp ageing maxage forwarddelay hellotime?
        ret = SetStpOnOff(brgname,brgnics,brgset)
        if ret != int(0):
            return ret
        ret = SetBridgeStpInfo(brgname,brgstps,brgset)
        if ret != int(0):
            return ret
        #set priority?
        prio = brgset[brgname][6]
        ret = os.system("/sbin/brctl setbridgeprio " + brgname +" "+ str(prio))
        if ret == int(0):
            getLogger("main").info("hello time setted")
        else:
            getLogger("main").info("hello time set failed")
            return ret
        """
    # InitNicSetTable()
    RefreshNicSetTable(False)
    InitBridgeTable()
    return ret


def ConfigAllBridge(bridges=[]):
    """only used to restore the bridge settings in database after rebooted"""
    getLogger('main').info('ConfigAllBridge Start')
    session = WafSessionManager()
    bridgelist_db = session.GetAllBridgeNameInfo()
    # print 'bridgelist:', bridgelist
    bridgelist = GetBridgeInfoFromConf().keys()
    bridge_diff = set(bridgelist) - set(bridgelist_db)
    if bridge_diff:
        getLogger('main').info('conf and db difference %s' % bridge_diff)
    if bridgelist:
        ConfigBridge(bridgelist, True)
    getLogger('main').info('ConfigAllBridge End')


def ClearAllBridge(bridges=[]):
    getLogger('main').info('ClearAllBridge Start')
    session = WafSessionManager()
    bridgelist = session.GetAllBridgeNameInfo()
    print bridgelist

    getLogger('main').info('ClearAllBridge End')

if __name__ == "__main__":
    # print GetBridgeInfoFromConf()
    print GetBridgeNics()
    print WafSessionManager().GetAllNicIpSetInfo().keys()
    # print GetBridgeStpInfo("br0")
    # InitBridgeTable()
    # GetBridgeStpInfo("br0")
    # ConfigBridge(["br2"])
    # ConfigAllBridge()
