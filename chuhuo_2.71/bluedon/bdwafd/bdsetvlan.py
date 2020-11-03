#! /usr/bin/env python
# -*- conding:utf-8 -*-
import MySQLdb
import os
import commands
from common import logger_init
from logging import getLogger
import re
from db import VlanInfo,Session,WafBridge


def getVlan(): # get vlan data from t_vlan
    session=Session()
    vlanport=[]
    for info in session.query(VlanInfo):
        a=[]
        a.append(info.nets)
        a.append(info.vlan_id)
        vlanport.append(a)
    interface=[]
    for i in range(len(vlanport)):
        nic=vlanport[i]
        a=nic[0].split(',')
        interface.append( a[0]+'.'+nic[1])
        interface.append(a[1]+'.'+nic[1])
    return interface

def getBridgeInfo(): #get data from t_bridge
    session=Session()
    brgport=[]
    for info in session.query(WafBridge.nics):
        info=list(tuple(info))
        info=''.join(info)
        brgport.append(info)
    brgport=' '.join(brgport)
    return brgport


def getSysInterface(): #Gets the configured interface
    info=os.popen('ifconfig').read()
    f=open('ifconfig_info.txt','w')
    print >>f,info
    f.close()
    match=re.compile(r'(.+?)\s*?Link')
    f=open('ifconfig_info.txt','r')
    interface=[]
    for line in f:
        if 'Link encap' in line:
           info=match.match(line).groups()
           interface.append(info)
    f.close()
    b=[]
    for i in range(len(interface)):
        a=list(tuple(interface[i]))
        a=''.join(a)
        b.append(a)
    strinfo=' '.join(b)
    listinfo=strinfo.split()
    port=[]
    nic=[]
    for i in range(len(listinfo)):
        if '.'in listinfo[i]:
           port.append(listinfo[i])
        else:
           nic.append(listinfo[i])
    all_port=[]
    all_port.append(port)
    all_port.append(nic)
    return all_port



def VlanConfig(): #config vlan(add and delete)
    logger_init('main','log/vlanconfig.log','INFO')
    config_interface=getVlan()
    configured_port=getSysInterface()
    vlan_port=' '.join(configured_port[0])
    configured_nic=' '.join(configured_port[1])
    for i in range(len(config_interface)):
        if config_interface[i] in vlan_port:
           continue
        else:
           a=config_interface[i].split('.')
           if a[0] not in configured_nic:
              (status,output)=commands.getstatusoutput('ifconfig %s up'%a[0])
              if status!=0:
                 return
           (status,output)=commands.getstatusoutput('vconfig add %s %s'%(a[0],a[1]))
           getLogger('main').info(output)
           (status,output)=commands.getstatusoutput('ifconfig %s up'%config_interface[i])
           if status==0:
              getLogger('main').info('ifconfig %s up OK'%config_interface[i])
    config_interface=' '.join(config_interface)
    vlan_port=configured_port[0]
    brgport=getBridgeInfo()
    for i in range(len(vlan_port)):
        if vlan_port[i] not in config_interface:
           if vlan_port[i] not in brgport:
              (status,output)=commands.getstatusoutput('vconfig rem %s'%vlan_port[i])
              if status==0:
                 getLogger('main').info('vconfig rem %s ok'%vlan_port[i])


if __name__=='__main__':
   VlanConfig()
#   getVlan()
#   getSysInterface()
#   getBridgeInfo()
