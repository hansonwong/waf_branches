#! /usr/bin/env python
# -*- coding:utf-8 -*-


import socket
import sys


target_host = "172.16.2.112"
target_port = 9999
data = "/tmp/176535233_httpsasdfaQWsafQW_HeidiSQL9.4.0.5125Setup.exe"
#data = sys.argv[1]
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((target_host, target_port))
c.send(data)
response = c.recv(4096)
print response
c.close()
