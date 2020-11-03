#! /usr/bin/env python
# -*- coding:utf-8 -*-


import socket


target_host = "172.16.5.151"
target_port = 33346
data = "/usr/local/bluedon/bdwafd/kugou8051.exe"

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((target_host, target_port))
c.send(data)
response = c.recv(4096)
print response
