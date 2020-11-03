#!/usr/bin/env python
# coding=utf-8


import os
import socket
import ConfigParser

SETTING = 'Setting'
IP = 'ip'
PORT = 'port'
STATUS = 'status'
PROTOCOL = 'protocol'


CFG_PATH = '/usr/local/bluedon/LogParser/conf/udp_sender.conf'

def read_send_conf(path=CFG_PATH):
    ip = '0.0.0.0'
    port = 9999
    proto = 'UDP'
    status = 'off'
    if not os.path.exists(path):
        print '%s is not exists' % path
        return ip, port, proto, status
    try:
    #what to do if log_config_ini DO NOT exist at the beginning
        config = ConfigParser.ConfigParser()
        config.read(path)
        ip = config.get(SETTING, IP)
        port = config.getint(SETTING, PORT)
        proto = config.get(SETTING, PROTOCOL)
        status = config.get(SETTING, STATUS)
    except Exception as e:
        status = 'off'
        pass

    return ip, port, proto, status

def send_out(key, js, ip, port, proto, status):
    # print ip, port, proto, status
    if status == 'off' or status == 'OFF':
        return
    if proto == 'TCP':
        # tcp client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    client.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    # tcp client
    # client.connect(("172.16.3.123", 38888))
    # test
    # instr = raw_input()
    instr = str(key) + ' ' + str(js)
    # tcp client
    # client.send(instr)
    client.sendto(instr, (ip, port))
    # print 'send %s' % instr
    # print client.recv(1024)
    client.close()

if __name__ == '__main__':
    pass
