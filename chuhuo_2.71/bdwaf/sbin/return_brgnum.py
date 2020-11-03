#! /usr/bin/env python
# -*-coding:utf-8-*-

import os
import sys
from collections import defaultdict
import re
import linecache

def get_bridgename(nic_port):

    args_port=[]  
    args_port.append(nic_port)
    inport=set(args_port)

    brg_nic=defaultdict(list)
    bridge_info=os.popen('brctl show')
    for line in bridge_info:
        brg = line.strip().split()
        if len(brg)>4 or len(brg)==3:
           continue
        elif len(brg)==4:
             brgname=brg[0]
             brg_nic[brgname].append(brg[-1])
        else:
             brg_nic[brgname].append(brg[-1])

    for k,v in brg_nic.items():
        nic_num=set(''.join(v).split('vEth'))
        if inport & nic_num:
           return k
    return 


def get_localmac(nic_port,mac):

    brgname=get_bridgename(nic_port)
    if not brgname:
       return 

    showmac_info=os.popen('brctl showmacs %s'%brgname)
    mac_port_local=[]
    for info in showmac_info:
        info=info.strip().split()
        tmp={}
        if len(info)==4:
           tmp['port_no']=info[0]
           tmp['mac']=info[1]
           tmp['islocal']=info[2]
           mac_port_local.append(tmp)
    portno=''
    for info in mac_port_local:
        if info['mac']==mac:
           portno=info['port_no']
           
    for info in mac_port_local:
        if portno==info['port_no'] and info['islocal']=='yes':
           return info['mac']
    return 

def get_nic_num():
    
    fw=open('nic_num.txt','w')
    if len(sys.argv)!=3:
       print>>fw,-1
       return 

    mac_compare=get_localmac(sys.argv[1],sys.argv[2])
    if not mac_compare:
       print>>fw,-1
       return 

    macstr='([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}'
    ifconfig_info=os.popen('ifconfig -a')
    mac_pattern=re.compile(r'(ether %s)'%macstr)
    pattern=re.compile(macstr)
    nic_pattern=re.compile(r'(.*?):\s*?')
    nic_mac={}
    for line in ifconfig_info:
        if "mtu 1500"in line:
            nic_match=nic_pattern.match(line)
            if nic_match:
               nic=nic_match.group()
        for mac in re.finditer(mac_pattern, str(line)):
            if mac:
               macaddr=pattern.search(mac.group())
               if macaddr:
                  if macaddr.group()!='00:00:00:00:00:00':
                     nic_mac[nic]=macaddr.group()
    for k,v in nic_mac.items():
        if mac_compare==v:
           if 'br' not in k:
               num=filter(str.isdigit,k)
               print>>fw,num
    fw.close()
          

if __name__=='__main__':
   get_nic_num()
