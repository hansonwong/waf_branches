#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import threading
import shutil
import subprocess
import json
import redis
import MySQLdb
from logging import getLogger
from db import conn_scope
from config import config
from modsecparser import split_log, processtask


class DispatcherAuditAnalyze(threading.Thread):
    def __init__(self):
        self.quit = 0
        self.item = None
        self.lines_list = []

        super(DispatcherAuditAnalyze, self).__init__(
            name=self.__class__.__name__)

    def start(self):
        getLogger('audit').debug(self.__class__.__name__ + ' starting...')
        super(DispatcherAuditAnalyze, self).start()
        getLogger('audit').info(self.__class__.__name__ + ' started.')

    def stop(self):
        getLogger('audit').debug(self.__class__.__name__ + ' Exiting...')
        self.event.set()
        self.join()
        self.quit = 1
        getLogger('audit').info(self.__class__.__name__ + ' Exited.')

    def proc(self):
        if self.item['type'] == 'message':
            log_source, _, log_msg = self.item['data'].partition('|')
            self.lines_list.append((log_source, split_log(log_msg)))
            if len(self.lines_list) == 200:
                processtask(self.lines_list)
                self.lines_list = []

    def run(self):
        while True:
            try:
                if self.quit == 1:
                    return
                try:
                    rc = redis.StrictRedis(host='localhost', port=6379)
                    rc.ping()
                    ps = rc.pubsub()
                    ps.subscribe('bdwaf')
                except Exception, e:
                    getLogger(
                        'audit').error('redis connect fail, try connect...')
                    time.sleep(1)
                    continue

                while True:
                    try:
                        if self.quit == 1:
                            return
                        try:
                            self.item = ps.get_message()
                        except Exception, e:
                            getLogger('audit').error('redis disconnect')
                            break
                        if not self.item:
                            processtask(self.lines_list)
                            self.lines_list = []
                            time.sleep(0.1)
                        else:
                            self.proc()
                    except Exception, e:
                        getLogger('audit').exception(e)
            except Exception, e:
                getLogger('audit').exception(e)

if __name__ == '__main__':
    DispatcherAuditAnalyze().proc()
