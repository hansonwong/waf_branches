#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import signal
import threading
import time
from logging import getLogger
from task import TaskDispatcher, TaskProcessor
from systeminfo import SystemInfoThread
from daemon import Daemon
from config import config
from common import logger_init
from nginx import init_tenv
from alertor import Alertor
from scantask import ScanTask
from sitechecker import SiteChecker
# from replication import Replication
# from webmonitor_log import WebMonitorLog
# from accessparse import AccessParse
# from scanfile import ScanFile
# from abnormal_analyse import AbnormalAnalysis
# from modeling import Modeling


class BDWafd(Daemon):
    args = {}
    taskDispatcher = None
    systemInfoThread = None
    cwd = os.getcwd()
    app = None

    def __init__(self, args):
        super(BDWafd, self).__init__('/var/run/bdwafd.pid',
                                     debug=config['debug'])
        self.args = args
        self.cwd = self.args['-d'] or config['cwd']
        os.chdir(self.cwd)
        logger_init('main', config['logger']['main']['path'],
                    config['logger']['main']['level'])
        logger_init('webtask', config['logger']['webtask']['path'],
                    config['logger']['webtask']['level'])
        init_tenv()
        self.taskProcessor = TaskProcessor()
        self.systemInfoThread = SystemInfoThread()
        self.taskDispatcher = TaskDispatcher(self.taskProcessor)
        self.alertor = Alertor()
        self.scantask = ScanTask()
        self.sitechecker = SiteChecker()
        # self.cmdreplication = Replication()
        # self.webmonitor = WebMonitorLog()
        # self.accessparse = AccessParse()
        # self.scanfiles = ScanFile()
        # self.abnormalanalyse = AbnormalAnalysis()
        # self.modeling = Modeling()

    def begin(self):
        getLogger('main').debug('BDWafd begin...')
        self.alertor.start()
        self.systemInfoThread.start()
        self.taskProcessor.start()
        self.taskDispatcher.start()
        self.scantask.start()
        self.sitechecker.start()
        # self.cmdreplication.start()
        # self.webmonitor.start()
        # self.accessparse.start()
        # self.scanfiles.start()
        # self.abnormalanalyse.start()
        # self.modeling.start()
        getLogger('main').info('BDWafd begin done.')

    def end(self):
        getLogger('main').debug('BDWafd end...')
        self.alertor.stop()
        self.systemInfoThread.stop()
        self.taskProcessor.stop()
        self.taskDispatcher.stop()
        self.scantask.stop()
        self.sitechecker.stop()
        # self.cmdreplication.stop()
        # self.webmonitor.stop()
        # self.accessparse.stop()
        # self.scanfiles.stop()
        # self.abnormalanalyse.stop()
        # self.modeling.stop()
        getLogger('main').info('BDWafd end done.')
