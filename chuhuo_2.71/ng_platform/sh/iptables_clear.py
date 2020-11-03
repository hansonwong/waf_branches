#! /usr/bin/env python 
# -*- coding:utf-8 -*-

import os

def clear_iptable():
    os.system('/usr/sbin/iptables -F')
    os.system('/usr/sbin/iptables -X')

    os.system('/usr/sbin/iptables -t nat -F')
    os.system('/usr/sbin/iptables -t nat -X')

    os.system('/usr/sbin/iptables -t mangle -F')
    os.system('/usr/sbin/iptables -t mangle -X')

if __name__=="__main__":
   clear_iptable()
    
