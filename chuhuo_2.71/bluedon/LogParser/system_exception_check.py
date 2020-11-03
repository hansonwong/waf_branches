#!/usr/bin/env python
# coding=utf-8

import os
import json
import time
import threading
from adutils.config import fetchone_sql as fetch_3306
from adutils.file_monitor_redis import FsMonitorClient
from adutils.system_info_check import CPUSystemInfoCheck, MEMSystemInfoCheck, DISKSystemInfoCheck


class SystemExceptionCheck(threading.Thread):
    def __init__(self):
        super(SystemExceptionCheck, self).__init__()
        self.setName('exception_check')
        self.event = threading.Event()
        self.cpu_threshold = 90
        self.mem_threshold = 90
        self.disk_threshold = 90

        self.cpu_check = CPUSystemInfoCheck(self.cpu_threshold)
        self.mem_check = MEMSystemInfoCheck(self.mem_threshold)
        self.disk_check = DISKSystemInfoCheck(self.disk_threshold)

        # get threhold from mysql
        self.update_threshold()



    def update_threshold(self, *args, **kwargs):
        print 'update_threshold'
        sql = 'SELECT sValue FROM m_tbconfig WHERE sName="UseFullRate";'
        res = fetch_3306(sql)
        if res.get('sValue') is None:
            return
        try:
            thresholds = json.loads(res['sValue'])
            print thresholds
            self.cpu_threshold = int(thresholds.get('iCpu', 90))
            self.mem_threshold = int(thresholds.get('iRrm', 90))
            self.disk_threshold = int(thresholds.get('iDisk', 90))
        except Exception as e:
            print e
            pass

        self.cpu_check.set_alert_threshold(self.cpu_threshold)
        self.mem_check.set_alert_threshold(self.mem_threshold)
        self.disk_check.set_alert_threshold(self.disk_threshold)


    def run(self):
        # start cpu and mem checking
        fs_client = FsMonitorClient()
        fs_client.start()
        fs_client.add_table_monitor('m_tbconfig', self.update_threshold)

        while 1:
            if self.event.isSet():
                break
            time.sleep(1)

        fs_client.stop()


    def start(self):
        self.cpu_check.start()
        self.mem_check.start()
        self.disk_check.start()
        super(SystemExceptionCheck, self).start()


    def stop(self):
        self.event.set()
        self.cpu_check.stop()
        self.mem_check.stop()
        self.disk_check.stop()


if __name__ == '__main__':
    from adutils.file_monitor_redis import FsMonitor
    fmt = FsMonitor()
    fmt.start()
    el = SystemExceptionCheck()
    el.start()
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    fmt.stop()
    el.stop()


    pass
