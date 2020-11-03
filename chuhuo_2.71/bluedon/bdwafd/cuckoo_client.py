#! /usr/bin/env python
# -*- coding:utf-8 -*-


import socket
import sys


# target_host = "172.16.2.155"
# target_port = 33347
# #data = "/usr/local/bluedon/bdwafd/kugou8051.exe"
# data = sys.argv[1]
# c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# c.connect_ex((target_host, target_port))
# c.send(data)
# response = c.recv(4096)
# # print response

target_host = "172.16.2.112"
target_port = 9999
data = sys.argv[1]#.replace("\\","|a|")
#data = sys.argv[1]
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((target_host, target_port))
c.send(data)
response = c.recv(4096)
c.close()
