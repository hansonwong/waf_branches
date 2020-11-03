#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" Second Firewall LOG IMPORT Application

Usage:
  mysql_log_daemon.py [-hv]
  mysql_log_daemon.py [-d DIR] -s (start|stop|restart)

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

os.chdir('/usr/local/bluedon')
if '/usr/local/bluedon' not in sys.path:
    sys.path.append('/usr/local/bluedon')

while 1:
       """(status,output)=commands.getstatusoutput("ps -ef |grep /home/ng_platform/bd_dpdk_warper/server/mp_server|awk '{print $8}'")
       mp_server = ['/home/ng_platform/bd_dpdk_warper/server/mp_server']
       mp_server_set = set(mp_server)
       mp_server_process = output.split('\n')
       mp_server_process = set(mp_server_process)"""

       (status,output_mp)=commands.getstatusoutput('ps -ef |grep mp_server |grep -v grep |wc -l')
       (status,output_kni)=commands.getstatusoutput('ps -ef |grep kni |grep -v grep | wc -l')

       """(status,output) = commands.getstatusoutput("ps -ef |grep /usr/sbin/mysqld|awk '{print $8}'")
       mysql = ['/usr/sbin/mysqld']
       mysql_set = set(mysql)
       mysql_process = output.split('\n')
       mysql_process = set(mysql_process)"""

       if int(output_mp) and int(output_kni) and os.path.exists('/tmp/mysql3306.sock') and os.path.exists('/tmp/mysql3307.sock'):
          print "mp_server  mysql"
          break
       else:
          time.sleep(1)

import os
import threading
import logging
import sys
import ConfigParser
import commands
import utils.crontab
import utils.thread
from utils.docopt import docopt
from utils.logger_init import logger_init
from utils.file_monitor import FsMonitor
from logging import getLogger
from core.daemon import Daemon
from reportlog.log_mail_config import LogMail
from homepage.statistics import HomePageUpdate,stop_traffic_info
# from reportlog.mysql_get_tblog3 import LogImport
from reportlog.mysql_get_tblog import LogImport
from reportlog.log_config import set_crontab,log_config_recovery
from reportlog.log_config import msmtprc_path,muttrc_path,read_config_ini,log_cron_recovery
from reportlog.traffic_statistic import TrafficStatistic
from db.mysql_observer import MysqlUpdateObserver

class MysqlLogDaemon(Daemon):

    cwd = os.getcwd()

    def __init__(self,args):
        super(MysqlLogDaemon,self).__init__('/var/run/mysql_log_daemon.pid',debug=True)
        self.name = self.__class__.__name__
        self.cwd='/usr/local/bluedon'
        os.chdir(self.cwd)
        logger_init('log_daemon','log/log_daemon.log','DEBUG')

        # log_config recover
        log_cron_recovery()
        log_config_recovery()

        # self.wb_log = WebLog()
        self.import_log = LogImport()
        self.hmp = HomePageUpdate()
        self.logmail = LogMail()
        self.tfs = TrafficStatistic()
        self.myob = MysqlUpdateObserver()
        self.fsmt = FsMonitor()

    def begin(self):
        self.import_log.start()
        # self.wb_log.start()
        self.hmp.start()
        self.logmail.start()
        self.tfs.start()
        self.myob.start()
        self.fsmt.start()
        getLogger('log_daemon').debug('Mysql Log Daemon is Started')
        pass

    def end(self):
        self.import_log.stop()
        # self.wb_log.stop()
        self.tfs.stop()
        self.hmp.stop()
        self.logmail.stop()
        self.myob.stop()
        self.fsmt.stop()
        getLogger('log_daemon').debug('Mysql Log Daemon is Stopping...all Stop')


#if __name__ == '__main__':
#     arg = {'cycle':'every_day'}
#     set_crontab(arg)
##    read_config_ini('LOG Config')

if __name__=='__main__':
   args=docopt(__doc__, version='1.0.0')
   app = MysqlLogDaemon(args)

   if args['start']:
      getLogger('log_daemon').debug('Mysql Daemon Starting...')
      app.start()

   elif args['stop']:
      getLogger('log_daemon').debug('Mysql Log Daemon is Stopping...')
      app.stop()
      print 'main: stopped'
      getLogger('log_daemon').debug('Mysql Log Daemon is Stopped')
      #stop_traffic_info()

   elif args['restart']:
      getLogger('log_daemon').debug('Mysql Log Daemon is Stopping...')
      app.stop()
      #stop_traffic_info()
      print 'main: stop'
      getLogger('log_daemon').debug('Mysql Log Daemon is Stopped')
      getLogger('log_daemon').debug('Mysql Daemon Restarting...')
      app.start()

   else:
      exit(0)


