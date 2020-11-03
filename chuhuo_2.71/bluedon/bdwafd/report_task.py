#! /usr/bin/env python
# -*- coding:utf-8 -*-

import time
import threading
from subprocess import Popen, PIPE
from logging import getLogger


class ReportTask(threading.Thread):
    '''
    报表任务
    '''

    def __init__(self):
        super(ReportTask, self).__init__(name=self.__class__.__name__)
        self.event = threading.Event()

    def start(self):
        getLogger('audit').debug(self.__class__.__name__ + ' starting...')
        super(ReportTask, self).start()
        getLogger('audit').info(self.__class__.__name__ + ' started.')

    def stop(self):
        getLogger('audit').debug(self.__class__.__name__ + ' Exiting...')
        self.event.set()
        self.join()
        getLogger('audit').info(self.__class__.__name__ + ' Exited.')

    def run(self):
        '''每天4:00定时执行报表任务'''
        while 1:
            try:
                if self.event.isSet():
                    break
                now = time.localtime()
                if now.tm_hour == 4 and now.tm_min == 0:
                    Popen('php /Data/apps/wwwroot/waf/www/yii timer-report/do',
                          stdout=PIPE, stdin=PIPE, shell=True)
                    getLogger('audit').info('timer-report/do start at %s' % now)
                    time.sleep(24 * 60 * 60)  # sleep 1 day
                else:
                    time.sleep(10)
            except Exception, e:
                getLogger('audit').exception(e)


if __name__ == '__main__':
    ReportTask().start()
