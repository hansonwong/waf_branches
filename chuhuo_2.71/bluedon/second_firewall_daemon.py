#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" Second Firewall Application

Usage:
  second_firewall_daemon.py [-hv]
  second_firewall_daemon.py [-d DIR] -s (start|stop|restart)

Arguments:
  DIR app working directory

Options:
  -h --help                  show this help message and exit
  -v --version               show version and exit
  -d NAME                    set the working directory
"""
import commands
import os
import sys
import time
import json

os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

while 1:
    (status, output_mp) = commands.getstatusoutput('ps -ef |grep mp_server |grep -v grep |wc -l')
    (status, output_kni) = commands.getstatusoutput('ps -ef |grep kni |grep -v grep | wc -l')
    (status, output_mpsql) = commands.getstatusoutput('ps -ef|grep mysqld|grep -v grep|wc -l')
    #(status,output_init)=commands.getstatusoutput('ps -ef |grep second_firewall_init.py |grep -v grep | wc -l')
    #print (status,output_init)

    #if int(output_init) > 1:
    #   print 'exit output_init'
    #   exit(0)

    if (int(output_mp) and int(output_kni) and int(output_mpsql) >= 4 and
        os.path.exists('/tmp/mysql3306.sock') and os.path.exists('/tmp/mysql3307.sock')):
        print "mp_server  mysql"
        break
    else:
        time.sleep(1)

from core.daemon import Daemon
from core.task import TaskDispatcher, TaskProcessor
from utils.docopt import docopt
from utils.logger_init import logger_init
from db.config import mkdir_file


class SecondFirewall(Daemon):
    args={}
    taskDispatcher=None
    taskProcessor=None
    cwd = os.getcwd()
    nic=None

    def __init__(self,args):
        super(SecondFirewall,self).__init__('/var/run/second_firewall.pid',debug=True)
        self.args=args

        # 2016-8-16 防止fifo文件夹不存在导致报错
        mkdir_file('/Data/apps/wwwroot/firewall/fifo/second_firewall.fifo', 'fifo')

        self.cwd='/usr/local/bluedon'
        os.chdir(self.cwd)
        logger_init('main','log/main.log','INFO')
        logger_init('webtask','log/webtask.log','INFO')
        self.taskProcessor = TaskProcessor()
        self.taskDispatcher = TaskDispatcher(self.taskProcessor)

    def begin(self):
        self.taskProcessor.start()
        self.taskDispatcher.start()

    def end(self):
        self.taskDispatcher.stop()
        self.taskProcessor.stop()


if __name__=='__main__':
    args=docopt(__doc__, version='1.0.0')
    app = SecondFirewall(args)
    SecondFirewall.app = app

    if not os.path.isdir('/tmp/fifo'):
        os.mkdir('/tmp/fifo')
    if args['start']:
        app.start()
        print "SecondFirewall start.........."

    elif args['stop']:
        os.system('/etc/antidetect/antidet stop')
        content = json.dumps({'start': 0})
        fw2=open('/tmp/fifo/revcamera', 'w')
        print>>fw2,content
        fw2.close()

        os.system('killall snort')
        fw=open('/tmp/fifo/revscan','w')
        print>>fw,content
        fw.close()

        app.stop()
        print "SecondFirewall end..........."

    elif args['restart']:
        app.restart()

    else:
        exit(0)



