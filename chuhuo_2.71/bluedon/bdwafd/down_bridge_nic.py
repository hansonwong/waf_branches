#! /usr/bin/env python 
# -*-coding:utf-8-*-

import os
import re

def down_bridge_nic():
    match=re.compile(r'(.+?)\s*?Link')
    fw=open('ifconfig_info.txt','w')
    info=os.popen('ifconfig').read()
    print >>fw,info
    fw.close()
    fr=open('ifconfig_info.txt',"r")
    interface=[]
    for line in fr:
        if 'Link encap' in line:
           info=match.match(line).groups()
           interface.append(info)
    fr.close()
    for i in  range(len(interface)):
        if interface[i][0]!='eth0' and interface[i][0]!='lo':
           os.system('ifconfig %s down'%interface[i][0])
  
if __name__=="__main__":
   down_bridge_nic()
