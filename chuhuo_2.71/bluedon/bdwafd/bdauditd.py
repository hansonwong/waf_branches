#!/usr/bin/env python
# -*- coding: utf-8 -*-

# created by szl 2014-03-14

""" Bluedon Web Application Firewall Audit Log Collector Daemon

Usage:
  bdauditd.py [-hv]
  bdauditd.py [-d DIR] -s (start|stop|restart)

Arguments:
  DIR app working directory

Options:
  -h --help                  show this help message and exit
  -v --version               show version and exit
  -d NAME                    set the working directory
"""

import os
import time
import MySQLdb
import stat
import os
import time
import threading
import logging
from common import logger_init
from config import config
from logging import getLogger
from docopt import docopt
from daemon import Daemon
from bdsyslog import SysLog
from parserddos import fileparser, DuDDOSTask
from bdblocked import seniorblock
from weboutlog import parserweblog
from dispatcher_audit_analyze import DispatcherAuditAnalyze
# from scan_virus import ScanVirus
from report_task import ReportTask


class BDAuditd(Daemon):
    args = {}
    fileParser = None
    syslog = None
    cwd = os.getcwd()

    def __init__(self, args):
        super(BDAuditd, self).__init__('/var/run/bdauditd.pid')
        self.args = args
        self.cwd = self.args['-d'] or config['cwd']
        os.chdir(self.cwd)
        logger_init('audit', config['logger']['audit']['path'],
                    config['logger']['audit']['level'])
        logger_init('audittask', config['logger']['audittask']['path'],
                    config['logger']['audittask']['level'])
        # self.syslog     = SysLog()
        self.dispatch = DispatcherAuditAnalyze()
        self.ddoslog = DuDDOSTask()
        self.ddosset = fileparser()
        self.blocked = seniorblock()
        self.weblog = parserweblog()
        self.reporttask = ReportTask()
        # self.scanvirus = ScanVirus()

    def begin(self):
        getLogger('audit').debug('BDAuditd begin...')
        # self.syslog.start()
        self.dispatch.start()
        self.ddoslog.start()
        self.ddosset.start()
        self.blocked.start()
        self.weblog.start()
        self.reporttask.start()
        # self.scanvirus.start()
        getLogger('audit').info('BDAuditd begin done.')

    def end(self):
        getLogger('audit').debug('BDAuditd end...')
        # self.syslog.stop()
        # self.scanvirus.stop()
        self.reporttask.stop()
        self.dispatch.stop()
        self.ddoslog.stop()
        self.ddosset.stop()
        self.blocked.stop()
        self.weblog.stop()
        getLogger('audit').info('BDAuditd end done.')

if __name__ == '__main__':
    args = docopt(__doc__, version='1.0.0')
    daemon = BDAuditd(args)
    if args['start']:
        daemon.start()
    elif args['stop']:
        daemon.stop()
    elif args['restart']:
        daemon.restart()
    else:
        print(__doc__)
        exit(0)
