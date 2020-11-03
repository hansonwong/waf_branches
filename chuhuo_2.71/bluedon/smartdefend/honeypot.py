#! /usr/bin/env python
# -*- coding:utf-8-*-

from networking.net_cmd import process_cmd
from networking.ihandler import ihandler
from db.config import search_data
import os
import sys
import json
import time
import commands

statusfile = '/tmp/fifo/honeypot'
php2pypath = '/tmp/fifo/'
IPTABLES = '/usr/sbin/iptables'

class honey_pot(ihandler):
    def handle_cmd(self, args):
        if len(args) < 1:
            print 'args error'
            return False
        if args[0] == 'help':
            return help()
        RetDict = {}
        Status = False
        Action = 'start'
        if args[0] == 'refresh':
            #Status = check()
            pass
        elif args[0] == 'start' or args[0] == 'stop' or args[0] == 'restart':
            os.system('rm -rf /tmp/fifo/honeypotfile_*.conf')
            data = json.loads(args[1])['honeypotfile']
            open('%s%s'%(php2pypath,data),'w').close()
            if args[0] == 'start':
                Status = start()
            if args[0] == 'stop':
                Status = stop()
            if args[0] == 'restart':
                Status = restart()
        else:
            return False

        RetDict[Action]= 1 if check() else 0
        content = json.dumps(RetDict)
        filew = open(statusfile,'w')
        print>>filew,content
        filew.close()

def check():
    (status,output) = commands.getstatusoutput('ps -ef |grep dionaea |grep -v grep|grep -v p0f|wc -l')
    if status != 0:
        return False
    if int(output) != 0:
        return True
    return False

def check_p0f():
    (status,output) = commands.getstatusoutput('ps -ef |grep p0f |grep -v grep|wc -l')
    if status != 0:
        return False
    if int(output) != 0:
        return True
    return False

def start():
    if check():
        return True
    sql = 'select distinct iServerPort from m_tbHoneypot where iStatus=1'
    datas = search_data(sql)
    lst = list()
    for item in datas:
        lst.append(str(item['iServerPort']))
    ports = ','.join(lst)
    cmd0 = IPTABLES + ' -N HONEYPOTINPUT'
    cmd1 = IPTABLES + ' -I HONEYPOTINPUT -p tcp -m multiport --dports {ports} -j ACCEPT'.format(ports=ports)
    cmd2 = IPTABLES + ' -I HONEYPOTINPUT -p udp -m multiport --dports {ports} -j ACCEPT'.format(ports=ports)
    cmdx = IPTABLES + ' -A HONEYPOTINPUT -m state --state ESTABLISHED -j ACCEPT'
    cmd3 = IPTABLES + ' -I INPUT -j HONEYPOTINPUT'
    commands.getstatusoutput(cmd0)    
    commands.getstatusoutput(cmd1)    
    commands.getstatusoutput(cmd2)
    commands.getstatusoutput(cmdx)
    commands.getstatusoutput(cmd3)
    if not check_p0f():
        process_cmd('/opt/dionaea/bin/p0f -u dionaea -i any -f /opt/dionaea/tmp/p0f.fp -Q /opt/dionaea/tmp/p0f.sock -q -l -d -o /var/log/dionaea/p0f.log')
    process_cmd('/opt/dionaea/bin/dionaea -D -c /opt/dionaea/etc/dionaea/dionaea.conf -u dionaea -g dionaea')
    i = 1
    while i <= 4:
        if check():
            return True
        time.sleep(0.5)
        i = i + 1
    return False

def stop():
    print("honypot.py ---stop().......")
    if not check():
        return True
    process_cmd('killall dionaea')
    process_cmd('killall p0f')
    cmd1 = IPTABLES + ' -D INPUT -j HONEYPOTINPUT'
    commands.getstatusoutput(cmd1)
    cmd2 = IPTABLES + ' -F HONEYPOTINPUT'
    commands.getstatusoutput(cmd2)
    cmd3 = IPTABLES + ' -X HONEYPOTINPUT'
    commands.getstatusoutput(cmd3)
    i = 1
    while i <= 4:
        if not check():
            return True
        time.sleep(0.5)
        i = i + 1
    return False

def restart():
    if not stop():
        return False
    if not start():
        return False
    return True

def OS_restart():
    RetDict = {}
    Action = 'start'
    RetDict[Action]= 1
    content = json.dumps(RetDict)
    if os.path.exists(statusfile):
        with open(statusfile, 'r') as filew:
            state = filew.read()
            print state
         #state ==> {"start": 0} or {"start": 1}
            print content
        #content ==>{"start": 1}
            if content in state:
                print("restart OS and restart dionaea")
                start()

def help():
    print '***\t\"--start\"\tstart honeypot'
    print '***\t\"--stop\"\tstop honeypot'
    print '***\t\"--restart\"\trestart honeypot'
    print '***\t\"--refresh\"\trefresh honeypot status'
    print '***\t\"--help\"\tprint help'
    return True

def printerr(errmsg):
    print errmsg
    help()

if __name__=="__main__":
	OS_restart()
